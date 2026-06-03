"""
provider.py

Central data access layer that coordinates:
- fetching raw data (via fetcher)
- cleaning and normalization (via cleaner)
- disk caching (via DataStore)

All higher-level modules should access market and fundamental data
exclusively through Provider.
"""

import random
import time
from typing import Any

import pandas as pd

from backend.data.cleaner import (
    clean_balance_sheet,
    clean_cashflow,
    clean_fundamentals,
    clean_income_statement,
    clean_metadata,
    clean_price_history,
    clean_quarterly_balance_sheet,
    clean_quarterly_cashflow,
    clean_quarterly_income_statement,
    clean_ttm_cashflow,
    clean_ttm_income_statement,
)
from backend.data.fetcher import (
    fetch_balance_sheet,
    fetch_cashflow,
    fetch_fundamentals,
    fetch_income_statement,
    fetch_metadata,
    fetch_price_history,
    fetch_quarterly_balance_sheet,
    fetch_quarterly_cashflow,
    fetch_quarterly_income_statement,
    fetch_ttm_cashflow,
    fetch_ttm_income_statement,
)
from backend.data_store.storage import DataStore


class Provider:
    """
    Unified interface for data fetching, cleaning and caching data for a given ticker.
    """

    def __init__(
        self, data_store: DataStore, max_retries: int = 3, base_delay: float = 1.0
    ) -> None:
        self.store: DataStore = data_store
        self.max_retries: int = max_retries
        self.base_delay: float = base_delay

    # -------------------------------
    # Internal helpers
    # -------------------------------

    def fetch_with_retry(self, ticker: str, category, fetch) -> pd.DataFrame | Any:
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                raw = fetch(ticker)

                if raw is None:
                    raise RuntimeError(
                        f"{category} for {ticker} returned empty DataFrame"
                    )

                if isinstance(raw, pd.DataFrame) and raw.empty:
                    raise RuntimeError(
                        f"{category} for {ticker} returned empty DataFrame"
                    )

                return raw

            except Exception as e:
                last_error: Exception = e

                if attempt == self.max_retries:
                    break

                delay = self.base_delay * (2 ** (attempt - 1))
                delay += random.uniform(0, 0.5)

                print(
                    f"Retrying {category} for {ticker} "
                    f"after attempt {attempt}/{self.max_retries}: {e}"
                )

                time.sleep(delay)

        raise RuntimeError(
            f"Failed to fetch {category} for {ticker} "
            f"after {self.max_retries} attempts: {last_error}"
        )

    def load_fetch_df(self, ticker, category, fetch, clean) -> pd.DataFrame | Any:
        """
        Loads/fetches a Dataframe Dataset with caching.
        """
        cache = self.store.load_df(ticker, category)
        if cache is not None:
            return cache

        try:
            raw = self.fetch_with_retry(ticker, category, fetch)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {category} for {ticker}: {e}")

        if raw is None:
            raise RuntimeError(f"{category} for {ticker} returned None")

        cleaned = clean(raw)

        try:
            self.store.save_df(ticker, category, cleaned)
        except Exception as e:
            print(f"Could not save {category} for {ticker}. Error: {e}")

        return cleaned

    def load_fetch_json(self, ticker, category, fetch, clean) -> pd.DataFrame | Any:
        """
        Loads/fetches a JSON Dataset with caching.
        """
        cache = self.store.load_json(ticker, category)
        if cache is not None:
            return cache

        try:
            raw = raw = self.fetch_with_retry(ticker, category, fetch)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {category} for {ticker}: {e}")

        if raw is None:
            raise RuntimeError(f"{category} for {ticker} returned None")

        cleaned = clean(raw)

        try:
            self.store.save_json(ticker, category, cleaned)
        except Exception as e:
            print(f"Could not save {category} for {ticker}. Error: {e}")

        return cleaned

    # -------------------------------
    # Public API
    # -------------------------------

    def get_price_history(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_df(
            ticker,
            "price_history",
            lambda t: fetch_price_history(t, "2010-01-01", None),
            clean_price_history,
        )

    def get_fundamentals(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_json(
            ticker, "fundamentals", fetch_fundamentals, clean_fundamentals
        )

    def get_balance_sheet(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_df(
            ticker, "balance_sheet", fetch_balance_sheet, clean_balance_sheet
        )

    def get_quarterly_balance_sheet(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_df(
            ticker,
            "quarterly_balance_sheet",
            fetch_quarterly_balance_sheet,
            clean_quarterly_balance_sheet,
        )

    def get_income_statement(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_df(
            ticker, "income_statement", fetch_income_statement, clean_income_statement
        )

    def get_quarterly_income_statement(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_df(
            ticker,
            "quarterly_income_statement",
            fetch_quarterly_income_statement,
            clean_quarterly_income_statement,
        )

    def get_ttm_income_statement(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_df(
            ticker,
            "ttm_income_statement",
            fetch_ttm_income_statement,
            clean_ttm_income_statement,
        )

    def get_cashflow(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_df(ticker, "cashflow", fetch_cashflow, clean_cashflow)

    def get_quarterly_cashflow(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_df(
            ticker,
            "quarterly_cashflow",
            fetch_quarterly_cashflow,
            clean_quarterly_cashflow,
        )

    def get_ttm_cashflow(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_df(
            ticker, "ttm_cashflow", fetch_ttm_cashflow, clean_ttm_cashflow
        )

    def get_metadata(self, ticker: str) -> pd.DataFrame | Any:
        return self.load_fetch_json(ticker, "metadata", fetch_metadata, clean_metadata)

    def get_all_data(self, ticker: str) -> dict[str, Any]:
        data: dict[str, Any] = {
            "price_history": self.get_price_history(ticker),
            "fundamentals": self.get_fundamentals(ticker),
            "balance_sheet": self.get_balance_sheet(ticker),
            "quarterly_balance_sheet": self.get_quarterly_balance_sheet(ticker),
            "income_statement": self.get_income_statement(ticker),
            "quarterly_income_statement": self.get_quarterly_income_statement(ticker),
            "ttm_income_statement": self.get_ttm_income_statement(ticker),
            "cashflow": self.get_cashflow(ticker),
            "quarterly_cashflow": self.get_quarterly_cashflow(ticker),
            "ttm_cashflow": self.get_ttm_cashflow(ticker),
            "metadata": self.get_metadata(ticker),
        }
        return data
