from django.core.management.base import BaseCommand
from simulator.models import Stock
import yfinance as yf

class Command(BaseCommand):
    help = 'Update stock prices'

    def handle(self, *args, **kwargs):
        symbols = [stock.symbol for stock in Stock.objects.all()]
        if not symbols:
            self.stdout.write(self.style.WARNING('No stocks found in database.'))
            return

        data = yf.download(tickers=" ".join(symbols), group_by='ticker', period="1d")
        for symbol in symbols:
            try:
                if symbol in data:
                    price = data[symbol]['Close'].iloc[-1]
                    stock = Stock.objects.get(symbol=symbol)
                    stock.price = price
                    stock.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated {symbol}: {price}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No data for {symbol}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating {symbol}: {e}'))
