from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils import timezone


class Portfolio(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='portfolios', on_delete=models.CASCADE, verbose_name='مالک')
    name = models.CharField(max_length=120, verbose_name='نام پرتفوی')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    cash_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='موجودی نقدی')
    target_return = models.DecimalField(max_digits=5, decimal_places=2, default=12, verbose_name='بازده هدف')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین به روزرسانی')

    class Meta:
        ordering = ['name']
        verbose_name = 'پرتفوی'
        verbose_name_plural = 'پرتفوی ها'

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
        STOCK = 'stock', 'سهام'
        ETF = 'etf', 'ETF'
        CRYPTO = 'crypto', 'رمزارز'
        BOND = 'bond', 'اوراق'
        CASH = 'cash', 'نقد'

    portfolio = models.ForeignKey(Portfolio, related_name='assets', on_delete=models.CASCADE, verbose_name='پرتفوی')
    symbol = models.CharField(max_length=12, verbose_name='نماد')
    name = models.CharField(max_length=120, verbose_name='نام دارایی')
    asset_type = models.CharField(max_length=20, choices=AssetType.choices, default=AssetType.STOCK, verbose_name='نوع دارایی')
    quantity = models.DecimalField(max_digits=12, decimal_places=4, validators=[MinValueValidator(Decimal('0'))], verbose_name='تعداد')
    average_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))], verbose_name='میانگین قیمت خرید')
    current_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))], verbose_name='قیمت فعلی')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='آخرین به روزرسانی')

    class Meta:
        ordering = ['symbol']
        unique_together = ('portfolio', 'symbol')
        verbose_name = 'دارایی'
        verbose_name_plural = 'دارایی ها'

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
        BUY = 'buy', 'خرید'
        SELL = 'sell', 'فروش'
        DIVIDEND = 'dividend', 'سود نقدی'
        DEPOSIT = 'deposit', 'واریز'

    portfolio = models.ForeignKey(Portfolio, related_name='transactions', on_delete=models.CASCADE, verbose_name='پرتفوی')
    asset = models.ForeignKey(Asset, related_name='transactions', on_delete=models.CASCADE, blank=True, null=True, verbose_name='دارایی')
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices, verbose_name='نوع تراکنش')
    quantity = models.DecimalField(max_digits=12, decimal_places=4, default=0, validators=[MinValueValidator(Decimal('0'))], verbose_name='تعداد')
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))], verbose_name='قیمت هر واحد')
    notes = models.CharField(max_length=255, blank=True, verbose_name='یادداشت')
    executed_at = models.DateField(default=timezone.localdate, verbose_name='تاریخ اجرا')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')

    class Meta:
        ordering = ['-executed_at', '-created_at']
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش ها'

    def __str__(self):
        return f'{self.get_transaction_type_display()} - {self.portfolio.name}'

    @property
    def total_amount(self):
        return self.quantity * self.price_per_unit
