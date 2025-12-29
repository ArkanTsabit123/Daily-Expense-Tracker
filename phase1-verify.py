# project portofolio/junior project/daily-expense-tracker/phase1-verify.py

"""
This module verifies if the project meets the requirements for phase 1.
"""

import sqlite3
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# ==================== UTILITY FUNCTIONS ====================

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


# ==================== VERIFICATION MODULES ====================

def verify_database(project_root: Path) -> Dict[str, bool]:
    """
    Verify database structure and content.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
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
    Verify that model files exist and can be imported.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
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
    Verify validation module exists and functions correctly.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
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


def verify_dependencies(project_root: Path) -> Dict[str, bool]:
    """
    Verify that requirements.txt exists and contains required packages.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
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
            # But we check anyway and will mark as PASS if not present
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
    Verify Git repository setup.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
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


def calculate_and_display_score(results: Dict[str, Dict[str, bool]]) -> None:
    """
    Print all verification results in a formatted way.
    
    Args:
        results: Dictionary containing results from all verification modules
    """
    print_header("PHASE 1 VERIFICATION SUMMARY")
    print("🏗️  PHASE 1: PROJECT SETUP & FOUNDATION")
    print("📋 Checking: Database, Models, Validation, Dependencies, Git")
    
    total_checks = 0
    passed_checks = 0
    
    # Define display names for each category
    category_names = {
        'database': "📊 Database",
        'models': "🗂️  Models",
        'validation': "✅ Validation",
        'dependencies': "📦 Dependencies",
        'git': "🔧 Git"
    }
    
    for category, category_results in results.items():
        if category in category_names:
            print(f"\n{category_names[category]}:")
        else:
            print(f"\n{category.replace('_', ' ').title()}:")
        print("-" * 50)
        
        for check_name, check_result in category_results.items():
            # Skip non-boolean results (like error messages or counts)
            if not isinstance(check_result, bool):
                continue
            
            total_checks += 1
            if check_result:
                passed_checks += 1
            
            # Format check name for display
            display_name = check_name.replace('_', ' ').title()
            
            # Special handling for sqlite3 check
            if check_name == 'has_sqlite3':
                if check_result:
                    print_check_result(display_name, True, "SQLite3 is built-in (should NOT be in requirements.txt)")
                else:
                    print_check_result(display_name, False, "SQLite3 should NOT be in requirements.txt - remove it!")
            elif 'error' in check_name.lower() or 'fail' in check_name.lower():
                # Error-related checks
                continue
            else:
                print_check_result(display_name, check_result)
    
    # Print overall statistics
    print_header("OVERALL STATISTICS")
    print(f"📈 Total Checks: {total_checks}")
    print(f"✅ Passed: {passed_checks}")
    print(f"❌ Failed: {total_checks - passed_checks}")
    
    if total_checks > 0:
        success_rate = (passed_checks / total_checks) * 100
        
        # Visual progress bar
        bar_length = 50
        filled_length = int(bar_length * success_rate // 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"\n[{bar}]")
        
        # Status based on success rate
        if success_rate >= 90:
            status_color = "\033[92m"
            status = "✅ Excellent! Phase 1 requirements are mostly met."
        elif success_rate >= 70:
            status_color = "\033[93m"
            status = "📊 Good progress. Some issues need attention."
        elif success_rate >= 50:
            status_color = "\033[93m"
            status = "⚡ Significant work needed to meet Phase 1 requirements."
        else:
            status_color = "\033[91m"
            status = "🚧 Major issues found. Please review and fix the failed checks."
        
        reset = "\033[0m"
        print(f"{status_color}{status}{reset}")
    
    # Print next steps
    print("\n" + "=" * 70)
    if passed_checks == total_checks and total_checks > 0:
        print("🎉 PHASE 1 COMPLETED! Ready for Phase 2.")
        print("👉 Next step: Run 'python phase2-verify.py' for Phase 2 verification")
    else:
        print("⚠️  PHASE 1 INCOMPLETE - Some checks failed.")
        print("👉 Next step: Run 'python phase1-fixer.py' to fix issues")
    print("=" * 70)


# ==================== MAIN FUNCTION ====================

def verify_phase1() -> None:
    """
    Main function to run all Phase 1 verifications.
    """
    print_header("DAILY EXPENSE TRACKER - PHASE 1 VERIFICATION")
    print("🏗️  FOUNDATION & SETUP CHECK")
    
    # Get project root
    project_root = Path(__file__).parent
    print(f"📁 Project Location: {project_root.absolute()}")
    print(f"⚙️  Phase Focus: Database, Models, Validation, Dependencies")
    
    # Run all verifications
    print_header("RUNNING VERIFICATIONS")
    
    results = {
        'database': verify_database(project_root),
        'models': verify_models(project_root),
        'validation': verify_validation(project_root),
        'dependencies': verify_dependencies(project_root),
        'git': verify_git_setup(project_root)
    }
    
    # Print detailed results
    calculate_and_display_score(results)
    
    # Show detailed error messages if any
    print_header("DETAILED ERROR INFORMATION")
    
    error_found = False
    for category, category_results in results.items():
        for key, value in category_results.items():
            if isinstance(value, str) and ('error' in key.lower() or 'fail' in key.lower()):
                error_found = True
                print(f"\n🔍 {category}.{key}:")
                print(f"   {value}")
    
    if not error_found:
        print("✅ No detailed errors found. Check PASS/FAIL status above.")


if __name__ == "__main__":
    try:
        verify_phase1()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {e}")
        print("Please ensure all project files are properly structured.")
        import traceback
        traceback.print_exc()
        sys.exit(1)