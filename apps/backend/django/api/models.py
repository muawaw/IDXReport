from django.db import models

class Stock(models.Model):
    # Unique Identifier
    update_price_date = models.BigIntegerField(null=True, blank=True)  # Unix Timestamp
    
    # Stock Info Fields
    code = models.CharField(max_length=20, unique=True, primary_key=True)
    short_name = models.CharField(max_length=255, blank=True, null=True)
    long_name = models.CharField(max_length=255, blank=True, null=True)
    
    industry = models.CharField(max_length=255, blank=True, null=True)
    industry_key = models.CharField(max_length=255, blank=True, null=True)
    sector = models.CharField(max_length=255, blank=True, null=True)
    sector_key = models.CharField(max_length=255, blank=True, null=True)
    
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    last_dividend_value = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    last_dividend_date = models.BigIntegerField(null=True, blank=True)  # Unix Timestamp
    finance_quarter_date = models.BigIntegerField(null=True, blank=True)  # Unix Timestamp
    dividend_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    dividend_yield = models.FloatField(null=True, blank=True)
    
    # Dividend History (Nested JSON mapping: {"DD-MM-YYYY": Amount})
    dividends = models.JSONField(default=dict, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.short_name}"