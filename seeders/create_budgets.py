import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from budgets.models import Budget
from seeders.create_users import create_users

def create_budgets():
    """
    Create budget entries for users with different budget types and amounts
    """
    # Get or create users
    users = create_users()
    
    # Define budget data for each user with varying amounts
    budget_data = {
        users[0].email: [  # John Doe - Higher income, urban lifestyle
            {'budget_type': 'daily', 'amount': Decimal('50.00')},
            {'budget_type': 'weekly', 'amount': Decimal('350.00')},
            {'budget_type': 'monthly', 'amount': Decimal('1500.00')},
            {'budget_type': 'yearly', 'amount': Decimal('18000.00')}
        ],
        users[1].email: [  # Jane Smith - Medium income, family-oriented
            {'budget_type': 'daily', 'amount': Decimal('40.00')},
            {'budget_type': 'weekly', 'amount': Decimal('280.00')},
            {'budget_type': 'monthly', 'amount': Decimal('1200.00')},
            {'budget_type': 'yearly', 'amount': Decimal('14400.00')}
        ],
        users[2].email: [  # Alex Wong - Lower expenses, frugal lifestyle
            {'budget_type': 'daily', 'amount': Decimal('30.00')},
            {'budget_type': 'weekly', 'amount': Decimal('210.00')},
            {'budget_type': 'monthly', 'amount': Decimal('900.00')},
            {'budget_type': 'yearly', 'amount': Decimal('10800.00')}
        ]
    }
    
    created_budgets = []
    
    # Create budgets for each user
    for user in users:
        if user.email in budget_data:
            for budget_info in budget_data[user.email]:
                budget, created = Budget.objects.update_or_create(
                    user=user,
                    budget_type=budget_info['budget_type'],
                    defaults={'amount': budget_info['amount']}
                )
                
                if created:
                    print(f"Created {budget.get_budget_type_display()} budget for {user.email}: ${budget.amount}")
                else:
                    print(f"Updated {budget.get_budget_type_display()} budget for {user.email}: ${budget.amount}")
                
                created_budgets.append(budget)
    
    return created_budgets

if __name__ == "__main__":
    print("Creating budgets...")
    create_budgets()
    print("Done creating budgets.")