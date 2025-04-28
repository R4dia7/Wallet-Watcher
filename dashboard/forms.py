from django import forms
from budgets.models import Budget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [ 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
                'placeholder': 'Enter budget amount',
                'min': '0.01',
                'step': '0.01',
            }),
        }
        