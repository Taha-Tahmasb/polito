from django.urls import path

from .views import (
    AssetCreateView,
    AssetUpdateView,
    DashboardView,
    PortfolioCreateView,
    PortfolioDeleteView,
    PortfolioDetailView,
    PortfolioListView,
    PortfolioUpdateView,
    SignUpView,
    TransactionListView,
    TransactionCreateView,
    UserLoginView,
    UserLogoutView,
    home_redirect,
)

app_name = 'portfolio'

urlpatterns = [
    path('', home_redirect, name='home'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('portfolios/', PortfolioListView.as_view(), name='list'),
    path('portfolios/create/', PortfolioCreateView.as_view(), name='create'),
    path('portfolios/<int:pk>/', PortfolioDetailView.as_view(), name='detail'),
    path('portfolios/<int:pk>/edit/', PortfolioUpdateView.as_view(), name='edit'),
    path('portfolios/<int:pk>/delete/', PortfolioDeleteView.as_view(), name='delete'),
    path('assets/create/', AssetCreateView.as_view(), name='asset-create'),
    path('assets/<int:pk>/edit/', AssetUpdateView.as_view(), name='asset-edit'),
    path('transactions/create/', TransactionCreateView.as_view(), name='transaction-create'),
]
