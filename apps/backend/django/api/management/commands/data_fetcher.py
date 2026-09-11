import pandas as pd
import json

from django.core.management.base import BaseCommand
from .get_stocks import CSV_PATH, StockDataFetcher
from helper.db_service import save_or_update_stocks

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
            help='Starting index in the ticker list.'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.5,
            help='Delay in seconds between individual API calls.'
        )

    def handle(self, *args, **options):
        input_tickers = options['tickers']
        limit = options['limit']
        offset = options['offset']
        delay = options['delay']
        
        # Normalize input tickers to ensure .JK suffix
        formatted_tickers = []
        if input_tickers:
            for t in input_tickers:
                t_clean = t.strip().upper()
                if not t_clean.endswith(".JK"):
                    t_clean += ".JK"
                formatted_tickers.append(t_clean)
                
        if offset > 0:
            formatted_tickers = formatted_tickers[offset:]
        if limit > 0:
            formatted_tickers = formatted_tickers[:limit]

        self.stdout.write(
            self.style.NOTICE(
                f"Processing batch execution... "
                f"(Offset: {offset}, Limit: {limit}, Delay: {delay}s)"
            )
        )
         
        fetcher = StockDataFetcher()
        stock_data = fetcher.fetch_stock_data(tickers=formatted_tickers, delay=delay)
        
        total_fetched = sum(
            len(board_data) 
            for board_data in stock_data.get("^JKSE", {}).get("Classification", {}).values()
        )

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {total_fetched} stock entries."))
        
        sample_data = {"^JKSE": {"Classification": {}}}

        for board, tickers in stock_data.get("^JKSE", {}).get("Classification", {}).items():
            # Slices the first item from each board dictionary
            sample_data["^JKSE"]["Classification"][board] = dict(list(tickers.items())[:1])

        # 3. Print only the sample
        self.stdout.write(self.style.SUCCESS('Stock Metadata Sample (1 per Board):'))
        self.stdout.write(json.dumps(sample_data, indent=4))
        
        # Insert or Update to table
        save_or_update_stocks(stock_data=stock_data)