import json
from decimal import Decimal
import csv

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import get_language
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import AssetForm, PersianAuthenticationForm, PortfolioForm, SignUpForm, TransactionForm
from .models import Asset, Portfolio, Transaction
from .services import apply_transaction


def tr(fa_text, en_text):
    language = (get_language() or 'fa').split('-')[0]
    return fa_text if language == 'fa' else en_text


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('portfolio:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            tr('حساب کاربری شما با موفقیت ساخته شد. خوش آمدید.', 'Your account was created successfully. Welcome.'),
        )
        return response


class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    authentication_form = PersianAuthenticationForm


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('portfolio:login')


class OwnerQuerysetMixin(LoginRequiredMixin):
    login_url = reverse_lazy('portfolio:login')

    def get_portfolios(self):
        return Portfolio.objects.filter(owner=self.request.user)


class DashboardView(OwnerQuerysetMixin, TemplateView):
    template_name = 'portfolio/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolios = list(self.get_portfolios().prefetch_related('assets', 'transactions'))
        assets = Asset.objects.filter(portfolio__owner=self.request.user).select_related('portfolio')
        transactions = list(
            Transaction.objects.filter(portfolio__owner=self.request.user)
            .select_related('portfolio', 'asset')[:8]
        )

        portfolio_rows = []
        total_value = Decimal('0')
        total_profit = Decimal('0')
        for portfolio in portfolios:
            invested_amount = portfolio.invested_amount
            current_return = Decimal('0')
            progress_percent = Decimal('0')
            if invested_amount > 0:
                current_return = (portfolio.unrealized_profit / invested_amount) * 100
            if portfolio.target_return > 0:
                progress_percent = max(Decimal('0'), min((current_return / portfolio.target_return) * 100, Decimal('100')))
            row = {
                'id': portfolio.pk,
                'name': portfolio.name,
                'total_value': portfolio.total_value,
                'invested_amount': invested_amount,
                'target_return': portfolio.target_return,
                'current_return': current_return,
                'target_gap': current_return - portfolio.target_return,
                'progress_percent': progress_percent,
            }
            portfolio_rows.append(row)
            total_value += row['total_value']
            total_profit += portfolio.unrealized_profit

        allocation = list(
            assets.values('asset_type')
            .annotate(
                total=Sum(
                    ExpressionWrapper(
                        F('quantity') * F('current_price'),
                        output_field=DecimalField(max_digits=14, decimal_places=2),
                    )
                )
            )
            .order_by('asset_type')
        )
        top_assets = sorted(assets, key=lambda asset: asset.market_value, reverse=True)[:3]
        watchlist_assets = sorted(assets, key=lambda asset: asset.pnl_percent)[:3]
        context.update(
            {
                'portfolio_count': len(portfolios),
                'asset_count': assets.count(),
                'transaction_count': Transaction.objects.filter(portfolio__owner=self.request.user).count(),
                'total_value': total_value,
                'total_profit': total_profit,
                'portfolio_rows': portfolio_rows,
                'recent_transactions': transactions,
                'allocation_labels': json.dumps([item['asset_type'].upper() for item in allocation]),
                'allocation_values': json.dumps([float(item['total']) for item in allocation]),
                'portfolio_mix_labels': json.dumps([row['name'] for row in portfolio_rows]),
                'portfolio_mix_values': json.dumps([float(row['total_value']) for row in portfolio_rows]),
                'goal_progress_rows': sorted(portfolio_rows, key=lambda row: row['target_gap'], reverse=True),
                'top_assets': top_assets,
                'watchlist_assets': watchlist_assets,
            }
        )
        return context


class PortfolioListView(OwnerQuerysetMixin, ListView):
    model = Portfolio
    template_name = 'portfolio/portfolio_list.html'
    context_object_name = 'portfolios'

    def get_queryset(self):
        return self.get_portfolios().prefetch_related('assets')


class PortfolioDetailView(OwnerQuerysetMixin, DetailView):
    model = Portfolio
    template_name = 'portfolio/portfolio_detail.html'
    context_object_name = 'portfolio'

    def get_queryset(self):
        return self.get_portfolios().prefetch_related('assets', 'transactions__asset')


class PortfolioHoldingsExportView(OwnerQuerysetMixin, DetailView):
    model = Portfolio

    def get_queryset(self):
        return self.get_portfolios().prefetch_related('assets')

    def render_to_response(self, context, **response_kwargs):
        portfolio = context['portfolio']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="portfolio-{portfolio.pk}-holdings.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ['نماد', 'نام', 'نوع', 'تعداد', 'میانگین قیمت خرید', 'قیمت فعلی', 'ارزش بازار', 'سود و زیان']
            if (get_language() or 'fa').split('-')[0] == 'fa'
            else ['symbol', 'name', 'type', 'quantity', 'average_cost', 'current_price', 'market_value', 'pnl']
        )
        for asset in portfolio.assets.all():
            writer.writerow(
                [
                    asset.symbol,
                    asset.name,
                    asset.get_asset_type_display(),
                    asset.quantity,
                    asset.average_cost,
                    asset.current_price,
                    asset.market_value,
                    asset.pnl,
                ]
            )
        return response


class PortfolioCreateView(OwnerQuerysetMixin, CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'portfolio/form.html'
    success_url = reverse_lazy('portfolio:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, tr('پرتفوی با موفقیت ایجاد شد.', 'Portfolio created successfully.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = tr('ایجاد پرتفوی', 'Create portfolio')
        return context


class PortfolioUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'portfolio/form.html'
    success_url = reverse_lazy('portfolio:list')

    def get_queryset(self):
        return self.get_portfolios()

    def form_valid(self, form):
        messages.success(self.request, tr('پرتفوی با موفقیت به روز شد.', 'Portfolio updated successfully.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = tr('ویرایش پرتفوی', 'Edit portfolio')
        return context


class PortfolioDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Portfolio
    template_name = 'portfolio/confirm_delete.html'
    success_url = reverse_lazy('portfolio:list')

    def get_queryset(self):
        return self.get_portfolios()

    def form_valid(self, form):
        messages.success(self.request, tr('پرتفوی با موفقیت حذف شد.', 'Portfolio deleted successfully.'))
        return super().form_valid(form)


class AssetCreateView(OwnerQuerysetMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'portfolio/form.html'
    success_url = reverse_lazy('portfolio:list')

    def get_initial(self):
        initial = super().get_initial()
        portfolio_id = self.request.GET.get('portfolio')
        if portfolio_id:
            initial['portfolio'] = portfolio_id
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, tr('دارایی با موفقیت اضافه شد.', 'Asset added successfully.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = tr('افزودن دارایی', 'Add asset')
        return context


class AssetUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = 'portfolio/form.html'

    def get_queryset(self):
        return Asset.objects.filter(portfolio__owner=self.request.user).select_related('portfolio')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('portfolio:detail', kwargs={'pk': self.object.portfolio_id})

    def form_valid(self, form):
        messages.success(self.request, tr('دارایی با موفقیت به روز شد.', 'Asset updated successfully.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = tr('ویرایش دارایی', 'Update asset')
        return context


class TransactionListView(OwnerQuerysetMixin, ListView):
    model = Transaction
    template_name = 'portfolio/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Transaction.objects.filter(portfolio__owner=self.request.user)
            .select_related('portfolio', 'asset')
            .order_by('-executed_at', '-created_at')
        )

        portfolio_id = self.request.GET.get('portfolio')
        transaction_type = self.request.GET.get('type')
        if portfolio_id:
            queryset = queryset.filter(portfolio_id=portfolio_id)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_transactions = self.get_queryset()
        context.update(
            {
                'filter_portfolios': self.get_portfolios(),
                'transaction_types': Transaction.TransactionType.choices,
                'selected_portfolio': self.request.GET.get('portfolio', ''),
                'selected_type': self.request.GET.get('type', ''),
                'filtered_total': sum((item.total_amount for item in filtered_transactions), Decimal('0')),
            }
        )
        return context


class TransactionExportView(OwnerQuerysetMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        transactions = (
            Transaction.objects.filter(portfolio__owner=request.user)
            .select_related('portfolio', 'asset')
            .order_by('-executed_at', '-created_at')
        )

        portfolio_id = request.GET.get('portfolio')
        transaction_type = request.GET.get('type')
        if portfolio_id:
            transactions = transactions.filter(portfolio_id=portfolio_id)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="polito-transactions.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ['تاریخ', 'نوع', 'پرتفوی', 'دارایی', 'مبلغ', 'یادداشت']
            if (get_language() or 'fa').split('-')[0] == 'fa'
            else ['date', 'type', 'portfolio', 'asset', 'amount', 'notes']
        )
        for transaction in transactions:
            writer.writerow(
                [
                    transaction.executed_at.isoformat(),
                    transaction.get_transaction_type_display(),
                    transaction.portfolio.name,
                    transaction.asset.symbol if transaction.asset else tr('گردش نقدی', 'Cash movement'),
                    transaction.total_amount,
                    transaction.notes,
                ]
            )
        return response


class TransactionCreateView(OwnerQuerysetMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'portfolio/form.html'
    success_url = reverse_lazy('portfolio:dashboard')

    def get_initial(self):
        initial = super().get_initial()
        portfolio_id = self.request.GET.get('portfolio')
        if portfolio_id:
            initial['portfolio'] = portfolio_id
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        apply_transaction(self.object)
        messages.success(self.request, tr('تراکنش با موفقیت ثبت شد.', 'Transaction logged successfully.'))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = tr('ثبت تراکنش', 'Log transaction')
        return context


def home_redirect(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy('portfolio:dashboard'))
    return HttpResponseRedirect(reverse_lazy('portfolio:login'))
