"""
storage.py

File-based data cache for fetched and cleaned financial data.
Stores per-ticker datasets to avoid repeated API calls.
"""

import json
import os
from typing import Any

import pandas as pd
from pandas import DataFrame


class DataStore:
    """
    Handles persistence of fetched data (dataframes and JSON)
    using a simple directory structure: one folder per ticker.
    """

    def __init__(self, base_path: str = "backend/data_store") -> None:
        self.base_path: str = base_path

    def ensure_dir(self, ticker) -> None:
        directory_path: str = f"{self.base_path}/{ticker}"
        os.makedirs(directory_path, exist_ok=True)

    def ticker_path(self, ticker: str) -> str:
        return f"{self.base_path}/{ticker}"

    def file_path(self, ticker, category: str, extension: str) -> str:
        return f"{self.base_path}/{ticker}/{category}.{extension}"

    # =========================
    # DATAFRAME STORAGE
    # =========================

    def save_df(self, ticker, category: str, df: pd.DataFrame) -> None:
        self.ensure_dir(ticker)
        file_path: str = self.file_path(ticker, category, "parquet")
        df.to_parquet(file_path)

    def load_df(self, ticker, category: str) -> None | DataFrame:
        file_path: str = self.file_path(ticker, category, "parquet")
        if not os.path.exists(file_path):
            return None
        df: DataFrame = pd.read_parquet(file_path)
        return df

    # =========================
    # JSON STORAGE
    # =========================

    def save_json(self, ticker, category: str, data: dict) -> None:
        self.ensure_dir(ticker)
        file_path: str = self.file_path(ticker, category, "json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_json(self, ticker, category: str) -> None | Any:
        file_path: str = self.file_path(ticker, category, "json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r") as f:
            return json.load(f)
