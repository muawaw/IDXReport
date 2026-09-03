from rest_framework import serializers
from .models import Stock, Dividend


class StockCombinedSerializer(serializers.ModelSerializer):
    """
    Serializer for Combined (Join) Stocks and Dividends data
    """
    dividend_history = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [
            'code', 
            'short_name', 
            'long_name', 
            'industry', 
            'sector',
            'open_price', 
            'regular_market_time', 
            'last_dividend_value',
            'last_dividend_date', 
            'dividend_rate', 
            'dividend_yield',
            'dividend_history',
        ]

    def get_dividend_history(self, obj: Stock) -> dict:
        """
        Safely reaches through the OneToOneField relationship 
        to return the raw JSON dict from the Dividend model.
        """
        try:
            # Reaches through the 'related_name' defined on OneToOneField
            if hasattr(obj, 'dividend_history') and obj.dividend_history is not None:
                return obj.dividend_history.dividends
        except Exception:
            return {}
            
        return {}
    
class StockOnlySerializer(serializers.ModelSerializer):
    """
    Serializer for Stock data only
    """
    
    class Meta:
        model = Stock
        fields = [
            'code', 
            'short_name', 
            'long_name', 
            'industry', 
            'sector',
            'open_price', 
            'regular_market_time', 
            'last_dividend_value',
            'last_dividend_date', 
            'dividend_rate', 
            'dividend_yield',
        ]
        
class DividendOnlySerializer(serializers.ModelSerializer):
    """
    Serializer for Dividend data only
    """
    
    code = serializers.CharField(source='stock.code', read_only=True)

    class Meta:
        model = Dividend
        fields = [
            'code', 
            'dividends', 
            'updated_at'
        ]