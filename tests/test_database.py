#  tests/test_database.py

"""
Unit tests for database service and models
"""

# services/database_service.py
"""
Database Service - Fixed Version
"""

import sqlite3
import os
from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any


class DatabaseService:
    def __init__(self, db_name: str = "expenses.db"):
        """Initialize database service"""
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        self.db_path = os.path.join(data_dir, db_name)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                category VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) UNIQUE NOT NULL,
                budget_limit DECIMAL(10,2) DEFAULT NULL,
                description TEXT
            )
        """)
        
        # Insert default categories
        default_categories = [
            ('Makanan & Minuman', None, 'Pengeluaran untuk makanan dan minuman'),
            ('Transportasi', None, 'Biaya transportasi'),
            ('Belanja', None, 'Belanja kebutuhan sehari-hari'),
            ('Hiburan', None, 'Pengeluaran hiburan dan rekreasi'),
            ('Kesehatan', None, 'Biaya kesehatan dan obat-obatan'),
            ('Pendidikan', None, 'Biaya pendidikan dan kursus'),
            ('Tagihan', None, 'Pembayaran tagihan rutin'),
            ('Lain-lain', None, 'Pengeluaran lainnya'),
        ]
        
        for category_name, budget_limit, description in default_categories:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name, budget_limit, description) VALUES (?, ?, ?)",
                (category_name, budget_limit, description)
            )
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def add_expense(self, expense) -> int:
        """Add new expense to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert date to string if it's a date object
        if isinstance(expense.date, date):
            date_str = expense.date.isoformat()
        else:
            date_str = expense.date
        
        # Convert amount to float if it's a Decimal
        if isinstance(expense.amount, Decimal):
            amount_float = float(expense.amount)
        else:
            amount_float = expense.amount
        
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
    
    def get_expense(self, expense_id: int):
        """Get expense by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None
    
    def get_all_expenses(self, limit=None, offset=None):
        """Get all expenses with optional pagination"""
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM expenses ORDER BY date DESC, created_at DESC"
        params = []
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
            if offset is not None:
                query += " OFFSET ?"
                params.append(offset)
        cursor.execute(query, params)
        expenses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return expenses
    
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
    
    def get_expenses_by_category(self, category: str):
        """Get expenses by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM expenses
            WHERE category = ?
            ORDER BY date DESC, created_at DESC
            """,
            (category,),
        )
        expenses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return expenses
    
    def get_expenses_by_month(self, year: int, month: int):
        """Get expenses by month"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM expenses
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            ORDER BY date DESC, created_at DESC
            """,
            (str(year), f"{month:02d}"),
        )
        expenses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return expenses
    
    def update_expense(self, expense_id: int, expense):
        """Update existing expense"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert date
        if isinstance(expense.date, date):
            date_str = expense.date.isoformat()
        else:
            date_str = expense.date
        
        # Convert amount
        if isinstance(expense.amount, Decimal):
            amount_float = float(expense.amount)
        else:
            amount_float = expense.amount
        
        cursor.execute(
            """
            UPDATE expenses
            SET date = ?, category = ?, amount = ?, description = ?
            WHERE id = ?
            """,
            (date_str, expense.category, amount_float, expense.description, expense_id),
        )
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    
    def delete_expense(self, expense_id: int):
        """Delete expense"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    
    def get_all_categories(self):
        """Get all categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY name")
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_categories(self):
        """Get all categories (alias for get_all_categories)"""
        return self.get_all_categories()
    
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
            "year": year,
            "month": month,
            "total_expenses": total,
            "category_breakdown": by_category,
        }
    
    def get_yearly_summary(self, year: int):
        """Get yearly expense summary"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get yearly total and count
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count
            FROM expenses
            WHERE strftime('%Y', date) = ?
            """,
            (str(year),),
        )
        year_row = cursor.fetchone()
        total = year_row["total"] if year_row else 0
        count = year_row["count"] if year_row else 0
        
        conn.close()
        return {
            "year": year,
            "total_expenses": total,
            "transaction_count": count,
        }


# Simple test to verify the class works
if __name__ == "__main__":
    print("Testing DatabaseService...")
    service = DatabaseService()
    
    # Test categories
    categories = service.get_categories()
    print(f"Found {len(categories)} categories")
    
    # Test creating a simple expense
    class SimpleExpense:
        def __init__(self):
            self.date = date.today()
            self.category = "Test"
            self.amount = Decimal("10000")
            self.description = "Test expense"
    
    try:
        expense_id = service.add_expense(SimpleExpense())
        print(f"Added test expense with ID: {expense_id}")
        
        # Get it back
        expense = service.get_expense(expense_id)
        if expense:
            print(f"Retrieved expense: {expense['description']}")
        
        # Delete it
        if service.delete_expense(expense_id):
            print(f"Deleted test expense")
    except Exception as e:
        print(f"Error: {e}")
    
    print("DatabaseService test complete!")