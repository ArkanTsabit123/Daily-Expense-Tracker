# project portfolio/junior project/daily-expense-tracker/phase2-verify.py

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
from typing import Dict, List, Optional, Tuple, Any


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


def get_class_from_module(module, class_name: str) -> Optional[type]:
    """
    Safely get a class from a module by exact name.
    
    Args:
        module: Module object
        class_name: Exact class name to find
        
    Returns:
        The class if found, None otherwise
    """
    try:
        # Try direct attribute access first
        if hasattr(module, class_name):
            attr = getattr(module, class_name)
            if isinstance(attr, type):
                return attr
        
        # Search through all attributes
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr.__name__ == class_name:
                return attr
        
        return None
    except Exception:
        return None


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
            # Find the DatabaseService class by exact name
            db_service_class = get_class_from_module(module, "DatabaseService")
            results['has_database_service_class'] = db_service_class is not None
            
            if db_service_class:
                # Check for methods based on ACTUAL blueprint (not assumptions)
                # From blueprint: DatabaseService should have these methods
                blueprint_methods = [
                    "add_expense",
                    "get_expenses",
                    "get_monthly_summary",
                    "update_expense",
                    "delete_expense",
                ]
                
                for method in blueprint_methods:
                    has_method = hasattr(db_service_class, method)
                    results[f'has_{method}'] = has_method
                    
                    # Debug: Print if method exists
                    if not has_method:
                        # Check what methods are actually available
                        actual_methods = [m for m in dir(db_service_class) 
                                        if not m.startswith('_') and callable(getattr(db_service_class, m))]
                        results['actual_methods'] = ", ".join(actual_methods) if actual_methods else "None"
            else:
                results['class_not_found'] = True
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
            # Find the ExpenseService class by exact name
            expense_service_class = get_class_from_module(module, "ExpenseService")
            results['has_expense_service_class'] = expense_service_class is not None
            
            if expense_service_class:
                # Check for business logic methods from blueprint
                business_methods = [
                    "create_expense",
                    "get_expense_history",
                    "get_monthly_analysis",
                    "get_categories",
                ]
                
                for method in business_methods:
                    has_method = hasattr(expense_service_class, method)
                    results[f'has_{method}'] = has_method
                    
                    # Debug
                    if not has_method:
                        actual_methods = [m for m in dir(expense_service_class) 
                                        if not m.startswith('_') and callable(getattr(expense_service_class, m))]
                        results['expense_actual_methods'] = ", ".join(actual_methods) if actual_methods else "None"
            else:
                results['expense_class_not_found'] = True
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
    
    # Instead of touching production database, check if filtering code exists
    db_service_path = project_root / "services" / "database_service.py"
    results['db_service_exists'] = db_service_path.exists()
    
    if results['db_service_exists']:
        content = read_file_with_encoding(db_service_path)
        if content:
            # Check for filtering logic in code
            results['has_date_filtering'] = 'strftime' in content or 'date BETWEEN' in content
            results['has_category_filtering'] = 'category =' in content or 'category LIKE' in content
            results['has_month_year_filter'] = 'strftime(\'%Y\', date)' in content or 'strftime(\'%m\', date)' in content
            
            # Check if get_expenses method accepts filter parameters
            results['has_filter_parameters'] = any(
                pattern in content for pattern in [
                    'def get_expenses(self',
                    'get_expenses(self, month',
                    'get_expenses(self, year',
                    'get_expenses(self, category'
                ]
            )
    
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
    
    if results['tests_directory_exists']:
        # Check for required test files
        required_test_files = [
            "test_database.py",
            "test_expenses.py",
            "__init__.py",
        ]
        
        optional_test_files = [
            "test_export.py",
            "test_integration.py",
            "conftest.py",
            "test_helper.py",
        ]
        
        for filename in required_test_files:
            file_path = test_dir / filename
            results[f'{filename}_exists'] = file_path.exists()
        
        for filename in optional_test_files:
            file_path = test_dir / filename
            if file_path.exists():
                results[f'{filename}_exists'] = True
        
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
    
    # Check if pytest is available (in requirements.txt or environment)
    req_path = project_root / "requirements.txt"
    results['requirements_exists'] = req_path.exists()
    
    if results['requirements_exists']:
        content = read_file_with_encoding(req_path)
        if content:
            content_lower = content.lower()
            results['has_pytest'] = 'pytest' in content_lower
            results['has_coverage'] = 'coverage' in content_lower or 'pytest-cov' in content_lower
        else:
            results['read_requirements_error'] = True
    
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
    generate_dir = project_root / "generate"
    results['generate_directory_exists'] = generate_dir.exists()
    
    if results['generate_directory_exists']:
        # Check for sample data file
        sample_data_path = generate_dir / "sample_data.py"
        results['sample_data_module_exists'] = sample_data_path.exists()
        
        if results['sample_data_module_exists']:
            success, module, message = import_module_from_path(sample_data_path, "sample_data")
            results['sample_data_importable'] = success
            
            if success:
                # Check for data generation functions (any function that generates data)
                data_generation_patterns = ['generate', 'create', 'sample', 'test_data']
                
                functions_found = []
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and any(pattern in attr_name.lower() for pattern in data_generation_patterns):
                        functions_found.append(attr_name)
                
                results['has_data_generation_functions'] = len(functions_found) > 0
                results['data_function_count'] = len(functions_found)
                if functions_found:
                    results['data_functions_list'] = ", ".join(functions_found[:5])
            else:
                results['import_error'] = message
    
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
        # Check file content for custom exceptions
        content = read_file_with_encoding(exceptions_path)
        if content:
            # Look for class definitions that look like exceptions
            results['has_exception_classes'] = 'class.*Error' in content or 'Exception' in content
            results['has_custom_exceptions'] = any(
                phrase in content for phrase in [
                    'class ExpenseError',
                    'class DatabaseError',
                    'class ValidationError',
                    'Exception'
                ]
            )
    else:
        # If no exceptions.py, check if error handling exists in services
        db_service_path = project_root / "services" / "database_service.py"
        if db_service_path.exists():
            content = read_file_with_encoding(db_service_path)
            if content:
                results['has_try_except'] = 'try:' in content and 'except' in content
                results['has_error_messages'] = 'error' in content.lower() or 'Error' in content
    
    return results


def verify_imports_and_initialization(project_root: Path) -> Dict[str, bool]:
    """
    Verify that key modules can be imported and initialized.
    SAFE version - doesn't execute any database operations.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # List of key imports to test
    key_imports = [
        ("config.database_config", "DatabaseConfig"),
        ("services.database_service", "DatabaseService"),
        ("services.expense_service", "ExpenseService"),
        ("models.expense_model", "Expense"),
        ("utils.validation", "validate_date"),
        ("utils.validation", "validate_amount"),
        ("utils.formatters", "format_currency"),
    ]
    
    sys.path.insert(0, str(project_root))
    
    try:
        import_stats = {}
        
        for module_path, item_name in key_imports:
            try:
                # Convert module path to file path
                parts = module_path.split('.')
                if len(parts) == 2:
                    folder, file = parts
                    file_path = project_root / folder / f"{file}.py"
                else:
                    folder = parts[0]
                    file = parts[1]
                    file_path = project_root / folder / f"{file}.py"
                
                if file_path.exists():
                    # Try to import
                    module = __import__(module_path, fromlist=[item_name])
                    
                    # Check if item exists in module
                    if hasattr(module, item_name):
                        import_stats[f"import_{item_name}"] = True
                        results[f"import_{item_name}"] = True
                    else:
                        import_stats[f"import_{item_name}"] = False
                        results[f"import_{item_name}"] = False
                        results[f"{item_name}_not_in_module"] = True
                else:
                    import_stats[f"import_{item_name}"] = False
                    results[f"import_{item_name}"] = False
                    results[f"{item_name}_file_missing"] = True
                    
            except ImportError as e:
                import_stats[f"import_{item_name}"] = False
                results[f"import_{item_name}"] = False
                results[f"{item_name}_import_error"] = str(e)
            except Exception as e:
                import_stats[f"import_{item_name}"] = False
                results[f"import_{item_name}"] = False
                results[f"{item_name}_error"] = str(e)
        
        # Calculate import success rate
        successful_imports = sum(1 for v in import_stats.values() if v)
        total_imports = len(import_stats)
        results['import_success_rate'] = (successful_imports / total_imports * 100) if total_imports > 0 else 0
        
        # Test initialization (without database operations)
        if results.get('import_DatabaseConfig', False) and results.get('import_DatabaseService', False):
            try:
                from config.database_config import DatabaseConfig
                from services.database_service import DatabaseService
                
                # Just create instances, don't connect to database
                config = DatabaseConfig()
                service = DatabaseService()
                
                results['config_initializable'] = True
                results['service_initializable'] = True
                
                # Check if they have required attributes
                results['config_has_db_path'] = hasattr(config, 'db_path')
                results['service_has_db_service'] = hasattr(service, 'db_service') or hasattr(service, 'db_config')
                
            except Exception as e:
                results['initialization_error'] = str(e)
                
    finally:
        if str(project_root) in sys.path:
            sys.path.remove(str(project_root))
    
    return results


def calculate_and_display_score(all_results: Dict[str, Dict[str, Any]]) -> None:
    """
    Calculate and display overall verification score.
    
    Args:
        all_results: Dictionary containing results from all verification modules
    """
    print_header("PHASE 2 VERIFICATION SUMMARY")
    print("🔧 PHASE 2: CRUD OPERATIONS & TESTING")
    print("📋 Checking: CRUD, Business Logic, Filtering, Testing, Error Handling")
    
    total_checks = 0
    passed_checks = 0
    
    # Category display names
    category_names = {
        'crud_operations': "🗃️  CRUD Operations",
        'business_logic': "💼 Business Logic",
        'filtering_search': "🔍 Filtering & Search",
        'testing_framework': "🧪 Testing Framework",
        'test_data': "📊 Test Data Generation",
        'error_handling': "⚠️  Error Handling",
        'imports_and_initialization': "📦 Imports & Initialization",
    }
    
    for category, category_results in all_results.items():
        display_name = category_names.get(category, category.replace('_', ' ').title())
        print(f"\n{display_name}:")
        print("-" * 50)
        
        for check_name, check_result in category_results.items():
            # Skip non-boolean results and debug info
            skip_patterns = ['error', 'actual_methods', 'list', 'rate', 'count', 'debug']
            if any(pattern in check_name.lower() for pattern in skip_patterns):
                continue
            
            if isinstance(check_result, bool):
                total_checks += 1
                if check_result:
                    passed_checks += 1
                
                # Format check name for display
                display_name = check_name.replace('_', ' ').title()
                print_check_result(display_name, check_result)
    
    # Calculate overall score
    if total_checks > 0:
        percentage = (passed_checks / total_checks) * 100
        
        print_header("OVERALL STATISTICS")
        print(f"📈 Total Checks: {total_checks}")
        print(f"✅ Passed: {passed_checks}")
        print(f"❌ Failed: {total_checks - passed_checks}")
        print(f"📊 Success Rate: {percentage:.1f}%")
        
        # Visual progress bar
        bar_length = 50
        filled_length = int(bar_length * percentage // 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"\n[{bar}]")
        
        # Status based on percentage
        if percentage >= 80:
            status_color = "\033[92m"
            status = "✅ Excellent! Phase 2 is well implemented."
        elif percentage >= 60:
            status_color = "\033[93m"
            status = "📊 Good progress. Some minor issues."
        elif percentage >= 40:
            status_color = "\033[93m"
            status = "⚡ Moderate progress. Needs attention."
        else:
            status_color = "\033[91m"
            status = "🚧 Needs significant work."
        
        reset = "\033[0m"
        print(f"{status_color}{status}{reset}")
        
        # Next steps
        print("\n" + "=" * 70)
        if percentage >= 80:
            print("🎉 PHASE 2 COMPLETED! Ready for Phase 3.")
            print("👉 Next step: Run 'python phase3-verify.py' for Phase 3 verification")
        else:
            print("⚠️  PHASE 2 INCOMPLETE - Some checks failed.")
            print("👉 Next step: Run 'python phase2-fixer.py' to fix issues")
        print("=" * 70)


# ==================== MAIN FUNCTION ====================

def verify_phase2() -> None:
    """
    Main function to run all Phase 2 verifications.
    """
    print_header("DAILY EXPENSE TRACKER - PHASE 2 VERIFICATION")
    print("🔧 CRUD OPERATIONS & TESTING CHECK")
    
    # Get project root
    project_root = Path(__file__).parent
    print(f"📁 Project Location: {project_root.absolute()}")
    print(f"⚙️  Phase Focus: CRUD Operations, Business Logic, Testing")
    
    print_header("RUNNING PHASE 2 VERIFICATIONS")
    print("This may take a moment...")
    
    # Run all verifications
    results = {
        'crud_operations': verify_crud_operations(project_root),
        'business_logic': verify_business_logic(project_root),
        'filtering_search': verify_filtering_search(project_root),
        'testing_framework': verify_testing_framework(project_root),
        'test_data': verify_test_data_generation(project_root),
        'error_handling': verify_error_handling(project_root),
        'imports_and_initialization': verify_imports_and_initialization(project_root),
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
        import traceback
        traceback.print_exc()
        sys.exit(1)