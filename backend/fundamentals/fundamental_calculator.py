import pandas as pd
import yfinance as yf

class FundamentalCalculator:
    def __init__(self,provider):
        self.provider = provider

    def get_latest_price(self, ticker):
        price_df = self.provider.get_price_history(ticker)
        if price_df is None or price_df.empty:
            return None
        if "close" not in price_df.columns:
            return None
        return price_df["close"].iloc[-1]
    
    def get_outstanding_shares(self, ticker):
        fundamentals = self.provider.get_fundamentals(ticker)
        shares = fundamentals.get("sharesOutstanding")

        if shares is not None:
            return shares

        bs = self.provider.get_balance_sheet(ticker)
        try:
            if "share_issued" in bs.index:
                row = bs.loc["share_issued"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        return None

    def get_net_income(self, ticker):
        try:
            inc = self.provider.get_income_statement(ticker)
            if "net_income" in inc.index:
                val = inc.loc["net_income"]
                if len(val) > 0 and pd.notna(val.iloc[0]):
                    return val.iloc[0]
        except Exception:
            pass

        try:
            ttm = self.provider.get_ttm_income_statement(ticker)
            if "net_income" in ttm.index:
                val = ttm.loc["net_income"]
                if len(val) > 0 and pd.notna(val.iloc[0]):
                    return val.iloc[0]
        except Exception:
            pass

        return None

    def get_equity(self, ticker):
        balance_sheet_df = self.provider.get_balance_sheet(ticker)

        try:
            if "stockholders_equity" in balance_sheet_df.index:
                row = balance_sheet_df.loc["stockholders_equity"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        try:
            if "common_stock_equity" in balance_sheet_df.index:
                row = balance_sheet_df.loc["common_stock_equity"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        return None
    
    def get_book_value_per_share(self, ticker):
        fundamentals = self.provider.get_fundamentals(ticker)
        bv = fundamentals.get("bookValue")
        if bv is not None:
            return bv
    
        equity = self.get_equity(ticker)
                
        if equity is None:
            return None
        
        shares = self.get_outstanding_shares(ticker)
        if shares is None or shares == 0:
            return None
        
        return equity / shares

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
        if stock_df is None or stock_df.empty or "close" not in stock_df.columns:
            return None
        stock_df = stock_df.reset_index()
        stock_df["stock_returns"] = stock_df["close"].pct_change()

        spy = yf.Ticker("SPY")
        market_df = self.provider.get_price_history(spy)
        if market_df is None or market_df.empty or "close" not in market_df.columns:
            return None
        market_df = market_df.reset_index()
        market_df["spy_returns"] = market_df["close"].pct_change()

        merged = stock_df.join(market_df[["spy_returns"]], how="inner")
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
        book_value_per_share = self.get_book_value_per_share(ticker)
        
        if book_value_per_share == 0 or book_value_per_share is None or price is None:
            return None
        
        return price/book_value_per_share
        
    def get_book_to_market(self,ticker):
        price_to_book = self.get_price_to_book(ticker)
        if price_to_book == 0 or price_to_book is None:
            return None
        
        return 1 / price_to_book
    
    def get_ep(self, ticker):
        ni = self.get_net_income(ticker)
        mc = self.get_market_cap(ticker)
        if ni is None or mc is None or mc == 0:
            return None
        return ni / mc
    
    def get_cash_flow(self, ticker):
        try:
            cf = self.provider.get_cashflow(ticker)
            if "free_cash_flow" in cf.index:
                val = cf.loc["free_cash_flow"].iloc[0]
                if pd.notna(val): return val
        except:
            pass

        try:
            ttm = self.provider.get_ttm_cashflow(ticker)
            if "free_cash_flow" in ttm.index:
                val = ttm.loc["free_cash_flow"].iloc[0]
                if pd.notna(val):
                    return val
        except Exception:
            pass

        return None
    
    def get_cp(self, ticker):
        cf = self.get_cash_flow(ticker)
        mc = self.get_market_cap(ticker)
        if cf is None or mc is None or mc == 0:
            return None
        return cf / mc

    def get_sales(self, ticker):
        try:
            inc = self.provider.get_income_statement(ticker)
            if "total_revenue" in inc.index:
                val = inc.loc["total_revenue"].iloc[0]
                if pd.notna(val): 
                    return val
        except Exception:
            pass

        return None

    def get_sp(self, ticker):
        sales = self.get_sales(ticker)
        mc = self.get_market_cap(ticker)
        if sales is None or mc is None or mc == 0:
            return None
        return sales / mc
    
    def get_gross_profit(self, ticker):
        try:
            inc = self.provider.get_income_statement(ticker)
            if "gross_profit" in inc.index:
                row = inc.loc["gross_profit"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        try:
            ttm = self.provider.get_ttm_income_statement(ticker)
            if "gross_profit" in ttm.index:
                row = ttm.loc["gross_profit"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        return None
    
    def get_total_assets(self, ticker):
        try:
            bs = self.provider.get_balance_sheet(ticker)
            if "total_assets" in bs.index:
                row = bs.loc["total_assets"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        try:
            qbs = self.provider.get_quarterly_balance_sheet(ticker)
            if "total_assets" in qbs.index:
                row = qbs.loc["total_assets"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        return None

    def get_total_debt(self, ticker):
        try:
            bs = self.provider.get_balance_sheet(ticker)
            if "total_debt" in bs.index:
                row = bs.loc["total_debt"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        try:
            qbs = self.provider.get_quarterly_balance_sheet(ticker)
            if "total_debt" in qbs.index:
                row = qbs.loc["total_debt"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        return None

    def get_total_revenue(self, ticker):
        try:
            inc = self.provider.get_income_statement(ticker)
            if "total_revenue" in inc.index:
                row = inc.loc["total_revenue"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        try:
            ttm = self.provider.get_ttm_income_statement(ticker)
            if "total_revenue" in ttm.index:
                row = ttm.loc["total_revenue"]
                if len(row) > 0 and pd.notna(row.iloc[0]):
                    return row.iloc[0]
        except Exception:
            pass

        return None


    def get_gross_profitability(self, ticker):
        gross_profit = self.get_gross_profit(ticker)
        total_assets = self.get_total_assets(ticker)

        if gross_profit is None or total_assets is None or total_assets == 0:
            return None

        return gross_profit / total_assets
    
    def get_leverage(self, ticker):
        total_debt = self.get_total_debt(ticker)
        total_assets = self.get_total_assets(ticker)

        if total_debt is None or total_assets is None or total_assets == 0:
            return None
        
        return total_debt / total_assets
    
    def get_profit_margin(self, ticker): 
        try:
            fundamentals = self.provider.get_fundamentals(ticker)
            pm = fundamentals.get("profitMargins")
            if pm is not None:
                return pm
        except Exception:
            pass

        net_income = self.get_net_income(ticker)
        revenue = self.get_total_revenue(ticker)

        if net_income is None or revenue is None or revenue == 0:
            return None

        return net_income / revenue

    def get_volatility(self, ticker):
        df = self.provider.get_price_history(ticker)
        if df is None or df.empty or "close" not in df.columns:
            return None
        
        df["returns"] = df["close"].pct_change()
        recent = df.tail(252)
        recent = recent.dropna(subset=["returns"])
        if len(recent) < 60:
            return None
        vol = recent["returns"].std() * (252**0.5)

        return vol
    
    def get_vol_180(self, ticker):
        df = self.provider.get_price_history(ticker)
        if df is None or df.empty or "close" not in df.columns:
            return None
        
        df["returns"] = df["close"].pct_change()
        recent = df.tail(180)
        if len(recent) < 60: return None
        return recent["returns"].std() * (252**0.5)

       
    def get_momentum(self, ticker):
        df = self.provider.get_price_history(ticker)
        if df is None or df.empty or "close" not in df.columns:
            return None
        
        if len(df) < 252:
            return None
        
        df = df.dropna(subset=["close"])

        try:
            price_12m_ago = df["close"].iloc[-252]
            price_1m_ago = df["close"].iloc[-21]
        except Exception:
            return None
        
        if price_12m_ago is None or price_12m_ago == 0:
            return None
        
        else:
            return (price_1m_ago / price_12m_ago) - 1
        
    def get_6m_momentum(self, ticker):
        df = self.provider.get_price_history(ticker)
        if df is None or df.empty or "close" not in df.columns:
            return None
        
        if len(df) < 126:
            return None
        
        df = df.dropna(subset=["close"])

        try:
            price_6m_ago = df["close"].iloc[-126]
            price_1m_ago = df["close"].iloc[-21]
        except Exception:
            return None
        
        if price_6m_ago is None or price_6m_ago == 0:
            return None
        
        else:
            return (price_1m_ago / price_6m_ago) - 1
        

    def get_3m_momentum(self, ticker):
        df = self.provider.get_price_history(ticker)
        if df is None or df.empty or "close" not in df.columns:
            return None
        
        if len(df) < 63:
            return None
        
        df = df.dropna(subset=["close"])

        try:
            price_3m_ago = df["close"].iloc[-63]
            price_1m_ago = df["close"].iloc[-21]
        except Exception:
            return None
        
        if price_3m_ago is None or price_3m_ago == 0:
            return None
        
        else:
            return (price_1m_ago / price_3m_ago) - 1
    
    def get_sector(self, ticker):
        try:
            fundamentals = self.provider.get_fundamentals(ticker)
            sector = fundamentals.get("sector")
            if sector is not None:
                return sector
        except Exception:
            pass

        return None

        
