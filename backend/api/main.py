"""
main.py

FastAPI entry point for the stock factor ranking system.
Exposes endpoints for factor inspection and composite stock ranking.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from backend.data_store.storage import DataStore
from backend.data.provider import Provider
from backend.fundamentals.fundamental_calculator import FundamentalCalculator
from backend.factors.factor_model import FactorCalculator
from backend.ranking.ranking_engine import RankingEngine
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SYSTEM INITIALIZATION

store = DataStore("./data_store")
provider = Provider(store)
fundamentals = FundamentalCalculator(provider)
factors = FactorCalculator(fundamentals, provider)
ranker = RankingEngine(factors)     # <-- renamed from portfolio


@app.get("/")
def root():
    return {
    "name": "Stock Factor Ranking API",
    "status": "running",
    "endpoints": ["/rank", "/factors"]
    }


# GET FACTOR SCORES

@app.get("/factors")
def get_factors():
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
def rank_stocks(weights: FactorWeights):
    ranker.load_factor_scores()
    composite = ranker.compute_composite_scores(weights.dict())
    ranked = ranker.rank_stocks(composite)
    return {"ranked_stocks": ranked}
