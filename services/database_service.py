#project portofolio/junior project/daily-expense-tracker/services/database_service.py

"""
Database Service
Handles database connections and operations for the daily-expense-tracker application
"""

import sqlite3
from datetime import date
from decimal import Decimal
import logging

try:
    from config.database_config import DatabaseConfig
    from models.expense_model import Expense
    from models.category_model import Category
except ImportError:
    print("Warning: Some imports failed")
    
    class Expense:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    class Category:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    from config.database_config import DatabaseConfig

logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self):
        self.db_config = DatabaseConfig()
    
    def add_expense(self, expense: Expense) -> int:

    def add_batch_expenses(self, expenses: List[Expense]) -> List[int]:
        """Add multiple expenses in batch"""
        conn = self.db_config.get_connection()
        cursor = conn.cursor()
        expense_ids = []
        
        try:
            for expense in expenses:
                cursor.execute('''
                    INSERT INTO expenses (date, category, amount, description)
                    VALUES (?, ?, ?, ?)
                ''', (expense.date, expense.category, float(expense.amount), expense.description))
                expense_ids.append(cursor.lastrowid)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        
        return expense_ids
        """Add new expense to database"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO expenses (date, category, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (
                expense.date.isoformat() if isinstance(expense.date, date) else expense.date,
                expense.category,
                float(expense.amount) if isinstance(expense.amount, Decimal) else expense.amount,
                expense.description
            ))
            
            expense_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Expense added with ID: {expense_id}")
            return expense_id
            
        except sqlite3.Error as e:
            logger.error(f"Error adding expense: {e}")
            raise
    
    def get_expense(self, expense_id: int):
        """Get expense by ID"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Error getting expense {expense_id}: {e}")
            return None
    
    def get_all_expenses(self, limit=None, offset=None):
        """Get all expenses with optional pagination"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM expenses ORDER BY date DESC, created_at DESC"
            
            if limit is not None:
                query += f" LIMIT {limit}"
                if offset is not None:
                    query += f" OFFSET {offset}"
            
            cursor.execute(query)
            expenses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return expenses
            
        except sqlite3.Error as e:
            logger.error(f"Error getting all expenses: {e}")
            return []
    
    def get_expenses(self, month: int = None, year: int = None, category: str = None):
        """Get expenses with optional filters"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM expenses WHERE 1=1"
            params = []
            
            if month and year:
                query += " AND strftime('%Y', date) = ? AND strftime('%m', date) = ?"
                params.extend([str(year), f"{month:02d}"])
            elif year:
                query += " AND strftime('%Y', date) = ?"
                params.append(str(year))
                
            if category:
                query += " AND category = ?"
                params.append(category)
                
            query += " ORDER BY date DESC, created_at DESC"
            
            cursor.execute(query, params)
            expenses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return expenses
            
        except sqlite3.Error as e:
            logger.error(f"Error getting filtered expenses: {e}")
            return []
    
    def get_expenses_by_date_range(self, start_date: date, end_date: date):
        """Get expenses within date range"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM expenses 
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, created_at DESC
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            expenses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return expenses
            
        except sqlite3.Error as e:
            logger.error(f"Error getting expenses by date range: {e}")
            return []
    
    def get_expenses_by_category(self, category: str):
        """Get expenses by category"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM expenses 
                WHERE category = ?
                ORDER BY date DESC, created_at DESC
            ''', (category,))
            
            expenses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return expenses
            
        except sqlite3.Error as e:
            logger.error(f"Error getting expenses by category {category}: {e}")
            return []
    
    def get_expenses_by_month(self, year: int, month: int):
        """Get expenses by month"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM expenses 
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                ORDER BY date DESC, created_at DESC
            ''', (str(year), f"{month:02d}"))
            
            expenses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return expenses
            
        except sqlite3.Error as e:
            logger.error(f"Error getting expenses for {month}/{year}: {e}")
            return []
    
    def update_expense(self, expense_id: int, expense: Expense):
        """Update existing expense"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE expenses 
                SET date = ?, category = ?, amount = ?, description = ?
                WHERE id = ?
            ''', (
                expense.date.isoformat() if isinstance(expense.date, date) else expense.date,
                expense.category,
                float(expense.amount) if isinstance(expense.amount, Decimal) else expense.amount,
                expense.description,
                expense_id
            ))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            success = rows_affected > 0
            if success:
                logger.info(f"Expense {expense_id} updated successfully")
            else:
                logger.warning(f"Expense {expense_id} not found for update")
            
            return success
            
        except sqlite3.Error as e:
            logger.error(f"Error updating expense {expense_id}: {e}")
            return False
    
    def delete_expense(self, expense_id: int):
        """Delete expense"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            success = rows_affected > 0
            if success:
                logger.info(f"Expense {expense_id} deleted successfully")
            else:
                logger.warning(f"Expense {expense_id} not found for deletion")
            
            return success
            
        except sqlite3.Error as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            return False
    
    def get_all_categories(self):
        """Get all categories"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM categories ORDER BY name')
            categories = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return categories
            
        except sqlite3.Error as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    def get_categories(self):
        """Get all categories (alias for get_all_categories)"""
        return self.get_all_categories()
    
    def add_category(self, category: Category) -> int:
        """Add new category"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO categories (name, budget_limit, description)
                VALUES (?, ?, ?)
            ''', (
                category.name,
                float(category.budget_limit) if category.budget_limit else None,
                category.description
            ))
            
            category_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Category added: {category.name} (ID: {category_id})")
            return category_id
            
        except sqlite3.Error as e:
            logger.error(f"Error adding category {category.name}: {e}")
            raise
    
    def get_monthly_summary(self, year: int, month: int):
        """Get monthly expense summary"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total
                FROM expenses
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            ''', (str(year), f"{month:02d}"))
            
            total_row = cursor.fetchone()
            total = total_row['total'] if total_row else 0
            
            cursor.execute('''
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                GROUP BY category
                ORDER BY total DESC
            ''', (str(year), f"{month:02d}"))
            
            by_category = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT date, SUM(amount) as daily_total
                FROM expenses
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                GROUP BY date
                ORDER BY date
            ''', (str(year), f"{month:02d}"))
            
            daily_expenses = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'year': year,
                'month': month,
                'total_expenses': total,
                'category_breakdown': by_category,
                'daily_expenses': daily_expenses,
                'transaction_count': len(self.get_expenses_by_month(year, month))
            }
            
        except sqlite3.Error as e:
            logger.error(f"Error getting monthly summary for {month}/{year}: {e}")
            return {
                'year': year,
                'month': month,
                'total_expenses': 0,
                'category_breakdown': [],
                'daily_expenses': [],
                'transaction_count': 0
            }
    
    def get_category_summary(self, category: str):
        """Get summary for specific category"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count
                FROM expenses
                WHERE category = ?
            ''', (category,))
            
            category_row = cursor.fetchone()
            total = category_row['total'] if category_row else 0
            count = category_row['count'] if category_row else 0
            
            cursor.execute('''
                SELECT 
                    strftime('%Y', date) as year,
                    strftime('%m', date) as month,
                    SUM(amount) as monthly_total,
                    COUNT(*) as monthly_count
                FROM expenses
                WHERE category = ?
                GROUP BY strftime('%Y', date), strftime('%m', date)
                ORDER BY year DESC, month DESC
            ''', (category,))
            
            monthly_breakdown = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'category': category,
                'total_amount': total,
                'transaction_count': count,
                'monthly_breakdown': monthly_breakdown
            }
            
        except sqlite3.Error as e:
            logger.error(f"Error getting category summary for {category}: {e}")
            return {
                'category': category,
                'total_amount': 0,
                'transaction_count': 0,
                'monthly_breakdown': []
            }
    
    def get_yearly_summary(self, year: int):
        """Get yearly expense summary"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count
                FROM expenses
                WHERE strftime('%Y', date) = ?
            ''', (str(year),))
            
            year_row = cursor.fetchone()
            total = year_row['total'] if year_row else 0
            count = year_row['count'] if year_row else 0
            
            cursor.execute('''
                SELECT 
                    strftime('%m', date) as month,
                    SUM(amount) as monthly_total,
                    COUNT(*) as monthly_count
                FROM expenses
                WHERE strftime('%Y', date) = ?
                GROUP BY strftime('%m', date)
                ORDER BY month
            ''', (str(year),))
            
            monthly_breakdown = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE strftime('%Y', date) = ?
                GROUP BY category
                ORDER BY total DESC
            ''', (str(year),))
            
            category_breakdown = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'year': year,
                'total_expenses': total,
                'transaction_count': count,
                'monthly_breakdown': monthly_breakdown,
                'category_breakdown': category_breakdown
            }
            
        except sqlite3.Error as e:
            logger.error(f"Error getting yearly summary for {year}: {e}")
            return {
                'year': year,
                'total_expenses': 0,
                'transaction_count': 0,
                'monthly_breakdown': [],
                'category_breakdown': []
            }


def test_database_service():
    """Test database service functionality"""
    print("Testing Database Service...")
    
    service = DatabaseService()
    
    print("\n1. Testing categories...")
    categories = service.get_all_categories()
    print(f"   Found {len(categories)} categories:")
    for cat in categories[:5]:
        print(f"   - {cat['name']}")
    
    print("\n2. Testing expense operations...")
    
    from datetime import date
    from decimal import Decimal
    
    test_expense = Expense(
        date=date.today(),
        category="Food",
        amount=Decimal("25000"),
        description="Test expense"
    )
    
    try:
        expense_id = service.add_expense(test_expense)
        print(f"   Added test expense with ID: {expense_id}")
        
        expense = service.get_expense(expense_id)
        if expense:
            print(f"   Retrieved expense: {expense['description']} - Rp {expense['amount']}")
        
        all_expenses = service.get_all_expenses(limit=5)
        print(f"   Total expenses in DB: {len(all_expenses)}")
        
        today = date.today()
        monthly_summary = service.get_monthly_summary(today.year, today.month)
        print(f"   Monthly total: Rp {monthly_summary['total_expenses']}")
        
        if service.delete_expense(expense_id):
            print(f"   Deleted test expense {expense_id}")
        else:
            print(f"   Failed to delete test expense {expense_id}")
            
    except Exception as e:
        print(f"   Error during test: {e}")
    
    print("\nDatabase service test completed!")


if __name__ == "__main__":
    test_database_service()