from django.core.management.base import BaseCommand
from simulator.views import update_stock_prices  

class Command(BaseCommand):
    help = 'Update stock prices and historical data'

    def handle(self, *args, **kwargs):
        updated_stocks = update_stock_prices()
        self.stdout.write(self.style.SUCCESS(f"Successfully updated stocks: {', '.join(updated_stocks)}"))
