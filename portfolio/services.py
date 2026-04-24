from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.utils import timezone

from .models import Transaction


def validate_transaction_effect(portfolio, asset, transaction_type, quantity, price_per_unit):
    total_amount = quantity * price_per_unit

    if transaction_type == Transaction.TransactionType.DEPOSIT and asset is not None:
        raise ValidationError('Deposits should not be linked to an asset.')

    if transaction_type in {
        Transaction.TransactionType.BUY,
        Transaction.TransactionType.SELL,
        Transaction.TransactionType.DIVIDEND,
    } and asset is None:
        raise ValidationError('Select an asset for buys, sells, and dividends.')

    if asset is not None and asset.portfolio_id != portfolio.id:
        raise ValidationError('The selected asset does not belong to this portfolio.')

    if transaction_type == Transaction.TransactionType.BUY and portfolio.cash_balance < total_amount:
        raise ValidationError('This portfolio does not have enough cash for that purchase.')

    if transaction_type == Transaction.TransactionType.SELL and asset.quantity < quantity:
        raise ValidationError('You cannot sell more units than you currently hold.')


@db_transaction.atomic
def apply_transaction(transaction):
    portfolio = transaction.portfolio
    asset = transaction.asset
    quantity = transaction.quantity
    price_per_unit = transaction.price_per_unit
    total_amount = transaction.total_amount

    validate_transaction_effect(
        portfolio=portfolio,
        asset=asset,
        transaction_type=transaction.transaction_type,
        quantity=quantity,
        price_per_unit=price_per_unit,
    )

    if transaction.transaction_type == Transaction.TransactionType.DEPOSIT:
        portfolio.cash_balance += total_amount
        portfolio.save(update_fields=['cash_balance', 'updated_at'])
        transaction.save()
        return transaction

    if transaction.transaction_type == Transaction.TransactionType.BUY:
        existing_cost_basis = asset.quantity * asset.average_cost
        new_quantity = asset.quantity + quantity

        portfolio.cash_balance -= total_amount
        asset.quantity = new_quantity
        asset.average_cost = (existing_cost_basis + total_amount) / new_quantity if new_quantity else Decimal('0')
        asset.current_price = price_per_unit
        asset.updated_at = timezone.now()

        portfolio.save(update_fields=['cash_balance', 'updated_at'])
        asset.save(update_fields=['quantity', 'average_cost', 'current_price', 'updated_at'])
        transaction.save()
        return transaction

    if transaction.transaction_type == Transaction.TransactionType.SELL:
        portfolio.cash_balance += total_amount
        asset.quantity -= quantity
        asset.current_price = price_per_unit
        asset.updated_at = timezone.now()

        portfolio.save(update_fields=['cash_balance', 'updated_at'])
        asset.save(update_fields=['quantity', 'current_price', 'updated_at'])
        transaction.save()
        return transaction

    if transaction.transaction_type == Transaction.TransactionType.DIVIDEND:
        portfolio.cash_balance += total_amount
        asset.current_price = price_per_unit
        asset.updated_at = timezone.now()

        portfolio.save(update_fields=['cash_balance', 'updated_at'])
        asset.save(update_fields=['current_price', 'updated_at'])
        transaction.save()
        return transaction

    transaction.save()
    return transaction
