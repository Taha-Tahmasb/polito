from django.contrib import admin

from .models import Asset, Portfolio, Transaction


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'cash_balance', 'target_return', 'updated_at')
    search_fields = ('name', 'owner__username')


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'portfolio', 'asset_type', 'quantity', 'average_cost', 'current_price')
    list_filter = ('asset_type', 'portfolio')
    search_fields = ('symbol', 'name', 'portfolio__name')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'portfolio', 'asset', 'quantity', 'price_per_unit', 'executed_at')
    list_filter = ('transaction_type', 'portfolio')
    search_fields = ('portfolio__name', 'asset__symbol', 'notes')
