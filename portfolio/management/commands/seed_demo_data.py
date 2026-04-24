from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.translation import get_language

from portfolio.models import Asset, Portfolio, Transaction
from portfolio.services import apply_transaction


def tr(fa_text, en_text):
    language = (get_language() or 'fa').split('-')[0]
    return fa_text if language == 'fa' else en_text


class Command(BaseCommand):
    help = 'Create a reusable demo user with sample portfolios, assets, and transactions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='demo',
            help='Username for the seeded demo account.',
        )
        parser.add_argument(
            '--password',
            default='DemoPass123!',
            help='Password for the seeded demo account.',
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
            },
        )

        if created:
            user.set_password(password)
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(tr(f'کاربر نمایشی "{username}" ساخته شد.', f'Created demo user "{username}".')))
        else:
            self.stdout.write(self.style.WARNING(tr(f'از کاربر موجود "{username}" استفاده می شود.', f'Using existing user "{username}".')))

        if user.portfolios.exists():
            self.stdout.write(self.style.WARNING(tr('برای این کاربر از قبل داده نمایشی وجود دارد و تغییری اعمال نشد.', 'Demo data already exists for this user. Nothing changed.')))
            return

        growth = Portfolio.objects.create(
            owner=user,
            name=tr('رشد جهانی', 'Global Growth'),
            description=tr('ترکیبی از سهام و ETF برای رشد بلندمدت.', 'Long-term equities and ETFs with broad market exposure.'),
            cash_balance=Decimal('2000.00'),
            target_return=Decimal('11.50'),
        )
        income = Portfolio.objects.create(
            owner=user,
            name=tr('درآمد پایدار', 'Income Engine'),
            description=tr('تمرکز بر سود نقدی و جریان نقدی باثبات.', 'Dividend and fixed-income ideas for steadier cash flow.'),
            cash_balance=Decimal('3500.00'),
            target_return=Decimal('7.50'),
        )

        growth_equity = Asset.objects.create(
            portfolio=growth,
            symbol='NVDA',
            name=tr('انویدیا', 'NVIDIA'),
            asset_type=Asset.AssetType.STOCK,
            quantity=Decimal('8'),
            average_cost=Decimal('110.00'),
            current_price=Decimal('122.00'),
        )
        growth_etf = Asset.objects.create(
            portfolio=growth,
            symbol='QQQ',
            name=tr('صندوق QQQ', 'Invesco QQQ Trust'),
            asset_type=Asset.AssetType.ETF,
            quantity=Decimal('5'),
            average_cost=Decimal('410.00'),
            current_price=Decimal('438.00'),
        )
        income_equity = Asset.objects.create(
            portfolio=income,
            symbol='JNJ',
            name=tr('جانسون اند جانسون', 'Johnson & Johnson'),
            asset_type=Asset.AssetType.STOCK,
            quantity=Decimal('14'),
            average_cost=Decimal('148.00'),
            current_price=Decimal('156.00'),
        )

        apply_transaction(
            Transaction(
                portfolio=growth,
                asset=growth_equity,
                transaction_type=Transaction.TransactionType.BUY,
                quantity=Decimal('2'),
                price_per_unit=Decimal('126.00'),
                notes=tr('افزایش موقعیت در روند صعودی نیمه هادی.', 'Scaled into semiconductor strength.'),
            )
        )
        apply_transaction(
            Transaction(
                portfolio=growth,
                asset=growth_etf,
                transaction_type=Transaction.TransactionType.DIVIDEND,
                quantity=Decimal('1'),
                price_per_unit=Decimal('18.50'),
                notes=tr('دریافت سود دوره ای ETF.', 'Quarterly ETF distribution.'),
            )
        )
        apply_transaction(
            Transaction(
                portfolio=income,
                asset=income_equity,
                transaction_type=Transaction.TransactionType.BUY,
                quantity=Decimal('3'),
                price_per_unit=Decimal('154.00'),
                notes=tr('خرید در محدوده ارزنده تر.', 'Added on valuation dip.'),
            )
        )
        apply_transaction(
            Transaction(
                portfolio=income,
                transaction_type=Transaction.TransactionType.DEPOSIT,
                quantity=Decimal('1'),
                price_per_unit=Decimal('1200.00'),
                notes=tr('واریز ماهانه.', 'Monthly contribution.'),
            )
        )

        self.stdout.write(self.style.SUCCESS(tr('پرتفوی ها، دارایی ها و تراکنش های نمایشی ساخته شدند.', 'Seeded demo portfolios, assets, and transactions.')))
        self.stdout.write(self.style.SUCCESS(tr(f'با نام کاربری "{username}" و رمز عبور "{password}" وارد شوید.', f'Login with username "{username}" and password "{password}".')))
