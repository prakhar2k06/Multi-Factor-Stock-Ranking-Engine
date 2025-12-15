"""
ranking_engine.py

Combines multiple factor scores into a single composite ranking.
Responsible for weight normalization, score aggregation, and final ranking.
"""

class RankingEngine:
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
        """
        Combine factor scores into a single score per stock.
        Factor weights are normalized to add up to 1.
        """

        # Normalize weights to sum to 1
        total_w = sum(weights.values())
        if total_w == 0:
            n = len(weights)
            weights = {k: 1/n for k in weights}
        else:
            weights = {k: v / total_w for k, v in weights.items()}

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
        """
        Rank stocks by composite score (highest to lowest).
        """
        return sorted(composite_scores.items(), key = lambda x: x[1], reverse = True)
    
    def top_n(self, n, weights):
        """
        Method that returns top-N ranked stocks.
        """
        if not self.scores:
            self.load_factor_scores()

        comp = self.compute_composite_scores(weights)
        ranked = self.rank_stocks(comp)
        return ranked[:n]
    






