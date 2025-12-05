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