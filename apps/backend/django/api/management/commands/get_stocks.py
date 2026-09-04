import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import time

from .filter_data import DataFiltering
from helper.parse_date import parse_data_variable

CSV_PATH = Path(__file__).resolve().parent / "list_idx.csv"

class StockDataFetcher(DataFiltering):
    def __init__(self):
        super().__init__()
    
    def fetch_stock_data(self, tickers: Optional[List[str]], delay: float = 1.0) -> Dict[str, Any]:
        """
        Fetch stock data for the given tickers using yfinance.
        """
        raw_filtered_data, _ = self.read_data(dataset=CSV_PATH)  
        
        # Notes
        # Unique listingBoard values:
        # - Akselerasi
        # - Ekonomi Baru
        # - Pemantauan Khusus
        # - Pengembangan
        # - Utama 
        
        field_mapping = {
            "regularMarketTime": "RegularMarketTime",   # Last Price Update DateTime (Unix Timestamp -> ISO)
            "industry": "Industry",                     # Company Industry
            "industryKey": "IndustryKey",               # Company Industry Key ID
            "sector": "Sector",                         # Company Sector
            "sectorKey": "SectorKey",                   # Company Sector Key ID
            "symbol": "Code",                           # Company Ticker Symbol (e.g., BBCA.JK)
            "shortName": "ShortName",                   # Company Short Name
            "longName": "LongName",                     # Company Full Registered Name
            "open": "Open",                             # Opening Stock Price
            "previousClose": "Close",                   # Previous Market Closing Price
            "dayLow": "Low",                            # Lowest Traded Price Today
            "dayHigh": "High",                          # Highest Traded Price Today
            "lastDividendValue": "LastDividendValue",   # Most Recent Dividend Payout Amount
            "lastDividendDate": "LastDividendDate",     # Most Recent Dividend Date (Unix Timestamp -> ISO)
            "dividendRate": "DividendRate",             # Annualized Dividend Rate
            "dividendYield": "DividendYield",           # Dividend Yield Ratio (Price to Dividend Conversion)
            "mostRecentQuarter": "MostRecentQuarter"    # Most Recent Quarterly Financial Report Date (Unix Timestamp -> ISO)
        }
        
        start_time = time.time()
        stock_data = {"^JKSE": {"Classification": {}}}
        print(f"Processing Stock Data [{__name__}]")
        
        for board, ticker_list in raw_filtered_data["^JKSE"]["Classification"].items():
            stock_data["^JKSE"]["Classification"][board] = {}
            
            for symbol in ticker_list:
                try:
                    stock = yf.Ticker(str(symbol))
                    info = stock.info or {}
                    
                    processed_info = {
                        target_key: parse_data_variable(info.get(source_key))
                        for source_key, target_key in field_mapping.items()
                    }
                    processed_info["DividendHistory"] = self.get_dividend_data(symbol)
                    stock_data["^JKSE"]["Classification"][board][symbol] = processed_info
                    
                    if delay > 0:
                        time.sleep(delay)
                    
                except Exception as e:
                    print(f"Error fetching data for {symbol}: {e}")
                    
        end_time = time.time()
        elapsed_seconds = end_time - start_time
        
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        total_fetched = sum(
                    len(board_data) 
                    for board_data in stock_data.get("^JKSE", {}).get("Classification", {}).values()
                )
        
        print(f"Finish fetching data from yfinance {__name__}")
        print(f"Total Fetched: {total_fetched}")
        print(f"Time Elapsed: {int(hours)}h {int(minutes)}m {seconds:.2f}s (Total: {elapsed_seconds:.2f} seconds)")
        if total_fetched > 0:
            avg_speed = elapsed_seconds / total_fetched
            print(f"Average Speed: {avg_speed:.2f} seconds per stock")
        
        return stock_data

    def get_dividend_data(self, tickers: str) -> Dict[str, Any]:
        """
        Fetch dividend data for the given tickers using yfinance.
        """
        try:
            dividends = yf.Ticker(str(tickers)).get_dividends(period="5y")
            if dividends is not None and not dividends.empty:
                dividends.index = pd.to_datetime(dividends.index).strftime('%d-%m-%Y')
                return dividends.to_dict()
        except Exception as e:
            print(f"Error fetching dividend data for {self.tickers}: {e}") 
                
        return {}   
        