from django.contrib import admin
from .models import UserProfile, Stock, Transaction, PendingSell

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username',)
    ordering = ('user__username',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'price', 'market_cap', 'sector')
    search_fields = ('symbol', 'name', 'sector')
    list_filter = ('sector',)
    ordering = ('symbol',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock', 'quantity', 'price', 'date', 'type')
    search_fields = ('user__user__username', 'stock__symbol')
    list_filter = ('type', 'date')
    date_hierarchy = 'date'
    ordering = ('-date',)

@admin.register(PendingSell)
class PendingSellAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock', 'target_price', 'created_at')
    search_fields = ('user__user__username', 'stock__symbol')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
