"""
fetcher.py

Thin data access layer for pulling raw financial data from Yahoo Finance.
No caching, validation, or transformations are performed here.
"""

import yfinance as yf

def fetch_price_history(ticker_object: yf.ticker, start_date: str, end_date: str):
    """Fetch historical OHLC price data."""
    ticker_symbol = ticker_object.ticker
    ohlc_data = yf.download(ticker_symbol, start = start_date, end = end_date)
    return ohlc_data

def fetch_fundamentals(ticker_object: yf.Ticker):
    """Fetch general company fundamentals and metadata."""
    fundamentals = ticker_object.info
    return fundamentals

def fetch_balance_sheet(ticker_object: yf.Ticker):
    balance_sheet = ticker_object.balance_sheet
    return balance_sheet

def fetch_quarterly_balance_sheet(ticker_object: yf.Ticker):
    quarterly_balance_sheet = ticker_object.get_balance_sheet(freq="quarterly")
    return quarterly_balance_sheet

def fetch_income_statement(ticker_object: yf.Ticker):
    income_statement = ticker_object.income_stmt
    return income_statement

def fetch_quarterly_income_statement(ticker_object: yf.Ticker):
    quarterly_income_statement = ticker_object.quarterly_income_stmt
    return quarterly_income_statement

def fetch_ttm_income_statement(ticker_object: yf.Ticker):
    ttm_income_statement = ticker_object.ttm_income_stmt
    return ttm_income_statement

def fetch_cashflow(ticker_object: yf.Ticker):
    cashflow = ticker_object.cashflow
    return cashflow


def fetch_quarterly_cashflow(ticker_object: yf.Ticker):
    quarterly_cashflow = ticker_object.quarterly_cashflow
    return quarterly_cashflow


def fetch_ttm_cashflow(ticker_object: yf.Ticker):
    ttm_cashflow = ticker_object.ttm_cashflow
    return ttm_cashflow


def fetch_metadata(ticker_object: yf.Ticker):
    metadata = ticker_object.get_history_metadata()
    return metadata
