import yfinance as yf
import json
import requests
import pandas as pd
from typing import List, Dict, Any, Optional

class StockDataFetcher:
    def __init__(self, tickers: List[str]):
        self.tickers = tickers
        
    def read_data() -> pd.DataFrame:
        """
        Read data IDX listed companies.
        """
        df = pd.read_csv("list_idx.csv")
        listed_companies = []
        for index, row in df.iterrows():
            ticker = f"{row['code']}.JK"
            listed_companies.append({"emiten": ticker})
        return pd.DataFrame(listed_companies)
    
    def fetch_stock_data(tickers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch stock data for the given tickers using yfinance.
        """
        
        emiten = StockDataFetcher.read_data()
        ticker_data = []
        for ticker in tickers:
            if ticker in emiten['emiten'].values:
                ticker_data.append(ticker)
                continue
    
        returning_data = {}
        for ticker in ticker_data:
            try:
                stock = yf.Ticker(str(ticker))
                info = stock.info
                returning_data[str(ticker)] = {
                    "Industry": info.get("industry"),
                    "IndustryKey": info.get("industryKey"),
                    "Sector": info.get("sector"),
                    "SectorKey": info.get("sectorKey"),
                    "Code": info.get("symbol"),
                    "ShortName": info.get("shortName"),
                    "LongName": info.get("longName"),
                    "Open": info.get("open"),
                    "LastDividendValue": info.get("lastDividendValue"),
                    "LastDividendDate": info.get("lastDividendDate"),
                    "DividendRate": info.get("dividendRate"),
                    "DividendYield": info.get("dividendYield")
                }
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                
        return returning_data
        
if __name__ == "__main__":
    emiten1 = "BBCA"
    emiten2 = "BBCA.JK"
    emiten3 = "BBRI.JK"
    emiten = [emiten1, emiten2, emiten3]
    # breakpoint()
    data = StockDataFetcher.fetch_stock_data(tickers=emiten)
    print(json.dumps(data, indent=4))