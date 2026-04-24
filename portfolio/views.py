import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import AssetForm, PortfolioForm, SignUpForm, TransactionForm
from .models import Asset, Portfolio, Transaction


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
        messages.success(self.request, 'Welcome to Polito. Your account is ready.')
        return response


class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


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
            row = {
                'id': portfolio.pk,
                'name': portfolio.name,
                'total_value': portfolio.total_value,
                'invested_amount': portfolio.invested_amount,
                'target_return': portfolio.target_return,
            }
            portfolio_rows.append(row)
            total_value += row['total_value']
            total_profit += portfolio.unrealized_profit

        allocation = list(assets.values('asset_type').annotate(total=Sum('quantity')).order_by('asset_type'))
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


class PortfolioCreateView(OwnerQuerysetMixin, CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'portfolio/form.html'
    success_url = reverse_lazy('portfolio:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Portfolio created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create portfolio'
        return context


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
        messages.success(self.request, 'Asset added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add asset'
        return context


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
        messages.success(self.request, 'Transaction logged successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Log transaction'
        return context


def home_redirect(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy('portfolio:dashboard'))
    return HttpResponseRedirect(reverse_lazy('portfolio:login'))
