from django.contrib import admin
from .models import UserProfile, Stock, StockHistory, Transaction, PendingSell, Favorite

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username',)
    ordering = ('user__username',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'price', 'sector', 'last_updated')
    search_fields = ('symbol', 'name', 'sector')
    list_filter = ('sector',)
    ordering = ('symbol',)

@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'close_price')
    search_fields = ('stock__symbol',)
    list_filter = ('date',)
    date_hierarchy = 'date'
    ordering = ('-date',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock', 'quantity', 'price', 'type', 'date')
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

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock')
    search_fields = ('user__user__username', 'stock__symbol')
