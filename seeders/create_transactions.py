import os
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from transactions.models import Transaction, Category
from budgets.models import Budget
from seeders.create_users import create_users
from seeders.create_categories import create_categories
from seeders.create_budgets import create_budgets

def create_transactions():
    """
    Create diverse transaction records for users
    """
    # Ensure users, categories, and budgets exist
    users = create_users()
    create_categories()  # Make sure categories are created
    create_budgets()     # Make sure budgets are created
    
    # Get current date for reference
    now = timezone.now()
    
    # Transaction patterns for different users
    transaction_patterns = {}
    
    # Common transaction templates
    income_templates = [
        {"name": "Monthly Salary", "type": "income", "category": "Salary"},
        {"name": "Freelance Payment", "type": "income", "category": "Freelance"},
        {"name": "Dividends", "type": "income", "category": "Investments"},
        {"name": "Gift from Family", "type": "income", "category": "Gifts"},
    ]
    
    expense_templates = [
        {"name": "Grocery Shopping", "type": "expense", "category": "Groceries"},
        {"name": "Electric Bill", "type": "expense", "category": "Utilities"},
        {"name": "Internet Bill", "type": "expense", "category": "Utilities"},
        {"name": "Restaurant Dinner", "type": "expense", "category": "Dining Out"},
        {"name": "Monthly Rent", "type": "expense", "category": "Housing"},
        {"name": "Gas Station", "type": "expense", "category": "Transportation"},
        {"name": "Netflix Subscription", "type": "expense", "category": "Subscriptions"},
        {"name": "Clothing Purchase", "type": "expense", "category": "Shopping"},
        {"name": "Doctor Visit", "type": "expense", "category": "Healthcare"},
        {"name": "Movie Tickets", "type": "expense", "category": "Entertainment"},
    ]
    
    # User-specific transaction templates
    user_specific_templates = {
        users[0].email: [  # John Doe
            {"name": "Dog Food", "type": "expense", "category": "Pet Expenses"},
            {"name": "New Furniture", "type": "expense", "category": "Home Improvement"},
            {"name": "Annual Bonus", "type": "income", "category": "Bonus"},
        ],
        users[1].email: [  # Jane Smith
            {"name": "Craft Supplies", "type": "expense", "category": "Hobbies"},
            {"name": "Daycare Payment", "type": "expense", "category": "Child Care"},
            {"name": "Stock Dividends", "type": "income", "category": "Dividend"},
        ],
        users[2].email: [  # Alex Wong
            {"name": "Client Meeting", "type": "expense", "category": "Business Expenses"},
            {"name": "Gym Membership", "type": "expense", "category": "Fitness"},
            {"name": "Sales Commission", "type": "income", "category": "Commission"},
        ]
    }
    
    # Add common templates to each user's pattern
    for user in users:
        transaction_patterns[user.email] = income_templates + expense_templates
        
        # Add user-specific templates if available
        if user.email in user_specific_templates:
            transaction_patterns[user.email].extend(user_specific_templates[user.email])
    
    # Track how many transactions we've created
    created_count = 0
    
    # Generate transactions for each user
    for user in users:
        print(f"Creating transactions for {user.email}...")
        
        # Get categories and budgets for this user
        categories = {cat.name: cat for cat in Category.objects.filter(user=user)}
        budgets = {budget.budget_type: budget for budget in Budget.objects.filter(user=user)}
        
        # Generate transactions for different time periods
        
        # 1. Daily transactions for the past week
        for day in range(7):
            date = now - timedelta(days=day)
            
            # Daily transactions (2-5 per day)
            daily_count = random.randint(2, 5)
            for _ in range(daily_count):
                template = random.choice(transaction_patterns[user.email])
                
                # Set appropriate budget based on transaction type
                budget = None
                if template['type'] == 'expense':
                    budget = budgets.get('daily')
                
                amount = Decimal(str(round(random.uniform(5.0, 50.0), 2)))
                
                # Create transaction
                transaction = Transaction.objects.create(
                    user=user,
                    name=f"{template['name']} {date.strftime('%m/%d')}",
                    description=f"Daily {template['type']} on {date.strftime('%Y-%m-%d')}",
                    amount=amount,
                    type=template['type'],
                    date=date.replace(hour=random.randint(8, 20), minute=random.randint(0, 59)),
                    category=categories.get(template['category']),
                    budget=budget
                )
                created_count += 1
        
        # 2. Weekly patterns for the past month
        for week in range(4):
            date = now - timedelta(weeks=week)
            
            # Weekly expenses (3-6 per week)
            weekly_count = random.randint(3, 6)
            for _ in range(weekly_count):
                template = random.choice([t for t in transaction_patterns[user.email] if t['type'] == 'expense'])
                
                # Set appropriate budget
                budget = budgets.get('weekly')
                
                amount = Decimal(str(round(random.uniform(50.0, 150.0), 2)))
                
                # Create transaction
                transaction = Transaction.objects.create(
                    user=user,
                    name=f"Weekly {template['name']}",
                    description=f"Weekly {template['type']} for week of {date.strftime('%Y-%m-%d')}",
                    amount=amount,
                    type=template['type'],
                    date=date.replace(hour=random.randint(8, 20), minute=random.randint(0, 59)),
                    category=categories.get(template['category']),
                    budget=budget
                )
                created_count += 1
        
        # 3. Monthly patterns for the past 6 months
        for month in range(6):
            month_date = (now - timedelta(days=30*month))
            
            # Monthly salary
            salary_amount = Decimal(str(round(random.uniform(3000.0, 5000.0), 2)))
            salary_template = next((t for t in transaction_patterns[user.email] if t['name'] == 'Monthly Salary'), None)
            if salary_template:
                transaction = Transaction.objects.create(
                    user=user,
                    name=f"Salary for {month_date.strftime('%B %Y')}",
                    description=f"Monthly salary payment",
                    amount=salary_amount,
                    type='income',
                    date=month_date.replace(day=1, hour=9, minute=0),
                    category=categories.get('Salary'),
                    budget=None
                )
                created_count += 1
            
            # Monthly bills (rent, utilities, etc.)
            monthly_bills = [
                {"name": "Rent/Mortgage", "amount": Decimal(str(round(random.uniform(800.0, 1500.0), 2))), "category": "Housing"},
                {"name": "Electricity Bill", "amount": Decimal(str(round(random.uniform(50.0, 120.0), 2))), "category": "Utilities"},
                {"name": "Water Bill", "amount": Decimal(str(round(random.uniform(30.0, 80.0), 2))), "category": "Utilities"},
                {"name": "Internet & Cable", "amount": Decimal(str(round(random.uniform(60.0, 120.0), 2))), "category": "Utilities"},
                {"name": "Phone Bill", "amount": Decimal(str(round(random.uniform(50.0, 100.0), 2))), "category": "Utilities"},
            ]
            
            for bill in monthly_bills:
                # Randomize the day slightly but keep consistent for a given bill type
                bill_day = ((hash(bill['name']) % 15) + 5)  # bill due between 5th and 20th
                bill_date = month_date.replace(day=min(bill_day, 28))
                
                transaction = Transaction.objects.create(
                    user=user,
                    name=f"{bill['name']} - {bill_date.strftime('%B %Y')}",
                    description=f"Monthly {bill['name'].lower()}",
                    amount=bill['amount'],
                    type='expense',
                    date=bill_date.replace(hour=random.randint(8, 20), minute=random.randint(0, 59)),
                    category=categories.get(bill['category']),
                    budget=budgets.get('monthly')
                )
                created_count += 1
        
        # 4. Annual expenses (past 2 years)
        annual_expenses = [
            {"name": "Car Insurance", "amount": Decimal(str(round(random.uniform(800.0, 1500.0), 2))), "category": "Insurance"},
            {"name": "Property Tax", "amount": Decimal(str(round(random.uniform(1500.0, 3000.0), 2))), "category": "Housing"},
            {"name": "Vacation", "amount": Decimal(str(round(random.uniform(1000.0, 3000.0), 2))), "category": "Travel"},
            {"name": "Tax Return", "amount": Decimal(str(round(random.uniform(1000.0, 2000.0), 2))), "type": "income", "category": "Other Income"},
        ]
        
        for year in range(2):
            year_date = now.replace(year=now.year - year)
            
            for expense in annual_expenses:
                # Randomize the month
                expense_date = year_date.replace(month=random.randint(1, 12), day=random.randint(1, 28))
                
                transaction = Transaction.objects.create(
                    user=user,
                    name=f"{expense['name']} - {expense_date.strftime('%Y')}",
                    description=f"Annual {expense.get('type', 'expense')}",
                    amount=expense['amount'],
                    type=expense.get('type', 'expense'),
                    date=expense_date.replace(hour=random.randint(8, 20), minute=random.randint(0, 59)),
                    category=categories.get(expense['category']),
                    budget=budgets.get('yearly') if expense.get('type', 'expense') == 'expense' else None
                )
                created_count += 1
        
        # 5. Random one-off transactions
        one_off_count = random.randint(20, 30)
        for _ in range(one_off_count):
            # Random date in the past year
            days_ago = random.randint(1, 365)
            date = now - timedelta(days=days_ago)
            
            template = random.choice(transaction_patterns[user.email])
            
            # Determine budget type based on amount
            amount = Decimal(str(round(random.uniform(5.0, 500.0), 2)))
            budget = None
            if template['type'] == 'expense':
                if amount < 50:
                    budget = budgets.get('daily')
                elif amount < 200:
                    budget = budgets.get('weekly')
                elif amount < 1000:
                    budget = budgets.get('monthly')
                else:
                    budget = budgets.get('yearly')
            
            # Create transaction
            transaction = Transaction.objects.create(
                user=user,
                name=f"{template['name']} {date.strftime('%m/%d/%y')}",
                description=f"One-time {template['type']}",
                amount=amount,
                type=template['type'],
                date=date.replace(hour=random.randint(8, 20), minute=random.randint(0, 59)),
                category=categories.get(template['category']),
                budget=budget
            )
            created_count += 1
    
    print(f"Created {created_count} transactions in total.")
    return created_count

if __name__ == "__main__":
    print("Creating transactions...")
    create_transactions()
    print("Done creating transactions.")