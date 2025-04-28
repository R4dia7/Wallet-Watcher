import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from transactions.models import Category
from seeders.create_users import create_users

def create_categories():
    """
    Create transaction categories for users
    """
    # Get or create users
    users = create_users()
    
    # Define common categories for all users
    common_categories = {
        'income': [
            {'name': 'Salary', 'description': 'Regular employment income'},
            {'name': 'Freelance', 'description': 'Income from freelance work'},
            {'name': 'Investments', 'description': 'Income from stocks, bonds, etc.'},
            {'name': 'Gifts', 'description': 'Money received as gifts'},
            {'name': 'Rental Income', 'description': 'Income from rental properties'},
            {'name': 'Side Hustle', 'description': 'Income from side businesses'},
            {'name': 'Refunds', 'description': 'Money refunded from purchases'},
            {'name': 'Other Income', 'description': 'Miscellaneous income'}
        ],
        'expense': [
            {'name': 'Housing', 'description': 'Rent, mortgage, property taxes'},
            {'name': 'Utilities', 'description': 'Electricity, water, gas, internet'},
            {'name': 'Groceries', 'description': 'Food and household supplies'},
            {'name': 'Dining Out', 'description': 'Restaurants, cafes, takeout'},
            {'name': 'Transportation', 'description': 'Public transit, fuel, car maintenance'},
            {'name': 'Healthcare', 'description': 'Medical expenses, insurance'},
            {'name': 'Entertainment', 'description': 'Movies, events, subscriptions'},
            {'name': 'Shopping', 'description': 'Clothing, electronics, etc.'},
            {'name': 'Travel', 'description': 'Vacations, business trips'},
            {'name': 'Education', 'description': 'Tuition, books, courses'},
            {'name': 'Debt Payments', 'description': 'Credit card, loan payments'},
            {'name': 'Insurance', 'description': 'Life, home, auto insurance'},
            {'name': 'Personal Care', 'description': 'Haircuts, gym, spa'},
            {'name': 'Gifts & Donations', 'description': 'Presents, charitable giving'},
            {'name': 'Subscriptions', 'description': 'Digital services, memberships'},
            {'name': 'Miscellaneous', 'description': 'Other expenses'}
        ]
    }
    
    # User-specific categories to add variety
    user_specific_categories = {
        users[0].email: [  # John Doe
            {'name': 'Pet Expenses', 'description': 'Pet food, vet bills, supplies'},
            {'name': 'Home Improvement', 'description': 'Repairs, renovations, furniture'},
            {'name': 'Bonus', 'description': 'Annual or performance bonuses'}
        ],
        users[1].email: [  # Jane Smith
            {'name': 'Hobbies', 'description': 'Craft supplies, equipment, etc.'},
            {'name': 'Child Care', 'description': 'Daycare, babysitting'},
            {'name': 'Dividend', 'description': 'Dividend income from investments'}
        ],
        users[2].email: [  # Alex Wong
            {'name': 'Business Expenses', 'description': 'Costs related to business'},
            {'name': 'Fitness', 'description': 'Gym membership, equipment'},
            {'name': 'Commission', 'description': 'Sales commission income'}
        ]
    }
    
    all_categories = []
    
    # Create categories for each user
    for user in users:
        # Add common categories
        for category_data in common_categories['income'] + common_categories['expense']:
            category, created = Category.objects.get_or_create(
                user=user,
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            
            if created:
                print(f"Created category '{category.name}' for user: {user.email}")
            
            all_categories.append(category)
        
        # Add user-specific categories
        if user.email in user_specific_categories:
            for category_data in user_specific_categories[user.email]:
                category, created = Category.objects.get_or_create(
                    user=user,
                    name=category_data['name'],
                    defaults={'description': category_data['description']}
                )
                
                if created:
                    print(f"Created specific category '{category.name}' for user: {user.email}")
                
                all_categories.append(category)
    
    return all_categories

if __name__ == "__main__":
    print("Creating transaction categories...")
    create_categories()
    print("Done creating categories.")