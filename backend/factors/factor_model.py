"""
factor_model.py

Computes cross-sectional factor scores for a stock universe.
Implements multi-signal factors with winsorization and sector-neutral z-scoring.
"""

from typing import Any

import numpy as np
import pandas as pd
from pandas import Series

from backend.data.universe import load_sp500_universe
from backend.metrics.metric_builder import MetricBuilder


class FactorCalculator:
    def __init__(self, metric_builder: MetricBuilder) -> None:
        self.metric_builder: MetricBuilder = metric_builder
        raw_universe: list[str] = [t for t in load_sp500_universe()]
        self.metrics: dict[str, dict[str, Any] | None] = (
            self.metric_builder.load_universe_metrics(raw_universe)
        )
        self.universe: list[str] = [
            t for t in raw_universe if self.metrics.get(t) is not None
        ]
        self.sector_map: dict[str, str] = {
            t: self.metrics[t]["sector"]
            for t in self.universe
            if self.metrics[t].get("sector") is not None
        }

    def winsorize(self, raw_scores: dict, limit: float = 3.0) -> dict:
        """
        Clips extreme values using mean ± (limit × std).
        """
        s: Series[Any] = pd.Series(raw_scores, dtype=float)
        valid: Series[Any] = s.dropna()

        if len(valid) < 2:
            return raw_scores

        mean: float = valid.mean()
        std: float = valid.std()

        upper: float = mean + limit * std
        lower: float = mean - limit * std

        clipped: Series[Any] = s.clip(lower, upper)
        return clipped.to_dict()

    def z_score_calculator(self, raw_scores: dict) -> dict:
        """
        Computes sector neutral Z-scores with global Z-score fallback.
        """
        result: dict = {}
        sector_groups: dict = {}

        # Group tickers by sector
        for t in self.universe:
            sector: str | None = self.sector_map.get(t)
            if sector is None:
                continue
            sector_groups.setdefault(sector, []).append(t)

        # Sector-level z-scoring
        for sector, tickers in sector_groups.items():
            values: dict = {t: raw_scores.get(t) for t in tickers}

            clean_vals: dict = {t: v for t, v in values.items() if v is not None}

            if len(clean_vals) >= 2:
                mean: np.floating[Any] = np.mean(list(clean_vals.values()))
                std: np.floating[Any] = np.std(list(clean_vals.values()))
                if std > 0:
                    for t in tickers:
                        v = values.get(t)
                        result[t] = (v - mean) / std if v is not None else None
                    continue

            # If sector normalization fails, use global fallback
            for t in tickers:
                result[t] = None

        # Global fallback z-scoring
        global_s: Series[float] = pd.Series(raw_scores, dtype=float)
        global_valid: Series[float] = global_s.dropna()

        if len(global_valid) >= 2:
            global_mean: float = global_valid.mean()
            global_std: float = global_valid.std()
            global_z = (global_valid - global_mean) / global_std

            for t in self.universe:
                if result.get(t) is None:
                    v = raw_scores.get(t)
                    result[t] = global_z[t] if t in global_z else None

        return result

    def value_score_calculator(self) -> dict:
        """
        Value factor Z-score calculation using multiple valuation signals.
        """
        tickers: list = self.universe

        bm: dict = {t: self.metrics[t].get("book_to_market") for t in tickers}
        ep: dict = {t: self.metrics[t].get("earnings_to_price") for t in tickers}
        cp: dict = {t: self.metrics[t].get("cashflow_to_price") for t in tickers}
        sp: dict = {t: self.metrics[t].get("sales_to_price") for t in tickers}

        bm = self.winsorize(bm)
        ep = self.winsorize(ep)
        cp = self.winsorize(cp)
        sp = self.winsorize(sp)

        z_bm: dict = self.z_score_calculator(bm)
        z_ep: dict = self.z_score_calculator(ep)
        z_cp: dict = self.z_score_calculator(cp)
        z_sp: dict = self.z_score_calculator(sp)

        scores: dict = {}

        for t in tickers:
            vals: list = [z_bm[t], z_ep[t], z_cp[t], z_sp[t]]
            vals: list = [v for v in vals if v is not None]

            scores[t] = np.mean(vals) if vals else None

        return scores

    def size_score_calculator(self) -> dict:
        """
        Size factor Z-score calculation using inverse of log market capitalization.
        """
        tickers: list = self.universe

        mc: dict = {t: self.metrics[t].get("market_cap") for t in tickers}

        mc_rev: dict = {}

        for t, m in mc.items():
            if m is None or m <= 0:
                mc_rev[t] = None
            else:
                mc_rev[t] = -np.log(m)

        mc_rev = self.winsorize(mc_rev)

        return self.z_score_calculator(mc_rev)

    def momentum_score_calculator(self) -> dict:
        """
        Momentum factor Z-score calculation using momentum of different time frames.
        """
        tickers: list = self.universe

        m12: dict = {t: self.metrics[t].get("momentum_12_1") for t in tickers}
        m6: dict = {t: self.metrics[t].get("momentum_6_1") for t in tickers}
        m3: dict = {t: self.metrics[t].get("momentum_3_1") for t in tickers}

        m12 = self.winsorize(m12)
        m6 = self.winsorize(m6)
        m3 = self.winsorize(m3)

        z_12: dict = self.z_score_calculator(m12)
        z_6: dict = self.z_score_calculator(m6)
        z_3: dict = self.z_score_calculator(m3)

        scores: dict = {}

        for t in tickers:
            vals: list = [z_12[t], z_6[t], z_3[t]]
            vals: list = [v for v in vals if v is not None]

            scores[t] = np.mean(vals) if vals else None

        return scores

    def lowvol_score_calculator(self) -> dict:
        """
        Low-vol factor Z-score calculation using inverse of volatility.
        """
        tickers: list = self.universe

        vol252: dict = {t: self.metrics[t].get("volatility_252") for t in tickers}
        vol180: dict = {t: self.metrics[t].get("volatility_180") for t in tickers}

        vol252_r: dict = {
            t: (-vol252[t] if vol252[t] is not None else None) for t in tickers
        }
        vol180_r: dict = {
            t: (-vol180[t] if vol180[t] is not None else None) for t in tickers
        }

        vol252_r = self.winsorize(vol252_r)
        vol180_r = self.winsorize(vol180_r)

        z_252: dict = self.z_score_calculator(vol252_r)
        z_180: dict = self.z_score_calculator(vol180_r)

        scores: dict = {}

        for t in tickers:
            vals: list = [z_252[t], z_180[t]]
            vals: list = [v for v in vals if v is not None]

            scores[t] = np.mean(vals) if vals else None

        return scores

    def quality_score_calculator(self) -> dict:
        """
        Quality factor Z-score calculation using profitability and leverage signals.
        """
        tickers: list = self.universe

        roe: dict = {t: self.metrics[t].get("roe") for t in tickers}
        gp: dict = {t: self.metrics[t].get("gross_profitability") for t in tickers}
        pm: dict = {t: self.metrics[t].get("profit_margin") for t in tickers}
        lev: dict = {t: self.metrics[t].get("leverage") for t in tickers}

        lev_rev: dict = {t: (-lev[t] if lev[t] is not None else None) for t in lev}

        roe = self.winsorize(roe)
        gp = self.winsorize(gp)
        pm = self.winsorize(pm)
        lev_rev = self.winsorize(lev_rev)

        z_roe: dict = self.z_score_calculator(roe)
        z_gp: dict = self.z_score_calculator(gp)
        z_pm: dict = self.z_score_calculator(pm)
        z_lev: dict = self.z_score_calculator(lev_rev)

        scores: dict = {}

        for t in tickers:
            vals: list = [z_roe[t], z_gp[t], z_pm[t], z_lev[t]]
            vals: list = [v for v in vals if v is not None]

            scores[t] = np.mean(vals) if vals else None

        return scores

    def market_risk_score_calculator(self) -> dict:
        """
        Market Risk factor Z-score calculation using inverse of beta.
        """
        tickers: list = self.universe

        beta: dict = {t: self.metrics[t].get("beta") for t in tickers}

        beta_rev: dict = {t: (-beta[t] if beta[t] is not None else None) for t in beta}

        beta_rev = self.winsorize(beta_rev)

        return self.z_score_calculator(beta_rev)
