from django.shortcuts import render
from .models import Stock, Dividend
from .serializer import StockCombinedSerializer, StockOnlySerializer, DividendOnlySerializer
from django.http import JsonResponse
from django.db import connection

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

def health_check(request):
    """
    Root API Health Check
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse(
            {
                "status": "Connected",
                "message": "Server Successfully Connected"
            },
            status=200
        )
    except Exception as e:
        return JsonResponse(
            {
                "status": "Failed",
                "message": str(e)
            },
            status=500
        )
    

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides standard and custom endpoints dynamically:
    1. GET /api/stocks/              -> All Combined Data (Stock + Dividends)
    2. GET /api/stocks/stocks-only/   -> Stock Metadata ONLY
    3. GET /api/stocks/dividends-only/ -> Dividend JSON History ONLY
    """
    queryset = Stock.objects.all()
    serializer_class = StockCombinedSerializer

    def get_queryset(self):
        # Default endpoint uses select_related for the JOIN optimization
        if self.action == 'list' or self.action == 'retrieve':
            return Stock.objects.select_related('dividend_history').all()
        return Stock.objects.all()

    @action(detail=False, methods=['get'], url_path='stocks-only')
    def stocks_only(self, request):
        """Endpoint: /api/stocks/stocks-only/"""
        # NO JOIN executed here — ultra-fast metadata fetch
        stocks = self.get_queryset()
        serializer = StockOnlySerializer(stocks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='dividends-only')
    def dividends_only(self, request):
        """Endpoint: /api/stocks/dividends-only/"""
        # Fetches only the Dividend table JSON objects
        dividends = Dividend.objects.all()
        serializer = DividendOnlySerializer(dividends, many=True)
        return Response(serializer.data)