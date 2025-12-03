# project portofolio\junior projects\daily-expense-tracker\utils\validation.py

"""
Validation Utilities
Provides functions to validate expense data inputs
"""

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple, List


def validate_date(date_string: str, date_format: str = '%Y-%m-%d') -> Tuple[bool, Optional[date]]:
    """Validate date format"""
    try:
        parsed_date = datetime.strptime(date_string, date_format).date()
        return True, parsed_date
    except ValueError:
        return False, None


def validate_amount(amount_string: str) -> Tuple[bool, Optional[Decimal]]:
    """Validate amount format"""
    try:
        # Remove non-digit characters except dot, comma, and minus
        cleaned = re.sub(r'[^\d.,-]', '', amount_string)
        if not cleaned:
            return False, None
        
        # Check for multiple decimal points
        if cleaned.count('.') > 1 or cleaned.count(',') > 1:
            return False, None
        
        # Replace comma with dot for decimal
        cleaned = cleaned.replace(',', '.')
        
        # Parse to Decimal
        amount = Decimal(cleaned)
        
        # Validate amount is positive
        if amount <= Decimal('0'):
            return False, amount
            
        return True, amount
    except (InvalidOperation, ValueError):
        return False, None


def parse_amount(amount_string: str) -> Decimal:
    """Parse string amount to Decimal"""
    try:
        # Remove non-digit characters except dot and comma
        cleaned = re.sub(r'[^\d.,]', '', amount_string)
        # Replace comma with dot for decimal
        cleaned = cleaned.replace(',', '.')
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return Decimal('0')


def validate_category(category: str, allowed_categories: Optional[List[str]] = None) -> bool:
    """Validate category"""
    if allowed_categories is None:
        return bool(category and category.strip())
    return category in allowed_categories


def validate_expense_data(date_str: str, category: str, amount_str: str, 
                          description: str = "", allowed_categories: Optional[List[str]] = None) -> Tuple[bool, dict, str]:
    """Validate all expense data at once"""
    errors = []
    validated_data = {}
    
    # Validate date
    date_valid, date_value = validate_date(date_str)
    if not date_valid:
        errors.append("Invalid date format. Use YYYY-MM-DD")
    else:
        validated_data['date'] = date_value
    
    # Validate category
    if not category or not category.strip():
        errors.append("Category cannot be empty")
    else:
        validated_data['category'] = category.strip()
        
        if allowed_categories and category not in allowed_categories:
            errors.append(f"Category '{category}' is not in allowed categories")
    
    # Validate amount
    amount_valid, amount_value = validate_amount(amount_str)
    if not amount_valid:
        errors.append("Invalid amount. Must be a positive number")
    else:
        validated_data['amount'] = amount_value
    
    # Validate description (optional)
    if description:
        validated_data['description'] = description.strip()
    else:
        validated_data['description'] = ""
    
    # Return results
    if errors:
        return False, validated_data, "; ".join(errors)
    else:
        return True, validated_data, ""


def test_validation_functions():
    """Test validation functions"""
    print("Testing validation functions...")
    
    # Test date validation
    print("\n1. Testing date validation:")
    valid_date, date_obj = validate_date("2024-01-15")
    print(f"   '2024-01-15': {valid_date} {date_obj}")
    
    invalid_date, _ = validate_date("2024-13-15")
    print(f"   '2024-13-15': {invalid_date}")
    
    # Test amount validation
    print("\n2. Testing amount validation:")
    valid_amount, amount_val = validate_amount("50000")
    print(f"   '50000': {valid_amount} {amount_val}")
    
    valid_amount2, amount_val2 = validate_amount("50,000")
    print(f"   '50,000': {valid_amount2} {amount_val2}")
    
    invalid_amount, _ = validate_amount("not-a-number")
    print(f"   'not-a-number': {invalid_amount}")
    
    # Test parse_amount
    print("\n3. Testing parse_amount:")
    parsed1 = parse_amount("Rp 50.000")
    print(f"   'Rp 50.000': {parsed1}")
    
    parsed2 = parse_amount("25,500.75")
    print(f"   '25,500.75': {parsed2}")
    
    # Test expense data validation
    print("\n4. Testing expense data validation:")
    categories = ["Food", "Transport", "Shopping"]
    
    valid, data, error = validate_expense_data(
        "2024-01-15", "Food", "50000", "Lunch", categories
    )
    print(f"   Valid data: {valid}, Error: {error}")
    
    invalid, data2, error2 = validate_expense_data(
        "2024-13-15", "", "not-a-number", "", categories
    )
    print(f"   Invalid data: {invalid}, Error: {error2}")
    
    print("\nValidation functions test completed!")


if __name__ == "__main__":
    test_validation_functions()