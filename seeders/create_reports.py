import os
import django
import random
import json
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from reports.models import Report
from seeders.create_users import create_users
from transactions.models import Category

def create_reports():
    """
    Create sample reports for users with different configurations
    """
    # Get or create users
    users = create_users()
    
    # Get current date for reference
    now = timezone.now()
    
    # Define report templates
    report_templates = [
        {
            'title': 'Monthly Expense Summary',
            'report_type': 'monthly',
            'start_date': now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            'end_date': (now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)).replace(day=1) - timedelta(seconds=1),
            'transaction_types': ['expense'],
            'sort_by': 'date_desc'
        },
        {
            'title': 'Weekly Income Report',
            'report_type': 'weekly',
            'start_date': (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0),
            'end_date': (now - timedelta(days=now.weekday()) + timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1),
            'transaction_types': ['income'],
            'sort_by': 'amount_desc'
        },
        {
            'title': 'Last Quarter Financial Summary',
            'report_type': 'custom',
            'start_date': (now - timedelta(days=90)).replace(hour=0, minute=0, second=0, microsecond=0),
            'end_date': now,
            'transaction_types': ['income', 'expense'],
            'sort_by': 'date_desc'
        },
        {
            'title': 'Annual Budget Review',
            'report_type': 'yearly',
            'start_date': now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
            'end_date': now.replace(month=12, day=31, hour=23, minute=59, second=59),
            'transaction_types': ['expense'],
            'sort_by': 'category_desc'
        },
        {
            'title': "Today's Transactions",
            'report_type': 'daily',
            'start_date': now.replace(hour=0, minute=0, second=0, microsecond=0),
            'end_date': now.replace(hour=23, minute=59, second=59),
            'transaction_types': ['income', 'expense'],
            'sort_by': 'time_asc'
        }
    ]
    
    created_reports = []
    
    # Create reports for each user
    for user in users:
        print(f"Creating reports for {user.email}...")
        
        # Get categories for this user
        categories = list(Category.objects.filter(user=user).values_list('id', flat=True))
        
        # Create each report template for the user
        for template in report_templates:
            # Randomize which categories to include
            if categories:
                selected_categories = random.sample(
                    [str(cat_id) for cat_id in categories], 
                    k=min(random.randint(0, len(categories)), len(categories))
                )
            else:
                selected_categories = []
            
            # Create report
            report = Report.objects.create(
                user=user,
                title=template['title'],
                report_type=template['report_type'],
                start_date=template['start_date'],
                end_date=template['end_date'],
                transaction_types=template['transaction_types'],
                categories=selected_categories,
                sort_by=template['sort_by'],
                created_at=timezone.now(),
            )
            
            print(f"Created report: {report.title} for {user.email}")
            created_reports.append(report)
    
    return created_reports

if __name__ == "__main__":
    print("Creating sample reports...")
    create_reports()
    print("Done creating reports.")