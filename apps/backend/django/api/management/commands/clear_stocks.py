# app/management/commands/clear_stocks.py
from django.core.management.base import BaseCommand
from api.models import Stock

class Command(BaseCommand):
    help = "Clears all Stock and Dividend records from SQLite"

    def handle(self, *args, **kwargs):
        count, _ = Stock.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} records."))