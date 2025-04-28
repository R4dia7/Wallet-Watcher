import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import Dashboard
from seeders.create_users import create_users

def create_dashboards():
    """
    Create dashboard preferences for users
    """
    # Get or create users
    users = create_users()
    
    # Define dashboard preferences
    dashboard_preferences = [
        {
            'user': users[0],
            'theme_preference': 'light',
            'default_view': 'overview',
            'time_period': 'monthly'
        },
        {
            'user': users[1],
            'theme_preference': 'dark',
            'default_view': 'transactions',
            'time_period': 'weekly'
        },
        {
            'user': users[2],
            'theme_preference': 'light',
            'default_view': 'budgets',
            'time_period': 'yearly'
        }
    ]
    
    created_dashboards = []
    
    for pref in dashboard_preferences:
        # Check if dashboard already exists for user
        dashboard, created = Dashboard.objects.get_or_create(
            user=pref['user'],
            defaults=pref
        )
        
        if created:
            print(f"Created dashboard for user: {pref['user'].email}")
        else:
            # Update preferences if dashboard already exists
            for key, value in pref.items():
                if key != 'user':
                    setattr(dashboard, key, value)
            dashboard.save()
            print(f"Updated dashboard for user: {pref['user'].email}")
        
        created_dashboards.append(dashboard)
    
    return created_dashboards

if __name__ == "__main__":
    print("Creating dashboard preferences...")
    create_dashboards()
    print("Done creating dashboard preferences.")