#tests/test_expenses.py

"""
Unit tests for ExpenseService class
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.expense_service import ExpenseService


@pytest.fixture
def expense_service():
    """Create an expense service for testing"""
    return ExpenseService()


class TestExpenseService:
    """Test cases for ExpenseService"""
    
    def test_validate_expense_data_valid(self, expense_service):
        """Test validation with valid data"""
        result = expense_service.validate_expense_data(
            "2024-01-15", 
            "50000", 
            "Food"
        )
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_expense_data_invalid_date(self, expense_service):
        """Test validation with invalid date"""
        result = expense_service.validate_expense_data(
            "2024-13-15",  # Invalid month
            "50000", 
            "Food"
        )
        assert result['valid'] is False
        assert len(result['errors']) > 0
    
    def test_validate_expense_data_invalid_amount(self, expense_service):
        """Test validation with invalid amount"""
        result = expense_service.validate_expense_data(
            "2024-01-15", 
            "not-a-number", 
            "Food"
        )
        assert result['valid'] is False
        assert len(result['errors']) > 0
    
    def test_validate_expense_data_negative_amount(self, expense_service):
        """Test validation with negative amount"""
        result = expense_service.validate_expense_data(
            "2024-01-15", 
            "-10000", 
            "Food"
        )
        assert result['valid'] is False
        assert len(result['errors']) > 0
    
    def test_validate_expense_data_missing_category(self, expense_service):
        """Test validation with missing category"""
        result = expense_service.validate_expense_data(
            "2024-01-15", 
            "50000", 
            ""
        )
        assert result['valid'] is False
        assert len(result['errors']) > 0
    
    def test_create_expense_success(self, expense_service):
        """Test successful expense creation"""
        result = expense_service.create_expense(
            "2024-01-15",
            "Test Category",
            "25000",
            "Test expense"
        )
        
        assert result['success'] is True
        assert 'expense_id' in result
        
        # Clean up
        if result['success']:
            expense_service.delete_expense(result['expense_id'])
    
    def test_create_expense_invalid_date(self, expense_service):
        """Test expense creation with invalid date"""
        result = expense_service.create_expense(
            "2024-13-15",  # Invalid month
            "Test Category",
            "25000",
            "Test expense"
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_get_expense_history(self, expense_service):
        """Test getting expense history"""
        history = expense_service.get_expense_history()
        assert isinstance(history, list)
    
    def test_get_expense_history_with_filters(self, expense_service):
        """Test getting expense history with filters"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        filters = {'year': current_year, 'month': current_month}
        history = expense_service.get_expense_history(filters)
        
        assert isinstance(history, list)
    
    def test_get_monthly_analysis(self, expense_service):
        """Test monthly analysis"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        analysis = expense_service.get_monthly_analysis(current_year, current_month)
        
        assert isinstance(analysis, dict)
        assert 'total_expenses' in analysis
        assert 'category_breakdown' in analysis
    
    def test_get_available_categories(self, expense_service):
        """Test getting available categories"""
        categories = expense_service.get_available_categories()
        assert isinstance(categories, list)
    
    def test_delete_expense_not_found(self, expense_service):
        """Test deleting non-existent expense"""
        result = expense_service.delete_expense(999999)  # Non-existent ID
        assert result['success'] is False


def test_expense_service_integration():
    """Integration test for ExpenseService"""
    print("Running ExpenseService integration tests...")
    
    service = ExpenseService()
    
    # Test 1: Get categories
    categories = service.get_available_categories()
    print(f"✓ Available categories: {len(categories)}")
    assert isinstance(categories, list)
    
    # Test 2: Validate data
    validation = service.validate_expense_data("2024-01-15", "50000", "Food")
    print(f"✓ Validation test: {validation['valid']}")
    assert validation['valid'] is True
    
    # Test 3: Get history
    history = service.get_expense_history()
    print(f"✓ Expense history: {len(history)} expenses")
    assert isinstance(history, list)
    
    # Test 4: Monthly analysis
    current_year = datetime.now().year
    current_month = datetime.now().month
    analysis = service.get_monthly_analysis(current_year, current_month)
    print(f"✓ Monthly analysis: Rp {analysis.get('total_expenses', 0):,.0f}")
    assert isinstance(analysis, dict)
    
    print("✓ All integration tests passed!")


if __name__ == "__main__":
    test_expense_service_integration()