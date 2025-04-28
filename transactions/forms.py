from django import forms
from .models import Transaction, Category
from budgets.models import Budget
from decimal import Decimal

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
                'placeholder': 'Enter category description (optional)',
                'rows': 3
            }),
        }

class TransactionForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)

    class Meta:
        model = Transaction
        fields = ['name', 'description', 'amount', 'type', 'date', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
                'placeholder': 'Enter transaction name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
                'placeholder': 'Enter transaction description (optional)',
                'rows': 3
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
                'placeholder': '0.00',
                'min': '0.01',
                'step': '0.01'
            }),
            'type': forms.Select(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white'
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
                'type': 'datetime-local'
            }),
            'category': forms.Select(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount < Decimal('0.01'):
            raise forms.ValidationError('Amount must be greater than 0.')
        return amount

class TransactionFilterForm(forms.Form):
    type = forms.ChoiceField(
        choices=[('', 'All Types')] + Transaction.TRANSACTION_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white'
        })
    )
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white'
        })
    )
    budget = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='All Budgets',
        widget=forms.Select(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white'
        })
    )
    start_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
            'type': 'datetime-local'
        })
    )
    end_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
            'type': 'datetime-local'
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('-date', 'Newest First'),
            ('date', 'Oldest First'),
            ('amount', 'Amount (Low to High)'),
            ('-amount', 'Amount (High to Low)'),
            ('name', 'Name (A-Z)'),
            ('-name', 'Name (Z-A)'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white'
        })
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['budget'].queryset = Budget.objects.filter(user=user) 