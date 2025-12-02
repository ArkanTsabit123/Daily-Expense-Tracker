# project portofolio/junior project/daily-expense-tracker/phase1-verify.py

"""
This module verifies if the project meets the requirements for phase 1.
"""


import os
import sys
import sqlite3
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}".center(60))
    print("=" * 60)

def check_phase1():
    print_header("PHASE 1 STATUS CHECK")
    
    project_root = Path(__file__).parent
    
    print("Project location:", project_root)
    print()
    
    # Database check
    print("1. DATABASE CHECK")
    db_path = project_root / "data" / "expenses.db"
    
    if db_path.exists():
        print("   Database file exists")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            table_names = [t[0] for t in tables]
            print(f"   Found {len(tables)} tables")
            
            if 'expenses' in table_names and 'categories' in table_names:
                print("   Both tables exist")
            else:
                print(f"   Missing tables. Found: {table_names}")
                
        except Exception as e:
            print(f"   Database error: {e}")
    else:
        print("   Database file not found")
    
    # Models check
    print("\n2. MODELS CHECK")
    expense_path = project_root / "models" / "expense_model.py"
    category_path = project_root / "models" / "category_model.py"
    
    if expense_path.exists() and category_path.exists():
        print("   Model files exist")
        
        try:
            sys.path.insert(0, str(project_root))
            from models.expense_model import Expense
            from models.category_model import Category
            
            print("   Models can be imported")
            
            from datetime import date
            from decimal import Decimal
            
            expense = Expense(
                date=date.today(),
                category="Test",
                amount=Decimal("10000"),
                description="Test"
            )
            print("   Expense model works")
            
            category = Category(name="Test")
            print("   Category model works")
            
        except ImportError as e:
            print(f"   Import error: {e}")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("   Model files missing")
    
    # Validation check
    print("\n3. VALIDATION CHECK")
    validation_path = project_root / "utils" / "validation.py"
    
    if validation_path.exists():
        print("   Validation file exists")
        
        try:
            from utils.validation import validate_date, validate_amount
            
            print("   Validation functions can be imported")
            
            valid, _ = validate_date("2024-01-15")
            print(f"   Date validation works: {valid}")
            
        except ImportError as e:
            print(f"   Import error: {e}")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("   Validation file missing")
    
    # Requirements check
    print("\n4. REQUIREMENTS CHECK")
    requirements_path = project_root / "requirements.txt"
    
    if requirements_path.exists():
        print("   requirements.txt exists")
        
        try:
            with open(requirements_path, 'r') as f:
                content = f.read()
            
            if 'matplotlib' in content and 'pandas' in content:
                print("   Contains matplotlib and pandas")
            else:
                print("   Missing some dependencies")
        except:
            print("   Cannot read requirements.txt")
    else:
        print("   requirements.txt missing")
    
    # Git check
    print("\n5. GIT CHECK")
    git_dir = project_root / ".git"
    
    if git_dir.exists():
        print("   Git repository initialized")
        
        gitignore_path = project_root / ".gitignore"
        if gitignore_path.exists():
            print("   .gitignore exists")
        else:
            print("   .gitignore missing")
    else:
        print("   Git repository not initialized")
    
    print_header("SUMMARY")
    print("\nFix any items above before proceeding to Phase 2.")

if __name__ == "__main__":
    check_phase1()