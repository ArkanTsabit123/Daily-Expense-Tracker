# project portofolio/junior project/daily-expense-tracker/phase1-verify.py

"""
This module verifies if the project meets the requirements for phase 1.
"""


import os
import sys
import sqlite3
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 70)
    print(f" {text}".center(70))
    print("=" * 70)

def check_item(name, passed, message=""):
    if passed:
        status = "✅ PASS"
        symbol = "✅"
    else:
        status = "❌ FAIL"
        symbol = "❌"
    
    print(f"{symbol} {name:40} {status}")
    if message:
        print(f"   {message}")

def check_phase1():
    print_header("DAILY EXPENSE TRACKER - PHASE 1 VERIFICATION")
    
    project_root = Path(__file__).parent
    print(f"Project location: {project_root}\n")
    
    print_header("DATABASE CHECK")
    
    # Database file
    db_path = project_root / "data" / "expenses.db"
    db_exists = db_path.exists()
    check_item("Database file exists", db_exists)
    
    if db_exists:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            table_names = [t[0] for t in tables]
            has_expenses = 'expenses' in table_names
            has_categories = 'categories' in table_names
            
            check_item(f"Found {len(tables)} tables", len(tables) > 0)
            check_item("expenses table exists", has_expenses)
            check_item("categories table exists", has_categories)
            
        except Exception as e:
            check_item("Database connection", False, f"Error: {e}")
    
    print_header("MODELS CHECK")
    
    expense_path = project_root / "models" / "expense_model.py"
    category_path = project_root / "models" / "category_model.py"
    
    check_item("expense_model.py exists", expense_path.exists())
    check_item("category_model.py exists", category_path.exists())
    
    if expense_path.exists() and category_path.exists():
        try:
            sys.path.insert(0, str(project_root))
            from models.expense_model import Expense
            from models.category_model import Category
            
            from datetime import date
            from decimal import Decimal
            
            expense = Expense(
                date=date.today(),
                category="Test",
                amount=Decimal("10000"),
                description="Test"
            )
            check_item("Expense model import", True)
            
            category = Category(name="Test")
            check_item("Category model import", True)
            
        except ImportError as e:
            check_item("Models import", False, f"Import error: {e}")
        except Exception as e:
            check_item("Models instantiation", False, f"Error: {e}")
    
    print_header("VALIDATION CHECK")
    
    validation_path = project_root / "utils" / "validation.py"
    check_item("validation.py exists", validation_path.exists())
    
    if validation_path.exists():
        try:
            from utils.validation import validate_date, validate_amount
            check_item("Validation functions import", True)
            
            valid, _ = validate_date("2024-01-15")
            check_item("validate_date() works", valid)
            
        except ImportError as e:
            check_item("Validation import", False, f"Import error: {e}")
        except Exception as e:
            check_item("Validation functions", False, f"Error: {e}")
    
    print_header("REQUIREMENTS CHECK")
    
    requirements_path = project_root / "requirements.txt"
    check_item("requirements.txt exists", requirements_path.exists())
    
    if requirements_path.exists():
        try:
            with open(requirements_path, 'r') as f:
                content = f.read()
            
            has_matplotlib = 'matplotlib' in content
            has_pandas = 'pandas' in content
            
            check_item("matplotlib in requirements", has_matplotlib)
            check_item("pandas in requirements", has_pandas)
            
        except Exception as e:
            check_item("Read requirements.txt", False, f"Error: {e}")
    
    print_header("GIT CHECK")
    
    git_dir = project_root / ".git"
    gitignore_path = project_root / ".gitignore"
    
    check_item("Git repository initialized", git_dir.exists())
    check_item(".gitignore exists", gitignore_path.exists())
    
    print_header("PHASE 1 VERIFICATION RESULTS")
    
    print("\nRun: python phase2-verify.py for Phase 2 verification")

if __name__ == "__main__":
    check_phase1()