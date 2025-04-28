import os
import django
import time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from django.contrib.auth import get_user_model
from transactions.models import Transaction, Category
from budgets.models import Budget
from dashboard.models import Dashboard
from reports.models import Report

User = get_user_model()

def clear_seeded_data(confirm=False):
    """
    Clear all seeded data from the database.
    
    This will remove:
    - All transactions
    - All categories
    - All budgets
    - All reports
    - All user dashboards
    - Demo user accounts (but not superuser accounts)
    
    Args:
        confirm (bool): Set to True to confirm deletion, otherwise a confirmation will be requested
    """
    if not confirm:
        confirmation = input("This will delete ALL seed data including users, transactions, budgets, etc.\nAre you sure? (y/n): ").strip().lower()
        if confirmation != 'y':
            print("Operation cancelled.")
            return
    
    start_time = time.time()
    
    print("=== Clearing Seeded Data ===")
    
    with transaction.atomic():
        # Get demo users emails to identify seeded data
        # We'll keep this list updated with any users created in create_users.py
        demo_emails = ['john.doe@example.com', 'jane.smith@example.com', 'alex.wong@example.com']
        demo_users = User.objects.filter(email__in=demo_emails)
        
        # Get user IDs for filtering related records
        demo_user_ids = list(demo_users.values_list('id', flat=True))
        
        # 1. Delete transactions
        transaction_count = Transaction.objects.filter(user__in=demo_user_ids).count()
        Transaction.objects.filter(user__in=demo_user_ids).delete()
        print(f"Deleted {transaction_count} transactions.")
        
        # 2. Delete categories
        category_count = Category.objects.filter(user__in=demo_user_ids).count()
        Category.objects.filter(user__in=demo_user_ids).delete()
        print(f"Deleted {category_count} categories.")
        
        # 3. Delete budgets
        budget_count = Budget.objects.filter(user__in=demo_user_ids).count()
        Budget.objects.filter(user__in=demo_user_ids).delete()
        print(f"Deleted {budget_count} budgets.")
        
        # 4. Delete reports
        report_count = Report.objects.filter(user__in=demo_user_ids).count()
        Report.objects.filter(user__in=demo_user_ids).delete()
        print(f"Deleted {report_count} reports.")
        
        # 5. Delete dashboards
        dashboard_count = Dashboard.objects.filter(user__in=demo_user_ids).count()
        Dashboard.objects.filter(user__in=demo_user_ids).delete()
        print(f"Deleted {dashboard_count} dashboards.")
        
        # 6. Delete demo users
        user_count = demo_users.count()
        demo_users.delete()
        print(f"Deleted {user_count} demo users.")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n=== Data Clearing Completed in {elapsed_time:.2f} seconds ===")
    print(f"""
Summary of deleted items:
- Users: {user_count}
- Dashboards: {dashboard_count}
- Categories: {category_count}
- Budgets: {budget_count}
- Transactions: {transaction_count}
- Reports: {report_count}
    """)

if __name__ == "__main__":
    clear_seeded_data()