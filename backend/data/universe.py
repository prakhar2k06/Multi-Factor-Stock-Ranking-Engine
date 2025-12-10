import pandas as pd
import yfinance as yf

import os
import pandas as pd

def load_sp500_universe():
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, "sp500.csv")

    df = pd.read_csv(csv_path, header=None)   # <-- IMPORTANT: no header
    tickers = df[0].astype(str).str.strip().tolist()

    return tickers
