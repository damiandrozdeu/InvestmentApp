from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    market_cap = models.BigIntegerField(null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    last_updated = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

class StockHistory(models.Model):
    stock = models.ForeignKey(Stock, related_name='history', on_delete=models.CASCADE)
    date = models.DateField()
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('stock', 'date')  # Prevent duplicate records for the same stock and date

    def __str__(self):
        return f"{self.stock.symbol} - {self.date}: {self.close_price}"



class Transaction(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=4, choices=(('BUY', 'Buy'), ('SELL', 'Sell')))

    def __str__(self):
        return f"{self.user.user.username} - {self.stock.symbol} ({self.quantity})"


class PendingSell(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pending sell for {self.quantity} shares of {self.stock.symbol} at ${self.target_price} by {self.user.user.username}"
class Favorite(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.user.username} - {self.stock.symbol}"