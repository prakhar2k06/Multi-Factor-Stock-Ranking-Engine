from backend.data.universe import load_sp500_universe
import numpy as np
import pandas as pd
import yfinance as yf

class FactorCalculator:
    def __init__(self,fundamentalcalculator, provider):
        self.fundamental = fundamentalcalculator
        self.provider = provider
        self.universe = [t for t in load_sp500_universe()]

    def z_score_calculator(self, series):
        s = pd.Series(series, dtype=float)

        valid = s.dropna()
        if len(valid) < 2:
            return {k: None for k in series}

        z = (valid - valid.mean()) / valid.std()

        result = {k: (z[k] if k in z else None) for k in series}
        return result

    def value_score_calculator(self):
        tickers = self.universe

        bm = {t: self.fundamental.get_book_to_market(yf.Ticker(t)) for t in tickers}
        ep = {t: self.fundamental.get_ep(yf.Ticker(t)) for t in tickers}
        cp = {t: self.fundamental.get_cp(yf.Ticker(t)) for t in tickers}
        sp = {t: self.fundamental.get_sp(yf.Ticker(t)) for t in tickers}

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
        tickers = self.universe

        mc = {t: self.fundamental.get_market_cap(yf.Ticker(t)) for t in tickers}

        mc_rev = {}

        for t, m in mc.items():
            if m is None or m <= 0:
                mc_rev[t] = None
            else:
                mc_rev[t] = -np.log(m)

        return self.z_score_calculator(mc_rev)
    
    def momentum_score_calculator(self):
        tickers = self.universe

        m12 = {t: self.fundamental.get_momentum(yf.Ticker(t)) for t in tickers}
        m6 = {t: self.fundamental.get_6m_momentum(yf.Ticker(t)) for t in tickers}
        m3 = {t: self.fundamental.get_3m_momentum(yf.Ticker(t)) for t in tickers}

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
        tickers = self.universe

        vol252 = {t: self.fundamental.get_volatility(yf.Ticker(t)) for t in tickers}
        vol180 = {t: self.fundamental.get_vol_180(yf.Ticker(t)) for t in tickers}

        vol252_r = {t: (-vol252[t] if vol252[t] is not None else None) for t in tickers}
        vol180_r = {t: (-vol180[t] if vol180[t] is not None else None) for t in tickers}

        z_252 = self.z_score_calculator(vol252_r)
        z_180 = self.z_score_calculator(vol180_r)

        scores={}

        for t in tickers:
            vals = [z_252[t], z_180[t]]
            vals = [v for v in vals if v is not None]

            scores[t] = np.mean(vals) if vals else None

        return scores
    
    def quality_score_calculator(self):
        tickers = self.universe

        roe = {t: self.fundamental.get_roe(yf.Ticker(t)) for t in tickers}
        gp = {t: self.fundamental.get_gross_profitability(yf.Ticker(t)) for t in tickers}
        pm = {t: self.fundamental.get_profit_margin(yf.Ticker(t)) for t in tickers}
        lev = {t: self.fundamental.get_leverage(yf.Ticker(t)) for t in tickers}

        lev_rev = {t: (-lev[t] if lev[t] is not None else None) for t in lev}

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
        tickers = self.universe

        beta = {t: self.fundamental.get_beta(yf.Ticker(t)) for t in tickers}

        beta_rev = {t: (-beta[t] if beta[t] is not None else None) for t in beta}

        return self.z_score_calculator(beta_rev)
    
