from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils import timezone


class Portfolio(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='portfolios', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    cash_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_return = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.owner.username})'

    @cached_property
    def invested_amount(self):
        buys = Decimal('0')
        sells = Decimal('0')
        for transaction in self.transactions.all():
            amount = transaction.total_amount
            if transaction.transaction_type == Transaction.TransactionType.BUY:
                buys += amount
            elif transaction.transaction_type == Transaction.TransactionType.SELL:
                sells += amount
        return buys - sells

    @cached_property
    def holdings_value(self):
        total = Decimal('0')
        for asset in self.assets.all():
            total += asset.market_value
        return total

    @property
    def total_value(self):
        return self.cash_balance + self.holdings_value

    @cached_property
    def unrealized_profit(self):
        cost_basis = Decimal('0')
        for asset in self.assets.all():
            cost_basis += asset.cost_basis
        return self.holdings_value - cost_basis


class Asset(models.Model):
    class AssetType(models.TextChoices):
        STOCK = 'stock', 'Stock'
        ETF = 'etf', 'ETF'
        CRYPTO = 'crypto', 'Crypto'
        BOND = 'bond', 'Bond'
        CASH = 'cash', 'Cash'

    portfolio = models.ForeignKey(Portfolio, related_name='assets', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=12)
    name = models.CharField(max_length=120)
    asset_type = models.CharField(max_length=20, choices=AssetType.choices, default=AssetType.STOCK)
    quantity = models.DecimalField(max_digits=12, decimal_places=4, validators=[MinValueValidator(Decimal('0'))])
    average_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    current_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['symbol']
        unique_together = ('portfolio', 'symbol')

    def __str__(self):
        return f'{self.symbol} - {self.portfolio.name}'

    @property
    def cost_basis(self):
        return self.quantity * self.average_cost

    @property
    def market_value(self):
        return self.quantity * self.current_price

    @property
    def pnl(self):
        return self.market_value - self.cost_basis

    @property
    def pnl_percent(self):
        if self.cost_basis == 0:
            return Decimal('0')
        return (self.pnl / self.cost_basis) * 100


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        BUY = 'buy', 'Buy'
        SELL = 'sell', 'Sell'
        DIVIDEND = 'dividend', 'Dividend'
        DEPOSIT = 'deposit', 'Deposit'

    portfolio = models.ForeignKey(Portfolio, related_name='transactions', on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, related_name='transactions', on_delete=models.CASCADE, blank=True, null=True)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    quantity = models.DecimalField(max_digits=12, decimal_places=4, default=0, validators=[MinValueValidator(Decimal('0'))])
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    notes = models.CharField(max_length=255, blank=True)
    executed_at = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-executed_at', '-created_at']

    def __str__(self):
        return f'{self.get_transaction_type_display()} - {self.portfolio.name}'

    @property
    def total_amount(self):
        return self.quantity * self.price_per_unit
