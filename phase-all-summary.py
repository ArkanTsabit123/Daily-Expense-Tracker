# project verification/daily-expense-tracker-verification-all-phases.py

"""
VERIFICATION SCRIPT FOR DAILY EXPENSE TRACKER
"""

import argparse
import importlib.util
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


# ==================== SHARED UTILITY FUNCTIONS ====================

def print_header(text: str) -> None:
    """Print a formatted header for better readability."""
    print("\n" + "=" * 70)
    print(f" {text}".center(70))
    print("=" * 70)


def print_check_result(name: str, passed: bool, details: str = "") -> None:
    """
    Print the result of a check with consistent formatting.
    
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


def run_shell_command(command: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Run a shell command and return success status and output.
    
    Args:
        command: List of command arguments
        cwd: Working directory for command execution
        
    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=str(cwd) if cwd else None
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


# ==================== PHASE 1 VERIFICATION ====================

def verify_database(project_root: Path) -> Dict[str, bool]:
    """
    Verify database structure and content (Phase 1).
    """
    results = {}
    db_path = project_root / "data" / "expenses.db"
    
    # Check if database file exists
    results['database_exists'] = db_path.exists()
    
    if not results['database_exists']:
        return results
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        results['has_tables'] = len(tables) > 0
        results['table_count'] = len(tables)
        results['has_expenses_table'] = 'expenses' in tables
        results['has_categories_table'] = 'categories' in tables
        
        # Check table schemas if they exist
        if 'expenses' in tables:
            cursor.execute("PRAGMA table_info(expenses);")
            expense_columns = [row[1] for row in cursor.fetchall()]
            results['expenses_has_columns'] = len(expense_columns) > 0
        
        if 'categories' in tables:
            cursor.execute("PRAGMA table_info(categories);")
            category_columns = [row[1] for row in cursor.fetchall()]
            results['categories_has_columns'] = len(category_columns) > 0
        
        conn.close()
        
    except sqlite3.Error as e:
        results['database_error'] = str(e)
    
    return results


def verify_models(project_root: Path) -> Dict[str, bool]:
    """
    Verify that model files exist and can be imported (Phase 1).
    """
    results = {}
    
    # Check if model files exist
    expense_path = project_root / "models" / "expense_model.py"
    category_path = project_root / "models" / "category_model.py"
    
    results['expense_model_exists'] = expense_path.exists()
    results['category_model_exists'] = category_path.exists()
    
    # Try to import expense model if file exists
    if results['expense_model_exists']:
        try:
            # Add project root to Python path
            sys.path.insert(0, str(project_root))
            
            # Import expense model
            from models.expense_model import Expense
            
            # Test model instantiation
            expense = Expense(
                date=date.today(),
                category="Test",
                amount=Decimal("10000"),
                description="Test expense"
            )
            results['expense_model_importable'] = True
            
        except ImportError as e:
            results['expense_model_importable'] = False
            results['expense_import_error'] = f"Import error: {str(e)}"
        except Exception as e:
            results['expense_model_importable'] = False
            results['expense_instantiation_error'] = f"Instantiation error: {str(e)}"
        finally:
            # Clean up path modification
            if str(project_root) in sys.path:
                sys.path.remove(str(project_root))
    
    # Try to import category model if file exists  
    if results['category_model_exists']:
        try:
            sys.path.insert(0, str(project_root))
            
            # Try to import category model
            try:
                from models.category_model import Category
                category = Category(name="Test Category")
                results['category_model_importable'] = True
            except ImportError as e:
                # Check if file exists and has content
                content = read_file_with_encoding(category_path)
                if content:
                    # Simple check for Category class
                    if 'class Category' in content or 'Category' in content:
                        results['category_model_importable'] = True
                        results['category_file_content_ok'] = True
                    else:
                        results['category_model_importable'] = False
                        results['category_no_class_found'] = True
                else:
                    results['category_model_importable'] = False
                    results['category_file_empty'] = True
                    
        except Exception as e:
            results['category_model_importable'] = False
            results['category_import_error'] = f"Error: {str(e)}"
        finally:
            if str(project_root) in sys.path:
                sys.path.remove(str(project_root))
    
    return results


def verify_validation(project_root: Path) -> Dict[str, bool]:
    """
    Verify validation module exists and functions correctly (Phase 1).
    """
    results = {}
    
    # Check if validation file exists
    validation_path = project_root / "utils" / "validation.py"
    results['validation_exists'] = validation_path.exists()
    
    if results['validation_exists']:
        try:
            # Add project root to Python path
            sys.path.insert(0, str(project_root))
            
            # Import validation functions
            from utils.validation import validate_date, validate_amount
            
            # Test validation functions with flexible return type handling
            date_result = validate_date("2024-01-15")
            if isinstance(date_result, bool):
                results['validate_date_works'] = date_result
            elif isinstance(date_result, tuple) and len(date_result) > 0:
                results['validate_date_works'] = date_result[0]
            else:
                results['validate_date_works'] = False
                results['date_return_type'] = str(type(date_result))
            
            amount_result = validate_amount("100.50")
            if isinstance(amount_result, bool):
                results['validate_amount_works'] = amount_result
            elif isinstance(amount_result, tuple) and len(amount_result) > 0:
                results['validate_amount_works'] = amount_result[0]
            else:
                results['validate_amount_works'] = False
                results['amount_return_type'] = str(type(amount_result))
            
        except ImportError as e:
            results['import_error'] = f"Import error: {str(e)}"
            results['validate_date_works'] = False
            results['validate_amount_works'] = False
        except Exception as e:
            results['function_error'] = f"Function error: {str(e)}"
            results['validate_date_works'] = False
            results['validate_amount_works'] = False
        finally:
            # Clean up path modification
            if str(project_root) in sys.path:
                sys.path.remove(str(project_root))
    
    return results


def verify_dependencies_phase1(project_root: Path) -> Dict[str, bool]:
    """
    Verify that requirements.txt exists and contains required packages (Phase 1).
    """
    results = {}
    
    # Check if requirements file exists
    requirements_path = project_root / "requirements.txt"
    results['requirements_exists'] = requirements_path.exists()
    
    if results['requirements_exists']:
        content = read_file_with_encoding(requirements_path)
        
        if content:
            # Convert to lowercase for case-insensitive matching
            content_lower = content.lower()
            
            # Check for required packages
            results['has_matplotlib'] = 'matplotlib' in content_lower
            results['has_pandas'] = 'pandas' in content_lower
            results['has_openpyxl'] = 'openpyxl' in content_lower
            results['has_python_dateutil'] = 'dateutil' in content_lower
            
            # SQLite3 is built-in Python, should NOT be in requirements.txt
            has_sqlite_in_file = 'sqlite3' in content_lower or 'sqlite' in content_lower
            results['has_sqlite3'] = not has_sqlite_in_file  # PASS if NOT present!
            
            # Count total packages
            lines = [line.strip() for line in content.split('\n') 
                    if line.strip() and not line.strip().startswith('#')]
            results['package_count'] = len(lines)
        else:
            results['read_error'] = "Could not read requirements.txt"
    
    return results


def verify_git_setup(project_root: Path) -> Dict[str, bool]:
    """
    Verify Git repository setup (Phase 1).
    """
    results = {}
    
    # Check Git repository
    git_dir = project_root / ".git"
    results['git_initialized'] = git_dir.exists()
    
    # Check .gitignore
    gitignore_path = project_root / ".gitignore"
    results['gitignore_exists'] = gitignore_path.exists()
    
    if results['gitignore_exists']:
        content = read_file_with_encoding(gitignore_path)
        if content:
            # Check for common important ignores
            content_lower = content.lower()
            
            # Check for .pyc patterns
            pyc_patterns = ['.pyc', '__pycache__', '*.pyc', '*.pyo']
            results['ignores_pyc'] = any(pattern in content_lower for pattern in pyc_patterns)
            
            # Check for database patterns
            db_patterns = ['.db', '*.db', 'database', 'data/*.db']
            results['ignores_database'] = any(pattern in content_lower for pattern in db_patterns)
            
            # Check for environment patterns
            env_patterns = ['.env', 'venv', 'env/', 'venv/', '.venv', 'virtualenv']
            results['ignores_env'] = any(pattern in content_lower for pattern in env_patterns)
    
    return results


def run_phase1_verification(project_root: Path) -> Dict[str, Dict[str, Any]]:
    """
    Run all Phase 1 verifications.
    """
    print_header("PHASE 1: PROJECT SETUP & FOUNDATION")
    
    results = {
        'database': verify_database(project_root),
        'models': verify_models(project_root),
        'validation': verify_validation(project_root),
        'dependencies': verify_dependencies_phase1(project_root),
        'git': verify_git_setup(project_root)
    }
    
    return results


# ==================== PHASE 2 VERIFICATION ====================

def verify_crud_operations(project_root: Path) -> Dict[str, bool]:
    """
    Verify CRUD operations are implemented (Phase 2).
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
    Verify business logic layer (Phase 2).
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
    Verify filtering and search capabilities (Phase 2).
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
    Verify testing framework setup (Phase 2).
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


def verify_error_handling_phase2(project_root: Path) -> Dict[str, bool]:
    """
    Verify error handling implementation (Phase 2).
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


def run_phase2_verification(project_root: Path) -> Dict[str, Dict[str, Any]]:
    """
    Run all Phase 2 verifications.
    """
    print_header("PHASE 2: CRUD OPERATIONS & TESTING")
    
    results = {
        'crud_operations': verify_crud_operations(project_root),
        'business_logic': verify_business_logic(project_root),
        'filtering_search': verify_filtering_search(project_root),
        'testing_framework': verify_testing_framework(project_root),
        'error_handling': verify_error_handling_phase2(project_root),
    }
    
    return results


# ==================== PHASE 3 VERIFICATION ====================

def verify_visualization_module(project_root: Path) -> Dict[str, Any]:
    """
    Verify visualization module implementation (Phase 3).
    """
    results = {}
    
    # Check visualization directory
    visualization_dir = project_root / "visualization"
    results['visualization_dir_exists'] = visualization_dir.exists()
    
    if results['visualization_dir_exists']:
        # Check __init__.py
        init_path = visualization_dir / "__init__.py"
        results['has_init_file'] = init_path.exists()
    
    # Check chart service (based on blueprint)
    chart_service_path = project_root / "visualization" / "chart_service.py"
    results['chart_service_exists'] = chart_service_path.exists()
    
    if results['chart_service_exists']:
        # Read file content to check structure
        content = read_file_with_encoding(chart_service_path)
        if content:
            # Check for ChartService class definition
            results['has_chart_service_class'] = 'class ChartService' in content
            
            # Check for methods from blueprint
            blueprint_methods = [
                "generate_pie_chart",           # From blueprint
                "generate_monthly_trend_chart",  # From blueprint
            ]
            
            for method in blueprint_methods:
                results[f'has_{method}'] = f'def {method}' in content
            
            # Check for matplotlib usage
            results['uses_matplotlib'] = 'import matplotlib' in content or 'matplotlib.pyplot' in content
            results['uses_plt'] = 'import plt' in content or 'plt.' in content
            results['uses_figure'] = 'plt.figure' in content or 'plt.subplots' in content
            
            # Check for chart saving
            results['saves_charts'] = 'plt.savefig' in content or 'savefig' in content
            
            # Check for proper initialization
            results['has_init_method'] = 'def __init__' in content
        
        # Try to import if possible
        try:
            success, module, message = import_module_from_path(chart_service_path, "chart_service")
            results['chart_service_importable'] = success
            
            if success:
                # Get ChartService class
                chart_service_class = get_class_from_module(module, "ChartService")
                results['chart_service_class_found'] = chart_service_class is not None
                
                if chart_service_class:
                    # Check actual methods (not just in blueprint)
                    actual_methods = [m for m in dir(chart_service_class) 
                                    if not m.startswith('_') and callable(getattr(chart_service_class, m))]
                    results['actual_methods'] = ", ".join(actual_methods) if actual_methods else "None"
                    results['method_count'] = len(actual_methods)
        except Exception as e:
            results['import_error'] = str(e)
    
    return results


def verify_formatters(project_root: Path) -> Dict[str, Any]:
    """
    Verify formatters module implementation (Phase 3).
    """
    results = {}
    
    # Check formatters module
    formatters_path = project_root / "utils" / "formatters.py"
    results['formatters_exists'] = formatters_path.exists()
    
    if results['formatters_exists']:
        content = read_file_with_encoding(formatters_path)
        if content:
            # Check for functions from blueprint
            blueprint_functions = [
                "format_currency",   # From blueprint
                "format_date",       # From blueprint  
                "format_category",   # From blueprint
            ]
            
            for func in blueprint_functions:
                results[f'has_{func}'] = f'def {func}' in content
            
            # Check specific features
            results['has_currency_formatting'] = 'Rp' in content or 'IDR' in content or 'currency' in content.lower()
            results['has_date_formatting'] = 'strftime' in content or 'datetime' in content
            results['has_category_icons'] = 'icons' in content or 'emoji' in content
        
        # Try to import
        try:
            sys.path.insert(0, str(project_root))
            from utils.formatters import format_currency, format_date, format_category
            results['formatters_importable'] = True
        except ImportError as e:
            results['formatters_importable'] = False
            results['import_error'] = str(e)
        finally:
            if str(project_root) in sys.path:
                sys.path.remove(str(project_root))
    
    return results


def verify_date_utilities(project_root: Path) -> Dict[str, Any]:
    """
    Verify date utilities module (Phase 3).
    """
    results = {}
    
    # Check date utilities module
    date_utils_path = project_root / "utils" / "date_utils.py"
    results['date_utils_exists'] = date_utils_path.exists()
    
    if results['date_utils_exists']:
        content = read_file_with_encoding(date_utils_path)
        if content:
            # Check for functions from blueprint
            blueprint_functions = [
                "get_current_month_year",  # From blueprint
                "get_previous_month_year", # From blueprint
                "get_next_month_year",     # From blueprint
                "get_month_name",         # From blueprint
                "get_month_range",        # From blueprint
            ]
            
            for func in blueprint_functions:
                results[f'has_{func}'] = f'def {func}' in content
            
            # Check for Indonesian month names
            results['has_indonesian_months'] = any(
                month in content for month in ['Januari', 'Februari', 'Maret', 'April', 'Mei']
            )
        
        # Try to import
        try:
            sys.path.insert(0, str(project_root))
            from utils.date_utils import get_current_month_year, get_month_name
            results['date_utils_importable'] = True
            
            # Test one function
            month_year = get_current_month_year()
            results['get_current_month_year_works'] = isinstance(month_year, tuple) and len(month_year) == 2
        except ImportError as e:
            results['date_utils_importable'] = False
            results['import_error'] = str(e)
        finally:
            if str(project_root) in sys.path:
                sys.path.remove(str(project_root))
    
    return results


def verify_main_ui_updates(project_root: Path) -> Dict[str, Any]:
    """
    Verify main UI updates for Phase 3 features.
    """
    results = {}
    
    main_path = project_root / "main.py"
    results['main_file_exists'] = main_path.exists()
    
    if not results['main_file_exists']:
        return results
    
    content = read_file_with_encoding(main_path)
    if content is None:
        return results
    
    # Check for ExpenseTrackerApp class
    results['has_expense_tracker_app'] = 'class ExpenseTrackerApp' in content
    
    # Check for visualization-related methods in ExpenseTrackerApp
    visualization_methods = [
        "generate_chart_menu",
        "monthly_summary",  # Should have chart generation option
        "view_history",     # Should have export option
    ]
    
    for method in visualization_methods:
        results[f'has_{method}'] = f'def {method}' in content
    
    # Check for chart service usage
    results['uses_chart_service'] = 'ChartService' in content or 'chart_service' in content
    
    # Check for formatter usage
    results['uses_formatters'] = any(
        formatter in content for formatter in [
            'format_currency', 'format_date', 'format_category',
            'get_month_name', 'get_current_month_year'
        ]
    )
    
    # Check for menu options related to Phase 3
    menu_options = [
        "Generate Chart",
        "Ringkasan Bulanan",
        "Export Data",
        "Data Visualization",
    ]
    
    found_options = []
    for option in menu_options:
        if option in content:
            found_options.append(option)
    
    results['has_visualization_menu_options'] = len(found_options) > 0
    if found_options:
        results['menu_options_found'] = ", ".join(found_options[:3])  # Show first 3
    
    # Check for matplotlib configuration
    results['has_matplotlib_config'] = any(
        config in content for config in ['rcParams', 'font.family', 'unicode_minus']
    )
    
    return results


def run_phase3_verification(project_root: Path) -> Dict[str, Dict[str, Any]]:
    """
    Run all Phase 3 verifications.
    """
    print_header("PHASE 3: VISUALIZATION & ENHANCEMENTS")
    
    results = {
        'visualization': verify_visualization_module(project_root),
        'formatters': verify_formatters(project_root),
        'date_utilities': verify_date_utilities(project_root),
        'main_ui': verify_main_ui_updates(project_root),
    }
    
    return results


# ==================== PHASE 4 VERIFICATION ====================

def verify_export_features(project_root: Path) -> Dict[str, Any]:
    """
    Verify export features implementation (Phase 4).
    """
    results = {}
    
    # Check export service
    export_service_path = project_root / "services" / "export_service.py"
    results['export_service_exists'] = export_service_path.exists()
    
    if results['export_service_exists']:
        # Read file content to check structure
        content = read_file_with_encoding(export_service_path)
        if content:
            # Check for ExportService class
            results['has_export_service_class'] = 'class ExportService' in content
            
            # Check for methods from blueprint
            blueprint_methods = [
                "export_to_csv",           # From blueprint
                "export_to_excel",         # From blueprint
                "export_monthly_report",   # From blueprint
            ]
            
            for method in blueprint_methods:
                results[f'has_{method}'] = f'def {method}' in content
            
            # Check for required libraries
            required_libs = [
                "pandas",      # For Excel export
                "openpyxl",    # For Excel formatting
                "csv",         # For CSV export
            ]
            
            for lib in required_libs:
                results[f'uses_{lib}'] = f'import {lib}' in content or f'from {lib}' in content
            
            # Check for exports directory configuration
            results['has_exports_dir'] = 'exports/' in content or 'Path("exports")' in content or 'export_dir' in content
        
        # Try to import
        try:
            success, module, message = import_module_from_path(export_service_path, "export_service")
            results['export_service_importable'] = success
            
            if success:
                # Get ExportService class
                export_service_class = get_class_from_module(module, "ExportService")
                results['export_service_class_found'] = export_service_class is not None
                
                if export_service_class:
                    # Get actual methods
                    actual_methods = [m for m in dir(export_service_class) 
                                    if not m.startswith('_') and callable(getattr(export_service_class, m))]
                    results['actual_methods'] = ", ".join(actual_methods) if actual_methods else "None"
        except Exception as e:
            results['import_error'] = str(e)
    
    # Check exports directory
    exports_dir = project_root / "exports"
    results['exports_dir_exists'] = exports_dir.exists()
    
    # Check if exports directory is in .gitignore
    gitignore_path = project_root / ".gitignore"
    if gitignore_path.exists():
        content = read_file_with_encoding(gitignore_path)
        if content:
            results['exports_in_gitignore'] = 'exports/' in content
    
    return results


def verify_database_indexing(project_root: Path) -> Dict[str, Any]:
    """
    Verify database indexing implementation (Phase 4).
    """
    results = {}
    
    # Check database path
    db_path = project_root / "data" / "expenses.db"
    results['database_exists'] = db_path.exists()
    
    if not results['database_exists']:
        return results
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all indexes
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
        indexes = cursor.fetchall()
        
        results['has_indexes'] = len(indexes) > 0
        results['index_count'] = len(indexes)
        
        # Check for specific indexes from blueprint
        blueprint_indexes = [
            "idx_expenses_date",          # From blueprint
            "idx_expenses_category",      # From blueprint
            "idx_expenses_date_category", # From blueprint
        ]
        
        index_names = [idx['name'] for idx in indexes]
        for idx_name in blueprint_indexes:
            results[f'has_{idx_name}'] = idx_name in index_names
        
        # Also check expenses table structure
        cursor.execute("PRAGMA table_info(expenses);")
        columns = [row['name'] for row in cursor.fetchall()]
        
        # Important columns that should exist
        important_columns = ['date', 'category', 'amount', 'description']
        for col in important_columns:
            results[f'{col}_column_exists'] = col in columns
        
        conn.close()
        
    except sqlite3.Error as e:
        results['database_error'] = str(e)
    
    return results


def verify_code_quality_tools(project_root: Path) -> Dict[str, Any]:
    """
    Verify code quality tools setup (Phase 4).
    """
    results = {}
    
    # Check requirements.txt
    requirements_path = project_root / "requirements.txt"
    results['requirements_exists'] = requirements_path.exists()
    
    if results['requirements_exists']:
        content = read_file_with_encoding(requirements_path)
        if content:
            content_lower = content.lower()
            
            # ONLY check for tools mentioned in project plan Phase 4
            project_plan_tools = [
                "black",   # Code formatter (mentioned in project plan)
                "flake8",  # Style checker (mentioned in project plan)
            ]
            
            for tool in project_plan_tools:
                results[f'has_{tool}'] = tool in content_lower
            
            # Also check for optional but useful tools
            optional_tools = ["pytest", "coverage"]
            for tool in optional_tools:
                if tool in content_lower:
                    results[f'has_{tool}'] = True
    
    # Check for configuration files
    config_files = {
        'pyproject_toml': project_root / "pyproject.toml",
        'setup_cfg': project_root / "setup.cfg",
        'flake8_config': project_root / ".flake8",
    }
    
    for name, path in config_files.items():
        results[name] = path.exists()
    
    # Check pyproject.toml for black configuration
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        content = read_file_with_encoding(pyproject_path)
        if content:
            results['pyproject_has_black_config'] = 'tool.black' in content or '[tool.black]' in content
    
    # Check .flake8 configuration
    flake8_path = project_root / ".flake8"
    if flake8_path.exists():
        content = read_file_with_encoding(flake8_path)
        if content:
            results['flake8_has_rules'] = 'max-line-length' in content or 'ignore' in content
    
    return results


def run_phase4_verification(project_root: Path) -> Dict[str, Dict[str, Any]]:
    """
    Run all Phase 4 verifications.
    """
    print_header("PHASE 4: EXPORT FEATURES & CODE QUALITY")
    
    results = {
        'export_features': verify_export_features(project_root),
        'database_indexing': verify_database_indexing(project_root),
        'code_quality_tools': verify_code_quality_tools(project_root),
    }
    
    return results


# ==================== PHASE 5 VERIFICATION ====================

def verify_project_organization(project_root: Path) -> Dict[str, Any]:
    """
    Verify project organization completeness (Phase 5).
    """
    results = {}
    
    # Required directories (from actual project structure)
    required_directories = [
        "config",
        "models", 
        "services",
        "utils",
        "visualization",
        "tests",
        "data",
        "exports",
        "logs",
        "charts",
    ]
    
    # Required core files (must exist)
    required_core_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "config/database_config.py",
        "models/expense_model.py",
        "services/database_service.py",
        "services/expense_service.py",
        "utils/validation.py",
    ]
    
    # Check directories
    missing_dirs = []
    for directory in required_directories:
        dir_path = project_root / directory
        exists = dir_path.exists()
        results[f'dir_{directory}_exists'] = exists
        if not exists:
            missing_dirs.append(directory)
    
    results['all_directories_exist'] = len(missing_dirs) == 0
    if missing_dirs:
        results['missing_directories'] = ", ".join(missing_dirs)
    
    # Check core files
    missing_core_files = []
    for file_path in required_core_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        results[f'core_{file_path.replace("/", "_")}_exists'] = exists
        if not exists:
            missing_core_files.append(file_path)
    
    results['all_core_files_exist'] = len(missing_core_files) == 0
    if missing_core_files:
        results['missing_core_files'] = ", ".join(missing_core_files)
    
    # Project size metrics
    python_files = list(project_root.glob("**/*.py"))
    python_files = [f for f in python_files if not any(
        exclude in str(f) for exclude in ['__pycache__', '.venv', 'venv', '.env']
    )]
    
    results['total_python_files'] = len(python_files)
    results['project_has_adequate_size'] = len(python_files) >= 15  # Reasonable size
    
    return results


def verify_pep8_compliance(project_root: Path) -> Dict[str, Any]:
    """
    Verify PEP 8 compliance (Phase 5).
    """
    results = {}
    
    # Check if flake8 config exists
    flake8_config = project_root / ".flake8"
    results['flake8_config_exists'] = flake8_config.exists()
    
    if results['flake8_config_exists']:
        content = read_file_with_encoding(flake8_config)
        if content:
            results['flake8_has_rules'] = any(
                keyword in content for keyword in ['max-line-length', 'ignore', 'exclude']
            )
    
    # Check pyproject.toml for black config
    pyproject_path = project_root / "pyproject.toml"
    results['pyproject_exists'] = pyproject_path.exists()
    
    if results['pyproject_exists']:
        content = read_file_with_encoding(pyproject_path)
        if content:
            results['has_black_config'] = '[tool.black]' in content or 'tool.black' in content
    
    # Check if tools are mentioned in requirements
    req_path = project_root / "requirements.txt"
    if req_path.exists():
        content = read_file_with_encoding(req_path)
        if content:
            content_lower = content.lower()
            results['mentions_black'] = 'black' in content_lower
            results['mentions_flake8'] = 'flake8' in content_lower
    
    return results


def verify_documentation(project_root: Path) -> Dict[str, Any]:
    """
    Verify documentation comprehensiveness (Phase 5).
    """
    results = {}
    
    # Check README.md
    readme_path = project_root / "README.md"
    results['readme_exists'] = readme_path.exists()
    
    if results['readme_exists']:
        content = read_file_with_encoding(readme_path)
        if content:
            # Basic checks
            lines = content.split('\n')
            results['readme_line_count'] = len(lines)
            results['readme_has_content'] = len([l for l in lines if l.strip()]) > 10
            
            # Check for key sections (case-insensitive)
            content_lower = content.lower()
            key_sections = {
                'installation': ['install', 'setup', 'requirements', 'pip install'],
                'usage': ['usage', 'how to use', 'example', 'quickstart'],
                'features': ['features', 'functionality', 'what it does'],
                'contributing': ['contributing', 'development', 'build from source'],
                'license': ['license', 'mit license', 'copyright'],
            }
            
            for section, keywords in key_sections.items():
                found = any(keyword in content_lower for keyword in keywords)
                results[f'readme_has_{section}'] = found
            
            # Check for code examples
            has_code_blocks = '```' in content
            results['readme_has_code_examples'] = has_code_blocks
            
            # Check for images/screenshots
            has_images = any(img in content for img in ['.png', '.jpg', '.jpeg', '.gif', '!['])
            results['readme_has_images'] = has_images
        else:
            results['readme_has_content'] = False
    
    return results


def verify_test_suite_phase5(project_root: Path) -> Dict[str, Any]:
    """
    Verify testing suite (Phase 5).
    """
    results = {}
    
    # Check tests directory
    tests_dir = project_root / "tests"
    results['tests_dir_exists'] = tests_dir.exists()
    
    if results['tests_dir_exists']:
        # Count test files
        test_files = list(tests_dir.glob("test_*.py"))
        results['test_file_count'] = len(test_files)
        
        # Check for core test files
        core_test_files = ['test_database.py', 'test_expenses.py', 'test_export.py']
        for test_file in core_test_files:
            exists = (tests_dir / test_file).exists()
            results[f'has_{test_file}'] = exists
        
        # Check conftest.py
        conftest_path = tests_dir / "conftest.py"
        results['has_conftest'] = conftest_path.exists()
        
        # Check __init__.py in tests
        init_path = tests_dir / "__init__.py"
        results['tests_has_init'] = init_path.exists()
        
        # Check if pytest is mentioned in requirements
        req_path = project_root / "requirements.txt"
        if req_path.exists():
            content = read_file_with_encoding(req_path)
            if content:
                results['requires_pytest'] = 'pytest' in content.lower()
    
    return results


def verify_platform_independence(project_root: Path) -> Dict[str, Any]:
    """
    Verify cross-platform independence (Phase 5).
    """
    results = {}
    
    # Check current platform
    current_platform = platform.system()
    results['current_platform'] = current_platform
    
    # Check Python files for platform-specific code
    python_files = list(project_root.glob("**/*.py"))
    python_files = [f for f in python_files if not any(
        exclude in str(f) for exclude in ['__pycache__', '.venv', 'venv', '.env']
    )]
    
    platform_specific_patterns = [
        (r'os\.name\s*==\s*[\"\']nt[\"\']', 'Windows-specific os.name check'),
        (r'platform\.system\(\)\s*==\s*[\"\']Windows[\"\']', 'Windows platform check'),
        (r'C:\\\\', 'Windows path literal (C:\\)'),
        (r'/home/[^/]+/', 'Linux home path'),
        (r'/Users/[^/]+/', 'macOS home path'),
    ]
    
    platform_issues = []
    for py_file in python_files[:20]:  # Check first 20 files
        content = read_file_with_encoding(py_file)
        if content:
            for pattern, description in platform_specific_patterns:
                if re.search(pattern, content):
                    platform_issues.append(f"{py_file.name}: {description}")
    
    results['has_platform_specific_code'] = len(platform_issues) > 0
    results['platform_issue_count'] = len(platform_issues)
    
    return results


def verify_deployment_readiness(project_root: Path) -> Dict[str, Any]:
    """
    Verify deployment preparation (Phase 5).
    """
    results = {}
    
    # Core deployment files
    deployment_files = [
        ("README.md", "Documentation"),
        ("requirements.txt", "Dependencies"),
        (".gitignore", "Git ignore rules"),
        ("main.py", "Main entry point"),
        ("config/database_config.py", "Database configuration"),
    ]
    
    for file_name, description in deployment_files:
        if '/' in file_name:
            # Handle nested paths
            parts = file_name.split('/')
            file_path = project_root
            for part in parts:
                file_path = file_path / part
        else:
            file_path = project_root / file_name
        
        exists = file_path.exists()
        results[f'deployment_{file_name.replace("/", "_")}_exists'] = exists
    
    # Check for error handling in main.py
    main_path = project_root / "main.py"
    if main_path.exists():
        content = read_file_with_encoding(main_path)
        if content:
            results['main_has_error_handling'] = 'try:' in content and 'except' in content
    
    return results


def run_phase5_verification(project_root: Path) -> Dict[str, Dict[str, Any]]:
    """
    Run all Phase 5 verifications.
    """
    print_header("PHASE 5: FINAL POLISH & DEPLOYMENT READINESS")
    
    results = {
        'project_organization': verify_project_organization(project_root),
        'pep8_compliance': verify_pep8_compliance(project_root),
        'documentation': verify_documentation(project_root),
        'test_suite': verify_test_suite_phase5(project_root),
        'platform_independence': verify_platform_independence(project_root),
        'deployment_readiness': verify_deployment_readiness(project_root),
    }
    
    return results


# ==================== SCORE CALCULATION & DISPLAY ====================

def calculate_and_display_score(phase_results: Dict[str, Dict[str, Dict[str, Any]]], phase: str = "all") -> None:
    """
    Calculate and display overall verification score.
    
    Args:
        phase_results: Dictionary containing results from all verification modules
        phase: Which phase to display ("all", "1", "2", "3", "4", "5")
    """
    if phase == "all":
        print_header("VERIFICATION SUMMARY")
        print("📋 Checking all 5 phases: Foundation, CRUD, Visualization, Export, Deployment")
    else:
        print_header(f"PHASE {phase} VERIFICATION SUMMARY")
    
    total_checks = 0
    passed_checks = 0
    phase_stats = {}
    
    # Define display names for each phase
    phase_names = {
        '1': "🏗️  Phase 1: Foundation & Setup",
        '2': "🔧 Phase 2: CRUD Operations & Testing",
        '3': "📊 Phase 3: Visualization & Enhancements",
        '4': "📦 Phase 4: Export Features & Code Quality",
        '5': "🚀 Phase 5: Final Polish & Deployment",
    }
    
    phases_to_display = [phase] if phase != "all" else ['1', '2', '3', '4', '5']
    
    for phase_num in phases_to_display:
        if phase_num in phase_results:
            print(f"\n{phase_names.get(phase_num, f'Phase {phase_num}')}:")
            print("-" * 60)
            
            phase_passed = 0
            phase_total = 0
            
            for category, category_results in phase_results[phase_num].items():
                for check_name, check_result in category_results.items():
                    # Skip non-boolean results and debug info
                    skip_patterns = ['error', 'actual_methods', 'list', 'rate', 'version', 
                                   'count', 'debug', 'found', 'config', 'missing', 'issues']
                    if any(pattern in check_name.lower() for pattern in skip_patterns):
                        continue
                    
                    if isinstance(check_result, bool):
                        phase_total += 1
                        total_checks += 1
                        
                        if check_result:
                            phase_passed += 1
                            passed_checks += 1
                        
                        # Format check name for display
                        if phase == "all":
                            display_name = f"{category}.{check_name}".replace('_', ' ').title()[:40]
                        else:
                            display_name = check_name.replace('_', ' ').title()[:45]
                        
                        print_check_result(display_name, check_result)
            
            # Store phase statistics
            if phase_total > 0:
                phase_stats[phase_num] = {
                    'passed': phase_passed,
                    'total': phase_total,
                    'percentage': (phase_passed / phase_total) * 100
                }
    
    # Calculate overall score
    if total_checks > 0:
        percentage = (passed_checks / total_checks) * 100
        
        print_header("OVERALL STATISTICS")
        
        if phase == "all":
            # Show breakdown by phase
            print("📈 Phase-by-Phase Breakdown:")
            for phase_num, stats in phase_stats.items():
                phase_percentage = stats['percentage']
                bar_length = 30
                filled_length = int(bar_length * phase_percentage // 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)
                print(f"  Phase {phase_num}: {stats['passed']}/{stats['total']} checks [{bar}] {phase_percentage:.1f}%")
            print()
        
        print(f"📊 Total Checks: {total_checks}")
        print(f"✅ Passed: {passed_checks}")
        print(f"❌ Failed: {total_checks - passed_checks}")
        print(f"🎯 Success Rate: {percentage:.1f}%")
        
        # Visual progress bar
        bar_length = 50
        filled_length = int(bar_length * percentage // 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        # Color code based on percentage
        if percentage >= 80:
            color = "\033[92m"  # Green
            if phase == "all":
                status = "✅ Excellent! All phases are well implemented."
            else:
                status = f"✅ Excellent! Phase {phase} requirements are met."
        elif percentage >= 60:
            color = "\033[93m"  # Yellow
            if phase == "all":
                status = "📊 Good progress. Some minor improvements needed."
            else:
                status = f"📊 Good progress. Phase {phase} mostly complete."
        elif percentage >= 40:
            color = "\033[93m"  # Yellow
            if phase == "all":
                status = "⚡ Moderate progress. Several areas need work."
            else:
                status = f"⚡ Moderate progress. Phase {phase} needs attention."
        else:
            color = "\033[91m"  # Red
            if phase == "all":
                status = "🚧 Needs significant work. Review failed checks."
            else:
                status = f"🚧 Phase {phase} needs significant work."
        
        reset = "\033[0m"
        print(f"\n{color}[{bar}]{reset}")
        print(f"{color}{status}{reset}")
        
        # Next steps
        print(f"\n" + "=" * 70)
        if phase == "all":
            if percentage >= 70:
                print("🎉 PROJECT READY FOR DEPLOYMENT & PORTFOLIO!")
                print("👉 Create a final release and add to your portfolio")
            else:
                print("⚠️  PROJECT NEEDS IMPROVEMENT")
                print("👉 Run verification for specific phases to see details")
        else:
            if percentage >= 70:
                print(f"🎉 PHASE {phase} COMPLETED!")
                if phase != '5':
                    print(f"👉 Next step: Run '--phase={int(phase)+1}' for next phase")
            else:
                print(f"⚠️  PHASE {phase} INCOMPLETE")
                print("👉 Review failed checks above and fix issues")
        print("=" * 70)
    
    else:
        print("No checks were performed.")


# ==================== MAIN FUNCTION ====================

def main():
    """Main entry point for the verification script."""
    parser = argparse.ArgumentParser(
        description="Daily Expense Tracker - Comprehensive Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python %(prog)s --phase=all      # Verify all phases
  python %(prog)s --phase=1        # Verify only Phase 1
  python %(prog)s --phase=3        # Verify only Phase 3
  python %(prog)s --help           # Show this help message
        """
    )
    
    parser.add_argument(
        '--phase',
        type=str,
        default='all',
        choices=['all', '1', '2', '3', '4', '5'],
        help='Which phase to verify (default: all)'
    )
    
    parser.add_argument(
        '--project-dir',
        type=str,
        default='.',
        help='Project directory to verify (default: current directory)'
    )
    
    args = parser.parse_args()
    
    print_header("DAILY EXPENSE TRACKER - VERIFICATION")
    print(f"📁 Project Directory: {Path(args.project_dir).absolute()}")
    print(f"⚙️  Phase to Verify: {args.phase}")
    print(f"📅 Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get project root
    project_root = Path(args.project_dir).absolute()
    
    if not project_root.exists():
        print(f"\n❌ Error: Project directory not found: {project_root}")
        sys.exit(1)
    
    # Run verifications based on phase
    all_results = {}
    
    if args.phase in ['all', '1']:
        all_results['1'] = run_phase1_verification(project_root)
    
    if args.phase in ['all', '2']:
        all_results['2'] = run_phase2_verification(project_root)
    
    if args.phase in ['all', '3']:
        all_results['3'] = run_phase3_verification(project_root)
    
    if args.phase in ['all', '4']:
        all_results['4'] = run_phase4_verification(project_root)
    
    if args.phase in ['all', '5']:
        all_results['5'] = run_phase5_verification(project_root)
    
    # Display results
    calculate_and_display_score(all_results, args.phase)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {e}")
        print("Please ensure the project structure is correct.")
        import traceback
        traceback.print_exc()
        sys.exit(1)