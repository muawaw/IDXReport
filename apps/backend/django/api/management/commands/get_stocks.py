import yfinance as yf
import pandas as pd
<<<<<<< HEAD
from typing import List, Tuple, Dict, Any, Optional
import os
=======
from typing import List, Dict, Any, Optional
>>>>>>> 6875b589f16cf4e950b7f77270f0259a7fd45bad
from pathlib import Path
import time

<<<<<<< HEAD
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Stock, Dividend


CSV_PATH = Path(__file__).resolve().parent / "list_idx.csv"

class StockDataFetcher:
    def __init__(self, tickers: List[str]):
        self.tickers = tickers
        
    def read_data(self, tickers: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
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
    
    @staticmethod
    def parse_data_variable(variable: Any) -> Any:
        """
        Data validation checker if the data is Unix Timestamp then Parse it to ISO Format else dont
        """
        # Detect Unix Epoch Timestamps (e.g. 1700000000+ is post-2023)
        if isinstance(variable, (int, float)) and not isinstance(variable, bool):
            if variable > 946684800:  # Epoch for Jan 1, 2000
                try:
                    converted_timestamp = pd.to_datetime(variable, unit = 's').strftime("%Y-%m-%dT%H:%M:%S")
                    return converted_timestamp
                except Exception:
                    return variable
            else:
                return variable
        else:
            return variable
    
    def fetch_stock_data(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Fetch stock data for the given tickers using yfinance.
        """
        listed_companies, not_listed_companies = self.read_data(tickers)
        
        field_map = {
            "regularMarketTime",  # Last Price Update DateTime
            "industry", # Company Industry Running on
            "industryKey", # Company Industry Key
            "sector", # Company Sector Running on
            "sectorKey", # Company Sector Key
            "symbol", # Company IDX Code List
            "shortName", # Company Name (Short Name)
            "longName", # Company Name (Full Name)
            "open", # Open Price
            "lastDividendValue", # Last Dividend Payout
            "lastDividendDate", # Last Dividend Payout DateTime
            "dividendRate", # Dividend Rate (maybe average)
            "dividendYield", # Dividend Yield (Stock Price to Dividend Payout Value Conversion Ratio)
            "mostRecentQuarter" # Last Quarterly Finance Report DateTime
        }
        
        stock_data = {}
        for company in listed_companies:
            ticker = company["emiten"]
            try:
                stock = yf.Ticker(str(ticker))
                info = stock.info
                
                processed_field = {}
                for field in field_map:
                    raw_field = info.get(field)
                    processed_field[field] = self.parse_data_variable(variable=raw_field) 
                    
                stock_data[str(ticker)] = processed_field
                
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                not_listed_companies.append({"emiten": ticker, "error": str(e)})
                
=======
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
        
>>>>>>> 6875b589f16cf4e950b7f77270f0259a7fd45bad
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
                
<<<<<<< HEAD
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
        )
        parser.add_argument(
            '--limit', 
            type=int, 
            default=0,
            help='Maximum number of stock tickers to fetch data'
        )
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
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Wipe existing Stock and Dividend data before fetching new records'
        )
        
    def insert_update_method(self, stock_data: dict, dividend_data: dict) -> tuple[int, int]:
        """
        Handle the method to insert or update of Django ORM
        """
        stocks_created = 0
        stocks_updated = 0
        
        with transaction.atomic():
            for ticker, data in stock_data.items():
                # Extract and format last_dividend_date to match DateField (YYYY-MM-DD)
                raw_div_date = data.get("lastDividendDate")
                formatted_div_date = raw_div_date.split('T')[0] if raw_div_date and 'T' in str(raw_div_date) else raw_div_date

                # Insert or Update Stock Data using camelCase dict keys
                stock_obj, created = Stock.objects.update_or_create(
                    code = ticker,
                    defaults= {
                        "regular_market_time": data.get("regularMarketTime"),
                        "industry": data.get("industry"),
                        "industry_key": data.get("industryKey"),
                        "sector": data.get("sector"),
                        "sector_key": data.get("sectorKey"),
                        "short_name": data.get("shortName"),
                        "long_name": data.get("longName"),
                        "open_price": data.get("open"),
                        "last_dividend_value": data.get("lastDividendValue"),
                        "last_dividend_date": formatted_div_date,
                        "dividend_rate": data.get("dividendRate"),
                        "dividend_yield": data.get("dividendYield"),
                        "most_recent_quarter": data.get("mostRecentQuarter"),
                    }
                )
                
                if created:
                    stocks_created += 1
                else:
                    stocks_updated += 1
                    
                # Upsert related Dividend model JSONField
                ticker_divs = dividend_data.get(ticker, {})
                Dividend.objects.update_or_create(
                    stock=stock_obj,
                    defaults= {
                        "dividends": ticker_divs
                    }
                )
                    
        return stocks_created, stocks_updated  
        

    def handle(self, *args, **options):
        input_tickers = options['tickers']
        limit = options['limit']
        offset = options['offset']
        delay = options['delay']
        
        if options['clear']:
            deleted_count, _ = Stock.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Cleaned database: Removed {deleted_count} stock/dividend records.")
            )
            
        self.stdout.write(self.style.SUCCESS(f"Starting ingestion (Limit: {limit or 'All'})..."))
        
        if not input_tickers:
            df = pd.read_csv(CSV_PATH)
            input_tickers = [f"{str(code).strip().upper()}" for code in df['code']]
            
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
        
        created_count, updated_count = self.insert_update_method(stock_data, dividend_data)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully ingested data into DB! Created: {created_count}, Updated: {updated_count}."
            )
        )

        if stock_data:
            sample_code = next(iter(stock_data))
            sample_payload = {
                "stock": stock_data[sample_code],
                "dividends": dividend_data.get(sample_code, {})
            }
            
            self.stdout.write(self.style.NOTICE("Sample Output (1 record):"))
            self.stdout.write(json.dumps({sample_code: sample_payload}, indent=2, default=str))
=======
        return {}   
        
>>>>>>> 6875b589f16cf4e950b7f77270f0259a7fd45bad
