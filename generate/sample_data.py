#generate\sample_data.py

"""
Generate sample data for testing
""" 
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from models.expense_model import Expense
    from models.category_model import Category
    from services.database_service import DatabaseService
    from config.database_config import DatabaseConfig
except ImportError:
    print("Warning: Some imports failed. Make sure project structure is correct.")
    sys.exit(1)


# Sample categories with icons
SAMPLE_CATEGORIES = [
    {"name": "Food & Drinks", "icon": "🍔", "budget_limit": 1500000},
    {"name": "Transportation", "icon": "🚗", "budget_limit": 500000},
    {"name": "Shopping", "icon": "🛍️", "budget_limit": 1000000},
    {"name": "Entertainment", "icon": "🎬", "budget_limit": 300000},
    {"name": "Healthcare", "icon": "🏥", "budget_limit": 200000},
    {"name": "Education", "icon": "📚", "budget_limit": 500000},
    {"name": "Bills", "icon": "📋", "budget_limit": 2000000},
    {"name": "Investment", "icon": "💰", "budget_limit": 1000000},
    {"name": "Clothing", "icon": "👕", "budget_limit": 300000},
    {"name": "Others", "icon": "📦", "budget_limit": 0},
]

# Sample expense descriptions
FOOD_DESCRIPTIONS = [
    "Lunch at restaurant", "Coffee break", "Groceries", "Dinner with friends",
    "Fast food", "Snacks", "Beverages", "Food delivery"
]

TRANSPORT_DESCRIPTIONS = [
    "Taxi fare", "Bus ticket", "Train ticket", "Fuel", 
    "Parking fee", "Car maintenance", "Public transport"
]

SHOPPING_DESCRIPTIONS = [
    "Supermarket", "Electronics", "Household items", "Online shopping",
    "Gifts", "Accessories", "Books"
]

ENTERTAINMENT_DESCRIPTIONS = [
    "Movie tickets", "Concert", "Games", "Streaming subscription",
    "Sports event", "Hobby supplies"
]


def generate_test_categories():
    """Generate sample categories in the database"""
    print("Generating sample categories...")
    
    db_config = DatabaseConfig()
    db_config.initialize_database()  # Ensure tables exist
    
    service = DatabaseService()
    
    # First, get existing categories
    existing_categories = service.get_all_categories()
    existing_names = [cat['name'] for cat in existing_categories]
    
    added_count = 0
    for cat_data in SAMPLE_CATEGORIES:
        if cat_data['name'] not in existing_names:
            category = Category(
                name=cat_data['name'],
                budget_limit=Decimal(str(cat_data['budget_limit'])),
                description=f"Sample category: {cat_data['name']}",
                icon=cat_data['icon']
            )
            
            try:
                service.add_category(category)
                added_count += 1
                print(f"  Added category: {cat_data['name']}")
            except Exception as e:
                print(f"  Error adding category {cat_data['name']}: {e}")
    
    print(f"✓ Added {added_count} new categories")
    return added_count


def generate_sample_expenses(count=100, year=2024):
    """Generate sample expense data"""
    print(f"Generating {count} sample expenses for year {year}...")
    
    service = DatabaseService()
    
    # Get available categories
    categories = service.get_all_categories()
    if not categories:
        print("Warning: No categories found. Generating categories first...")
        generate_test_categories()
        categories = service.get_all_categories()
    
    category_names = [cat['name'] for cat in categories]
    
    added_count = 0
    errors = 0
    
    for i in range(count):
        try:
            # Random date within the year
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            days_between = (end_date - start_date).days
            random_days = random.randint(0, days_between)
            expense_date = start_date + timedelta(days=random_days)
            
            # Random category
            category = random.choice(category_names)
            
            # Random amount based on category
            if category == "Food & Drinks":
                amount = random.randint(15000, 150000)
                description = random.choice(FOOD_DESCRIPTIONS)
            elif category == "Transportation":
                amount = random.randint(10000, 100000)
                description = random.choice(TRANSPORT_DESCRIPTIONS)
            elif category == "Shopping":
                amount = random.randint(50000, 500000)
                description = random.choice(SHOPPING_DESCRIPTIONS)
            elif category == "Entertainment":
                amount = random.randint(20000, 200000)
                description = random.choice(ENTERTAINMENT_DESCRIPTIONS)
            else:
                amount = random.randint(10000, 300000)
                description = f"Expense #{i+1}"
            
            # Add some randomness to description
            if random.random() > 0.7:  # 30% chance
                description += f" - {expense_date.strftime('%b %d')}"
            
            # Create expense
            expense = Expense(
                date=expense_date,
                category=category,
                amount=Decimal(str(amount)),
                description=description
            )
            
            # Add to database
            expense_id = service.add_expense(expense)
            added_count += 1
            
            if (i + 1) % 20 == 0:
                print(f"  Generated {i + 1} expenses...")
                
        except Exception as e:
            errors += 1
            if errors <= 5:  # Print only first few errors
                print(f"  Error generating expense {i+1}: {e}")
    
    print(f"✓ Generated {added_count} sample expenses")
    if errors > 0:
        print(f"⚠️  {errors} errors occurred during generation")
    
    return added_count


def generate_test_database(expense_count=50):
    """Generate a complete test database with categories and expenses"""
    print("=" * 60)
    print("Generating test database...")
    print("=" * 60)
    
    # Initialize database
    db_config = DatabaseConfig()
    db_config.initialize_database()
    
    # Generate categories
    category_count = generate_test_categories()
    
    # Generate expenses
    expense_count = generate_sample_expenses(count=expense_count)
    
    # Show summary
    service = DatabaseService()
    total_expenses = len(service.get_all_expenses())
    total_categories = len(service.get_all_categories())
    
    print("\n" + "=" * 60)
    print("TEST DATABASE SUMMARY")
    print("=" * 60)
    print(f"Total categories: {total_categories}")
    print(f"Total expenses: {total_expenses}")
    
    # Show monthly summary for current month
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    summary = service.get_monthly_summary(current_year, current_month)
    print(f"Current month expenses: Rp {summary['total_expenses']:,.0f}")
    
    print("=" * 60)
    print("Test database generation complete!")
    
    return {
        'categories': total_categories,
        'expenses': total_expenses,
        'monthly_total': summary['total_expenses']
    }


def clear_test_data():
    """Clear all test data from database (use with caution!)"""
    confirm = input("Are you sure you want to clear ALL expense data? (yes/no): ")
    
    if confirm.lower() == 'yes':
        try:
            conn = DatabaseConfig().get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM expenses")
            rows_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"✓ Deleted {rows_deleted} expense records")
            
        except Exception as e:
            print(f"✗ Error clearing data: {e}")
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate sample data for Daily Expense Tracker")
    parser.add_argument("--count", type=int, default=50, help="Number of expenses to generate")
    parser.add_argument("--year", type=int, default=2024, help="Year for expenses")
    parser.add_argument("--clear", action="store_true", help="Clear all expense data")
    parser.add_argument("--categories-only", action="store_true", help="Generate only categories")
    
    args = parser.parse_args()
    
    if args.clear:
        clear_test_data()
    elif args.categories_only:
        generate_test_categories()
    else:
        generate_test_database(expense_count=args.count)