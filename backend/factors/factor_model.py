"""
factor_model.py

Computes cross-sectional factor scores for a stock universe.
Implements multi-signal factors with winsorization and sector-neutral z-scoring.
"""

from backend.data.universe import load_sp500_universe
import numpy as np
import pandas as pd
import yfinance as yf

class FactorCalculator:
    def __init__(self,fundamentalcalculator, provider):
        """
        Initialize the factor model using the fundamentals calculator and provider.
        """
        self.fundamental = fundamentalcalculator
        self.provider = provider
        # Universe is a list of valid S&P 500 tickers
        self.universe = [t for t in load_sp500_universe()]
        # Precomputed sector mapping
        self.sector_map = {t: self.fundamental.get_sector(yf.Ticker(t)) for t in self.universe}

    def winsorize(self, raw_scores, limit = 3.0):
        """
        Clips extreme values using mean ± (limit × std).
        """
        s = pd.Series(raw_scores, dtype=float)
        valid = s.dropna()

        if len(valid) < 2:
            return raw_scores
        
        mean = valid.mean()
        std = valid.std()

        upper = mean + limit * std
        lower = mean - limit * std

        clipped = s.clip(lower,upper)
        return clipped.to_dict()
        
    def z_score_calculator(self, raw_scores):
        """
        Computes sector neutral Z-scores with global Z-score fallback.
        """
        result = {}
        sector_groups = {}

        # Group tickers by sector
        for t in self.universe:
            sector = self.sector_map.get(t)
            if sector is None:
                continue
            sector_groups.setdefault(sector, []).append(t)

         # Sector-level z-scoring
        for sector,tickers in sector_groups.items():
            values = {t: raw_scores.get(t) for t in tickers}

            clean_vals = {t: v for t, v in values.items() if v is not None}

            if len(clean_vals) >= 2:
                mean = np.mean(list(clean_vals.values()))
                std = np.std(list(clean_vals.values()))
                if std > 0:
                    for t in tickers:
                        v = values.get(t)
                        result[t] = (v - mean) / std if v is not None else None
                    continue
            
            # If sector normalization fails, use global fallback
            for t in tickers:
                result[t] = None

        # Global fallback z-scoring
        global_s = pd.Series(raw_scores, dtype=float)   
        global_valid = global_s.dropna()

        if len(global_valid) >= 2:
            global_mean = global_valid.mean()
            global_std= global_valid.std()
            global_z = (global_valid - global_mean) / global_std

            for t in self.universe:
                if result.get(t) is None:
                    v = raw_scores.get(t)
                    result[t] = global_z[t] if t in global_z else None
                    
        return result
 
    def value_score_calculator(self):
        """
        Value factor Z-score calculation using multiple valuation signals.
        """
        tickers = self.universe

        bm = {t: self.fundamental.get_book_to_market(yf.Ticker(t)) for t in tickers}
        ep = {t: self.fundamental.get_ep(yf.Ticker(t)) for t in tickers}
        cp = {t: self.fundamental.get_cp(yf.Ticker(t)) for t in tickers}
        sp = {t: self.fundamental.get_sp(yf.Ticker(t)) for t in tickers}

        bm = self.winsorize(bm)
        ep = self.winsorize(ep)
        cp = self.winsorize(cp)
        sp = self.winsorize(sp)

        z_bm = self.z_score_calculator(bm)
        z_ep = self.z_score_calculator(ep)
        z_cp = self.z_score_calculator(cp)
        z_sp = self.z_score_calculator(sp)

        scores={}

        for t in tickers:
            vals = [z_bm[t], z_ep[t], z_cp[t], z_sp[t]]
            vals = [v for v in vals if v is not None]

            scores[t] = np.mean(vals) if vals else None

        return scores 

    def size_score_calculator(self):
        """
        Size factor Z-score calculation using inverse of log market capitalization.
        """
        tickers = self.universe

        mc = {t: self.fundamental.get_market_cap(yf.Ticker(t)) for t in tickers}

        mc_rev = {}

        for t, m in mc.items():
            if m is None or m <= 0:
                mc_rev[t] = None
            else:
                mc_rev[t] = -np.log(m)

        mc_rev = self.winsorize(mc_rev)

        return self.z_score_calculator(mc_rev)
    
    def momentum_score_calculator(self):
        """
        Momentum factor Z-score calculation using momentum of different time frames.
        """
        tickers = self.universe

        m12 = {t: self.fundamental.get_momentum(yf.Ticker(t)) for t in tickers}
        m6 = {t: self.fundamental.get_6m_momentum(yf.Ticker(t)) for t in tickers}
        m3 = {t: self.fundamental.get_3m_momentum(yf.Ticker(t)) for t in tickers}

        m12 = self.winsorize(m12)
        m6 = self.winsorize(m6)
        m3 = self.winsorize(m3)

        z_12 = self.z_score_calculator(m12)
        z_6 = self.z_score_calculator(m6)
        z_3 = self.z_score_calculator(m3)

        scores={}

        for t in tickers:
            vals = [z_12[t], z_6[t], z_3[t]]
            vals = [v for v in vals if v is not None]

            scores[t] = np.mean(vals) if vals else None

        return scores
    
    def lowvol_score_calculator(self):
        """
        Low-vol factor Z-score calculation using inverse of volatility.
        """
        tickers = self.universe

        vol252 = {t: self.fundamental.get_volatility(yf.Ticker(t)) for t in tickers}
        vol180 = {t: self.fundamental.get_vol_180(yf.Ticker(t)) for t in tickers}

        vol252_r = {t: (-vol252[t] if vol252[t] is not None else None) for t in tickers}
        vol180_r = {t: (-vol180[t] if vol180[t] is not None else None) for t in tickers}

        vol252_r = self.winsorize(vol252_r)
        vol180_r = self.winsorize(vol180_r)

        z_252 = self.z_score_calculator(vol252_r)
        z_180 = self.z_score_calculator(vol180_r)

        scores={}

        for t in tickers:
            vals = [z_252[t], z_180[t]]
            vals = [v for v in vals if v is not None]

            scores[t] = np.mean(vals) if vals else None

        return scores
    
    def quality_score_calculator(self):
        """
        Quality factor Z-score calculation using profitability and leverage signals.
        """
        tickers = self.universe

        roe = {t: self.fundamental.get_roe(yf.Ticker(t)) for t in tickers}
        gp = {t: self.fundamental.get_gross_profitability(yf.Ticker(t)) for t in tickers}
        pm = {t: self.fundamental.get_profit_margin(yf.Ticker(t)) for t in tickers}
        lev = {t: self.fundamental.get_leverage(yf.Ticker(t)) for t in tickers}

        lev_rev = {t: (-lev[t] if lev[t] is not None else None) for t in lev}

        roe = self.winsorize(roe)
        gp = self.winsorize(gp)
        pm = self.winsorize(pm)
        lev_rev = self.winsorize(lev_rev)

        z_roe = self.z_score_calculator(roe)
        z_gp = self.z_score_calculator(gp)
        z_pm = self.z_score_calculator(pm)
        z_lev = self.z_score_calculator(lev_rev)

        scores={}

        for t in tickers:
            vals = [z_roe[t], z_gp[t], z_pm[t], z_lev[t]]
            vals = [v for v in vals if v is not None]

            scores[t] = np.mean(vals) if vals else None

        return scores
    
    def market_risk_score_calculator(self):
        """
        Market Risk factor Z-score calculation using inverse of beta.
        """
        tickers = self.universe

        beta = {t: self.fundamental.get_beta(yf.Ticker(t)) for t in tickers}

        beta_rev = {t: (-beta[t] if beta[t] is not None else None) for t in beta}

        beta_rev = self.winsorize(beta_rev)

        return self.z_score_calculator(beta_rev)
    
