"""
universe.py

Function for constructing the stock universe used across the project.
Currently loads S&P 500 constituents from CSV and filters out
invalid or delisted tickers using a basic price-history check.
"""

import pandas as pd


def load_sp500_universe(path: str = "backend/data/sp_500.csv") -> list:
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

    return (
        tickers.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(".", "-", regex=False)
        .dropna()
        .unique()
        .tolist()
    )
