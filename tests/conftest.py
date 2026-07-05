# tests/conftest.py

"""
Pytest configuration and fixtures for expense tracker tests
"""

import tempfile
import os
import sys
from pathlib import Path
import pytest

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================
# SETUP & TEARDOWN FUNCTIONS
# ============================================================

def setup_module():
    """Setup before any tests run - called once at module start."""
    print("\n🔧 Setting up test environment...")
    # Create necessary directories
    Path("exports").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("charts").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)


def teardown_module():
    """Teardown after all tests complete - called once at module end."""
    print("\n🧹 Cleaning up test environment...")


def setup_function():
    """Setup before each test function."""
    pass


def teardown_function():
    """Teardown after each test function."""
    pass


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def clean_exports_dir():
    """Clean exports directory before test"""
    exports_dir = Path("exports")
    exports_dir.mkdir(exist_ok=True)
    
    # Remove any test files
    for file in exports_dir.glob("test_*.csv"):
        try:
            file.unlink()
        except:
            pass
    for file in exports_dir.glob("test_*.xlsx"):
        try:
            file.unlink()
        except:
            pass
    yield exports_dir


@pytest.fixture
def expense_service_fixture():
    """Create ExpenseService fixture with in-memory database"""
    from services.expense_service import ExpenseService
    from services.database_service import DatabaseService
    
    # Create an in-memory database service
    db_service = DatabaseService(":memory:")
    
    # Create expense service
    service = ExpenseService()
    # Replace the internal db_service with our in-memory one
    service.db_service = db_service
    
    yield service
    
    # Cleanup - close database connection
    if hasattr(db_service, 'close'):
        db_service.close()


@pytest.fixture
def export_service_fixture(clean_exports_dir):
    """Create ExportService fixture"""
    from services.export_service import ExportService
    service = ExportService()
    yield service


@pytest.fixture
def sample_expense_data():
    """Provide sample expense data for tests"""
    return {
        'date': '2024-12-01',
        'category': 'Makanan & Minuman',
        'amount': '50000',
        'description': 'Test expense'
    }


@pytest.fixture
def sample_expenses_list():
    """Provide a list of sample expenses for tests"""
    return [
        {
            'date': '2024-12-01',
            'category': 'Makanan & Minuman',
            'amount': 50000,
            'description': 'Lunch'
        },
        {
            'date': '2024-12-01',
            'category': 'Transportasi',
            'amount': 25000,
            'description': 'Taxi'
        },
        {
            'date': '2024-12-02',
            'category': 'Belanja',
            'amount': 150000,
            'description': 'Groceries'
        }
    ]


@pytest.fixture
def sample_income_data():
    """Provide sample income data for tests"""
    return {
        'date': '2024-12-01',
        'source': 'Salary',
        'amount': 5000000,
        'description': 'Monthly salary',
        'is_recurring': False
    }


@pytest.fixture
def sample_budget_data():
    """Provide sample budget data for tests"""
    return {
        'category': 'Makanan & Minuman',
        'monthly_limit': 1000000
    }


@pytest.fixture
def test_db():
    """Create a temporary database for testing"""
    # Setup - create temporary database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db_path = temp_db.name
    temp_db.close()
    
    # Create tables
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    
    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            payment_method TEXT DEFAULT 'Cash',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Create budgets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE,
            monthly_limit REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create incomes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            is_recurring INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create recurring expenses table
    cursor.execute('''
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
    ''')
    
    # Create expense tags table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expense_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY (expense_id) REFERENCES expenses(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Provide the database path to tests
    yield temp_db_path
    
    # Teardown - delete temporary database
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


@pytest.fixture
def db_connection(test_db):
    """Create database connection for testing"""
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_test_expense(conn, expense_data):
    """Helper to insert test expense"""
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO expenses (date, category, amount, description, payment_method) 
           VALUES (?, ?, ?, ?, ?)""",
        (expense_data['date'], expense_data['category'], 
         expense_data['amount'], expense_data.get('description', ''),
         expense_data.get('payment_method', 'Cash'))
    )
    conn.commit()
    return cursor.lastrowid


def create_test_income(conn, income_data):
    """Helper to insert test income"""
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO incomes (date, source, amount, description, is_recurring) 
           VALUES (?, ?, ?, ?, ?)""",
        (income_data['date'], income_data['source'],
         income_data['amount'], income_data.get('description', ''),
         income_data.get('is_recurring', 0))
    )
    conn.commit()
    return cursor.lastrowid


def create_test_budget(conn, budget_data):
    """Helper to insert test budget"""
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO budgets (category, monthly_limit) 
           VALUES (?, ?)""",
        (budget_data['category'], budget_data['monthly_limit'])
    )
    conn.commit()
    return cursor.lastrowid


def get_all_expenses(conn):
    """Helper to get all expenses"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    return cursor.fetchall()


def clear_expenses(conn):
    """Helper to clear all expenses"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses")
    conn.commit()


def clear_incomes(conn):
    """Helper to clear all incomes"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM incomes")
    conn.commit()


def clear_budgets(conn):
    """Helper to clear all budgets"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets")
    conn.commit()