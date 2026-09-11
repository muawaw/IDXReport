from django.db import transaction
from api.models import Stock, StockPriceHistory  # Adjust app name accordingly

def save_or_update_stocks(stock_data: dict) -> int:
    classification_data = stock_data.get("^JKSE", {}).get("Classification", {})
    records_processed = 0

    history_snapshots = []

    with transaction.atomic():
        for board_name, tickers_map in classification_data.items():
            for symbol, info in tickers_map.items():
                if not info:
                    continue

                defaults = {
                    "listing_board": board_name,
                    "short_name": info.get("ShortName"),
                    "long_name": info.get("LongName"),
                    "industry": info.get("Industry"),
                    "industry_key": info.get("IndustryKey"),
                    "sector": info.get("Sector"),
                    "sector_key": info.get("SectorKey"),
                    "open_price": info.get("Open"),
                    "close_price": info.get("Close"),
                    "low_price": info.get("Low"),
                    "high_price": info.get("High"),
                    "last_dividend_value": info.get("LastDividendValue"),
                    "last_dividend_date": info.get("LastDividendDate"),
                    "dividend_rate": info.get("DividendRate"),
                    "dividend_yield": info.get("DividendYield"),
                    "dividends": info.get("DividendHistory", {}),
                }

                # 1. Upsert stock metadata
                stock_obj, _ = Stock.objects.update_or_create(
                    code=symbol,
                    defaults=defaults
                )

                # 2. Prepare historical snapshot entry
                history_snapshots.append(
                    StockPriceHistory(
                        stock=stock_obj,
                        open_price=info.get("Open"),
                        close_price=info.get("Close"),
                        low_price=info.get("Low"),
                        high_price=info.get("High"),
                        dividend_yield=info.get("DividendYield"),
                        market_time=info.get("RegularMarketTime"),
                    )
                )
                records_processed += 1

        # Bulk create history entries in one DB query for high performance
        if history_snapshots:
            StockPriceHistory.objects.bulk_create(history_snapshots, batch_size=500)

    return records_processed