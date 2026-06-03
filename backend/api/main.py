"""
main.py

FastAPI entry point for the stock factor ranking system.
Exposes endpoints for factor inspection and composite stock ranking.
"""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.data.provider import Provider
from backend.data_store.storage import DataStore
from backend.factors.factor_model import FactorCalculator
from backend.fundamentals.fundamental_calculator import FundamentalCalculator
from backend.metrics.metric_builder import MetricBuilder
from backend.ranking.ranking_engine import RankingEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SYSTEM INITIALIZATION

store = DataStore("./data_store")
provider: Provider = Provider(store)
fundamentals: FundamentalCalculator = FundamentalCalculator(provider)
metric_builder: MetricBuilder = MetricBuilder(fundamentals, store)
factors: FactorCalculator = FactorCalculator(metric_builder)
ranker: RankingEngine = RankingEngine(factors)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "name": "Stock Factor Ranking API",
        "status": "running",
        "endpoints": ["/rank", "/factors"],
    }


# GET FACTOR SCORES


@app.get("/factors")
def get_factors() -> dict[str, dict]:
    return {
        "value": factors.value_score_calculator(),
        "size": factors.size_score_calculator(),
        "momentum": factors.momentum_score_calculator(),
        "lowvol": factors.lowvol_score_calculator(),
        "quality": factors.quality_score_calculator(),
        "market_risk": factors.market_risk_score_calculator(),
    }


# INPUT MODEL FOR WEIGHTS


class FactorWeights(BaseModel):
    value: float
    size: float
    momentum: float
    lowvol: float
    quality: float
    market_risk: float


# RANKING ENDPOINT


@app.post("/rank")
def rank_stocks(weights: FactorWeights) -> dict[str, list]:
    ranker.load_factor_scores()
    composite: dict = ranker.compute_composite_scores(weights.dict())
    ranked: list = ranker.rank_stocks(composite)
    return {"ranked_stocks": ranked}
