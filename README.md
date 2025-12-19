# Multi-Factor Stock Ranking Engine

## Overview
This project is a factor-based stock ranking system that ranks large-cap US equities (S&P 500) using well-established investment factors.

Stocks are scored across six factors (Value, Size, Momentum, Low Volatility, Quality, Market Risk). Users can assign a custom weight to each factor which is then used to produce a list of top-N stocks based on the composite score.

This project focuses on stock ranking rather than portfolio optimization or backtesting.
## Background: Factor Investing

Factor investing is a strategy that involves investing in stocks with certain attributes that have been proven to deliver higher risk-adjusted returns than the market.

Extensive academic research on historical market data has shown that certain characteristics can be associated with increased excess returns. This forms the basis for factor investing.

Rather than selecting stocks based on predictions, factor investing evaluates securities based on these attributes or "Factors".

For a factor to qualify as investable it must be <b>performing, proven, persistent, explainable and executable.</b>

Using this concept, this project aims to rank stocks based on cross-sectional factor scores.

## Factors Used in This Project

This project evaluates stocks on the basis of the following six commonly researched factors:

<details>

<summary><b>Value</b></summary>

Stocks that are inexpensive relative to their fundamentals tend to outperform.

Signals used:
- Book to Market Ratio
- Earning to Price Ratio 
- Cashflow to Price Ratio
- Sales to Price Ratio
  
</details>

<details>

<summary><b>Size</b></summary>

Smaller-cap companies have historically exhibited higher returns than larger companies.

Signals used:
- Negative log of market capitalization
  
</details>

<details>

<summary><b>Momentum</b></summary>

Stocks with strong recent price performance tend to continue outperforming.

Signals used:
- 12-month Momentum
- 6-month Momentum
- 3-month Momentum
  
</details>

<details>

<summary><b>Low Volatility</b></summary>

Stocks with lower volatility have historically delivered greater returns with lower drawdown. 

Signals used:
- 252-day Volatility
- 180-day Volatility
  
</details>

<details>

<summary><b>Quality</b></summary>

Companies with strong profitability and solid balance sheets tend to outperform over time.

Signals used:
- Return on Equity (ROE)
- Gross Profitability
- Profit Margins
- Leverage
  
</details>

<details>

<summary><b>Market-Risk</b></summary>

Lower exposure to  market (systematic) has been associated with greater and more stable returns.

Signals used:
- Beta
  
</details>

## Key Features
- **Multi-factor stock ranking model** based on academic research
- **Multi-signal factor score evaluation** for accurate scoring
- **Sector-neutral z-scoring** to avoid sector bias
- **Outlier clipping (winsorization)** for robust factor signals
- **Cached data layer** for fast re-runs
- **FastAPI backend** with clean REST endpoints
- **Interactive React frontend** for real-time ranking

## System Architecture
### Backend:
- Python + FastAPI
- Modular data pipeline
  - Fetch → Clean → Cache → Compute → Rank
- Easily extensible for new factors or universes.

### Frontend:
- React + Material UI
- Factor weight sliders
- Ranked Stock Table (Top 20)
- Communicates with backend via FastAPI

## Project Structure
```
Multi-Factor-Stock-Ranking-Engine/
│
├── backend/
│   ├── api/
│   │   └── main.py
│   │       # FastAPI entry point and REST endpoints
│   │
│   ├── data/
│   │   ├── fetcher.py
│   │   │   # Raw data retrieval from yfinance
│   │   ├── cleaner.py
│   │   │   # Data cleaning and normalization utilities
│   │   ├── provider.py
│   │   │   # Unified interface for fetch → clean → cache logic
│   │   ├── universe.py
│   │   │   # Stock universe construction (S&P 500 filtering)
│   │   └── sp_500.csv
│   │       # Base universe file
│   │
│   ├── data_store/
│   │   └── storage.py
│   │       # Local on-disk caching (Parquet + JSON)
│   │
│   ├── fundamentals/
│   │   └── fundamental_calculator.py
│   │       # Fundamental metric calculations (ROE, beta, momentum, etc.)
│   │
│   ├── factors/
│   │   └── factor_model.py
│   │       # Factor construction, winsorization, sector z-scoring
│   │
│   ├── ranking/
│   │   └── ranking_engine.py
│   │       # Composite scoring, normalization, ranking logic
│   │
│   └── __init__.py
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── App.js
│   │   │   # Main UI container
│   │   ├── FactorWeightSliders.js
│   │   │   # Factor weight controls
│   │   ├── index.js
│   │   │   # React entry point
│   │   ├── App.css
│   │   └── index.css
│   │
│   ├── package.json
│   └── package-lock.json
│
├── requirements.txt
│   # Python dependencies
│
├── README.md
│
└── .gitignore

```

## Setup and Running Instructions

### 1. Clone the repository
```
git clone https://github.com/prakhar2k06/Multi-Factor-Stock-Ranking-Engine.git
cd Multi-Factor-Stock-Ranking-Engine
```

### 2. Backend Setup (FastAPI)

2.1 Creating and Activating Virtual Environment
```
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows
```
2.2 Installing Backend Dependencies
```
pip install -r requirements.txt
```
2.3 Starting the Backend Server
```bash
cd backend
uvicorn api.main:app --reload
```
If successful you should see:
```
Uvicorn running on http://127.0.0.1:8000
```
Please wait till you see before sending requests:
```
INFO:     Application startup complete.
```

### 3. Frontend Setup (React)

3.1 Navigating to Frontend directory
```bash
cd frontend
```
3.2 Install Frontend Dependencies
```
npm install
```
3.3 Start the Frontend
```
npm start
```
This will launch the frontend at:
```
http://localhost:3000
```

**Note: First run takes some time as data is being fetched. Subsequent runs are faster.**

## API Endpoints
### Retrieve Raw Factor Scores
```
GET /factors
```
### Rank Stocks (POST)
```
POST /rank
```
Example Request Body
```
{
  "value": 0.2,
  "size": 0.2,
  "momentum": 0.2,
  "lowvol": 0.15,
  "quality": 0.15,
  "market_risk": 0.1
}

```

## Future Improvements
- Historical backtesting engine
- Portfolio Construction and weighting
- Additional Factors
- Support for Multiple Universes
- Production Deployment (Docker)

## License

This project is licensed under the MIT License.

## Disclaimer

This project is for educational and research purposes only and does not constitute investment advice.

