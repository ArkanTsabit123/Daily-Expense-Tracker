

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple, List

def validate_date(date_string: str, date_format: str = '%Y-%m-%d') -> Tuple[bool, Optional[date]]:
    try:
        datetime.strptime(date_string, date_format)
        return True, None
    except ValueError:
        return False, None

def validate_amount(amount_string: str) -> Tuple[bool, Optional[Decimal]]:
    try:
        cleaned = re.sub(r'[^\d.,-]', '', amount_string)
        if not cleaned:
            return False, None
        
        if cleaned.count('.') > 1 or cleaned.count(',') > 1:
            return False, None
        
        cleaned = cleaned.replace(',', '.')
        amount = Decimal(cleaned)
        
        if amount <= Decimal('0'):
            return False, amount
            
        return True, amount
    except (InvalidOperation, ValueError):
        return False, None

def validate_expense_data(date_str: str, category: str, amount_str: str, 
                          description: str = "", allowed_categories: Optional[List[str]] = None) -> Tuple[bool, dict, str]:
    errors = []
    validated_data = {}
    
    date_valid, _ = validate_date(date_str)
    if not date_valid:
        errors.append("Invalid date format")
    else:
        validated_data['date'] = date_str
    
    if not category or not category.strip():
        errors.append("Category cannot be empty")
    else:
        validated_data['category'] = category.strip()
    
    amount_valid, amount_decimal = validate_amount(amount_str)
    if not amount_valid:
        errors.append("Invalid amount")
    else:
        validated_data['amount'] = amount_decimal
    
    if description:
        validated_data['description'] = description.strip()
    else:
        validated_data['description'] = ""
    
    if errors:
        return False, validated_data, "; ".join(errors)
    else:
        return True, validated_data, ""
