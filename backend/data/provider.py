"""
provider.py

Central data access layer that coordinates:
- fetching raw data (via fetcher)
- cleaning and normalization (via cleaner)
- disk caching (via DataStore)

All higher-level modules should access market and fundamental data
exclusively through Provider.
"""

from backend.data.fetcher import (
    fetch_price_history,
    fetch_fundamentals,
    fetch_balance_sheet,
    fetch_quarterly_balance_sheet,
    fetch_income_statement,
    fetch_quarterly_income_statement,
    fetch_ttm_income_statement,
    fetch_cashflow,
    fetch_quarterly_cashflow,
    fetch_ttm_cashflow,
    fetch_metadata,
)

from backend.data.cleaner import (
    clean_price_history,
    clean_fundamentals,
    clean_balance_sheet,
    clean_quarterly_balance_sheet,
    clean_income_statement,
    clean_quarterly_income_statement,
    clean_ttm_income_statement,
    clean_cashflow,
    clean_quarterly_cashflow,
    clean_ttm_cashflow,
    clean_metadata,
)

class Provider:
    """
    Unified interface for data fetching, cleaning and caching data for a given ticker.
    """

    def __init__(self, data_store):
        self.store = data_store

    # -------------------------------
    # Internal helpers
    # -------------------------------

    def load_fetch_df(self, ticker, category, fetch, clean):
        """
        Loads/fetches a Dataframe Dataset with caching.
        """
        cache = self.store.load_df(ticker, category)
        if cache is not None:
            return cache
        
        try:
            raw = fetch(ticker)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {category} for {ticker.ticker}: {e}")
        
        if raw is None:
            raise RuntimeError(f"{category} for {ticker.ticker} returned None")
        
        cleaned = clean(raw)

        try:
            self.store.save_df(ticker, category, cleaned)
        except Exception as e:
            print(f"Could not save {category} for {ticker,ticker}. Error: {e}")

        return cleaned

    def load_fetch_json(self, ticker, category, fetch, clean):
        """
        Loads/fetches a JSON Dataset with caching.
        """
        cache = self.store.load_json(ticker, category)
        if cache is not None:
            return cache
        
        try:
            raw = fetch(ticker)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {category} for {ticker.ticker}: {e}")
        
        if raw is None:
            raise RuntimeError(f"{category} for {ticker.ticker} returned None")
        
        cleaned = clean(raw)

        try:
            self.store.save_json(ticker, category, cleaned)
        except Exception as e:
            print(f"Could not save {category} for {ticker.ticker}. Error: {e}")

        return cleaned

    # -------------------------------
    # Public API
    # -------------------------------

    def get_price_history(self, ticker):
        return self.load_fetch_df(ticker, "price_history", lambda t: fetch_price_history(t, "2010-01-01", None), clean_price_history)
    
    def get_fundamentals(self, ticker):
        return self.load_fetch_json(ticker, "fundamentals", fetch_fundamentals, clean_fundamentals)
    
    def get_balance_sheet(self, ticker):
        return self.load_fetch_df(ticker, "balance_sheet", fetch_balance_sheet, clean_balance_sheet)
    
    def get_quarterly_balance_sheet(self, ticker):
        return self.load_fetch_df(ticker, "quarterly_balance_sheet", fetch_quarterly_balance_sheet, clean_quarterly_balance_sheet)
    
    def get_income_statement(self, ticker):
        return self.load_fetch_df(ticker, "income_statement", fetch_income_statement, clean_income_statement)

    def get_quarterly_income_statement(self, ticker):
        return self.load_fetch_df(ticker, "quarterly_income_statement", fetch_quarterly_income_statement, clean_quarterly_income_statement)

    def get_ttm_income_statement(self, ticker):
        return self.load_fetch_df(ticker, "ttm_income_statement", fetch_ttm_income_statement, clean_ttm_income_statement)
        
    def get_cashflow(self, ticker):
        return self.load_fetch_df(ticker, "cashflow", fetch_cashflow, clean_cashflow)
        
    def get_quarterly_cashflow(self, ticker):
        return self.load_fetch_df(ticker, "quarterly_cashflow", fetch_quarterly_cashflow, clean_quarterly_cashflow)
        
    def get_ttm_cashflow(self, ticker):
        return self.load_fetch_df(ticker, "ttm_cashflow", fetch_ttm_cashflow, clean_ttm_cashflow)
    
    def get_metadata(self, ticker):
        return self.load_fetch_json(ticker, "metadata", fetch_metadata, clean_metadata)
    
    def get_all_data(self, ticker):
        data = {
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
            "metadata": self.get_metadata(ticker)
        }
        return data
