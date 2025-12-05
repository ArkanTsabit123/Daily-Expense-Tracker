from dataclasses import dataclass
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
            "id": self.id,
            "name": self.name,
            "budget_limit": float(self.budget_limit) if self.budget_limit else None,
            "description": self.description,
        }
