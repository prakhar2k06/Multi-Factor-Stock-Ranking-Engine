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
    def get_price_history(self, ticker):
        start = "2010-01-01"
        end = None 
        raw_df=fetch_price_history(ticker, start, end)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch price_history for {ticker.ticker}")
        try:
            clean_df=clean_price_history(raw_df)
        except Exception as e:
            raise ValueError(f"Could not clean price_history for {ticker.ticker}: {e}")
        return clean_df
    
    def get_fundamentals(self, ticker):
        raw_df = fetch_fundamentals(ticker)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch fundamentals for {ticker.ticker}: {e}")
        try:
            clean_df = clean_fundamentals(raw_df)
        except Exception as e:
            raise ValueError(f"Could not clean fundamentals for {ticker.ticker}")
        return clean_df
    
    def get_balance_sheet(self, ticker):
        raw_df = fetch_balance_sheet(ticker)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch balance_sheet for {ticker.ticker}")
        try:
            clean_df = clean_balance_sheet(raw_df)
        except Exception as e:
            raise ValueError(f"Could not clean balance_sheet for {ticker.ticker}: {e}")
        return clean_df
    
    def get_quarterly_balance_sheet(self, ticker):
        raw_df = fetch_quarterly_balance_sheet(ticker)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch quarterly_balance_sheet for {ticker.ticker}")
        try:
            clean_df = clean_quarterly_balance_sheet(raw_df)
        except Exception as e:
            raise ValueError(f"Could not clean quarterly_balance_sheet for {ticker.ticker}: {e}")
        return clean_df
    
    def get_income_statement(self, ticker):
        raw_df = fetch_income_statement(ticker)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch income_statement for {ticker.ticker}")
        try:
            clean_df = clean_income_statement(raw_df)
        except Exception as e:
            raise ValueError(f"Could not clean income_statement for {ticker.ticker}: {e}")
        return clean_df

    def get_quarterly_income_statement(self, ticker):
        raw_df = fetch_quarterly_income_statement(ticker)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch quarterly_income_statement for {ticker.ticker}")
        try:
            clean_df = clean_quarterly_income_statement(raw_df)
        except Exception as e:
            raise ValueError(f"Could not clean quarterly_income_statement for {ticker.ticker}: {e}")
        return clean_df

    def get_ttm_income_statement(self, ticker):
        raw_df = fetch_ttm_income_statement(ticker)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch ttm_income_statement for {ticker.ticker}")
        try:
            clean_df = clean_ttm_income_statement(raw_df)
        except Exception as e:
            raise ValueError(f"Could not clean ttm_income_statement for {ticker.ticker}: {e}")
        return clean_df
    
    def get_cashflow(self, ticker):
        raw_df = fetch_cashflow(ticker)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch cashflow for {ticker.ticker}")
        try:
            clean_df = clean_cashflow(raw_df)
        except Exception as e:
            raise ValueError(f"Could not clean cashflow for {ticker.ticker}: {e}")
        return clean_df
    
    def get_quarterly_cashflow(self, ticker):
        raw_df = fetch_quarterly_cashflow(ticker)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch quarterly_cashflow for {ticker.ticker}")
        try:
            clean_df = clean_quarterly_cashflow(raw_df)
        except Exception as e:
            raise ValueError(f"Could not clean quarterly_cashflow for {ticker.ticker}: {e}")
        return clean_df
    
    def get_ttm_cashflow(self, ticker):
        raw_df = fetch_ttm_cashflow(ticker)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch ttm_cashflow for {ticker.ticker}")
        try:
            clean_df = clean_ttm_cashflow(raw_df)
        except Exception as e:
            raise ValueError(f"Could not clean ttm_cashflow for {ticker.ticker}: {e}")
        return clean_df
    
    def get_metadata(self, ticker):
        raw_df = fetch_metadata(ticker)
        if raw_df is None or raw_df.empty:
            raise ValueError(f"Could not fetch metadata for {ticker.ticker}")
        try:
            clean_df = clean_metadata(raw_df)
        except Exception as e:
             raise ValueError(f"Could not clean metadata for {ticker.ticker}: {e}")
        return clean_df
    
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
