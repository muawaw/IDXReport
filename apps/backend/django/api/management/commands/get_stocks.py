import yfinance as yf
import json
import requests
import pandas as pd
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

from django.core.management.base import BaseCommand
from api.models import Stock


CSV_PATH = Path(__file__).resolve().parent / "list_idx.csv"

class StockDataFetcher:
    def __init__(self, tickers: List[str]):
        self.tickers = tickers
        
    def read_data(self, tickers: List[str]) -> List[str, Any]:
        """
        Read data IDX listed companies.
        """
        not_listed_companies = []
        listed_companies = []
        
        df = pd.read_csv(CSV_PATH)
        idx_codes = df['code'].tolist()
        for ticker in tickers:
            if ticker.strip().upper() in idx_codes:
                listed_companies.append({"emiten": f"{ticker}.JK"})
                continue
            else:
                not_listed_companies.append({"emiten": ticker, "error": "Ticker not found in IDX listed companies"})
        
        return listed_companies, not_listed_companies
    
    def fetch_stock_data(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Fetch stock data for the given tickers using yfinance.
        """
        listed_companies, not_listed_companies = self.read_data(tickers)
    
        stock_data = {}
        for company in listed_companies:
            ticker = company["emiten"]
            try:
                stock = yf.Ticker(str(ticker))
                info = stock.info
                stock_data[str(ticker)] = {
                    "RegularMarketTime": info.get("regularMarketTime"), # Last Price Update DateTime
                    "Industry": info.get("industry"), # Company Industry Running on
                    "IndustryKey": info.get("industryKey"), # Company Industry Key
                    "Sector": info.get("sector"), # Company Sector Running on
                    "SectorKey": info.get("sectorKey"), # Company Sector Key
                    "Code": info.get("symbol"), # Company IDX Code List
                    "ShortName": info.get("shortName"), # Company Name (Short Name)
                    "LongName": info.get("longName"), # Company Name (Full Name)
                    "Open": info.get("open"), # Open Price
                    "LastDividendValue": info.get("lastDividendValue"), # Last Dividend Payout
                    "LastDividendDate": info.get("lastDividendDate"), # Last Dividend Payout DateTime
                    "DividendRate": info.get("dividendRate"), # Dividend Rate (maybe average)
                    "DividendYield": info.get("dividendYield"), # Dividend Yield (Stock Price to Dividend Payout Value Conversion Ratio)
                    "MostRecentQuarter": info.get("mostRecentQuarter"), # Last Quarterly Finance Report DateTime
                }
                
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                not_listed_companies.append({"emiten": ticker, "error": str(e)})
                
        return stock_data

    def get_dividend_data(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Fetch dividend data for the given tickers using yfinance.
        """
        
        listed_companies, not_listed_companies = self.read_data(tickers)
        
        dividend_data = {}
        for company in listed_companies:
            ticker = company["emiten"]
            try:
                dividends = yf.Ticker(str(ticker)).get_dividends(period="5y")
                dividends.index = pd.to_datetime(dividends.index).strftime('%d-%m-%Y')
                dividend_data[str(ticker)] = dividends.to_dict()
            except Exception as e:
                print(f"Error fetching dividend data for {ticker}: {e}")
                not_listed_companies.append({"emiten": ticker, "error": str(e)}) 
                
        return dividend_data   
    
class Command(BaseCommand):
    help = 'Fetch stock data and dividend data for given tickers using yfinance'

    def add_arguments(self, parser):
        parser.add_argument(
            'tickers', 
            nargs='*', 
            type=str,
            default=[], 
            help='List of stock tickers to fetch data for'
        ),
        parser.add_argument(
            '--limit', 
            type=int, 
            default=0,
            help='Maximum number of stock tickers to fetch data'
        ),
        parser.add_argument(
            '--offset',
            type=int,
            default=0,
            help='Starting index in the ticker list (for chunked batch execution).'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Delay in seconds between individual API calls.'
        )

    def handle(self, *args, **options):
        input_tickers = options['tickers']
        limit = options['limit']
        offset = options['offset']
        delay = options['delay']
        
        if not input_tickers:
            df = pd.read_csv(CSV_PATH)
            for code in df['code'].astype(str):
                input_tickers.append(f"{code.strip().upper()}")
            
        if offset > 0:
            input_tickers = input_tickers[offset:]
        if limit > 0:
            input_tickers = input_tickers[:limit]

        self.stdout.write(
            self.style.NOTICE(
                f"Processing chunk of {len(input_tickers)} tickers "
                f"(Offset: {offset}, Limit: {limit}, Delay: {delay}s)..."
            )
        )
         
        fetcher = StockDataFetcher(input_tickers)
        
        stock_data = fetcher.fetch_stock_data(input_tickers)
        dividend_data = fetcher.get_dividend_data(input_tickers)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully processed {len(stock_data)} stock entries."))

        # Display output summary
        self.stdout.write(self.style.SUCCESS('Stock Metadata Sample:'))
        self.stdout.write(json.dumps(dict(list(stock_data.items())), indent=4))
        
        self.stdout.write(self.style.SUCCESS('Dividend Data Sample:'))
        self.stdout.write(json.dumps(dict(list(dividend_data.items())), indent=4))

        