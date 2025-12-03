#project portofolio/junior project/daily-expense-tracker/services/database_service.py

"""
Database Service
Handles database connections and operations for the daily-expense-tracker application
"""

import logging
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Any

from models.expense_model import Expense
from services.database_service import DatabaseService
from utils.validation import validate_date, validate_amount, parse_amount

logger = logging.getLogger(__name__)

class ExpenseService:
    """Business logic layer for expense operations"""
    
    def __init__(self):
        self.db_service = DatabaseService()
    
    def create_expense(self, date_str: str, category: str, 
                      amount_str: str, description: str = "") -> Dict[str, Any]:
        """Create a new expense with validation"""
        try:
            # Validate inputs
            if not validate_date(date_str):
                return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
            
            if not validate_amount(amount_str):
                return {"success": False, "error": "Invalid amount format"}
            
            # Parse inputs
            expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            amount = parse_amount(amount_str)
            
            if amount <= 0:
                return {"success": False, "error": "Amount must be greater than 0"}
            
            # Create expense object
            expense = Expense(
                date=expense_date,
                category=category,
                amount=amount,
                description=description
            )
            
            # Save to database
            expense_id = self.db_service.add_expense(expense)
            
            return {
                "success": True,
                "expense_id": expense_id,
                "message": f"Expense added successfully (ID: {expense_id})"
            }
            
        except ValueError as e:
            return {"success": False, "error": f"Validation error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error creating expense: {e}")
            return {"success": False, "error": f"System error: {str(e)}"}
    
    def get_expense_history(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get expense history with optional filters"""
        if filters is None:
            filters = {}
        
        month = filters.get('month')
        year = filters.get('year')
        category = filters.get('category')
        
        return self.db_service.get_expenses(month=month, year=year, category=category)
    
    def get_monthly_analysis(self, year: int, month: int) -> Dict[str, Any]:
        """Get detailed monthly analysis"""
        summary = self.db_service.get_monthly_summary(year, month)
        
        # Calculate percentages
        total = summary.get('total_expenses', 0)
        if total > 0:
            for item in summary.get('category_breakdown', []):
                item['percentage'] = (item['total'] / total) * 100
        
        return summary
    
    def validate_expense_data(self, date_str: str, amount_str: str, 
                            category: str = "") -> Dict[str, Any]:
        """Validate expense data before processing"""
        errors = []
        
        if not validate_date(date_str):
            errors.append("Invalid date format. Use YYYY-MM-DD")
        
        if not validate_amount(amount_str):
            errors.append("Invalid amount format")
        else:
            amount = parse_amount(amount_str)
            if amount <= 0:
                errors.append("Amount must be greater than 0")
        
        if not category or category.strip() == "":
            errors.append("Category is required")
        
        if errors:
            return {"valid": False, "errors": errors}
        
        return {"valid": True, "errors": []}
    
    def get_available_categories(self) -> List[str]:
        """Get list of available categories"""
        categories = self.db_service.get_categories()
        return [cat['name'] for cat in categories] if categories else []
    
    def delete_expense(self, expense_id: int) -> Dict[str, Any]:
        """Delete an expense"""
        try:
            success = self.db_service.delete_expense(expense_id)
            if success:
                return {"success": True, "message": f"Expense {expense_id} deleted"}
            else:
                return {"success": False, "error": f"Expense {expense_id} not found"}
        except Exception as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            return {"success": False, "error": f"Error deleting expense: {str(e)}"}
    
    def update_expense(self, expense_id: int, date_str: str, category: str,
                      amount_str: str, description: str = "") -> Dict[str, Any]:
        """Update an existing expense"""
        try:
            # Validate inputs
            validation = self.validate_expense_data(date_str, amount_str, category)
            if not validation['valid']:
                return {"success": False, "error": validation['errors'][0]}
            
            # Parse inputs
            expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            amount = parse_amount(amount_str)
            
            # Create expense object
            expense = Expense(
                date=expense_date,
                category=category,
                amount=amount,
                description=description
            )
            
            # Update in database
            success = self.db_service.update_expense(expense_id, expense)
            
            if success:
                return {"success": True, "message": f"Expense {expense_id} updated"}
            else:
                return {"success": False, "error": f"Expense {expense_id} not found"}
                
        except ValueError as e:
            return {"success": False, "error": f"Validation error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error updating expense {expense_id}: {e}")
            return {"success": False, "error": f"System error: {str(e)}"}


def test_expense_service():
    """Test the ExpenseService class"""
    print("Testing Expense Service...")
    
    service = ExpenseService()
    
    print("\n1. Testing validation...")
    validation = service.validate_expense_data("2024-01-15", "50000", "Food")
    print(f"   Validation result: {validation['valid']}")
    
    print("\n2. Testing available categories...")
    categories = service.get_available_categories()
    print(f"   Available categories: {len(categories)} found")
    
    print("\n3. Testing expense history...")
    history = service.get_expense_history()
    print(f"   Expense history: {len(history)} expenses")
    
    print("\n4. Testing monthly analysis...")
    current_year = datetime.now().year
    current_month = datetime.now().month
    analysis = service.get_monthly_analysis(current_year, current_month)
    print(f"   Monthly total: Rp {analysis.get('total_expenses', 0):,.0f}")
    
    print("\nExpense service test completed!")


if __name__ == "__main__":
    test_expense_service()