#root/check_methods.py

""""
Check Methods
This module checks for the existence of specific methods in service classes.
"""

# check_methods.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Checking DatabaseService methods...")
print("=" * 60)

try:
    from services.database_service import DatabaseService
    
    # Create instance
    db = DatabaseService(":memory:")
    
    # Check required methods
    required_methods = [
        'add_expense',
        'get_expenses', 
        'get_monthly_summary',
        'get_categories',
        'delete_expense',
        'update_expense',
        'get_expense_by_id',
        'get_all_categories'
    ]
    
    print("Checking methods:")
    for method in required_methods:
        if hasattr(db, method):
            print(f"  ✅ {method}")
        else:
            print(f"  ❌ {method} (MISSING)")
    
    # Test the methods
    print("\nTesting method functionality:")
    
    # Test add_expense
    print("1. Testing add_expense...")
    expense_data = {
        "date": "2024-12-01",
        "category": "Makanan & Minuman",
        "amount": 50000.0,
        "description": "Test"
    }
    
    expense_id = db.add_expense(expense_data)
    print(f"   ✅ Added expense with ID: {expense_id}")
    
    # Test get_monthly_summary
    print("2. Testing get_monthly_summary...")
    try:
        summary = db.get_monthly_summary(2024, 12)
        print(f"   ✅ Monthly summary: {summary.get('total_expenses', 0)}")
    except Exception as e:
        print(f"   ❌ get_monthly_summary failed: {e}")
    
    # Test get_expenses
    print("3. Testing get_expenses...")
    expenses = db.get_expenses()
    print(f"   ✅ Found {len(expenses)} expenses")
    
    # Test get_categories
    print("4. Testing get_categories...")
    categories = db.get_categories()
    print(f"   ✅ Found {len(categories)} categories")
    
    # Clean up
    print("5. Cleaning up...")
    if hasattr(db, 'close'):
        db.close()
        print("   ✅ Database closed")
    
    print("\n🎉 All checks completed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()