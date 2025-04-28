from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Dashboard(models.Model):
    """Model to store dashboard-specific settings and preferences"""
    TIME_PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme_preference = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    default_view = models.CharField(max_length=20, choices=[('overview', 'Overview'), ('budgets', 'Budgets'), ('transactions', 'Transactions')], default='overview')
    time_period = models.CharField(max_length=10, choices=TIME_PERIOD_CHOICES, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Dashboard"
