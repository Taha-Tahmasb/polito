from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Asset, Portfolio, Transaction
from .services import validate_transaction_effect


class DateInput(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'نام کاربری'
        self.fields['username'].help_text = 'فقط از حروف، اعداد و @/./+/-/_ استفاده کنید.'
        self.fields['email'].label = 'ایمیل'
        self.fields['password1'].label = 'رمز عبور'
        self.fields['password2'].label = 'تکرار رمز عبور'


class PersianAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='نام کاربری')
    password = forms.CharField(label='رمز عبور', strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'description', 'cash_balance', 'target_return']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'مثلا استراتژی رشد، درآمدی یا پس انداز بلندمدت'}),
        }


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['portfolio', 'symbol', 'name', 'asset_type', 'quantity', 'average_cost', 'current_price']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['symbol'].help_text = 'نماد بورسی یا شناسه دارایی را وارد کنید.'
        if user is not None:
            self.fields['portfolio'].queryset = Portfolio.objects.filter(owner=user)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['portfolio', 'asset', 'transaction_type', 'quantity', 'price_per_unit', 'executed_at', 'notes']
        widgets = {
            'executed_at': DateInput(),
            'notes': forms.TextInput(attrs={'placeholder': 'یادداشت اختیاری'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            owned_portfolios = Portfolio.objects.filter(owner=user)
            self.fields['portfolio'].queryset = owned_portfolios
            self.fields['asset'].queryset = Asset.objects.filter(portfolio__owner=user)

    def clean(self):
        cleaned_data = super().clean()
        portfolio = cleaned_data.get('portfolio')
        asset = cleaned_data.get('asset')
        transaction_type = cleaned_data.get('transaction_type')
        quantity = cleaned_data.get('quantity')
        price_per_unit = cleaned_data.get('price_per_unit')

        if not all([portfolio, transaction_type, quantity is not None, price_per_unit is not None]):
            return cleaned_data

        try:
            validate_transaction_effect(
                portfolio=portfolio,
                asset=asset,
                transaction_type=transaction_type,
                quantity=quantity,
                price_per_unit=price_per_unit,
            )
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages)

        return cleaned_data
