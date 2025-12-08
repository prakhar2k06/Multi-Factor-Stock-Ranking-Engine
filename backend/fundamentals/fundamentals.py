import pandas as pd
import yfinance as yf

class FundamentalCalculator:
    def __init__(self,provider):
        self.provider = provider

    def get_latest_price(self, ticker):
        price_df = self.provider.get_price_history(ticker)
        if price_df is None or price_df.empty:
            return None
        return price_df["close"].iloc[-1]
    
    def get_outstanding_shares(self, ticker):
        fundamentals = self.provider.get_fundamentals(ticker)
        shares = fundamentals.get("sharesOutstanding")

        if shares is not None:
            return shares

        bs = self.provider.get_balance_sheet(ticker)
        if "share_issued" in bs.index:
            val = bs.loc["share_issued"].iloc[0]
            if pd.notna(val):
                return val

        return None

    def get_net_income(self, ticker):
        inc = self.provider.get_income_statement(ticker)
        ni = inc.loc["net_income"].iloc[0]

        if pd.isna(ni):
            ttm = self.provider.get_ttm_income_statement(ticker)
            ni = ttm.loc["net_income"].iloc[0]

        return None if pd.isna(ni) else ni

    def get_equity(self, ticker):
        balance_sheet_df = self.provider.get_balance_sheet(ticker)
        equity = None
        if "stockholders_equity" in balance_sheet_df.index:
            val = balance_sheet_df.loc["stockholders_equity"].iloc[0]
            if pd.notna(val):
                equity = val

        if equity is None and "common_stock_equity" in balance_sheet_df.index:
            val = balance_sheet_df.loc["common_stock_equity"].iloc[0]
            if pd.notna(val):
                equity = val

        return equity
    
    def get_book_value(self, ticker):
        fundamentals = self.provider.get_fundamentals(ticker)
        bv = fundamentals.get("bookValue")
        if bv is not None:
            return bv
    
        bs = self.provider.get_balance_sheet(ticker)
        bv = None
        if "stockholders_equity" in bs.index:
            val = bs.loc["stockholders_equity"].iloc[0]
            if pd.notna(val):
                bv = val

        if bv is None and "common_stock_equity" in bs.index:
            val = bs.loc["common_stock_equity"].iloc[0]
            if pd.notna(val):
                bv = val
                
        return bv

    def get_market_cap(self, ticker):
        fundamentals = self.provider.get_fundamentals(ticker)
        mc = fundamentals.get("marketCap")
        if mc is not None:
            return mc
        
        shares = self.get_outstanding_shares(ticker)
        price = self.get_latest_price(ticker)

        if shares is None or price is None:
            return None
        
        return price * shares

    def get_roe(self, ticker):
        fundamentals = self.provider.get_fundamentals(ticker)
        roe = fundamentals.get("returnOnEquity")
        if roe is not None:
            return roe
        
        net_income = self.get_net_income(ticker)
        equity = self.get_equity(ticker)

        if net_income is None or equity is None:
            return None
        
        if equity == 0:
            return None
        
        return net_income / equity
            
    def get_beta(self, ticker):
        fundamentals = self.provider.get_fundamentals(ticker)
        beta = fundamentals.get("beta")
        if beta is not None:
            return beta
        
        stock_df = self.provider.get_price_history(ticker)
        stock_df = stock_df.reset_index()
        stock_df["stock_returns"] = stock_df["close"].pct_change()

        spy = yf.Ticker("SPY")
        market_df = self.provider.get_price_history(spy)
        market_df = market_df.reset_index()
        market_df["spy_returns"] = market_df["close"].pct_change()

        merged = stock_df.merge(market_df, on="date", how="inner")
        merged = merged.dropna(subset=["stock_returns", "spy_returns"])

        cov = merged["stock_returns"].cov(merged["spy_returns"])
        var = merged["spy_returns"].var()

        if var==0:
            return None

        return cov/var

    def get_price_to_book(self, ticker):
        fundamentals = self.provider.get_fundamentals(ticker)
        price_to_book = fundamentals.get("priceToBook")
        if price_to_book is not None:
            return price_to_book

        price = self.get_latest_price(ticker)
        shares = self.get_outstanding_shares(ticker)
        book_value = self.get_book_value(ticker)
        
        if price is None or shares is None or shares == 0 or book_value is None:
            return None
        
        book_value_per_share = book_value / shares

        if book_value_per_share == 0:
            return None
        
        return price/book_value_per_share
        
    def get_book_to_market(self,ticker):
        price_to_book = self.get_price_to_book(ticker)
        if price_to_book == 0 or price_to_book is None:
            return None
        
        return 1 / price_to_book
        
    def get_volatility(self, ticker):
        df = self.provider.get_price_history(ticker)
        df["returns"] = df["close"].pct_change()
        recent = df.tail(252)
        recent = recent.dropna(subset=["returns"])
        if len(recent) < 60:
            return None
        vol = recent["returns"].std() * (252**0.5)

        return vol
    
    def get_book_value_per_share(self, ticker):
        book_value = self.get_book_value(ticker)
        shares = self.get_outstanding_shares(ticker)
        if book_value is None or shares is None:
            return None

        if shares == 0:
            return None
        
        if book_value <= 0:
            return None
        
        return book_value / shares
    
    def get_momentum(self, ticker):
        df = self.provider.get_price_history(ticker)
        if df is None or df.empty:
            return None
        
        if len(df) > 252:
            return None
        
        try:
            price_12m_ago = df["close"].iloc[-252]
            price_1m_ago = df["close"].iloc[-21]
        except Exception:
            return None
        
        if price_12m_ago is None or price_12m_ago == 0:
            return None
        
        else:
            return (price_1m_ago / price_12m_ago) - 1
        

        



