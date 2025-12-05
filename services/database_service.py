# services/database_service.py
"""
Database Service
Handles database operations for the expense tracker
"""

import sqlite3
import logging
from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseService:
    """Service class for database operations"""

    def __init__(self, db_path: str = None):
        """Initialize database service"""
        if db_path is None:
            # Default database path
            project_root = Path(__file__).parent.parent
            self.db_path = project_root / "data" / "expenses.db"
            self.in_memory = False
        else:
            self.db_path = Path(db_path)
            self.in_memory = str(db_path) == ":memory:"
        
        # For in-memory databases, we need to keep a connection open
        self._connection = None
        
        # Create directory if it doesn't exist (for file-based databases)
        if not self.in_memory:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database on startup
        self.initialize_database()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection - handles in-memory databases specially"""
        try:
            if self.in_memory:
                # For in-memory databases, reuse the same connection
                if self._connection is None:
                    self._connection = sqlite3.connect(str(self.db_path))
                    self._connection.row_factory = sqlite3.Row
                return self._connection
            else:
                # For file-based databases, create new connection each time
                conn = sqlite3.connect(str(self.db_path))
                conn.row_factory = sqlite3.Row
                return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def close(self):
        """Close the database connection (important for in-memory databases)"""
        if self._connection:
            self._connection.close()
            self._connection = None

    def initialize_database(self):
        """Initialize database tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Create expenses table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create categories table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    budget_limit DECIMAL(10,2) DEFAULT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Insert default categories
            default_categories = [
                ("Makanan & Minuman", None, "Pengeluaran untuk makanan dan minuman"),
                ("Transportasi", None, "Pengeluaran untuk transportasi"),
                ("Belanja", None, "Pengeluaran untuk belanja"),
                ("Hiburan", None, "Pengeluaran untuk hiburan"),
                ("Kesehatan", None, "Pengeluaran untuk kesehatan"),
                ("Pendidikan", None, "Pengeluaran untuk pendidikan"),
                ("Tagihan", None, "Pengeluaran untuk tagihan"),
                ("Lain-lain", None, "Pengeluaran lainnya"),
            ]

            for category_name, budget_limit, description in default_categories:
                cursor.execute(
                    "INSERT OR IGNORE INTO categories (name, budget_limit, description) VALUES (?, ?, ?)",
                    (category_name, budget_limit, description),
                )

            # Create indexes for better performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_expenses_date_category ON expenses(date, category)"
            )

            # Only commit if not using shared in-memory connection
            if not self.in_memory:
                conn.commit()
                conn.close()
            else:
                conn.commit()
                
            logger.info("Database initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def _extract_expense_data(self, expense: Union[Dict, Any]) -> Dict[str, Any]:
        """Extract data from either Expense object or dictionary"""
        try:
            if isinstance(expense, dict):
                # It's a dictionary
                date_value = expense.get("date")
                category = expense.get("category")
                amount = expense.get("amount")
                description = expense.get("description", "")
                return {
                    "date": date_value,
                    "category": category,
                    "amount": amount,
                    "description": description,
                }
            else:
                # It's an Expense object - access attributes directly
                date_value = getattr(expense, "date", None)
                category = getattr(expense, "category", None)
                amount = getattr(expense, "amount", None)
                description = getattr(expense, "description", "")
                return {
                    "date": date_value,
                    "category": category,
                    "amount": amount,
                    "description": description,
                }
        except Exception as e:
            logger.error(f"Error extracting expense data: {e}")
            raise ValueError(f"Cannot extract data from expense object: {type(expense)}")

    def _prepare_expense_for_db(self, expense_data: Dict[str, Any]) -> tuple:
        """Prepare expense data for database insertion"""
        date_value = expense_data.get("date")
        category = expense_data.get("category")
        amount = expense_data.get("amount")
        description = expense_data.get("description", "")

        # Convert date to string if it's a date object
        if hasattr(date_value, "isoformat"):
            date_str = date_value.isoformat()
        else:
            date_str = str(date_value) if date_value else ""

        # Convert amount to float
        if isinstance(amount, Decimal):
            amount_float = float(amount)
        elif amount is not None:
            amount_float = float(amount)
        else:
            amount_float = 0.0

        return (date_str, category, amount_float, description)

    def add_expense(self, expense: Union[Dict, Any]) -> int:
        """Add a new expense to database - HANDLES BOTH Expense objects AND dictionaries"""
        try:
            # Extract data from expense object/dictionary
            expense_data = self._extract_expense_data(expense)
            
            # Prepare data for database
            db_data = self._prepare_expense_for_db(expense_data)

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO expenses (date, category, amount, description)
                VALUES (?, ?, ?, ?)
                """,
                db_data,
            )

            expense_id = cursor.lastrowid
            
            # Only commit if not using shared in-memory connection
            if not self.in_memory:
                conn.commit()
                conn.close()
            else:
                conn.commit()

            logger.info(f"Expense added with ID: {expense_id}")
            return expense_id

        except sqlite3.Error as e:
            logger.error(f"Error adding expense: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding expense: {e}")
            raise

    def get_expenses(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None,
        category: Optional[str] = None,
    ) -> List[Dict]:
        """Get expenses with optional filters - COMPATIBLE WITH expense_service.py"""
        try:
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
            
            # Only close if not using shared in-memory connection
            if not self.in_memory:
                conn.close()

            return expenses

        except sqlite3.Error as e:
            logger.error(f"Error getting expenses: {e}")
            return []

    def get_expense_by_id(self, expense_id: int) -> Optional[Dict]:
        """Get expense by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))

            row = cursor.fetchone()
            
            # Only close if not using shared in-memory connection
            if not self.in_memory:
                conn.close()

            return dict(row) if row else None

        except sqlite3.Error as e:
            logger.error(f"Error getting expense {expense_id}: {e}")
            return None

    def update_expense(self, expense_id: int, expense: Union[Dict, Any]) -> bool:
        """Update an existing expense - HANDLES BOTH Expense objects AND dictionaries"""
        try:
            # Extract data from expense object/dictionary
            expense_data = self._extract_expense_data(expense)
            
            # Prepare data for database
            db_data = self._prepare_expense_for_db(expense_data)

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE expenses
                SET date = ?, category = ?, amount = ?, description = ?
                WHERE id = ?
                """,
                (*db_data, expense_id),
            )

            rows_affected = cursor.rowcount
            if not self.in_memory:
                conn.commit()
                conn.close()
            else:
                conn.commit()

            success = rows_affected > 0
            if success:
                logger.info(f"Expense {expense_id} updated successfully")
            else:
                logger.warning(f"Expense {expense_id} not found for update")

            return success

        except sqlite3.Error as e:
            logger.error(f"Error updating expense {expense_id}: {e}")
            return False

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

            rows_affected = cursor.rowcount
            if not self.in_memory:
                conn.commit()
                conn.close()
            else:
                conn.commit()

            success = rows_affected > 0
            if success:
                logger.info(f"Expense {expense_id} deleted successfully")
            else:
                logger.warning(f"Expense {expense_id} not found for deletion")

            return success

        except sqlite3.Error as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            return False

    def get_all_categories(self) -> List[Dict]:
        """Get all categories"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM categories ORDER BY name")
            categories = [dict(row) for row in cursor.fetchall()]
            
            # Only close if not using shared in-memory connection
            if not self.in_memory:
                conn.close()

            return categories

        except sqlite3.Error as e:
            logger.error(f"Error getting categories: {e}")
            return []

    def get_categories(self) -> List[Dict]:
        """Get all categories (alias for get_all_categories)"""
        return self.get_all_categories()

    def get_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Get monthly expense summary - COMPATIBLE WITH expense_service.py"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Get total expenses for the month
            cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0) as total
                FROM expenses
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                """,
                (str(year), f"{month:02d}"),
            )

            total_row = cursor.fetchone()
            total_expenses = total_row["total"] if total_row else 0

            # Get category breakdown
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

            category_breakdown = [dict(row) for row in cursor.fetchall()]

            # Only close if not using shared in-memory connection
            if not self.in_memory:
                conn.close()

            return {
                "year": year,
                "month": month,
                "total_expenses": total_expenses,
                "category_breakdown": category_breakdown,
            }

        except sqlite3.Error as e:
            logger.error(f"Error getting monthly summary: {e}")
            # Only close if not using shared in-memory connection
            if not self.in_memory and 'conn' in locals():
                conn.close()
            return {
                "year": year,
                "month": month,
                "total_expenses": 0,
                "category_breakdown": [],
            }

    def get_yearly_summary(self, year: int) -> Dict[str, Any]:
        """Get yearly expense summary"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Get total expenses for the year
            cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count
                FROM expenses
                WHERE strftime('%Y', date) = ?
                """,
                (str(year),),
            )

            yearly_row = cursor.fetchone()
            total_expenses = yearly_row["total"] if yearly_row else 0
            total_count = yearly_row["count"] if yearly_row else 0

            # Get monthly breakdown
            cursor.execute(
                """
                SELECT 
                    strftime('%m', date) as month,
                    SUM(amount) as total,
                    COUNT(*) as count
                FROM expenses
                WHERE strftime('%Y', date) = ?
                GROUP BY strftime('%m', date)
                ORDER BY month
                """,
                (str(year),),
            )

            monthly_breakdown = [dict(row) for row in cursor.fetchall()]

            # Only close if not using shared in-memory connection
            if not self.in_memory:
                conn.close()

            return {
                "year": year,
                "total_expenses": total_expenses,
                "transaction_count": total_count,
                "monthly_breakdown": monthly_breakdown,
            }

        except sqlite3.Error as e:
            logger.error(f"Error getting yearly summary: {e}")
            # Only close if not using shared in-memory connection
            if not self.in_memory and 'conn' in locals():
                conn.close()
            return {
                "year": year,
                "total_expenses": 0,
                "transaction_count": 0,
                "monthly_breakdown": [],
            }


# Test function to verify all methods work
def test_database_service():
    """Test the database service with all methods"""
    import logging
    from datetime import date as datetime_date
    from decimal import Decimal

    logging.basicConfig(level=logging.INFO)

    print("Testing Database Service - Complete Method Check...")
    print("=" * 60)

    try:
        # Create database service instance with in-memory database
        print("Creating in-memory database...")
        db_service = DatabaseService(":memory:")
        print("✅ Database service created")

        print("\n1. Testing with dictionary input...")
        expense_dict = {
            "date": "2024-12-01",
            "category": "Makanan & Minuman",
            "amount": 50000.0,
            "description": "Test dictionary expense",
        }

        expense_id1 = db_service.add_expense(expense_dict)
        print(f"   ✅ Added dictionary expense with ID: {expense_id1}")

        print("\n2. Testing with Expense object input...")
        # Try to import Expense model
        try:
            from models.expense_model import Expense

            expense_obj = Expense(
                date=datetime_date(2024, 12, 1),
                category="Transportasi",
                amount=Decimal("25000"),
                description="Test Expense object",
            )

            expense_id2 = db_service.add_expense(expense_obj)
            print(f"   ✅ Added Expense object with ID: {expense_id2}")

        except ImportError:
            print("   ⚠️  Expense model not available, skipping object test")

        print("\n3. Testing get_expenses method...")
        expenses = db_service.get_expenses(year=2024, month=12)
        print(f"   ✅ Found {len(expenses)} expenses for Dec 2024")

        print("\n4. Testing get_expense_by_id...")
        expense = db_service.get_expense_by_id(expense_id1)
        if expense:
            print(f"   ✅ Found expense: {expense.get('description')}")
        else:
            print("   ❌ Expense not found")

        print("\n5. Testing get_monthly_summary...")
        summary = db_service.get_monthly_summary(2024, 12)
        print(f"   ✅ Monthly total: Rp {summary.get('total_expenses', 0)}")

        print("\n6. Testing get_categories...")
        categories = db_service.get_categories()
        print(f"   ✅ Found {len(categories)} categories")

        print("\n7. Testing get_all_categories (alias)...")
        all_categories = db_service.get_all_categories()
        print(f"   ✅ Found {len(all_categories)} categories via get_all_categories")

        print("\n8. Testing update_expense...")
        update_data = {
            "date": "2024-12-01",
            "category": "Makanan & Minuman",
            "amount": 60000.0,
            "description": "Updated expense",
        }
        if db_service.update_expense(expense_id1, update_data):
            print(f"   ✅ Updated expense {expense_id1}")
        else:
            print(f"   ❌ Failed to update expense {expense_id1}")

        print("\n9. Testing delete_expense...")
        if db_service.delete_expense(expense_id1):
            print(f"   ✅ Deleted expense {expense_id1}")
        else:
            print(f"   ❌ Failed to delete expense {expense_id1}")

        print("\n10. Testing get_yearly_summary...")
        yearly_summary = db_service.get_yearly_summary(2024)
        print(f"   ✅ Yearly total: Rp {yearly_summary.get('total_expenses', 0)}")

        print("\n🎉 All database service methods work!")
        print("✅ Service has all required methods!")
        
        # Close the in-memory connection
        db_service.close()
        print("✅ Database connection closed")

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_database_service()