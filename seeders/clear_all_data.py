import os
import django
import time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from budgets.models import Budget
from accounts.models import CustomUser
from dashboard.models import Dashboard
from transactions.models import Transaction, Category
from reports.models import Report

def clear_all_data():
    """
    Clear all seed data from the database to start fresh.
    This removes all transactions, budgets, categories, reports, dashboards, and users.
    """
    start_time = time.time()
    
    print("Clearing all seed data...")
    
    # Delete in order to avoid foreign key constraint issues
    with transaction.atomic():
        # Delete transactions first (they depend on budgets, categories, and users)
        transaction_count = Transaction.objects.all().count()
        Transaction.objects.all().delete()
        print(f"Deleted {transaction_count} transactions")
        
        # Delete budgets (they depend on users)
        budget_count = Budget.objects.all().count()
        Budget.objects.all().delete()
        print(f"Deleted {budget_count} budgets")
        
        # Delete categories (they depend on users)
        category_count = Category.objects.all().count()
        Category.objects.all().delete()
        print(f"Deleted {category_count} categories")
        
        # Delete reports (they depend on users)
        report_count = Report.objects.all().count()
        Report.objects.all().delete()
        print(f"Deleted {report_count} reports")
        
        # Delete dashboards (they depend on users)
        dashboard_count = Dashboard.objects.all().count()
        Dashboard.objects.all().delete()
        print(f"Deleted {dashboard_count} dashboards")
        
        # Finally, delete users
        # Note: If you want to keep superusers, modify this to filter out superusers
        user_count = CustomUser.objects.all().count()
        # CustomUser.objects.filter(is_superuser=False).delete()  # Uncomment to keep superusers
        CustomUser.objects.all().delete()
        print(f"Deleted {user_count} users")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Data clearing completed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    clear_all_data()
    print("Done clearing data.")