# utils/validation.py
"""
Validation Utilities
Provides functions to validate expense data inputs
"""

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Tuple, Union


def validate_date(date_string: str, date_format: str = "%Y-%m-%d") -> Tuple[bool, Optional[date]]:
    """Validate date format and return (is_valid, date_object)"""
    try:
        parsed_date = datetime.strptime(date_string, date_format).date()
        return True, parsed_date
    except ValueError:
        return False, None


def validate_amount(amount_string: str) -> Tuple[bool, Optional[Decimal]]:
    """Validate amount format and return (is_valid, decimal_amount)"""
    try:
        # Keep digits, dots, commas, and minus sign
        cleaned = re.sub(r"[^\d.,\-]", "", amount_string)
        if not cleaned:
            return False, None

        # Check for multiple decimal points or minus signs
        if cleaned.count(".") > 1 or cleaned.count(",") > 1 or cleaned.count("-") > 1:
            return False, None
        
        # Minus sign must be at the beginning if present
        if "-" in cleaned and not cleaned.startswith("-"):
            return False, None

        # Replace comma with dot for decimal
        cleaned = cleaned.replace(",", ".")

        # Parse to Decimal
        amount = Decimal(cleaned)

        # Validate amount is positive (greater than 0)
        # Negative amounts should return False
        if amount <= Decimal("0"):
            return False, amount

        return True, amount
    except (InvalidOperation, ValueError):
        return False, None


def validate_amount_simple(amount_string: str) -> bool:
    """Simple validation: returns True if amount is valid positive number"""
    valid, _ = validate_amount(amount_string)
    return valid


def parse_amount(amount_string: str) -> Decimal:
    """Parse string amount to Decimal (returns 0 if invalid)"""
    try:
        # Remove non-digit characters except dot, comma, and minus
        cleaned = re.sub(r"[^\d.,\-]", "", amount_string)
        if not cleaned:
            return Decimal("0")
            
        # Minus sign must be at the beginning if present
        if "-" in cleaned and not cleaned.startswith("-"):
            return Decimal("0")
            
        # Replace comma with dot for decimal
        cleaned = cleaned.replace(",", ".")
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return Decimal("0")


def validate_category(
    category: str, allowed_categories: Optional[List[str]] = None
) -> bool:
    """Validate category"""
    if not category or not category.strip():
        return False
    if allowed_categories is None:
        return True
    return category.strip() in allowed_categories


def validate_expense_data(
    date_str: str,
    category: str,
    amount_str: str,
    description: str = "",
    allowed_categories: Optional[List[str]] = None,
) -> Tuple[bool, dict, str]:
    """Validate all expense data at once"""
    errors = []
    validated_data = {}

    # Validate date
    date_valid, date_value = validate_date(date_str)
    if not date_valid:
        errors.append("Invalid date format. Use YYYY-MM-DD")
    else:
        validated_data["date"] = date_value

    # Validate category
    if not category or not category.strip():
        errors.append("Category cannot be empty")
    elif allowed_categories and category not in allowed_categories:
        errors.append(f"Category '{category}' is not in allowed categories")
    else:
        validated_data["category"] = category.strip()

    # Validate amount
    amount_valid, amount_value = validate_amount(amount_str)
    if not amount_valid:
        errors.append("Invalid amount. Must be a positive number")
    else:
        validated_data["amount"] = amount_value

    # Validate description (optional)
    if description:
        validated_data["description"] = description.strip()
    else:
        validated_data["description"] = ""

    # Return results
    if errors:
        return False, validated_data, "; ".join(errors)
    else:
        return True, validated_data, ""


# Backward compatibility functions for existing code
def validate_date_simple(date_string: str, format: str = "%Y-%m-%d") -> bool:
    """Simple date validation (for backward compatibility)"""
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False


def test_validation_logic():
    """Test the validation logic specifically for amounts"""
    print("Testing validation logic for failing test...")
    print("=" * 60)

    test_cases = [
        ("1000", True),  # Should be valid
        ("-1000", False),  # Should be invalid (negative)
        ("0", False),  # Should be invalid (zero)
        ("-500.50", False),  # Should be invalid (negative decimal)
        ("50,000", True),  # Should be valid
        ("not-a-number", False),  # Should be invalid
        ("", False),  # Should be invalid
        ("Rp 100.000", True),  # Should be valid (currency symbol removed)
        ("Rp -100.000", False),  # Should be invalid (negative with currency)
        ("1.000.000", False),  # Should be invalid (multiple dots)
        ("1,000,000", False),  # Should be invalid (multiple commas)
        ("10-00", False),  # Should be invalid (minus in middle)
    ]

    all_passed = True
    for amount_str, expected_valid in test_cases:
        valid, amount = validate_amount(amount_str)
        status = "✓" if valid == expected_valid else "✗"
        if valid != expected_valid:
            all_passed = False
            print(f"{status} ❌ '{amount_str}' -> valid={valid}, amount={amount} (expected valid={expected_valid})")
        else:
            print(f"{status} '{amount_str}' -> valid={valid}, amount={amount}")

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All amount validation tests passed!")
    else:
        print("❌ Some amount validation tests failed")

    # Test the simple function too
    print("\nTesting validate_amount_simple (used by tests):")
    simple_passed = True
    for amount_str, expected_valid in test_cases:
        result = validate_amount_simple(amount_str)
        status = "✓" if result == expected_valid else "✗"
        if result != expected_valid:
            simple_passed = False
            print(f"{status} ❌ '{amount_str}' -> {result} (expected: {expected_valid})")
        else:
            print(f"{status} '{amount_str}' -> {result}")
    
    if simple_passed:
        print("✅ All simple validation tests passed!")
    else:
        print("❌ Some simple validation tests failed")


def test_parse_amount():
    """Test parse_amount function"""
    print("\n" + "=" * 60)
    print("Testing parse_amount function:")
    
    test_cases = [
        ("1000", Decimal("1000")),
        ("-1000", Decimal("-1000")),  # parse_amount should parse negatives
        ("0", Decimal("0")),
        ("50,000", Decimal("50000")),
        ("Rp 100.000", Decimal("100.000")),
        ("invalid", Decimal("0")),
    ]
    
    for amount_str, expected in test_cases:
        result = parse_amount(amount_str)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{amount_str}' -> {result} (expected: {expected})")


def test_validation_functions():
    """Test all validation functions"""
    print("\n" + "=" * 60)
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
    # Run specific test for the failing case
    test_validation_logic()
    test_parse_amount()
    print("\n" + "=" * 60)
    # Run full test suite
    test_validation_functions()