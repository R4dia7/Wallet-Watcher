from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

User = get_user_model()

class Budget(models.Model):
    BUDGET_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    budget_type = models.CharField(max_length=10, choices=BUDGET_TYPES)  # Removed unique=True
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'budget_type']
        ordering = ['budget_type']

    def __str__(self):
        return f"{self.user.username}'s {self.get_budget_type_display()} Budget"

    def get_spent_amount(self):
        from transactions.models import Transaction
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        
        if self.budget_type == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif self.budget_type == 'weekly':
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        elif self.budget_type == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1)
        else:  # yearly
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=start_date.year + 1)

        return Transaction.objects.filter(
            user=self.user,
            date__gte=start_date,
            date__lt=end_date,
            type='expense'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    def get_remaining_amount(self):
        return self.amount - self.get_spent_amount()

    def get_percentage_spent(self):
        if self.amount == 0:
            return 0
        return (self.get_spent_amount() / self.amount) * 100

    def is_exceeded(self):
        """Check if the budget is exceeded based on transactions in the current period"""
        return self.get_spent_amount() > self.amount

    def reset_budget(self):
        """Reset the budget for the next period"""
        now = timezone.now()
        if self.budget_type == 'daily':
            self.start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.budget_type == 'weekly':
            self.start_date = now - timezone.timedelta(days=now.weekday())
            self.start_date = self.start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.budget_type == 'monthly':
            self.start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # yearly
            self.start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        self.save()