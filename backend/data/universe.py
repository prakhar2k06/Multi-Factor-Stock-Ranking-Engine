import pandas as pd
import yfinance as yf

def load_sp500_universe(path="backend/data/sp_500.csv"):
    df = pd.read_csv(path)

    # Get ticker column (Symbol / Ticker / first col)
    for col in ["Symbol", "Ticker"]:
        if col in df.columns:
            tickers = df[col]
            break
    else:
        tickers = df.iloc[:, 0]

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
        t = t.replace(".", "-")
        try:
            hist = yf.Ticker(t).history(period="1mo")
            if hist is not None and not hist.empty:
                clean_list.append(t)     # VALID TICKER
        except:
            pass   # ignore invalid tickers

    return clean_list


