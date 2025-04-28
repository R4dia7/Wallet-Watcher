from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from budgets.models import Budget

User = get_user_model()

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_transactions')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='category_transactions')
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True, blank=True, related_name='budget_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'budget']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()}) - {self.amount}"

    def save(self, *args, **kwargs):
        """Override save to update budget if transaction is associated with one"""
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to handle budget updates"""
        super().delete(*args, **kwargs)

    @classmethod
    def get_balance(cls, user, start_date=None, end_date=None):
        """Calculate the balance for a given time period"""
        queryset = cls.objects.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        income = queryset.filter(type='income').aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        expense = queryset.filter(type='expense').aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        return income - expense

    @classmethod
    def get_summary(cls, user, start_date=None, end_date=None):
        """Get a summary of transactions for a given time period"""
        queryset = cls.objects.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return {
            'total_income': queryset.filter(type='income').aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00'),
            'total_expense': queryset.filter(type='expense').aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00'),
            'balance': cls.get_balance(user, start_date, end_date),
            'transaction_count': queryset.count(),
        }
