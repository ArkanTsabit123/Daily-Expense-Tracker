#  tests/test_database.py

"""
Unit tests for database service and models
"""

import pytest
import sys
from pathlib import Path
from datetime import date
from decimal import Decimal

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.expense_model import Expense
from models.category_model import Category
from services.database_service import DatabaseService


@pytest.fixture
def db_service():
    """Create a database service for testing"""
    return DatabaseService()


@pytest.fixture
def sample_expense():
    """Create a sample expense for testing"""
    return Expense(
        date=date(2024, 1, 15),
        category="Test Category",
        amount=Decimal("50000"),
        description="Test expense for unit testing"
    )


class TestDatabaseService:
    """Test cases for DatabaseService"""
    
    def test_add_expense(self, db_service, sample_expense):
        """Test adding an expense"""
        expense_id = db_service.add_expense(sample_expense)
        assert expense_id > 0, "Expense ID should be positive"
        
        # Clean up
        db_service.delete_expense(expense_id)
    
    def test_get_expense(self, db_service, sample_expense):
        """Test retrieving an expense"""
        expense_id = db_service.add_expense(sample_expense)
        
        expense = db_service.get_expense(expense_id)
        assert expense is not None, "Should retrieve the expense"
        assert expense['description'] == sample_expense.description
        
        # Clean up
        db_service.delete_expense(expense_id)
    
    def test_get_all_expenses(self, db_service):
        """Test getting all expenses"""
        expenses = db_service.get_all_expenses(limit=5)
        assert isinstance(expenses, list), "Should return a list"
    
    def test_get_expenses_method(self, db_service):
        """Test the get_expenses method (with filters)"""
        expenses = db_service.get_expenses()
        assert isinstance(expenses, list), "Should return a list"
    
    def test_get_expenses_by_category(self, db_service, sample_expense):
        """Test filtering by category"""
        expense_id = db_service.add_expense(sample_expense)
        
        expenses = db_service.get_expenses_by_category("Test Category")
        assert isinstance(expenses, list), "Should return a list"
        
        # Clean up
        db_service.delete_expense(expense_id)
    
    def test_get_expenses_by_month(self, db_service):
        """Test filtering by month"""
        expenses = db_service.get_expenses_by_month(2024, 1)
        assert isinstance(expenses, list), "Should return a list"
    
    def test_update_expense(self, db_service, sample_expense):
        """Test updating an expense"""
        expense_id = db_service.add_expense(sample_expense)
        
        updated_expense = Expense(
            date=date(2024, 1, 16),
            category="Updated Category",
            amount=Decimal("75000"),
            description="Updated description"
        )
        
        success = db_service.update_expense(expense_id, updated_expense)
        assert success is True, "Update should succeed"
        
        # Clean up
        db_service.delete_expense(expense_id)
    
    def test_delete_expense(self, db_service, sample_expense):
        """Test deleting an expense"""
        expense_id = db_service.add_expense(sample_expense)
        
        success = db_service.delete_expense(expense_id)
        assert success is True, "Delete should succeed"
    
    def test_get_categories(self, db_service):
        """Test getting categories"""
        categories = db_service.get_categories()
        assert isinstance(categories, list), "Should return a list"
    
    def test_get_monthly_summary(self, db_service):
        """Test monthly summary"""
        summary = db_service.get_monthly_summary(2024, 1)
        assert isinstance(summary, dict), "Should return a dictionary"
        assert 'total_expenses' in summary
        assert 'category_breakdown' in summary
    
    def test_get_yearly_summary(self, db_service):
        """Test yearly summary"""
        summary = db_service.get_yearly_summary(2024)
        assert isinstance(summary, dict), "Should return a dictionary"
        assert 'total_expenses' in summary
        assert 'monthly_breakdown' in summary


def test_expense_model():
    """Test Expense model"""
    expense = Expense(
        date=date(2024, 1, 15),
        category="Food",
        amount=Decimal("25000"),
        description="Lunch"
    )
    
    assert expense.date == date(2024, 1, 15)
    assert expense.category == "Food"
    assert expense.amount == Decimal("25000")
    assert expense.description == "Lunch"


def test_category_model():
    """Test Category model"""
    category = Category(
        name="Transportation",
        budget_limit=Decimal("500000"),
        description="Transport expenses"
    )
    
    assert category.name == "Transportation"
    assert category.budget_limit == Decimal("500000")
    assert category.description == "Transport expenses"


if __name__ == "__main__":
    # Run tests when file is executed directly
    print("Running database tests...")
    
    service = DatabaseService()
    test_service = TestDatabaseService()
    
    # Run some basic tests
    try:
        categories = service.get_categories()
        print(f"✓ Categories test: {len(categories)} categories found")
        
        expenses = service.get_all_expenses(limit=2)
        print(f"✓ Expenses test: {len(expenses)} expenses found")
        
        print("✓ All tests passed!")
    except Exception as e:
        print(f"✗ Test failed: {e}")