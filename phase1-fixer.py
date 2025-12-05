#daily-expense-tracker/phase1-fixer.py

"""
This module checks if a given phase is valid for phase 1.
"""

import sys
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}".center(60))
    print("=" * 60)

def fix_expense_model():
    print_header("Fixing Expense Model")
    project_root = Path(__file__).parent
    expense_model_path = project_root / "models" / "expense_model.py"
    expense_model_content = """from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

@dataclass
class Expense:
    id: Optional[int] = None
    date: date = None
    category: str = ""
    amount: Decimal = Decimal('0.00')
    description: str = ""
    created_at: Optional[str] = None
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'category': self.category,
            'amount': float(self.amount),
            'description': self.description,
            'created_at': self.created_at
        }
"""
    with open(expense_model_path, "w", encoding="utf-8") as f:
        f.write(expense_model_content)
    print("Fixed expense_model.py")
    return True

def fix_category_model():
    print_header("Fixing Category Model")
    project_root = Path(__file__).parent
    category_model_path = project_root / "models" / "category_model.py"
    category_model_content = """from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class Category:
    id: Optional[int] = None
    name: str = ""
    budget_limit: Optional[Decimal] = None
    description: str = ""
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'budget_limit': float(self.budget_limit) if self.budget_limit else None,
            'description': self.description
        }
"""
    with open(category_model_path, "w", encoding="utf-8") as f:
        f.write(category_model_content)
    print("Fixed category_model.py")
    return True

def test_models():
    print_header("Testing Models")
    project_root = Path(__file__).parent
    try:
        sys.path.insert(0, str(project_root))
        from models.category_model import Category
        from models.expense_model import Expense

        print("Imported Expense model")
        print("Imported Category model")
        from datetime import date
        from decimal import Decimal

        expense = Expense(
            date=date.today(),
            category="Food",
            amount=Decimal("25000"),
            description="Lunch",
        )
        print(f"Expense: {expense.category} - Rp {expense.amount}")
        category = Category(name="Food", budget_limit=Decimal("1000000"))
        print(f"Category: {category.name} - Budget: Rp {category.budget_limit}")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print_header("Phase 1 Model Fixer")
    fix_expense_model()
    fix_category_model()
    success = test_models()
    if success:
        print_header("Models fixed successfully")
        print("/nRun: python phase1-verify.py")
    else:
        print_header("Model fix failed")
    return success

if __name__ == "__main__":
    main()
