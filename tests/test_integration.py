# tests/test_integration.py
"""
Integration tests for export functionality
"""

import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIntegration:
    """End-to-end integration tests"""

    def test_complete_workflow(self, expense_service_fixture, export_service_fixture, clean_exports_dir):
        """Test complete workflow: add expense -> get history -> export"""
        try:
            print("\n🔧 Testing complete workflow...")
            
            # Add test expense
            result = expense_service_fixture.create_expense(
                "2024-12-01", 
                "Makanan & Minuman", 
                "50000", 
                "Test integration meal"
            )
            
            assert result["success"] == True, f"Failed to add expense: {result.get('error', 'Unknown error')}"
            print("✅ Expense added successfully")
            
            # Get expense ID
            expense_id = result.get("expense_id")
            assert expense_id is not None, "Expense ID not returned"
            print(f"✅ Expense ID: {expense_id}")
            
            # Get history
            expenses = expense_service_fixture.get_expense_history()
            assert len(expenses) > 0, "No expenses found in history"
            print(f"✅ Found {len(expenses)} expenses in history")
            
            # Find our test expense
            test_expense = None
            for expense in expenses:
                if expense.get('description') == "Test integration meal":
                    test_expense = expense
                    break
            
            assert test_expense is not None, "Test expense not found in history"
            print("✅ Test expense found in history")
            
            # Export to CSV
            csv_filepath = export_service_fixture.export_to_csv(expenses, "test_integration.csv")
            assert os.path.exists(csv_filepath), f"CSV file not created: {csv_filepath}"
            assert "test_integration.csv" in csv_filepath
            print(f"✅ CSV exported: {csv_filepath}")
            
            # Export to Excel
            excel_filepath = export_service_fixture.export_to_excel(expenses, "test_integration.xlsx")
            assert os.path.exists(excel_filepath), f"Excel file not created: {excel_filepath}"
            assert "test_integration.xlsx" in excel_filepath
            print(f"✅ Excel exported: {excel_filepath}")
            
            # Verify file sizes
            csv_size = os.path.getsize(csv_filepath)
            excel_size = os.path.getsize(excel_filepath)
            assert csv_size > 0, "CSV file is empty"
            assert excel_size > 0, "Excel file is empty"
            
            print(f"\n📊 Test results:")
            print(f"  CSV file: {csv_filepath} ({csv_size} bytes)")
            print(f"  Excel file: {excel_filepath} ({excel_size} bytes)")
            
            # Clean up test files
            try:
                if os.path.exists(csv_filepath):
                    os.remove(csv_filepath)
                if os.path.exists(excel_filepath):
                    os.remove(excel_filepath)
                print("✅ Test files cleaned up")
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up test files: {e}")
            
            print("\n🎉 Complete workflow test passed!")
            
        except AssertionError as e:
            print(f"❌ Assertion error: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

    def test_monthly_report_export(self, expense_service_fixture, export_service_fixture, clean_exports_dir):
        """Test monthly report export functionality"""
        try:
            print("\n📅 Testing monthly report export...")
            
            # Add a test expense first
            result = expense_service_fixture.create_expense(
                "2024-12-01",
                "Makanan & Minuman",
                "75000",
                "Monthly report test"
            )
            
            if not result["success"]:
                print(f"⚠️  Could not add test expense: {result.get('error')}")
                # Skip this test if we can't add an expense
                # Don't use return in pytest test method
                # Instead, use pytest.skip() or just pass
                import pytest
                pytest.skip(f"Could not add test expense: {result.get('error')}")
            
            # Get current month data
            from utils.date_utils import get_current_month_year
            month, year = get_current_month_year()
            
            # Get monthly analysis
            analysis = expense_service_fixture.get_monthly_analysis(year, month)
            assert analysis is not None, "Monthly analysis failed"
            print(f"✅ Monthly analysis retrieved")
            
            # Get expenses for the month
            expenses = expense_service_fixture.get_expense_history({'year': year, 'month': month})
            print(f"✅ Found {len(expenses)} expenses for {month}/{year}")
            
            # Export monthly report (only if there are expenses)
            if expenses:
                report_path = export_service_fixture.export_monthly_report(analysis, expenses)
                assert os.path.exists(report_path), f"Monthly report not created: {report_path}"
                assert "monthly_report" in report_path
                
                # Verify file
                report_size = os.path.getsize(report_path)
                assert report_size > 0, "Monthly report file is empty"
                
                print(f"✅ Monthly report created: {report_path} ({report_size} bytes)")
                
                # Clean up
                try:
                    if os.path.exists(report_path):
                        os.remove(report_path)
                        print("✅ Monthly report cleaned up")
                except Exception as e:
                    print(f"⚠️  Could not clean up report: {e}")
            else:
                print("⚠️  No expenses found for monthly report test")
            
            print("\n✅ Monthly report test completed!")
            
        except AssertionError as e:
            print(f"❌ Assertion error: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise


def test_imports():
    """Test that all necessary imports work"""
    print("Testing imports...")
    
    # Test service imports
    from services.expense_service import ExpenseService
    from services.export_service import ExportService
    from services.database_service import DatabaseService
    
    # Test model imports
    from models.expense_model import Expense
    from models.category_model import Category
    
    # Test utility imports
    from utils.validation import validate_amount, validate_date
    from utils.date_utils import get_current_month_year
    from utils.formatters import format_currency
    
    print("✅ All imports successful!")
    
    # Create instances
    expense_service = ExpenseService()
    export_service = ExportService()
    database_service = DatabaseService()
    
    assert expense_service is not None, "ExpenseService should not be None"
    assert export_service is not None, "ExportService should not be None"
    assert database_service is not None, "DatabaseService should not be None"
    
    print("✅ Service instances created successfully!")
    # Tidak perlu return apapun - fungsi test harus mengembalikan None


if __name__ == "__main__":
    # Run integration tests directly
    print("Running integration tests...")
    print("=" * 60)
    
    # Test imports first
    try:
        # Test imports
        from services.expense_service import ExpenseService
        from services.export_service import ExportService
        from services.database_service import DatabaseService
        from models.expense_model import Expense
        from models.category_model import Category
        from utils.validation import validate_amount, validate_date
        from utils.date_utils import get_current_month_year
        from utils.formatters import format_currency
        
        print("✅ All imports successful!")
        
        # Create instances
        expense_service = ExpenseService()
        export_service = ExportService()
        database_service = DatabaseService()
        
        print("✅ Service instances created successfully!")
        
        print("\n" + "=" * 60)
        print("Running integration tests with pytest...")
        
        # Run pytest on this file
        import pytest
        import sys
        
        # Run specific tests
        test_result = pytest.main([
            __file__,
            "-v",
            "-s",
            "--tb=short"
        ])
        
        if test_result == 0:
            print("\n" + "=" * 60)
            print("✅ All integration tests passed!")
        else:
            print("\n" + "=" * 60)
            print("❌ Some integration tests failed")
            sys.exit(1)
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n" + "=" * 60)
        print("❌ Import test failed, skipping integration tests")
        sys.exit(1)