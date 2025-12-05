# Github/project portofolio/junior project/daily-expense-tracker/models/expense_model.py

"""
Expense Model for Daily Expense Tracker.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

@dataclass
class Expense:
    id: Optional[int] = None
    date: date = None
    category: str = ""
    amount: Decimal = Decimal("0.00")
    description: str = ""
    created_at: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "category": self.category,
            "amount": float(self.amount),
            "description": self.description,
            "created_at": self.created_at,
        }
