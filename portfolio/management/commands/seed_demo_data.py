from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from portfolio.models import Asset, Portfolio, Transaction
from portfolio.services import apply_transaction


class Command(BaseCommand):
    help = 'یک کاربر نمایشی با پرتفوی، دارایی و تراکنش های نمونه ایجاد می کند.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='demo',
            help='نام کاربری حساب نمایشی.',
        )
        parser.add_argument(
            '--password',
            default='DemoPass123!',
            help='رمز عبور حساب نمایشی.',
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
            self.stdout.write(self.style.SUCCESS(f'کاربر نمایشی "{username}" ساخته شد.'))
        else:
            self.stdout.write(self.style.WARNING(f'از کاربر موجود "{username}" استفاده می شود.'))

        if user.portfolios.exists():
            self.stdout.write(self.style.WARNING('برای این کاربر از قبل داده نمایشی وجود دارد و تغییری اعمال نشد.'))
            return

        growth = Portfolio.objects.create(
            owner=user,
            name='رشد جهانی',
            description='ترکیبی از سهام و ETF برای رشد بلندمدت.',
            cash_balance=Decimal('2000.00'),
            target_return=Decimal('11.50'),
        )
        income = Portfolio.objects.create(
            owner=user,
            name='درآمد پایدار',
            description='تمرکز بر سود نقدی و جریان نقدی باثبات.',
            cash_balance=Decimal('3500.00'),
            target_return=Decimal('7.50'),
        )

        growth_equity = Asset.objects.create(
            portfolio=growth,
            symbol='NVDA',
            name='انویدیا',
            asset_type=Asset.AssetType.STOCK,
            quantity=Decimal('8'),
            average_cost=Decimal('110.00'),
            current_price=Decimal('122.00'),
        )
        growth_etf = Asset.objects.create(
            portfolio=growth,
            symbol='QQQ',
            name='صندوق QQQ',
            asset_type=Asset.AssetType.ETF,
            quantity=Decimal('5'),
            average_cost=Decimal('410.00'),
            current_price=Decimal('438.00'),
        )
        income_equity = Asset.objects.create(
            portfolio=income,
            symbol='JNJ',
            name='جانسون اند جانسون',
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
                notes='افزایش موقعیت در روند صعودی نیمه هادی.',
            )
        )
        apply_transaction(
            Transaction(
                portfolio=growth,
                asset=growth_etf,
                transaction_type=Transaction.TransactionType.DIVIDEND,
                quantity=Decimal('1'),
                price_per_unit=Decimal('18.50'),
                notes='دریافت سود دوره ای ETF.',
            )
        )
        apply_transaction(
            Transaction(
                portfolio=income,
                asset=income_equity,
                transaction_type=Transaction.TransactionType.BUY,
                quantity=Decimal('3'),
                price_per_unit=Decimal('154.00'),
                notes='خرید در محدوده ارزنده تر.',
            )
        )
        apply_transaction(
            Transaction(
                portfolio=income,
                transaction_type=Transaction.TransactionType.DEPOSIT,
                quantity=Decimal('1'),
                price_per_unit=Decimal('1200.00'),
                notes='واریز ماهانه.',
            )
        )

        self.stdout.write(self.style.SUCCESS('پرتفوی ها، دارایی ها و تراکنش های نمایشی ساخته شدند.'))
        self.stdout.write(self.style.SUCCESS(f'با نام کاربری "{username}" و رمز عبور "{password}" وارد شوید.'))
