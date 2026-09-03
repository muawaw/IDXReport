from django.db import models

class Stock(models.Model):
    # Primary Key
    code = models.CharField(max_length=20, primary_key=True)
    
    # Metadata
    short_name = models.CharField(max_length=255, null=True, blank=True)
    long_name = models.CharField(max_length=255, null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    industry_key = models.CharField(max_length=255, null=True, blank=True)
    sector = models.CharField(max_length=255, null=True, blank=True)
    sector_key = models.CharField(max_length=255, null=True, blank=True)
    
    # Financial Metrics
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    last_dividend_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Properly typed Dates instead of BigIntegerField
    last_dividend_date = models.DateField(null=True, blank=True)
    regular_market_time = models.DateTimeField(null=True, blank=True)
    most_recent_quarter = models.DateTimeField(null=True, blank=True)
    
    dividend_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    dividend_yield = models.FloatField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.code

class Dividend(models.Model):   
    stock = models.OneToOneField(
        'Stock', 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='dividend_history'
    )
     
    # Dividend History (Nested JSON mapping: {"ISO Format Date": Amount})
    dividends = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dividends for {self.stock_id}"