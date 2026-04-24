from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management import call_command
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


class TransactionWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='morgan', password='secret123')
        self.portfolio = Portfolio.objects.create(
            owner=self.user,
            name='Active Account',
            cash_balance=Decimal('5000.00'),
            target_return=Decimal('12.00'),
        )
        self.asset = Asset.objects.create(
            portfolio=self.portfolio,
            symbol='MSFT',
            name='Microsoft',
            asset_type=Asset.AssetType.STOCK,
            quantity=Decimal('5'),
            average_cost=Decimal('200.00'),
            current_price=Decimal('220.00'),
        )

    def test_buy_transaction_updates_cash_and_weighted_average_cost(self):
        self.client.login(username='morgan', password='secret123')
        response = self.client.post(
            reverse('portfolio:transaction-create'),
            {
                'portfolio': self.portfolio.pk,
                'asset': self.asset.pk,
                'transaction_type': Transaction.TransactionType.BUY,
                'quantity': '3',
                'price_per_unit': '260.00',
                'executed_at': '2025-01-10',
                'notes': 'Added on pullback',
            },
        )

        self.assertRedirects(response, reverse('portfolio:dashboard'))
        self.portfolio.refresh_from_db()
        self.asset.refresh_from_db()
        self.assertEqual(self.portfolio.cash_balance, Decimal('4220.00'))
        self.assertEqual(self.asset.quantity, Decimal('8.0000'))
        self.assertEqual(self.asset.average_cost, Decimal('222.50'))
        self.assertEqual(self.asset.current_price, Decimal('260.00'))

    def test_sell_transaction_rejects_position_that_is_too_large(self):
        self.client.login(username='morgan', password='secret123')
        response = self.client.post(
            reverse('portfolio:transaction-create'),
            {
                'portfolio': self.portfolio.pk,
                'asset': self.asset.pk,
                'transaction_type': Transaction.TransactionType.SELL,
                'quantity': '7',
                'price_per_unit': '230.00',
                'executed_at': '2025-01-10',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'نمی توانید بیشتر از تعداد دارایی موجود، فروش ثبت کنید.')

    def test_deposit_transaction_requires_no_asset_and_increases_cash(self):
        self.client.login(username='morgan', password='secret123')
        response = self.client.post(
            reverse('portfolio:transaction-create'),
            {
                'portfolio': self.portfolio.pk,
                'transaction_type': Transaction.TransactionType.DEPOSIT,
                'quantity': '1',
                'price_per_unit': '1000.00',
                'executed_at': '2025-01-12',
            },
        )

        self.assertRedirects(response, reverse('portfolio:dashboard'))
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.cash_balance, Decimal('6000.00'))


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
        self.assertContains(response, 'نمای کلی پرتفوی')
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

    def test_portfolio_update_only_allows_owner(self):
        self.client.login(username='jamie', password='secret123')
        response = self.client.post(
            reverse('portfolio:edit', args=[self.portfolio.pk]),
            {
                'name': 'Income Plan Reloaded',
                'description': 'Updated thesis',
                'cash_balance': '1300.00',
                'target_return': '10.00',
            },
        )

        self.assertRedirects(response, reverse('portfolio:list'))
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.name, 'Income Plan Reloaded')

    def test_portfolio_delete_blocks_other_users(self):
        self.client.login(username='jamie', password='secret123')
        response = self.client.post(reverse('portfolio:delete', args=[self.other_portfolio.pk]))
        self.assertEqual(response.status_code, 404)

    def test_transaction_list_only_shows_owned_activity(self):
        asset = Asset.objects.create(
            portfolio=self.portfolio,
            symbol='KO',
            name='Coca-Cola',
            asset_type=Asset.AssetType.STOCK,
            quantity=Decimal('12'),
            average_cost=Decimal('55'),
            current_price=Decimal('60'),
        )
        other_asset = Asset.objects.create(
            portfolio=self.other_portfolio,
            symbol='SPY',
            name='SPDR S&P 500 ETF',
            asset_type=Asset.AssetType.ETF,
            quantity=Decimal('2'),
            average_cost=Decimal('480'),
            current_price=Decimal('500'),
        )
        Transaction.objects.create(
            portfolio=self.portfolio,
            asset=asset,
            transaction_type=Transaction.TransactionType.DIVIDEND,
            quantity=Decimal('1'),
            price_per_unit=Decimal('12.00'),
        )
        Transaction.objects.create(
            portfolio=self.other_portfolio,
            asset=other_asset,
            transaction_type=Transaction.TransactionType.BUY,
            quantity=Decimal('1'),
            price_per_unit=Decimal('500.00'),
        )

        self.client.login(username='jamie', password='secret123')
        response = self.client.get(reverse('portfolio:transactions'))
        self.assertContains(response, 'Income Plan')
        self.assertNotContains(response, 'Private Plan')

    def test_transaction_list_supports_filters(self):
        asset = Asset.objects.create(
            portfolio=self.portfolio,
            symbol='KO',
            name='Coca-Cola',
            asset_type=Asset.AssetType.STOCK,
            quantity=Decimal('12'),
            average_cost=Decimal('55'),
            current_price=Decimal('60'),
        )
        Transaction.objects.create(
            portfolio=self.portfolio,
            asset=asset,
            transaction_type=Transaction.TransactionType.DIVIDEND,
            quantity=Decimal('1'),
            price_per_unit=Decimal('12.00'),
        )
        Transaction.objects.create(
            portfolio=self.portfolio,
            asset=asset,
            transaction_type=Transaction.TransactionType.BUY,
            quantity=Decimal('2'),
            price_per_unit=Decimal('58.00'),
            notes='Accumulated shares',
        )

        self.client.login(username='jamie', password='secret123')
        response = self.client.get(
            reverse('portfolio:transactions'),
            {'portfolio': self.portfolio.pk, 'type': Transaction.TransactionType.DIVIDEND},
        )
        self.assertContains(response, 'جمع فیلتر شده')
        self.assertContains(response, '$12.00')
        self.assertNotContains(response, 'Accumulated shares')

    def test_transaction_export_returns_csv(self):
        asset = Asset.objects.create(
            portfolio=self.portfolio,
            symbol='KO',
            name='Coca-Cola',
            asset_type=Asset.AssetType.STOCK,
            quantity=Decimal('12'),
            average_cost=Decimal('55'),
            current_price=Decimal('60'),
        )
        Transaction.objects.create(
            portfolio=self.portfolio,
            asset=asset,
            transaction_type=Transaction.TransactionType.DIVIDEND,
            quantity=Decimal('1'),
            price_per_unit=Decimal('12.00'),
            notes='Quarterly payout',
        )

        self.client.login(username='jamie', password='secret123')
        response = self.client.get(reverse('portfolio:transactions-export'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertContains(response, 'Income Plan')
        self.assertContains(response, 'Quarterly payout')

    def test_dashboard_includes_goal_progress_and_asset_insights(self):
        asset = Asset.objects.create(
            portfolio=self.portfolio,
            symbol='KO',
            name='Coca-Cola',
            asset_type=Asset.AssetType.STOCK,
            quantity=Decimal('12'),
            average_cost=Decimal('55'),
            current_price=Decimal('60'),
        )
        Transaction.objects.create(
            portfolio=self.portfolio,
            asset=asset,
            transaction_type=Transaction.TransactionType.BUY,
            quantity=Decimal('12'),
            price_per_unit=Decimal('55.00'),
        )

        self.client.login(username='jamie', password='secret123')
        response = self.client.get(reverse('portfolio:dashboard'))
        self.assertContains(response, 'پیشرفت نسبت به هدف')
        self.assertContains(response, 'بزرگ ترین موقعیت ها')
        self.assertContains(response, 'KO')

    def test_portfolio_holdings_export_returns_csv(self):
        Asset.objects.create(
            portfolio=self.portfolio,
            symbol='KO',
            name='Coca-Cola',
            asset_type=Asset.AssetType.STOCK,
            quantity=Decimal('12'),
            average_cost=Decimal('55'),
            current_price=Decimal('60'),
        )

        self.client.login(username='jamie', password='secret123')
        response = self.client.get(reverse('portfolio:export', args=[self.portfolio.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertContains(response, 'نماد,نام,نوع')
        self.assertContains(response, 'KO')


class SeedDemoDataCommandTests(TestCase):
    def test_seed_demo_data_creates_reusable_demo_workspace(self):
        call_command('seed_demo_data', username='demo_user', password='StrongPass123!')

        user = User.objects.get(username='demo_user')
        self.assertEqual(user.portfolios.count(), 2)
        self.assertTrue(user.check_password('StrongPass123!'))
        self.assertEqual(
            Transaction.objects.filter(portfolio__owner=user).count(),
            4,
        )
