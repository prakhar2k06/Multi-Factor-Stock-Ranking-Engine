from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any

from backend.data_store.storage import DataStore
from backend.fundamentals.fundamental_calculator import FundamentalCalculator

MAX_WORKERS = 4


class MetricBuilder:
    METRICS_CATEGORY = "derived_metrics"

    def __init__(
        self, fundamentalcalculator: FundamentalCalculator, datastore: DataStore
    ) -> None:
        self.fundamental: FundamentalCalculator = fundamentalcalculator
        self.store: DataStore = datastore

    def build_metrics(self, ticker: str) -> dict[str, Any]:
        metrics: dict[str, Any] = {
            "ticker": ticker,
            "sector": self.fundamental.get_sector(ticker),
            "market_cap": self.fundamental.get_market_cap(ticker),
            "book_to_market": self.fundamental.get_book_to_market(ticker),
            "earnings_to_price": self.fundamental.get_ep(ticker),
            "cashflow_to_price": self.fundamental.get_cp(ticker),
            "sales_to_price": self.fundamental.get_sp(ticker),
            "momentum_12_1": self.fundamental.get_momentum(ticker),
            "momentum_6_1": self.fundamental.get_6m_momentum(ticker),
            "momentum_3_1": self.fundamental.get_3m_momentum(ticker),
            "volatility_252": self.fundamental.get_volatility(ticker),
            "volatility_180": self.fundamental.get_vol_180(ticker),
            "roe": self.fundamental.get_roe(ticker),
            "gross_profitability": self.fundamental.get_gross_profitability(ticker),
            "profit_margin": self.fundamental.get_profit_margin(ticker),
            "leverage": self.fundamental.get_leverage(ticker),
            "beta": self.fundamental.get_beta(ticker),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        return metrics

    def load_metrics(self, ticker: str) -> dict[str, Any] | None:
        return self.store.load_json(ticker, self.METRICS_CATEGORY)

    def save_metrics(self, ticker: str, metrics: dict[str, Any]) -> None:
        self.store.save_json(ticker, self.METRICS_CATEGORY, metrics)

    def load_or_build_metrics(
        self, ticker: str, force_refresh: bool = False
    ) -> dict[str, Any]:
        if not force_refresh:
            cached: dict[str, Any] | None = self.load_metrics(ticker)
            if cached is not None:
                return cached

        metrics: dict = self.build_metrics(ticker)
        self.save_metrics(ticker, metrics)
        return metrics

    def load_universe_metrics(self, universe: list, force_refresh=False) -> dict:
        universe_metrics: dict = {}

        # Warmup
        try:
            self.fundamental.provider.get_price_history("SPY")
        except Exception as e:
            print(f"SPY warm-up failed: {e}")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_ticker: dict[Future[dict[str, Any]], str] = {
                executor.submit(
                    self.load_or_build_metrics, ticker, force_refresh
                ): ticker
                for ticker in universe
            }

            for future in as_completed(future_to_ticker):
                ticker: str = future_to_ticker[future]

                try:
                    universe_metrics[ticker] = future.result()
                except Exception as e:
                    print(f"Failed to build metrics for {ticker}: {e}")
                    universe_metrics[ticker] = None

        return universe_metrics
