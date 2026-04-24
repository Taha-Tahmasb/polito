from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Asset, Portfolio, Transaction


class PortfolioModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alex', password='secret123')
        self.portfolio = Portfolio.objects.create(
            owner=self.user,
            name='Core Growth',
            cash_balance=Decimal('2500.00'),
            target_return=Decimal('14.50'),
        )
        self.asset = Asset.objects.create(
            portfolio=self.portfolio,
            symbol='AAPL',
            name='Apple',
            asset_type=Asset.AssetType.STOCK,
            quantity=Decimal('10'),
            average_cost=Decimal('150'),
            current_price=Decimal('180'),
        )
        Transaction.objects.create(
            portfolio=self.portfolio,
            asset=self.asset,
            transaction_type=Transaction.TransactionType.BUY,
            quantity=Decimal('10'),
            price_per_unit=Decimal('150'),
        )

    def test_portfolio_total_value_includes_cash_and_assets(self):
        self.assertEqual(self.portfolio.holdings_value, Decimal('1800'))
        self.assertEqual(self.portfolio.total_value, Decimal('4300.00'))

    def test_asset_profit_metrics(self):
        self.assertEqual(self.asset.cost_basis, Decimal('1500'))
        self.assertEqual(self.asset.market_value, Decimal('1800'))
        self.assertEqual(self.asset.pnl, Decimal('300'))


class PortfolioViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jamie', password='secret123')
        self.other_user = User.objects.create_user(username='riley', password='secret123')
        self.portfolio = Portfolio.objects.create(
            owner=self.user,
            name='Income Plan',
            description='Dividend focus',
            cash_balance=Decimal('1200.00'),
            target_return=Decimal('9.00'),
        )
        self.other_portfolio = Portfolio.objects.create(
            owner=self.other_user,
            name='Private Plan',
            cash_balance=Decimal('900.00'),
            target_return=Decimal('7.00'),
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('portfolio:dashboard'))
        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_dashboard_page_renders_for_authenticated_user(self):
        self.client.login(username='jamie', password='secret123')
        response = self.client.get(reverse('portfolio:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Portfolio overview')
        self.assertContains(response, 'Income Plan')
        self.assertNotContains(response, 'Private Plan')

    def test_create_portfolio_flow_assigns_logged_in_user(self):
        self.client.login(username='jamie', password='secret123')
        response = self.client.post(
            reverse('portfolio:create'),
            {
                'name': 'Retirement Vault',
                'description': 'Long-term index strategy',
                'cash_balance': '4500.00',
                'target_return': '8.50',
            },
        )
        self.assertRedirects(response, reverse('portfolio:list'))
        self.assertTrue(Portfolio.objects.filter(name='Retirement Vault', owner=self.user).exists())

    def test_detail_view_blocks_other_users_portfolio(self):
        self.client.login(username='jamie', password='secret123')
        response = self.client.get(reverse('portfolio:detail', args=[self.other_portfolio.pk]))
        self.assertEqual(response.status_code, 404)
