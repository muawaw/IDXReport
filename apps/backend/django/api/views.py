from django.shortcuts import render
from .models import Stock, StockPriceHistory
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
    1. GET /api/stocks/              -> All Combined Data (Stock + Price History)
    2. GET /api/stocks/stocks-only/   -> Stock Metadata ONLY
    """
    queryset = Stock.objects.all()
    serializer_class = StockCombinedSerializer

    def get_queryset(self):
        # Optimized query using the valid related name defined on StockPriceHistory
        if self.action in ['list', 'retrieve']:
            return Stock.objects.prefetch_related('price_history').all()
        return Stock.objects.all()

    @action(detail=False, methods=['get'], url_path='stocks-only')
    def stocks_only(self, request):
        """Endpoint: /api/stocks/stocks-only/"""
        stocks = self.get_queryset()
        serializer = StockOnlySerializer(stocks, many=True)
        return Response(serializer.data)