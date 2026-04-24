from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Asset, Portfolio, Transaction


class DateInput(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'description', 'cash_balance', 'target_return']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['portfolio', 'symbol', 'name', 'asset_type', 'quantity', 'average_cost', 'current_price']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['portfolio'].queryset = Portfolio.objects.filter(owner=user)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['portfolio', 'asset', 'transaction_type', 'quantity', 'price_per_unit', 'executed_at', 'notes']
        widgets = {
            'executed_at': DateInput(),
            'notes': forms.TextInput(attrs={'placeholder': 'Optional note'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            owned_portfolios = Portfolio.objects.filter(owner=user)
            self.fields['portfolio'].queryset = owned_portfolios
            self.fields['asset'].queryset = Asset.objects.filter(portfolio__owner=user)
