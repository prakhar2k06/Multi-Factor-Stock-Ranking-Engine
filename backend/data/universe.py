"""
universe.py

Function for constructing the stock universe used across the project.
Currently loads S&P 500 constituents from CSV and filters out
invalid or delisted tickers using a basic price-history check.
"""

import pandas as pd
import yfinance as yf

def load_sp500_universe(path="backend/data/sp_500.csv"):
    """
    Loads and normalizes and validates the S&P 500 ticker universe.
    """
    df = pd.read_csv(path)

    for col in ["Symbol", "Ticker"]:
        if col in df.columns:
            tickers = df[col]
            break
    else:
        tickers = df.iloc[:, 0]
    # Normalize tickers
    tickers = (
        tickers
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
        .tolist()
    )

    clean_list = []

    for t in tickers:
        #Yahoo Finance format
        t = t.replace(".", "-")
        try:
            hist = yf.Ticker(t).history(period="1mo")
            if hist is not None and not hist.empty:
                clean_list.append(t)     
        except:
            # Skip tickers that fail to fetch
            pass 

    return clean_list


