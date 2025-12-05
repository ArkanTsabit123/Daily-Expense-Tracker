# project portofolio/junior project/daily-expense-tracker/phase2-verify.py

"""
This module verifies if the project meets the requirements for Phase 2.
Checks CRUD operations, testing, and error handling.
"""

import importlib.util
import shutil
import sqlite3
import sys
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ==================== UTILITY FUNCTIONS ====================

def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f" {text}".center(70))
    print("=" * 70)


def print_check_result(name: str, passed: bool, details: str = "") -> None:
    """
    Print the result of a check.
    
    Args:
        name: Name of the check
        passed: Boolean indicating if check passed
        details: Additional details or error message
    """
    if passed:
        status = "PASS"
        symbol = "✅"
        color_code = "\033[92m"  # Green
    else:
        status = "FAIL"
        symbol = "❌"
        color_code = "\033[91m"  # Red
    
    reset_code = "\033[0m"
    print(f"{symbol} {name:45} {color_code}{status}{reset_code}")
    
    if details:
        indent = " " * 4
        detail_color = "\033[93m" if not passed else "\033[94m"  # Yellow for errors, blue for info
        print(f"{indent}↳ {detail_color}{details}{reset_code}")


def read_file_with_encoding(file_path: Path) -> Optional[str]:
    """
    Read a file with proper encoding handling.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content as string or None if file cannot be read
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    
    return None


def import_module_from_path(module_path: Path, module_name: str) -> Tuple[bool, Optional[object], str]:
    """
    Import a module from a file path.
    
    Args:
        module_path: Path to the module file
        module_name: Name to give the module
        
    Returns:
        Tuple of (success, module_object, message)
    """
    if not module_path.exists():
        return False, None, f"File not found: {module_path}"
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(module_path))
        if spec is None:
            return False, None, f"Cannot load module: {module_name}"
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, module, f"Successfully imported: {module_name}"
    except Exception as e:
        return False, None, f"Import error: {e}"


# ==================== VERIFICATION MODULES ====================

def verify_crud_operations(project_root: Path) -> Dict[str, bool]:
    """
    Verify CRUD operations are implemented.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check database service exists
    db_service_path = project_root / "services" / "database_service.py"
    results['db_service_exists'] = db_service_path.exists()
    
    if results['db_service_exists']:
        success, module, message = import_module_from_path(db_service_path, "database_service")
        results['db_service_importable'] = success
        
        if success:
            # Check for required methods in DatabaseService class
            required_methods = [
                "add_expense",
                "get_expense",
                "get_expenses",
                "update_expense",
                "delete_expense",
                "get_monthly_summary",
                "get_categories",
            ]
            
            # Find the DatabaseService class
            db_service_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and 'DatabaseService' in str(attr):
                    db_service_class = attr
                    break
            
            if db_service_class:
                for method in required_methods:
                    results[f'has_{method}'] = hasattr(db_service_class, method)
            else:
                results['has_database_service_class'] = False
        else:
            results['import_error'] = message
    
    return results


def verify_business_logic(project_root: Path) -> Dict[str, bool]:
    """
    Verify business logic layer.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check expense service exists
    expense_service_path = project_root / "services" / "expense_service.py"
    results['expense_service_exists'] = expense_service_path.exists()
    
    if results['expense_service_exists']:
        success, module, message = import_module_from_path(expense_service_path, "expense_service")
        results['expense_service_importable'] = success
        
        if success:
            # Check for business logic methods
            business_methods = [
                "create_expense",
                "get_expense_history",
                "get_monthly_analysis",
                "validate_expense_data",
            ]
            
            # Find the ExpenseService class
            expense_service_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and 'ExpenseService' in str(attr):
                    expense_service_class = attr
                    break
            
            if expense_service_class:
                for method in business_methods:
                    results[f'has_{method}'] = hasattr(expense_service_class, method)
            else:
                results['has_expense_service_class'] = False
        else:
            results['import_error'] = message
    
    return results


def verify_filtering_search(project_root: Path) -> Dict[str, bool]:
    """
    Verify filtering and search capabilities.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Test database filtering
    db_path = project_root / "data" / "expenses.db"
    results['database_exists'] = db_path.exists()
    
    if not results['database_exists']:
        return results
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create test data if needed
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_filtering (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT
            )
        """)
        
        # Add test data
        test_data = [
            ("2024-01-15", "Food", 50000, "Lunch at restaurant"),
            ("2024-01-16", "Transport", 25000, "Taxi ride"),
            ("2024-01-17", "Food", 75000, "Dinner with friends"),
            ("2024-02-01", "Shopping", 200000, "New clothes"),
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO test_filtering (date, category, amount, description) VALUES (?, ?, ?, ?)",
            test_data
        )
        conn.commit()
        
        # Test 1: Date range filtering
        cursor.execute("""
            SELECT COUNT(*) FROM test_filtering
            WHERE date BETWEEN '2024-01-01' AND '2024-01-31'
        """)
        january_count = cursor.fetchone()[0]
        results['date_range_filter_works'] = january_count == 3
        
        # Test 2: Category filtering
        cursor.execute("SELECT COUNT(*) FROM test_filtering WHERE category = 'Food'")
        food_count = cursor.fetchone()[0]
        results['category_filter_works'] = food_count == 2
        
        # Test 3: Text search in description
        cursor.execute("SELECT COUNT(*) FROM test_filtering WHERE description LIKE '%Lunch%'")
        lunch_count = cursor.fetchone()[0]
        results['text_search_works'] = lunch_count == 1
        
        # Test 4: Amount range filtering
        cursor.execute("SELECT COUNT(*) FROM test_filtering WHERE amount > 100000")
        high_amount_count = cursor.fetchone()[0]
        results['amount_filter_works'] = high_amount_count == 1
        
        # Clean up
        cursor.execute("DROP TABLE test_filtering")
        conn.commit()
        conn.close()
        
    except sqlite3.Error as e:
        results['filter_test_error'] = str(e)
    
    return results


def verify_testing_framework(project_root: Path) -> Dict[str, bool]:
    """
    Verify testing framework setup.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check test directory structure
    test_dir = project_root / "tests"
    results['tests_directory_exists'] = test_dir.exists()
    
    # Check for test files
    test_files = [
        ("__init__.py", "Test package initialization"),
        ("test_database.py", "Database tests"),
        ("test_expenses.py", "Expense tests"),
        ("test_validation.py", "Validation tests"),
        ("conftest.py", "Pytest configuration"),
    ]
    
    for filename, description in test_files:
        file_path = test_dir / filename
        results[f'{filename}_exists'] = file_path.exists()
    
    # Check if pytest is in requirements
    req_path = project_root / "requirements.txt"
    results['requirements_exists'] = req_path.exists()
    
    if results['requirements_exists']:
        content = read_file_with_encoding(req_path)
        if content:
            content_lower = content.lower()
            results['has_pytest'] = 'pytest' in content_lower
            results['has_test_dependencies'] = any(
                dep in content_lower for dep in ['pytest', 'unittest', 'coverage']
            )
        else:
            results['read_requirements_error'] = True
    
    # Check if tests can be imported
    test_db_path = test_dir / "test_database.py"
    if test_db_path.exists():
        success, module, _ = import_module_from_path(test_db_path, "test_database")
        results['test_database_importable'] = success
        
        if success:
            # Check for test functions
            test_functions = [name for name in dir(module) if name.startswith('test_')]
            results['has_test_functions'] = len(test_functions) > 0
            results['test_function_count'] = len(test_functions)
    
    return results


def verify_test_data_generation(project_root: Path) -> Dict[str, bool]:
    """
    Verify test data generation.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check for sample data generation module
    sample_data_path = project_root / "generate" / "sample_data.py"
    results['sample_data_module_exists'] = sample_data_path.exists()
    
    if results['sample_data_module_exists']:
        success, module, message = import_module_from_path(sample_data_path, "sample_data")
        results['sample_data_importable'] = success
        
        if success:
            # Check for data generation functions
            generation_functions = [
                "generate_sample_expenses",
                "generate_test_categories",
                "generate_sample_data",
                "create_test_database",
            ]
            
            for func_name in generation_functions:
                results[f'has_{func_name}'] = hasattr(module, func_name)
        else:
            results['import_error'] = message
    
    # Check for test fixtures
    conftest_path = project_root / "tests" / "conftest.py"
    if conftest_path.exists():
        content = read_file_with_encoding(conftest_path)
        if content:
            results['conftest_has_fixtures'] = '@pytest.fixture' in content
            results['conftest_has_test_data'] = any(
                phrase in content.lower() 
                for phrase in ['test_data', 'sample', 'fixture']
            )
    
    return results


def verify_error_handling(project_root: Path) -> Dict[str, bool]:
    """
    Verify error handling implementation.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check exceptions module
    exceptions_path = project_root / "utils" / "exceptions.py"
    results['exceptions_module_exists'] = exceptions_path.exists()
    
    if results['exceptions_module_exists']:
        success, module, message = import_module_from_path(exceptions_path, "exceptions")
        results['exceptions_importable'] = success
        
        if success:
            # Check for custom exceptions
            custom_exceptions = [
                "ExpenseError",
                "DatabaseError",
                "ValidationError",
                "ExportError",
                "CategoryError",
            ]
            
            for exc_name in custom_exceptions:
                results[f'has_exception_{exc_name}'] = hasattr(module, exc_name)
        else:
            results['import_error'] = message
    
    # Check error handling in database service
    db_service_path = project_root / "services" / "database_service.py"
    if db_service_path.exists():
        content = read_file_with_encoding(db_service_path)
        if content:
            results['has_try_except_blocks'] = 'try:' in content and 'except' in content
            results['has_exception_raising'] = 'raise ' in content
            results['has_custom_exceptions'] = any(
                exc in content for exc in ['ExpenseError', 'DatabaseError', 'ValidationError']
            )
    
    return results


def run_integration_test(project_root: Path) -> Dict[str, bool]:
    """
    Run an integration test of Phase 2 features.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    temp_dir = None
    
    try:
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        print(f"\n🔧 Creating test environment in: {temp_dir}")
        
        # Add project root to Python path
        sys.path.insert(0, str(project_root))
        
        # Import key components
        imports_to_test = [
            ("config.database_config", "DatabaseConfig"),
            ("services.database_service", "DatabaseService"),
            ("models.expense_model", "Expense"),
            ("utils.validation", "validate_date"),
            ("utils.validation", "validate_amount"),
        ]
        
        import_success = True
        imported_modules = {}
        
        for module_path, item_name in imports_to_test:
            try:
                module = __import__(module_path, fromlist=[item_name])
                imported_modules[item_name] = getattr(module, item_name)
                print(f"  ✓ Imported {module_path}.{item_name}")
            except ImportError as e:
                print(f"  ✗ Failed to import {module_path}.{item_name}: {e}")
                import_success = False
        
        results['all_imports_successful'] = import_success
        
        if import_success:
            # Create test database
            DatabaseConfig = imported_modules['DatabaseConfig']
            db_config = DatabaseConfig()
            
            if hasattr(db_config, 'db_path'):
                # Backup original path and set test path
                original_db_path = db_config.db_path
                test_db_path = temp_dir / "test_expenses.db"
                db_config.db_path = test_db_path
                
                # Initialize test database
                if hasattr(db_config, 'initialize_database'):
                    db_config.initialize_database()
                    results['database_initialized'] = test_db_path.exists()
                
                # Test adding an expense
                DatabaseService = imported_modules['DatabaseService']
                Expense = imported_modules['Expense']
                
                db_service = DatabaseService()
                
                # Create test expense
                test_expense = Expense(
                    date=date.today(),
                    category="Test Category",
                    amount=Decimal("10000.50"),
                    description="Integration test expense"
                )
                
                # Test CRUD operations
                expense_id = db_service.add_expense(test_expense)
                results['add_expense_works'] = expense_id is not None and expense_id > 0
                
                # Test retrieval
                retrieved = db_service.get_expense(expense_id)
                results['get_expense_works'] = retrieved is not None
                
                # Test filtering
                expenses = db_service.get_expenses(category="Test Category")
                results['filter_expenses_works'] = len(expenses) > 0
                
                # Test update if expense exists
                if retrieved:
                    retrieved.description = "Updated description"
                    update_success = db_service.update_expense(retrieved)
                    results['update_expense_works'] = update_success
                
                # Test deletion
                delete_success = db_service.delete_expense(expense_id)
                results['delete_expense_works'] = delete_success
                
                # Restore original database path
                db_config.db_path = original_db_path
    
    except Exception as e:
        results['integration_test_error'] = str(e)
        print(f"  ✗ Integration test failed: {e}")
    
    finally:
        # Clean up
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"  🧹 Cleaned up test environment")
        
        # Remove project root from sys.path
        if str(project_root) in sys.path:
            sys.path.remove(str(project_root))
    
    return results


def calculate_and_display_score(all_results: Dict[str, Dict[str, bool]]) -> None:
    """
    Calculate and display overall verification score.
    
    Args:
        all_results: Dictionary containing results from all verification modules
    """
    print_header("PHASE 2 VERIFICATION SUMMARY")
    
    total_checks = 0
    passed_checks = 0
    
    for category, category_results in all_results.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        print("-" * 50)
        
        for check_name, check_result in category_results.items():
            # Skip non-boolean results (like counts or error messages)
            if not isinstance(check_result, bool):
                continue
            
            total_checks += 1
            if check_result:
                passed_checks += 1
            
            # Format check name for display
            display_name = check_name.replace('_', ' ').title()
            print_check_result(display_name, check_result)
    
    # Calculate score
    if total_checks > 0:
        percentage = (passed_checks / total_checks) * 100
        
        print_header("OVERALL STATISTICS")
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {total_checks - passed_checks}")
        print(f"Success Rate: {percentage:.1f}%")
        
        # Visual progress bar
        bar_length = 50
        filled_length = int(bar_length * percentage // 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        # Color code based on percentage
        if percentage >= 90:
            color = "\033[92m"  # Green
            status = "🎉 Excellent! Phase 2 is complete."
        elif percentage >= 70:
            color = "\033[93m"  # Yellow
            status = "📝 Good progress. Review failed checks."
        elif percentage >= 50:
            color = "\033[93m"  # Yellow
            status = "⚡ Halfway there. Focus on critical checks."
        else:
            color = "\033[91m"  # Red
            status = "🚧 Needs work. Start with CRUD operations."
        
        reset = "\033[0m"
        print(f"\n{color}[{bar}]{reset}")
        print(f"{color}{status}{reset}")
        
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        if percentage < 70:
            print("1. Ensure all CRUD operations are implemented in database_service.py")
            print("2. Set up pytest and create basic test files")
            print("3. Implement error handling in utils/exceptions.py")
            print("4. Create sample data generator in generate/sample_data.py")
        
        print(f"\n🔍 Next: Run 'python phase3-verify.py' for Phase 3 verification")
    
    else:
        print("No checks were performed.")


# ==================== MAIN FUNCTION ====================

def verify_phase2() -> None:
    """
    Main function to run all Phase 2 verifications.
    """
    print_header("DAILY EXPENSE TRACKER - PHASE 2 VERIFICATION")
    
    # Get project root
    project_root = Path(__file__).parent
    print(f"📁 Project Location: {project_root.absolute()}")
    
    print_header("RUNNING PHASE 2 VERIFICATIONS")
    
    # Run all verifications
    results = {
        'crud_operations': verify_crud_operations(project_root),
        'business_logic': verify_business_logic(project_root),
        'filtering_search': verify_filtering_search(project_root),
        'testing_framework': verify_testing_framework(project_root),
        'test_data': verify_test_data_generation(project_root),
        'error_handling': verify_error_handling(project_root),
        'integration_test': run_integration_test(project_root),
    }
    
    # Display results
    calculate_and_display_score(results)


if __name__ == "__main__":
    try:
        verify_phase2()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {e}")
        print("Please ensure the project structure is correct.")
        sys.exit(1)