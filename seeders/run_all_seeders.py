import os
import django
import time
import argparse

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def run_all_seeders(reset=False, clear=False):
    """
    Run all seeder scripts in the correct order to populate the database
    with comprehensive demo data
    
    Args:
        reset (bool): If True, clear all existing seed data before seeding
        clear (bool): If True, clear all data
    """
    print("=== Starting Database Seeding Process ===")
    
    # Import seeders
    from seeders.create_users import create_users
    from seeders.create_dashboards import create_dashboards
    from seeders.create_categories import create_categories
    from seeders.create_budgets import create_budgets
    from seeders.create_transactions import create_transactions
    from seeders.create_reports import create_reports
    
    # Import clear data function
    if reset:
        from seeders.clear_data import clear_seeded_data
        print("\nResetting database - clearing all seed data...")
        clear_seeded_data(confirm=True)
        print("Database reset complete.")
    
    if clear:
        from seeders.clear_all_data import clear_all_data
        print("\nClearing all data...")
        clear_all_data()
        print("All data cleared.")
    
    # Track timing
    start_time = time.time()
    
    # Run seeders in order
    print("\n1. Creating user accounts...")
    users = create_users()
    print(f"Created {len(users)} user accounts.")
    
    print("\n2. Setting up dashboard preferences...")
    dashboards = create_dashboards()
    print(f"Set up {len(dashboards)} dashboard preferences.")
    
    print("\n3. Creating transaction categories...")
    categories = create_categories()
    print(f"Created {len(categories)} transaction categories.")
    
    print("\n4. Setting up budgets...")
    budgets = create_budgets()
    print(f"Created {len(budgets)} budgets.")
    
    print("\n5. Generating transaction history...")
    transaction_count = create_transactions()
    print(f"Generated {transaction_count} transactions.")
    
    print("\n6. Creating sample reports...")
    reports = create_reports()
    print(f"Created {len(reports)} sample reports.")
    
    # Calculate total time
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n=== Seeding Completed in {elapsed_time:.2f} seconds ===")
    print("""
Summary:
- Users: {0}
- Dashboards: {1}
- Budgets: {2}
- Transactions: {3}
- Reports: {4}
    """.format(len(users), len(dashboards), len(budgets), transaction_count, len(reports)))
    
    print("Your budget tracker application now has comprehensive demo data.")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Seed the database with demo data')
    parser.add_argument('--reset', action='store_true', help='Clear all existing seed data before seeding')
    parser.add_argument('--clear', action='store_true', help='Clear all data')
    args = parser.parse_args()
    
    # Run seeders with reset option if specified
    run_all_seeders(reset=args.reset)