# utils/dummy_data.py

"""
Dummy Data Generator for Daily Expense Tracker
Generate realistic sample data for testing and demonstration
"""

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# ============================================================
# CONFIGURATION
# ============================================================

# Categories with their typical amounts
CATEGORIES = {
    'Food': {'min': 10000, 'max': 150000, 'icon': '🍔'},
    'Transport': {'min': 5000, 'max': 50000, 'icon': '🚗'},
    'Shopping': {'min': 20000, 'max': 500000, 'icon': '🛍️'},
    'Entertainment': {'min': 15000, 'max': 200000, 'icon': '🎮'},
    'Bills': {'min': 50000, 'max': 500000, 'icon': '📄'},
    'Health': {'min': 20000, 'max': 300000, 'icon': '🏥'},
    'Education': {'min': 50000, 'max': 1000000, 'icon': '📚'},
    'Other': {'min': 10000, 'max': 100000, 'icon': '📦'},
}

# Food items
FOOD_DESCRIPTIONS = [
    'Lunch at restaurant', 'Dinner with friends', 'Coffee break',
    'Groceries', 'Snacks', 'Takeaway', 'Food delivery',
    'Breakfast', 'Team lunch', 'Birthday dinner', 'Fast food'
]

# Transport descriptions
TRANSPORT_DESCRIPTIONS = [
    'Gojek ride', 'Grab car', 'Bus ticket', 'Train ticket',
    'Fuel', 'Taxi', 'Bike rental', 'Parking fee', 'Toll fee'
]

# Shopping descriptions
SHOPPING_DESCRIPTIONS = [
    'Clothes', 'Electronics', 'Books', 'Home supplies',
    'Kitchen items', 'Accessories', 'Gifts', 'Stationery'
]

# Entertainment descriptions
ENTERTAINMENT_DESCRIPTIONS = [
    'Movie ticket', 'Concert ticket', 'Theme park entry',
    'Netflix subscription', 'Spotify premium', 'Game purchase',
    'Bowling', 'Karaoke', 'Museum entry'
]

# Bills descriptions
BILLS_DESCRIPTIONS = [
    'Electricity bill', 'Water bill', 'Internet bill',
    'Phone bill', 'Gas bill', 'Rent', 'Maintenance fee'
]

# Health descriptions
HEALTH_DESCRIPTIONS = [
    'Doctor visit', 'Medicine', 'Health checkup',
    'Dentist', 'Eye checkup', 'Vitamins', 'Insurance'
]

# Education descriptions
EDUCATION_DESCRIPTIONS = [
    'Course fee', 'Books', 'Training', 'Workshop',
    'Online course', 'Certification', 'Tutoring'
]

# Payment methods
PAYMENT_METHODS = ['Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 'E-Wallet']

# Income sources (with realistic amounts)
INCOME_SOURCES = [
    {'name': 'Salary', 'min': 3000000, 'max': 15000000},
    {'name': 'Bonus', 'min': 500000, 'max': 5000000},
    {'name': 'Freelance', 'min': 100000, 'max': 3000000},
    {'name': 'Investment', 'min': 100000, 'max': 2000000},
    {'name': 'Side business', 'min': 200000, 'max': 5000000},
    {'name': 'Gift', 'min': 50000, 'max': 1000000},
    {'name': 'Dividend', 'min': 100000, 'max': 1000000},
    {'name': 'Rental income', 'min': 500000, 'max': 3000000},
]

# Tags for expenses
TAGS = ['important', 'work', 'personal', 'urgent', 'recurring', 'one-time', 'family', 'social']

# Guaranteed income data (PASTI MASUK!)
FORCE_INCOMES = [
    ('2026-07-01', 'Salary', 5000000, 'Monthly salary - July', 0),
    ('2026-07-05', 'Bonus', 2000000, 'Performance bonus', 0),
    ('2026-07-10', 'Freelance', 1500000, 'Freelance project', 0),
    ('2026-06-25', 'Investment', 1000000, 'Dividend payment', 0),
    ('2026-06-15', 'Salary', 5000000, 'Monthly salary - June', 0),
    ('2026-06-01', 'Rental income', 3000000, 'Property rental', 1),
    ('2026-05-20', 'Bonus', 1500000, 'Quarterly bonus', 0),
    ('2026-05-10', 'Freelance', 800000, 'Website project', 0),
    ('2026-04-15', 'Salary', 4500000, 'Monthly salary - April', 0),
    ('2026-04-01', 'Side business', 2000000, 'Side business income', 0),
]


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def init_database(db_path: str):
    """Initialize database with all required tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            payment_method TEXT DEFAULT 'Cash',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check and add missing columns
    cursor.execute("PRAGMA table_info(expenses)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    if 'payment_method' not in existing_columns:
        cursor.execute("ALTER TABLE expenses ADD COLUMN payment_method TEXT DEFAULT 'Cash'")
        print("✅ Added payment_method column to expenses")
    
    # Create incomes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            is_recurring INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create budgets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE,
            monthly_limit REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create recurring_expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recurring_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            frequency TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create expense_tags table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY (expense_id) REFERENCES expenses(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database tables initialized")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_random_date(start_date: datetime, end_date: datetime) -> str:
    """Generate random date between start and end dates"""
    time_between = end_date - start_date
    days_between = time_between.days
    random_day = random.randint(0, days_between)
    result_date = start_date + timedelta(days=random_day)
    return result_date.strftime('%Y-%m-%d')


def random_description(category: str) -> str:
    """Generate random description based on category"""
    descriptions_map = {
        'Food': FOOD_DESCRIPTIONS,
        'Transport': TRANSPORT_DESCRIPTIONS,
        'Shopping': SHOPPING_DESCRIPTIONS,
        'Entertainment': ENTERTAINMENT_DESCRIPTIONS,
        'Bills': BILLS_DESCRIPTIONS,
        'Health': HEALTH_DESCRIPTIONS,
        'Education': EDUCATION_DESCRIPTIONS,
        'Other': FOOD_DESCRIPTIONS + TRANSPORT_DESCRIPTIONS + SHOPPING_DESCRIPTIONS,
    }
    return random.choice(descriptions_map.get(category, ['General expense']))


def generate_expense(date: str, category: str = None) -> Dict[str, Any]:
    """Generate a single expense"""
    if not category:
        category = random.choice(list(CATEGORIES.keys()))
    
    category_info = CATEGORIES[category]
    amount = random.randint(category_info['min'], category_info['max'])
    amount = round(amount / 1000) * 1000  # Round to nearest 1000
    
    description = random_description(category)
    payment_method = random.choice(PAYMENT_METHODS)
    
    # Sometimes add tags
    tags = []
    if random.random() < 0.3:
        num_tags = random.randint(1, 3)
        tags = random.sample(TAGS, num_tags)
    
    return {
        'date': date,
        'category': category,
        'amount': amount,
        'description': description,
        'payment_method': payment_method,
        'tags': tags
    }


def generate_income(date: str) -> Dict[str, Any]:
    """Generate a single income entry with realistic amounts"""
    source_info = random.choice(INCOME_SOURCES)
    source = source_info['name']
    amount = random.randint(source_info['min'], source_info['max'])
    amount = round(amount / 10000) * 10000  # Round to nearest 10000
    is_recurring = random.random() < 0.3
    
    desc_templates = [
        f"{source} payment for this month",
        f"{source} transfer",
        f"{source} deposit",
        f"{source} income",
        f"Monthly {source.lower()}",
        f"{source} revenue"
    ]
    description = random.choice(desc_templates)
    
    return {
        'date': date,
        'source': source,
        'amount': amount,
        'description': description,
        'is_recurring': is_recurring
    }


def generate_budget(used_categories: list = None) -> Dict[str, Any]:
    """Generate a budget for a category (with unique category)"""
    if used_categories is None:
        used_categories = []
    
    available_categories = [cat for cat in CATEGORIES.keys() if cat not in used_categories]
    
    if not available_categories:
        category = random.choice(list(CATEGORIES.keys()))
    else:
        category = random.choice(available_categories)
    
    budget_limits = {
        'Food': (500000, 2000000),
        'Transport': (200000, 1000000),
        'Shopping': (300000, 3000000),
        'Entertainment': (200000, 1500000),
        'Bills': (500000, 3000000),
        'Health': (200000, 1000000),
        'Education': (500000, 5000000),
        'Other': (100000, 1000000),
    }
    
    min_limit, max_limit = budget_limits.get(category, (200000, 2000000))
    limit = random.randint(min_limit, max_limit)
    limit = round(limit / 100000) * 100000  # Round to nearest 100000
    
    return {
        'category': category,
        'monthly_limit': limit
    }


# ============================================================
# MAIN GENERATE FUNCTION
# ============================================================

def generate_dummy_data(
    num_expenses: int = 100,
    num_incomes: int = 10,
    num_budgets: int = 5,
    months_back: int = 3,
    db_path: str = "data/expenses.db"
) -> Dict[str, int]:
    """
    Generate dummy data and insert into database
    
    Args:
        num_expenses: Number of expenses to generate
        num_incomes: Number of incomes to generate
        num_budgets: Number of budgets to generate
        months_back: How many months back to generate data
        db_path: Path to database
    
    Returns:
        Dict with statistics of inserted data
    """
    # Create data directory if not exists
    Path(db_path).parent.mkdir(exist_ok=True)
    
    # Initialize database
    init_database(db_path)
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months_back * 30)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {
        'expenses_inserted': 0,
        'force_incomes_inserted': 0,
        'random_incomes_inserted': 0,
        'budgets_inserted': 0,
        'tags_inserted': 0,
        'recurring_inserted': 0,
    }
    
    try:
        # ============================================================
        # 1. GENERATE EXPENSES
        # ============================================================
        print(f"📊 Generating {num_expenses} expenses...")
        for i in range(num_expenses):
            date_str = get_random_date(start_date, end_date)
            expense = generate_expense(date_str)
            
            cursor.execute("""
                INSERT INTO expenses (date, category, amount, description, payment_method)
                VALUES (?, ?, ?, ?, ?)
            """, (
                expense['date'],
                expense['category'],
                expense['amount'],
                expense['description'],
                expense['payment_method']
            ))
            
            expense_id = cursor.lastrowid
            stats['expenses_inserted'] += 1
            
            # Insert tags if any
            if expense['tags']:
                for tag in expense['tags']:
                    cursor.execute("""
                        INSERT INTO expense_tags (expense_id, tag)
                        VALUES (?, ?)
                    """, (expense_id, tag))
                    stats['tags_inserted'] += 1
        
        # ============================================================
        # 2. GENERATE FORCE INCOMES (PASTI MASUK!)
        # ============================================================
        print("💰 Inserting guaranteed incomes...")
        for date, source, amount, desc, recurring in FORCE_INCOMES:
            cursor.execute("""
                INSERT INTO incomes (date, source, amount, description, is_recurring)
                VALUES (?, ?, ?, ?, ?)
            """, (date, source, amount, desc, recurring))
            stats['force_incomes_inserted'] += 1
        
        # ============================================================
        # 3. GENERATE RANDOM INCOMES
        # ============================================================
        print(f"💰 Generating {num_incomes} random incomes...")
        
        # Get available months
        available_months = []
        current_date = start_date
        while current_date <= end_date:
            available_months.append(current_date.strftime('%Y-%m'))
            current_date += timedelta(days=30)
        
        # Ensure income in every month
        for month in available_months:
            num_income_this_month = random.randint(1, 2)
            for i in range(num_income_this_month):
                day = random.randint(1, 28)
                date_str = f"{month}-{str(day).zfill(2)}"
                income = generate_income(date_str)
                
                cursor.execute("""
                    INSERT INTO incomes (date, source, amount, description, is_recurring)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    income['date'],
                    income['source'],
                    income['amount'],
                    income['description'],
                    1 if income['is_recurring'] else 0
                ))
                stats['random_incomes_inserted'] += 1
        
        # ============================================================
        # 4. GENERATE BUDGETS
        # ============================================================
        print(f"🎯 Generating {num_budgets} budgets...")
        
        cursor.execute("DELETE FROM budgets")
        
        used_categories = []
        budget_count = min(num_budgets, len(CATEGORIES))
        for i in range(budget_count):
            budget = generate_budget(used_categories)
            used_categories.append(budget['category'])
            
            cursor.execute("""
                INSERT INTO budgets (category, monthly_limit)
                VALUES (?, ?)
            """, (
                budget['category'],
                budget['monthly_limit']
            ))
            stats['budgets_inserted'] += 1
        
        # ============================================================
        # 5. GENERATE RECURRING EXPENSES
        # ============================================================
        print(f"🔄 Generating recurring expenses...")
        recurring_categories = ['Bills', 'Entertainment', 'Transport', 'Food']
        frequencies = ['daily', 'weekly', 'monthly', 'yearly']
        
        for i in range(5):
            category = random.choice(recurring_categories)
            amount = random.randint(50000, 500000)
            amount = round(amount / 10000) * 10000
            frequency = random.choice(frequencies)
            start_date_str = get_random_date(start_date, end_date)
            
            desc_templates = [
                f"{category} subscription",
                f"Recurring {category.lower()} expense",
                f"{category} monthly fee",
                f"{category} regular payment"
            ]
            description = random.choice(desc_templates)
            
            cursor.execute("""
                INSERT INTO recurring_expenses (category, amount, description, frequency, start_date, active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                category,
                amount,
                description,
                frequency,
                start_date_str,
                1 if random.random() < 0.8 else 0
            ))
            stats['recurring_inserted'] += 1
        
        # Commit all changes
        conn.commit()
        
        total_income = stats['force_incomes_inserted'] + stats['random_incomes_inserted']
        
        print(f"\n✅ Dummy data generated successfully!")
        print(f"   📊 {stats['expenses_inserted']} expenses inserted")
        print(f"   💰 {stats['force_incomes_inserted']} guaranteed incomes inserted")
        print(f"   💰 {stats['random_incomes_inserted']} random incomes inserted")
        print(f"   📊 TOTAL INCOME: {total_income} entries")
        print(f"   🎯 {stats['budgets_inserted']} budgets inserted")
        print(f"   🏷️  {stats['tags_inserted']} tags inserted")
        print(f"   🔄 {stats['recurring_inserted']} recurring expenses inserted")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error generating dummy data: {e}")
        raise
    finally:
        conn.close()
    
    return stats


# ============================================================
# PREVIEW FUNCTIONS
# ============================================================

def generate_and_show_preview(num_expenses: int = 10):
    """Generate dummy data and show preview"""
    print("=" * 60)
    print("  DAILY EXPENSE TRACKER - DUMMY DATA GENERATOR")
    print("=" * 60)
    
    # Generate data
    generate_dummy_data(
        num_expenses=num_expenses,
        num_incomes=10,
        num_budgets=5,
        months_back=3
    )
    
    # Show expense preview
    print("\n" + "=" * 60)
    print("  PREVIEW OF RECENT EXPENSES")
    print("=" * 60)
    
    conn = sqlite3.connect("data/expenses.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, date, category, amount, description, payment_method
        FROM expenses 
        ORDER BY date DESC 
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    
    print(f"\n{'ID':>4} {'Date':12} {'Category':15} {'Amount':>12} {'Payment':12} {'Description':20}")
    print("-" * 80)
    
    for row in rows:
        print(f"{row[0]:>4} {row[1]:12} {row[2]:15} Rp {row[3]:>10,.0f} {row[4]:12} {row[5][:18]:20}")
    
    conn.close()
    
    # Show income preview
    print("\n" + "=" * 60)
    print("  PREVIEW OF INCOMES")
    print("=" * 60)
    
    conn = sqlite3.connect("data/expenses.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, date, source, amount, description
        FROM incomes 
        ORDER BY date DESC 
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    
    print(f"\n{'ID':>4} {'Date':12} {'Source':18} {'Amount':>12} {'Description':25}")
    print("-" * 75)
    
    for row in rows:
        print(f"{row[0]:>4} {row[1]:12} {row[2]:18} Rp {row[3]:>10,.0f} {row[4][:23]:25}")
    
    conn.close()
    
    # Show budget preview
    print("\n" + "=" * 60)
    print("  PREVIEW OF BUDGETS")
    print("=" * 60)
    
    conn = sqlite3.connect("data/expenses.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT category, monthly_limit
        FROM budgets 
        ORDER BY category
    """)
    
    rows = cursor.fetchall()
    
    print(f"\n{'Category':20} {'Monthly Limit':>15}")
    print("-" * 40)
    
    for row in rows:
        print(f"{row[0]:20} Rp {row[1]:>10,.0f}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("  ✅ Dummy data ready for testing!")
    print("  📁 Database: data/expenses.db")
    print("  💰 Total Income: Check the Income tab or All Time view")
    print("  💡 Run 'python gui.py' to see the dashboard")
    print("=" * 60)


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate dummy data for testing")
    parser.add_argument(
        '-n', '--num-expenses', 
        type=int, 
        default=100, 
        help='Number of expenses to generate (default: 100)'
    )
    parser.add_argument(
        '-i', '--num-incomes', 
        type=int, 
        default=10, 
        help='Number of incomes to generate (default: 10)'
    )
    parser.add_argument(
        '-m', '--months-back', 
        type=int, 
        default=3, 
        help='Months back to generate data (default: 3)'
    )
    parser.add_argument(
        '-b', '--num-budgets', 
        type=int, 
        default=5, 
        help='Number of budgets to generate (default: 5)'
    )
    parser.add_argument(
        '--preview', 
        action='store_true', 
        help='Show preview after generation'
    )
    
    args = parser.parse_args()
    
    if args.preview:
        generate_and_show_preview(args.num_expenses)
    else:
        generate_dummy_data(
            num_expenses=args.num_expenses,
            num_incomes=args.num_incomes,
            num_budgets=args.num_budgets,
            months_back=args.months_back
        )


if __name__ == "__main__":
    main()