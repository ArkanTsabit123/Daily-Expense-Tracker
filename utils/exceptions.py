# project portofolio/junior projects/daily-expense-tracker/utils/exceptions.py

"""
Custom Exceptions
Defines custom exception classes for the daily-expense-tracker application.
"""

class ExpenseError(Exception):
    """Base exception for expense-related errors"""

    def __init__(self, message="Expense error occurred"):
        self.message = message
        super().__init__(self.message)

class DatabaseError(ExpenseError):
    """Exception for database-related errors"""

    def __init__(self, message="Database error occurred"):
        super().__init__(message)

class ValidationError(ExpenseError):
    """Exception for validation errors"""

    def __init__(self, message="Validation error occurred"):
        super().__init__(message)

class ExportError(ExpenseError):
    """Exception for export-related errors"""

    def __init__(self, message="Export error occurred"):
        super().__init__(message)

class CategoryError(ExpenseError):
    """Exception for category-related errors"""

    def __init__(self, message="Category error occurred"):
        super().__init__(message)

class DataNotFoundError(ExpenseError):
    """Exception when data is not found"""

    def __init__(self, message="Data not found"):
        super().__init__(message)

class ConfigurationError(ExpenseError):
    """Exception for configuration errors"""

    def __init__(self, message="Configuration error occurred"):
        super().__init__(message)

# Test the exceptions
if __name__ == "__main__":
    print("Testing custom exceptions...")

    try:
        raise DatabaseError("Could not connect to database")
    except DatabaseError as e:
        print(f"✓ DatabaseError caught: {e}")

    try:
        raise ValidationError("Invalid date format")
    except ValidationError as e:
        print(f"✓ ValidationError caught: {e}")

    try:
        raise ExportError("Failed to export to Excel")
    except ExportError as e:
        print(f"✓ ExportError caught: {e}")

    print("✓ All exceptions work correctly!")
