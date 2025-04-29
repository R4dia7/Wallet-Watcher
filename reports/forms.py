from django import forms
from .models import Report
from transactions.models import Category
from django.utils import timezone
from datetime import timedelta

class ReportFilterForm(forms.Form):
    TIME_PERIODS = [
        ('', 'All Time'),
        ('day', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('year', 'This Year'),
    ]
    
    REPORT_TYPES = [
        ('', 'All Types'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ]
    
    SORT_BY = [
        ('created_at', 'Date Created (Newest First)'),
        ('-created_at', 'Date Created (Oldest First)'),
        ('title', 'Title (A-Z)'),
        ('-title', 'Title (Z-A)'),
        ('report_type', 'Report Type'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPES, 
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
        })
    )
    
    date_range = forms.ChoiceField(
        choices=TIME_PERIODS, 
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_BY, 
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
        })
    )

class ReportForm(forms.ModelForm):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'p-2 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
        'placeholder': 'Report Title',
    }))
    
    start_date = forms.DateTimeField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'p-2 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
            'type': 'date',
        }),
    )
    
    end_date = forms.DateTimeField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'p-2 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
            'type': 'date',
        }),
    )
    
    transaction_types = forms.MultipleChoiceField(
        choices=TRANSACTION_TYPES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'h-4 w-4 border-gray-300 dark:border-gray-600 text-primary-600 dark:text-primary-400 focus:ring-primary-500 dark:focus:ring-primary-400',
        }),
    )
    
    categories = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'h-4 w-4 border-gray-300 dark:border-gray-600 text-primary-600 dark:text-primary-400 focus:ring-primary-500 dark:focus:ring-primary-400',
        }),
    )
    
    sort_by = forms.ChoiceField(
        choices=Report.SORT_OPTIONS,
        widget=forms.Select(attrs={
            'class': 'p-2 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
        }),
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Get user's categories
            categories = Category.objects.filter(user=user)
            self.fields['categories'].choices = [(str(c.id), c.name) for c in categories]
    
    class Meta:
        model = Report
        fields = ['title', 'start_date', 'end_date', 'transaction_types', 'categories', 'sort_by']
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be earlier than start date.")
        
        return cleaned_data


class StandardReportForm(forms.Form):
    """Form for creating standard reports (daily, weekly, monthly, yearly)"""
    
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
        'placeholder': 'Report Title',
    }))
    
    period_offset = forms.IntegerField(required=False, widget=forms.HiddenInput())
    
    sort_by = forms.ChoiceField(
        choices=Report.SORT_OPTIONS,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white',
        }),
    )
    
    def get_date_range(self, report_type, period_offset=0):
        """Calculate date range based on report type and period offset"""
        today = timezone.now().date()
        
        if report_type == 'daily':
            target_date = today + timedelta(days=period_offset)
            start_date = timezone.datetime.combine(target_date, timezone.datetime.min.time())
            end_date = timezone.datetime.combine(target_date, timezone.datetime.max.time())
            
        elif report_type == 'weekly':
            target_date = today + timedelta(weeks=period_offset)
            start_date = target_date - timedelta(days=target_date.weekday())
            start_date = timezone.datetime.combine(start_date, timezone.datetime.min.time())
            end_date = start_date + timedelta(days=6)
            end_date = timezone.datetime.combine(end_date, timezone.datetime.max.time())
            
        elif report_type == 'monthly':
            # Calculate target month and year
            target_month = today.month + period_offset
            target_year = today.year
            
            # Adjust year if month goes out of range
            while target_month > 12:
                target_month -= 12
                target_year += 1
            while target_month < 1:
                target_month += 12
                target_year -= 1
                
            start_date = today.replace(year=target_year, month=target_month, day=1)
            start_date = timezone.datetime.combine(start_date, timezone.datetime.min.time())
            
            # Calculate last day of month
            if target_month == 12:
                end_date = start_date.replace(day=31)
            else:
                next_month = start_date.replace(month=target_month + 1 if target_month < 12 else 1, 
                                             year=target_year if target_month < 12 else target_year + 1)
                end_date = next_month - timedelta(days=1)
            
            end_date = timezone.datetime.combine(end_date, timezone.datetime.max.time())
            
        else:  # yearly
            target_year = today.year + period_offset
            start_date = today.replace(year=target_year, month=1, day=1)
            start_date = timezone.datetime.combine(start_date, timezone.datetime.min.time())
            end_date = today.replace(year=target_year, month=12, day=31)
            end_date = timezone.datetime.combine(end_date, timezone.datetime.max.time())
        
        return start_date, end_date