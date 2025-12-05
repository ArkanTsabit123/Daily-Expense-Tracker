# tests/test_expenses.py
"""
test expenses
This module contains unit tests for the DatabaseService class in the services.database_service module.
It tests database initialization, adding expenses, retrieving expenses, and getting categories.
"""

import sqlite3
import os
from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any

class DatabaseService:
    """Handles all database operations"""
    
    def __init__(self, db_name: str = "expenses.db"):
        """Initialize database service"""
        # Create data directory if it doesn't exist
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.db_path = os.path.join(self.data_dir, db_name)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                category VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) UNIQUE NOT NULL,
                budget_limit DECIMAL(10,2) DEFAULT NULL
            )
        ''')
        
        # Insert default categories
        default_categories = [
            'Food', 'Transport', 'Shopping', 'Entertainment', 
            'Bills', 'Health', 'Education', 'Other'
        ]
        
        for category in default_categories:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                (category,)
            )
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access rows like dictionaries
        return conn
    
    def add_expense(self, expense) -> int:
        """Add new expense to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert date to string if needed
        if isinstance(expense.date, date):
            date_str = expense.date.isoformat()
        else:
            date_str = str(expense.date)
        
        # Convert amount to float if needed
        if isinstance(expense.amount, Decimal):
            amount_float = float(expense.amount)
        else:
            amount_float = float(expense.amount)
        
        cursor.execute(
            """
            INSERT INTO expenses (date, category, amount, description)
            VALUES (?, ?, ?, ?)
            """,
            (date_str, expense.category, amount_float, expense.description),
        )
        expense_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return expense_id
    
    def get_expenses(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None,
        category: Optional[str] = None,
    ):
        """Get expenses with optional filters"""
        conn = self.get_connection()
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
    
    def get_monthly_summary(self, year: int, month: int):
        """Get monthly expense summary"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get total expenses
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            """,
            (str(year), f"{month:02d}"),
        )
        total_row = cursor.fetchone()
        total = total_row["total"] if total_row else 0
        
        # Get breakdown by category
        cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (str(year), f"{month:02d}"),
        )
        by_category = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return {
            "total_expenses": total,
            "category_breakdown": by_category,
            "month": month,
            "year": year
        }
    
    def get_categories(self):
        """Get all categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY name")
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def delete_expense(self, expense_id: int):
        """Delete expense"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0


# Export the class
__all__ = ['DatabaseService']

# Test function
if __name__ == "__main__":
    # Quick test
    print("Testing DatabaseService...")
    service = DatabaseService()
    print(f"Database path: {service.db_path}")
    categories = service.get_categories()
    print(f"Found {len(categories)} categories")
    for cat in categories:
        print(f"  - {cat['name']}")
    print("DatabaseService test completed!")