import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import yfinance as yf

class DataFiltering:
    def __init__(self, ticker_list: List[str] = None):
        self.ticker_list = ticker_list or []
        self.dataset = None
        
    def read_data(self, dataset: Optional[Any]) -> Dict[List[str, Any]]:
        """
        Read data IDX listed companies.
        """        
        self.dataset = dataset
        
        df = pd.read_csv(dataset)
            
        nested_dict = {
            "^JKSE": {
                "Classification": (
                    (df["code"]+ ".JK").groupby(df["listingBoard"]).apply(list).to_dict()
                )
            }
        }
        
        filtered_data, active_tickers = self.filter_data(dataset=nested_dict)
        
        return filtered_data, active_tickers
    
    def filter_data(self, dataset: Optional[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[str]]:
        
        self.dataset = dataset
        if not self.dataset or "^JKSE" not in self.dataset:
            print("Dataset empty or invalid structure!")
            return {"^JKSE": {"Classification": {}}}, []
        
        self.ticker_list = []
        for board, tickers in self.dataset["^JKSE"]["Classification"].items():
            self.ticker_list.extend(tickers)
            
        print(f"Total tickers: {len(self.ticker_list)}")
        
        batch_data = yf.download(
            tickers=self.ticker_list,
            period="1d",
            group_by="ticker",
            threads=True,
            progress=False
        )
        
        # Notes
        # Unique listingBoard values:
        # - Akselerasi
        # - Ekonomi Baru
        # - Pemantauan Khusus
        # - Pengembangan
        # - Utama 
        
        clean_dict = {"^JKSE": {"Classification": {}}}
        active_tickers_list = []
                
        for board, ticker_list in self.dataset["^JKSE"]["Classification"].items():
            clean_dict["^JKSE"]["Classification"][board] = {}
            
            for symbol in ticker_list:
                # checking if in the past days in batch download contains valid price data
                if symbol in batch_data.columns.levels[0]:
                    symbol_df = batch_data[symbol]["Close"].dropna()
                    
                    if not symbol_df.empty:
                        clean_dict["^JKSE"]["Classification"][board][symbol] = {
                            "status": "ACTIVE"
                        }
                        active_tickers_list.append(symbol)
                        
        total_active = sum(len(tickers) for tickers in clean_dict["^JKSE"]["Classification"].values())
        print(f"Active ticker check completed. Total Active: {total_active}")
        
        return clean_dict, active_tickers_list