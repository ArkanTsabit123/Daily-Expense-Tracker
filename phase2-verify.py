# project portofolio/junior project/daily-expense-tracker/phase2-verify.py

"""
This module verifies if the project meets the requirements for Phase 2.
Checks CRUD operations, testing, and error handling.
"""

import os
import sys
import sqlite3
import importlib.util
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
import tempfile
import shutil
from colorama import init, Fore, Back, Style

init(autoreset=True)

class Phase2Verifier:
    """Verifies Phase 2 requirements for Daily Expense Tracker"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {
            "CRUD Operations": [],
            "Business Logic": [],
            "Filtering & Search": [],
            "Testing Framework": [],
            "Test Data": [],
            "Error Handling": []
        }
        self.score = 0
        self.total_checks = 0
        
    def print_header(self, text):
        print("\n" + "=" * 70)
        print(f" {text}".center(70))
        print("=" * 70)
    
    def print_check(self, check_name, passed, message=""):
        self.total_checks += 1
        if passed:
            self.score += 1
            status = f"{Fore.GREEN}✅ PASS"
            symbol = "✅"
        else:
            status = f"{Fore.RED}❌ FAIL"
            symbol = "❌"
        
        print(f"{symbol} {check_name:40} {status}")
        if message:
            print(f"   {Fore.YELLOW}{message}")
        print()
    
    def check_module_exists(self, module_path, module_name):
        """Check if a module exists and can be imported"""
        full_path = self.project_root / module_path
        if not full_path.exists():
            return False, f"File not found: {module_path}"
        
        try:
            # Try to import the module
            spec = importlib.util.spec_from_file_location(module_name, full_path)
            if spec is None:
                return False, f"Cannot load module: {module_name}"
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True, f"Module imported successfully: {module_name}"
        except Exception as e:
            return False, f"Import error: {str(e)}"
    
    def check_crud_operations(self):
        """Check if CRUD operations are implemented"""
        self.print_header("CRUD OPERATIONS CHECK")
        
        # Check database service exists
        db_service_path = "services/database_service.py"
        passed, msg = self.check_module_exists(db_service_path, "database_service")
        self.print_check("Database Service Exists", passed, msg)
        
        if passed:
            try:
                # Import the service
                spec = importlib.util.spec_from_file_location(
                    "database_service", 
                    self.project_root / db_service_path
                )
                db_service = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(db_service)
                
                # Check for required methods
                required_methods = [
                    'add_expense', 'get_expense', 'get_expenses',
                    'update_expense', 'delete_expense',
                    'get_monthly_summary', 'get_categories'
                ]
                
                for method in required_methods:
                    if hasattr(db_service.DatabaseService, method):
                        self.print_check(f"Method {method}() exists", True)
                    else:
                        self.print_check(f"Method {method}() exists", False)
                
            except Exception as e:
                self.print_check("Database Service Implementation", False, str(e))
    
    def check_business_logic(self):
        """Check business logic layer"""
        self.print_header("BUSINESS LOGIC LAYER CHECK")
        
        # Check expense service exists
        expense_service_path = "services/expense_service.py"
        passed, msg = self.check_module_exists(expense_service_path, "expense_service")
        self.print_check("Expense Service Exists", passed, msg)
        
        if passed:
            try:
                spec = importlib.util.spec_from_file_location(
                    "expense_service",
                    self.project_root / expense_service_path
                )
                expense_service = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(expense_service)
                
                # Check for business logic methods
                business_methods = [
                    'create_expense', 'get_expense_history',
                    'get_monthly_analysis', 'validate_expense_data'
                ]
                
                for method in business_methods:
                    if hasattr(expense_service.ExpenseService, method):
                        self.print_check(f"Business method {method}()", True)
                    else:
                        self.print_check(f"Business method {method}()", False)
                
            except Exception as e:
                self.print_check("Expense Service Implementation", False, str(e))
    
    def check_filtering_search(self):
        """Check filtering and search capabilities"""
        self.print_header("FILTERING & SEARCH CHECK")
        
        # Test database filtering
        try:
            db_path = self.project_root / "data" / "expenses.db"
            if not db_path.exists():
                self.print_check("Database exists for filtering test", False)
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create test data if needed
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_filtering (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    category TEXT,
                    amount REAL,
                    description TEXT
                )
            """)
            
            # Add test data
            test_data = [
                ('2024-01-15', 'Food', 50000, 'Lunch'),
                ('2024-01-16', 'Transport', 25000, 'Taxi'),
                ('2024-01-17', 'Food', 75000, 'Dinner'),
                ('2024-02-01', 'Shopping', 200000, 'Clothes'),
            ]
            
            cursor.executemany(
                "INSERT OR IGNORE INTO test_filtering (date, category, amount, description) VALUES (?, ?, ?, ?)",
                test_data
            )
            conn.commit()
            
            # Test filtering by date range
            cursor.execute("""
                SELECT * FROM test_filtering 
                WHERE date BETWEEN '2024-01-01' AND '2024-01-31'
            """)
            january_results = cursor.fetchall()
            self.print_check("Date range filtering", len(january_results) == 3, 
                           f"Found {len(january_results)} January expenses")
            
            # Test filtering by category
            cursor.execute("""
                SELECT * FROM test_filtering WHERE category = 'Food'
            """)
            food_results = cursor.fetchall()
            self.print_check("Category filtering", len(food_results) == 2,
                           f"Found {len(food_results)} Food expenses")
            
            # Test search in description
            cursor.execute("""
                SELECT * FROM test_filtering WHERE description LIKE '%Lunch%'
            """)
            search_results = cursor.fetchall()
            self.print_check("Text search", len(search_results) == 1,
                           "Found expense with 'Lunch' in description")
            
            # Clean up
            cursor.execute("DROP TABLE test_filtering")
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.print_check("Filtering tests", False, str(e))
    
    def check_testing_framework(self):
        """Check if testing framework is set up"""
        self.print_header("TESTING FRAMEWORK CHECK")
        
        # Check for test files
        test_files = [
            ("tests/__init__.py", "Test package init"),
            ("tests/test_database.py", "Database tests"),
            ("tests/test_expenses.py", "Expense tests"),
            ("tests/test_export.py", "Export tests"),
            ("tests/conftest.py", "Test configuration")
        ]
        
        for file_path, description in test_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.print_check(f"{description} exists", True)
            else:
                self.print_check(f"{description} exists", False)
        
        # Check if pytest is in requirements
        req_path = self.project_root / "requirements.txt"
        if req_path.exists():
            with open(req_path, 'r') as f:
                content = f.read()
            
            if 'pytest' in content.lower():
                self.print_check("Pytest in requirements", True)
            else:
                self.print_check("Pytest in requirements", False, "Add 'pytest' to requirements.txt")
        else:
            self.print_check("Requirements file", False)
        
        # Check if tests can run
        test_path = self.project_root / "tests" / "test_database.py"
        if test_path.exists():
            try:
                # Try to import test module
                spec = importlib.util.spec_from_file_location("test_database", test_path)
                test_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(test_module)
                
                # Check for test functions
                test_functions = [name for name in dir(test_module) if name.startswith('test_')]
                self.print_check("Test functions found", len(test_functions) > 0,
                               f"Found {len(test_functions)} test functions")
                
            except Exception as e:
                self.print_check("Test module import", False, str(e))
    
    def check_test_data_generation(self):
        """Check test data generation"""
        self.print_header("TEST DATA GENERATION CHECK")
        
        # Check sample data generator
        sample_data_path = "generate/sample_data.py"
        passed, msg = self.check_module_exists(sample_data_path, "sample_data")
        self.print_check("Sample data generator exists", passed, msg)
        
        if passed:
            try:
                spec = importlib.util.spec_from_file_location(
                    "sample_data",
                    self.project_root / sample_data_path
                )
                sample_data = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(sample_data)
                
                # Check for data generation functions
                if hasattr(sample_data, 'generate_sample_expenses'):
                    self.print_check("generate_sample_expenses() function", True)
                else:
                    self.print_check("generate_sample_expenses() function", False)
                
                if hasattr(sample_data, 'generate_test_categories'):
                    self.print_check("generate_test_categories() function", True)
                else:
                    self.print_check("generate_test_categories() function", False)
                    
            except Exception as e:
                self.print_check("Sample data module", False, str(e))
    
    def check_error_handling(self):
        """Check error handling implementation"""
        self.print_header("ERROR HANDLING CHECK")
        
        # Check exceptions module
        exceptions_path = "utils/exceptions.py"
        passed, msg = self.check_module_exists(exceptions_path, "exceptions")
        self.print_check("Exceptions module exists", passed, msg)
        
        if passed:
            try:
                spec = importlib.util.spec_from_file_location(
                    "exceptions",
                    self.project_root / exceptions_path
                )
                exceptions = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(exceptions)
                
                # Check for custom exceptions
                custom_exceptions = [
                    'ExpenseError', 'DatabaseError', 
                    'ValidationError', 'ExportError'
                ]
                
                for exc in custom_exceptions:
                    if hasattr(exceptions, exc):
                        self.print_check(f"Custom exception {exc} exists", True)
                    else:
                        self.print_check(f"Custom exception {exc} exists", False)
                        
            except Exception as e:
                self.print_check("Exceptions module", False, str(e))
        
        # Check try-except in database operations
        db_service_path = self.project_root / "services" / "database_service.py"
        if db_service_path.exists():
            with open(db_service_path, 'r') as f:
                content = f.read()
            
            # Check for error handling patterns
            if 'try:' in content and 'except' in content:
                self.print_check("Try-except blocks in database service", True)
            else:
                self.print_check("Try-except blocks in database service", False,
                               "Add error handling to database operations")
            
            if 'raise' in content:
                self.print_check("Proper exception raising", True)
            else:
                self.print_check("Proper exception raising", False,
                               "Raise exceptions for error conditions")
    
    def run_integration_test(self):
        """Run an integration test of Phase 2 features"""
        self.print_header("INTEGRATION TEST")
        
        try:
            # Create a temporary test environment
            temp_dir = tempfile.mkdtemp()
            print(f"Creating test environment in: {temp_dir}")
            
            # Test if we can import and use the system
            sys.path.insert(0, str(self.project_root))
            
            # Try to import key components
            imports_to_test = [
                ("config.database_config", "DatabaseConfig"),
                ("services.database_service", "DatabaseService"),
                ("services.expense_service", "ExpenseService"),
                ("utils.validation", "validate_date"),
                ("utils.validation", "validate_amount"),
            ]
            
            all_imports_ok = True
            for module_name, item_name in imports_to_test:
                try:
                    module = __import__(module_name, fromlist=[item_name])
                    getattr(module, item_name)
                    self.print_check(f"Import {module_name}.{item_name}", True)
                except ImportError as e:
                    self.print_check(f"Import {module_name}.{item_name}", False, str(e))
                    all_imports_ok = False
            
            if all_imports_ok:
                # Try to create and use a database connection
                from config.database_config import DatabaseConfig
                
                # Use a test database
                test_db_path = Path(temp_dir) / "test_expenses.db"
                original_db_path = None
                
                # Temporarily modify database path if possible
                db_config = DatabaseConfig()
                if hasattr(db_config, 'db_path'):
                    original_db_path = db_config.db_path
                    db_config.db_path = test_db_path
                
                try:
                    # Initialize test database
                    db_config.initialize_database()
                    
                    # Test adding an expense
                    from services.database_service import DatabaseService
                    from models.expense_model import Expense
                    
                    db_service = DatabaseService()
                    
                    # Create test expense
                    test_expense = Expense(
                        date=date.today(),
                        category="Test Category",
                        amount=Decimal("10000"),
                        description="Test expense"
                    )
                    
                    expense_id = db_service.add_expense(test_expense)
                    self.print_check("Add expense to database", expense_id > 0,
                                   f"Added expense with ID: {expense_id}")
                    
                    # Test retrieving expense
                    retrieved = db_service.get_expense(expense_id)
                    self.print_check("Retrieve expense from database", retrieved is not None,
                                   f"Retrieved expense: {retrieved}")
                    
                    # Test filtering
                    expenses = db_service.get_expenses(category="Test Category")
                    self.print_check("Filter expenses by category", len(expenses) > 0,
                                   f"Found {len(expenses)} expenses in category")
                    
                    # Clean up
                    db_service.delete_expense(expense_id)
                    
                finally:
                    # Restore original database path if modified
                    if original_db_path and hasattr(db_config, 'db_path'):
                        db_config.db_path = original_db_path
                    
                    # Clean up temp directory
                    shutil.rmtree(temp_dir)
            
        except Exception as e:
            self.print_check("Integration test", False, f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def calculate_score(self):
        """Calculate and display final score"""
        percentage = (self.score / self.total_checks * 100) if self.total_checks > 0 else 0
        
        self.print_header("PHASE 2 VERIFICATION RESULTS")
        
        print(f"\n{Fore.CYAN}📊 OVERALL SCORE: {self.score}/{self.total_checks} ({percentage:.1f}%){Style.RESET_ALL}")
        
        # Progress bar
        bar_length = 50
        filled = int(percentage / 100 * bar_length)
        bar = f"{Fore.GREEN}{'█' * filled}{Fore.WHITE}{'░' * (bar_length - filled)}{Style.RESET_ALL}"
        print(f"  [{bar}]")
        
        # Phase completion assessment
        print(f"\n{Fore.CYAN}📈 PHASE 2 COMPLETION:{Style.RESET_ALL}")
        
        if percentage >= 90:
            print(f"{Fore.GREEN}🎉 Excellent! Phase 2 is complete. Ready for Phase 3.{Style.RESET_ALL}")
        elif percentage >= 70:
            print(f"{Fore.YELLOW}📝 Good progress. Review the failed checks above.{Style.RESET_ALL}")
        elif percentage >= 50:
            print(f"{Fore.YELLOW}⚡ Halfway there. Focus on the critical checks.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}🚧 Needs work. Start with CRUD operations and testing.{Style.RESET_ALL}")
        
        # Recommendations
        print(f"\n{Fore.CYAN}📋 RECOMMENDATIONS:{Style.RESET_ALL}")
        
        if percentage < 70:
            print("1. Ensure all CRUD operations are implemented in database_service.py")
            print("2. Set up pytest and create basic test files")
            print("3. Implement error handling in utils/exceptions.py")
            print("4. Create sample data generator in generate/sample_data.py")
        
        print(f"\n{Fore.CYAN}Next: Run 'python phase2-verify.py' after implementing fixes.{Style.RESET_ALL}")
    
    def run_all_checks(self):
        """Run all Phase 2 checks"""
        self.print_header("DAILY EXPENSE TRACKER - PHASE 2 VERIFICATION")
        print(f"Project location: {self.project_root}\n")
        
        self.check_crud_operations()
        self.check_business_logic()
        self.check_filtering_search()
        self.check_testing_framework()
        self.check_test_data_generation()
        self.check_error_handling()
        self.run_integration_test()
        self.calculate_score()


def main():
    """Main function"""
    verifier = Phase2Verifier()
    verifier.run_all_checks()


if __name__ == "__main__":
    main()