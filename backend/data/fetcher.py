"""
fetcher.py

Thin data access layer for pulling raw financial data from Yahoo Finance.
No caching, validation, or transformations are performed here.
"""

import yfinance as yf
from pandas import DataFrame


def fetch_price_history(ticker, start_date: str, end_date: str) -> DataFrame | None:
    """Fetch historical OHLC price data."""
    ohlc_data: DataFrame | None = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False,
        threads=False,
        multi_level_index=False,
    )
    return ohlc_data


def fetch_fundamentals(ticker: str) -> dict:
    """Fetch general company fundamentals and metadata."""
    ticker_object: yf.Ticker = yf.Ticker(ticker)
    fundamentals: dict = ticker_object.info
    return fundamentals


def fetch_balance_sheet(ticker: str) -> DataFrame:
    ticker_object: yf.Ticker = yf.Ticker(ticker)
    balance_sheet: DataFrame = ticker_object.balance_sheet
    return balance_sheet


def fetch_quarterly_balance_sheet(ticker: str):
    ticker_object: yf.Ticker = yf.Ticker(ticker)
    quarterly_balance_sheet = ticker_object.get_balance_sheet(freq="quarterly")
    return quarterly_balance_sheet


def fetch_income_statement(ticker: str) -> DataFrame:
    ticker_object: yf.Ticker = yf.Ticker(ticker)
    income_statement: DataFrame = ticker_object.income_stmt
    return income_statement


def fetch_quarterly_income_statement(ticker: str) -> DataFrame:
    ticker_object: yf.Ticker = yf.Ticker(ticker)
    quarterly_income_statement: DataFrame = ticker_object.quarterly_income_stmt
    return quarterly_income_statement


def fetch_ttm_income_statement(ticker: str) -> DataFrame:
    ticker_object: yf.Ticker = yf.Ticker(ticker)
    ttm_income_statement: DataFrame = ticker_object.ttm_income_stmt
    return ttm_income_statement


def fetch_cashflow(ticker: str) -> DataFrame:
    ticker_object: yf.Ticker = yf.Ticker(ticker)
    cashflow: DataFrame = ticker_object.cashflow
    return cashflow


def fetch_quarterly_cashflow(ticker: str) -> DataFrame:
    ticker_object: yf.Ticker = yf.Ticker(ticker)
    quarterly_cashflow: DataFrame = ticker_object.quarterly_cashflow
    return quarterly_cashflow


def fetch_ttm_cashflow(ticker: str) -> DataFrame:
    ticker_object: yf.Ticker = yf.Ticker(ticker)
    ttm_cashflow: DataFrame = ticker_object.ttm_cashflow
    return ttm_cashflow


def fetch_metadata(ticker: str) -> dict:
    ticker_object: yf.Ticker = yf.Ticker(ticker)
    metadata: dict = ticker_object.get_history_metadata()
    return metadata
