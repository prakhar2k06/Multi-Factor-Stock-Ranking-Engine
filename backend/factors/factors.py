from backend.data.universe import load_sp500_universe
import numpy as np
import yfinance as yf

class FactorCalculator:
    def __init__(self,fundamentalcalculator, provider):
        self.fundamental = fundamentalcalculator
        self.provider = provider
        self.universe = [yf.Ticker(t) for t in load_sp500_universe()]

    def z_score_calculator(self, value, mean, std):
        if value is None or np.isnan(value) or std==0 or np.isnan(std):
            return None
        
        return (value-mean)/std
    
    def value_score_calculator(self):
        values = []
        for ticker in self.universe:
            btm = self.fundamental.get_book_to_market(ticker)
            if btm is None:
                btm = np.nan
            values.append(btm)
        
        clean = [v for v in values if not np.isnan(v)]
        if len(clean) == 0:
            return {t.ticker: None for t in self.universe}
        mean = np.mean(clean)
        std = np.std(clean)

        scores={}
        for ticker_object, val in zip(self.universe, values):
            symbol = ticker_object.ticker
            scores[symbol] = self.z_score_calculator(val, mean, std)

        return scores 

    def size_score_calculator(self):
        values = []
        for ticker in self.universe:
            market_cap = self.fundamental.get_market_cap(ticker)
            if market_cap is None or market_cap <= 0:
                values.append(np.nan)
            else:
                values.append(np.log(market_cap))

        clean = [v for v in values if not np.isnan(v)]
        if len(clean) == 0:
            return {t.ticker: None for t in self.universe}
        mean = np.mean(clean)
        std = np.std(clean)

        scores={}
        for ticker_object,val in zip(self.universe, values):
            z = self.z_score_calculator(val, mean, std)
            symbol = ticker_object.ticker
            scores[symbol] = -z if z is not None else None

        return scores
    
    def momentum_score_calculator(self):
        values = []
        for ticker in self.universe:
            momentum = self.fundamental.get_momentum (ticker)
            if momentum is None:
                momentum = np.nan
            values.append(momentum)

        clean = [v for v in values if not np.isnan(v)]
        if len(clean) == 0:
            return {t.ticker: None for t in self.universe}
        mean = np.mean(clean)
        std = np.std(clean)

        scores={}
        for ticker_object, val in zip(self.universe, values):
            symbol = ticker_object.ticker
            scores[symbol] = self.z_score_calculator(val, mean, std)

        return scores
    
    def lowvol_score_calculator(self):
        values = []
        for ticker in self.universe:
            volatility = self.fundamental.get_volatility(ticker)
            if volatility is None:
                volatility = np.nan
            values.append(volatility)

        clean = [v for v in values if not np.isnan(v)]
        if len(clean) == 0:
            return {t.ticker: None for t in self.universe}
        mean = np.mean(clean)
        std = np.std(clean)

        scores={}
        for ticker_object,val in zip(self.universe, values):
            z = self.z_score_calculator(val, mean, std)
            symbol = ticker_object.ticker
            scores[symbol] = -z if z is not None else None

        return scores
    
    def quality_score_calculator(self):
        values = []
        for ticker in self.universe:
            roe = self.fundamental.get_roe(ticker)
            if roe is None:
                roe = np.nan
            values.append(roe)

        clean = [v for v in values if not np.isnan(v)]
        if len(clean) == 0:
            return {t.ticker: None for t in self.universe}
        mean = np.mean(clean)
        std = np.std(clean)

        scores={}
        for ticker_object, val in zip(self.universe, values):
            symbol = ticker_object.ticker
            scores[symbol] = self.z_score_calculator(val, mean, std)

        return scores
    
    def market_risk_score_calculator(self):
        values = []
        for ticker in self.universe:
            beta = self.fundamental.get_beta(ticker)
            if beta is None:
                beta = np.nan
            values.append(beta)

        clean = [v for v in values if not np.isnan(v)]
        if len(clean) == 0:
            return {t.ticker: None for t in self.universe}
        mean = np.mean(clean)
        std = np.std(clean)

        scores={}
        for ticker_object,val in zip(self.universe, values):
            z = self.z_score_calculator(val, mean, std)
            symbol = ticker_object.ticker
            scores[symbol] = -z if z is not None else None

        return scores
    
    