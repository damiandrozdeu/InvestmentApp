from django.contrib import admin
from .models import UserProfile, Stock, Transaction

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'price', 'market_cap', 'sector')
    search_fields = ('symbol', 'name', 'sector')
    list_filter = ('sector',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock', 'quantity', 'price', 'date', 'type')
    search_fields = ('user__user__username', 'stock__symbol')
    list_filter = ('type', 'date')
    date_hierarchy = 'date'
