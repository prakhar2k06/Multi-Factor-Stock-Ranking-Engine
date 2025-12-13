class PortfolioConstructor:
    def __init__(self, factor_calculator):
        self.factor_calc = factor_calculator
        self.scores = {}

    def load_factor_scores(self):
        self.scores = {"value": self.factor_calc.value_score_calculator(),
                       "size": self.factor_calc.size_score_calculator(),
                       "momentum": self.factor_calc.momentum_score_calculator(),
                       "lowvol": self.factor_calc.lowvol_score_calculator(),
                       "quality": self.factor_calc.quality_score_calculator(),
                       "market_risk": self.factor_calc.market_risk_score_calculator()
                       }
        
        return self.scores
    
    def compute_composite_scores(self, weights: dict):
        composite = {}

        for ticker in self.factor_calc.universe:
            ticker = ticker
            score_sum = 0
            count = 0

            for factor, score in self.scores.items():
                value = score.get(ticker)
                if value is None:
                    continue

                score_sum += value * weights[factor]
                count += 1 

            if count == 0:
                continue
            
            composite[ticker] = score_sum

        return composite
    
    def rank_stocks(self, composite_scores):
        return sorted(composite_scores.items(), key = lambda x: x[1], reverse = True)
    
    def top_n(self, n, weights):
        if not self.scores:
            self.load_factor_scores()

        comp = self.compute_composite_scores(weights)
        ranked = self.rank_stocks(comp)
        return ranked[:n]
    






