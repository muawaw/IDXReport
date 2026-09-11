from django.db import models

class Stock(models.Model):
    """Current state and metadata for each listed stock."""
    code = models.CharField(max_length=20, primary_key=True)  # e.g., BBCA.JK
    short_name = models.CharField(max_length=255, blank=True, null=True)
    long_name = models.CharField(max_length=255, blank=True, null=True)
    listing_board = models.CharField(max_length=100, blank=True, null=True)

    # Sector & Industry Metadata
    industry = models.CharField(max_length=255, blank=True, null=True)
    industry_key = models.CharField(max_length=255, blank=True, null=True)
    sector = models.CharField(max_length=255, blank=True, null=True)
    sector_key = models.CharField(max_length=255, blank=True, null=True)

    # Latest Dividend Metadata
    last_dividend_value = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    last_dividend_date = models.CharField(max_length=50, blank=True, null=True)  # Fixed: String to match ISO output
    dividend_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    dividend_yield = models.FloatField(null=True, blank=True)
    dividends = models.JSONField(default=dict, blank=True)  # Full historical dividend dict

    # Latest Pricing Snapshot
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    close_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    low_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    high_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stocks"

    def __str__(self):
        return f"{self.code} - {self.short_name or 'N/A'}"


class StockPriceHistory(models.Model):
    """Time-series table for historical analytics and frontend charts."""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="price_history")
    
    # Snapshot Metrics
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    close_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    low_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    high_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    dividend_yield = models.FloatField(null=True, blank=True)
    
    # Timestamps
    market_time = models.CharField(max_length=50, blank=True, null=True, db_index=True)  # Fixed: String to match ISO output
    fetched_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Creation timestamp

    class Meta:
        db_table = "stock_price_history"
        ordering = ["-fetched_at"]
        indexes = [
            models.Index(fields=["stock", "-fetched_at"]),  # Speeds up analytics queries for JSX
        ]