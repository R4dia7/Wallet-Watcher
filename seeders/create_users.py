import os
import django
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_users():
    """
    Create demo users for the application
    """
    users = [
        {
            'email': 'john.doe@example.com',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': datetime(1985, 5, 15),
            'phone_number': '+1234567890',
            'theme_preference': 'light'
        },
        {
            'email': 'jane.smith@example.com',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'date_of_birth': datetime(1990, 8, 22),
            'phone_number': '+1987654321',
            'theme_preference': 'dark'
        },
        {
            'email': 'alex.wong@example.com',
            'password': 'password123',
            'first_name': 'Alex',
            'last_name': 'Wong',
            'date_of_birth': datetime(1988, 3, 10),
            'phone_number': '+1567890123',
            'theme_preference': 'light'
        }
    ]
    
    created_users = []
    
    for user_data in users:
        # Skip if user already exists
        if User.objects.filter(email=user_data['email']).exists():
            print(f"User {user_data['email']} already exists. Skipping.")
            created_users.append(User.objects.get(email=user_data['email']))
            continue
            
        # Extract password
        password = user_data.pop('password')
        
        # Create user
        user = User.objects.create_user(
            **user_data
        )
        user.set_password(password)
        user.save()
        
        print(f"Created user: {user.email}")
        created_users.append(user)
    
    return created_users

if __name__ == "__main__":
    print("Creating users...")
    create_users()
    print("Done creating users.")