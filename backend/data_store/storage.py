import os
import json
import pandas as pd

class DataStore:
    def __init__(self, base_path: str = "backend/data_store"):
        self.base_path=base_path

    def ensure_dir(self, ticker: str):
        directory_path = f"{self.base_path}/{ticker}"
        os.makedirs(directory_path, exist_ok = True)

    def ticker_path(self, ticker: str):
        return f"{self.base_path}/{ticker}"
    
    def file_path(self, ticker: str, category: str, extension:str):
        return f"{self.base_path}/{ticker}/{category}.{extension}"

    def save_df(self, ticker: str, category: str, df: pd.DataFrame):
        self.ensure_dir(ticker)
        file_path = self.file_path(ticker, category, "parquet")
        df.to_parquet(file_path)

    def load_df(self,ticker: str, category: str):
        file_path = self.file_path(ticker, category, "parquet")
        if not os.path.exists(file_path):
            return None
        df = pd.read_parquet(file_path)
        return df

    def save_json(self, ticker: str, category: str, data: dict):
        self.ensure_dir(ticker)
        file_path = self.file_path(ticker, category, "json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent = 4)

    def load_json(self,ticker: str, category: str):
        file_path = self.file_path(ticker, category, "json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r") as f:
            return json.load(f)




    



    

