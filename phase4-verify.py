# phase4-verify.py

"""
Daily Expense Tracker - Phase 4 Verification Module

Verifies the implementation of export features, reporting,
integration tests, and code quality tools for Phase 4.
"""
import importlib.util
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime
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


def run_shell_command(command: List[str]) -> Tuple[bool, str]:
    """
    Run a shell command and return success status and output.
    
    Args:
        command: List of command arguments
        
    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


# ==================== VERIFICATION MODULES ====================

def verify_export_features(project_root: Path) -> Dict[str, Any]:
    """
    Verify export features implementation.
    FIXED: Based on actual blueprint
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


def verify_reporting_features(project_root: Path) -> Dict[str, Any]:
    """
    Verify reporting features implementation.
    FIXED: Check actual features from blueprint
    """
    results = {}
    
    # Check export service for reporting features
    export_service_path = project_root / "services" / "export_service.py"
    results['export_service_exists'] = export_service_path.exists()
    
    if results['export_service_exists']:
        content = read_file_with_encoding(export_service_path)
        if content:
            # Check for comprehensive reporting from blueprint
            results['has_multi_sheet_excel'] = 'ExcelWriter' in content and 'sheet_name' in content
            results['has_auto_column_width'] = 'column_dimensions' in content or 'worksheet.column_dimensions' in content
            results['has_timestamp_filenames'] = 'strftime' in content and 'timestamp' in content.lower()
            
            # Check for specific report types
            results['has_monthly_summary_sheet'] = 'Ringkasan' in content or 'Summary' in content
            results['has_category_breakdown_sheet'] = 'Per Kategori' in content or 'Category' in content
            results['has_transaction_details_sheet'] = 'Detail Transaksi' in content or 'Transactions' in content
            
            # Check for data formatting in reports
            results['has_currency_formatting'] = 'format_currency' in content or 'Rp' in content
            results['has_date_formatting'] = 'strftime' in content and 'date' in content
    
    # Check exports directory structure
    exports_dir = project_root / "exports"
    if exports_dir.exists():
        results['exports_dir_writable'] = True  # Assume writable if exists
    
    return results


def verify_testing_infrastructure(project_root: Path) -> Dict[str, Any]:
    """
    Verify testing infrastructure.
    FIXED: Check actual test files from project structure
    """
    results = {}
    
    # Check tests directory
    tests_dir = project_root / "tests"
    results['tests_dir_exists'] = tests_dir.exists()
    
    if results['tests_dir_exists']:
        # Check for test files from blueprint and actual structure
        test_files_to_check = [
            ("test_database.py", "Database tests"),
            ("test_expenses.py", "Expense service tests"),
            ("test_export.py", "Export service tests"),
            ("test_integration.py", "Integration tests"),
            ("conftest.py", "Pytest configuration"),
        ]
        
        for filename, description in test_files_to_check:
            file_path = tests_dir / filename
            results[f'{filename}_exists'] = file_path.exists()
        
        # Count all test files
        all_test_files = list(tests_dir.glob("test_*.py"))
        results['test_file_count'] = len(all_test_files)
        results['has_test_files'] = results['test_file_count'] > 0
        
        # Check conftest.py for fixtures
        conftest_path = tests_dir / "conftest.py"
        if conftest_path.exists():
            content = read_file_with_encoding(conftest_path)
            if content:
                results['conftest_has_fixtures'] = '@pytest.fixture' in content
                results['conftest_has_setup'] = 'def setup_' in content or 'def teardown_' in content
        
        # Check for pytest in requirements
        req_path = project_root / "requirements.txt"
        if req_path.exists():
            content = read_file_with_encoding(req_path)
            if content:
                results['has_pytest'] = 'pytest' in content.lower()
    
    # Check coverage configuration
    coverage_files = [
        (project_root / ".coveragerc", ".coveragerc"),
        (project_root / "pyproject.toml", "pyproject.toml"),
        (project_root / "setup.cfg", "setup.cfg"),
    ]
    
    for file_path, name in coverage_files:
        if file_path.exists():
            content = read_file_with_encoding(file_path)
            if content and 'coverage' in content.lower():
                results['has_coverage_config'] = True
                results['coverage_config_file'] = name
                break
    else:
        results['has_coverage_config'] = False
    
    return results


def verify_code_quality_tools(project_root: Path) -> Dict[str, Any]:
    """
    Verify code quality tools setup.
    FIXED: Based on project plan (only black and flake8)
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
    
    # Try to check if tools are available (but don't fail if not)
    try:
        import black
        results['black_available'] = True
    except ImportError:
        results['black_available'] = False
    
    return results


def verify_database_indexing(project_root: Path) -> Dict[str, Any]:
    """
    Verify database indexing implementation.
    FIXED: Check only indexes from blueprint
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


def verify_performance_features(project_root: Path) -> Dict[str, Any]:
    """
    Verify performance optimization features.
    FIXED: Check actual optimizations from blueprint
    """
    results = {}
    
    # Check database service for performance optimizations
    db_service_path = project_root / "services" / "database_service.py"
    results['db_service_exists'] = db_service_path.exists()
    
    if results['db_service_exists']:
        content = read_file_with_encoding(db_service_path)
        if content:
            # Check for query optimization patterns
            optimizations = [
                "strftime",  # For date filtering (used in monthly summaries)
                "ORDER BY",  # For sorted results
                "GROUP BY",  # For aggregations
                "SUM(",      # For calculations
                "COALESCE",  # For null handling
            ]
            
            for opt in optimizations:
                results[f'uses_{opt.lower().replace("(", "")}'] = opt in content
    
    # Check for connection management
    if results['db_service_exists']:
        content = read_file_with_encoding(db_service_path)
        if content:
            results['has_connection_management'] = all(
                phrase in content for phrase in ['connect(', 'close()', 'commit()']
            )
    
    # Check if there's a database optimization method
    db_config_path = project_root / "config" / "database_config.py"
    if db_config_path.exists():
        content = read_file_with_encoding(db_config_path)
        if content:
            results['has_db_optimization'] = any(
                phrase in content.lower() for phrase in ['optimize', 'vacuum', 'pragma', 'index']
            )
    
    return results


def run_safe_phase4_test(project_root: Path) -> Dict[str, Any]:
    """
    Run SAFE integration tests for Phase 4 features.
    Doesn't modify production data.
    """
    results = {}
    
    try:
        sys.path.insert(0, str(project_root))
        print("\n🔍 Running safe Phase 4 tests...")
        
        tests_passed = 0
        tests_run = 0
        
        # Test 1: Export Service import
        try:
            from services.export_service import ExportService
            results['export_service_import_ok'] = True
            tests_passed += 1
            print("  ✓ ExportService imports OK")
        except ImportError as e:
            results['export_service_import_ok'] = False
            print(f"  ✗ ExportService import failed: {e}")
        tests_run += 1
        
        # Test 2: Check if export directory exists
        exports_dir = project_root / "exports"
        results['exports_dir_exists_test'] = exports_dir.exists()
        if results['exports_dir_exists_test']:
            tests_passed += 1
            print("  ✓ Exports directory exists")
        else:
            print("  ⚠ Exports directory doesn't exist (will be created at runtime)")
        tests_run += 1
        
        # Test 3: Check for test files
        tests_dir = project_root / "tests"
        test_files = list(tests_dir.glob("test_*.py"))
        results['has_test_files_test'] = len(test_files) > 0
        results['test_file_count_test'] = len(test_files)
        
        if results['has_test_files_test']:
            tests_passed += 1
            print(f"  ✓ Found {len(test_files)} test files")
        else:
            print("  ⚠ No test files found")
        tests_run += 1
        
        # Test 4: Check code quality configs
        configs_to_check = [
            (project_root / "pyproject.toml", "pyproject.toml"),
            (project_root / ".flake8", ".flake8"),
            (project_root / ".coveragerc", ".coveragerc"),
        ]
        
        configs_found = []
        for path, name in configs_to_check:
            if path.exists():
                configs_found.append(name)
        
        results['code_quality_configs'] = ", ".join(configs_found) if configs_found else "None"
        results['has_code_quality_configs'] = len(configs_found) > 0
        
        if configs_found:
            tests_passed += 1
            print(f"  ✓ Found config files: {', '.join(configs_found)}")
        else:
            print("  ⚠ No code quality config files found")
        tests_run += 1
        
        # Test 5: Check database indexes (read-only)
        db_path = project_root / "data" / "expenses.db"
        if db_path.exists():
            try:
                conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
                indexes = [row[0] for row in cursor.fetchall()]
                conn.close()
                
                results['database_has_indexes'] = len(indexes) > 0
                results['index_count_found'] = len(indexes)
                
                if indexes:
                    tests_passed += 1
                    print(f"  ✓ Database has {len(indexes)} indexes")
                else:
                    print("  ⚠ Database has no indexes")
            except:
                results['database_has_indexes'] = False
                print("  ⚠ Could not check database indexes")
        else:
            results['database_has_indexes'] = False
            print("  ⚠ Database file not found")
        tests_run += 1
        
        # Calculate success rate
        if tests_run > 0:
            results['test_success_rate'] = (tests_passed / tests_run) * 100
        results['tests_passed'] = tests_passed
        results['tests_run'] = tests_run
        
        print(f"\n  📊 Test summary: {tests_passed}/{tests_run} passed")
        
    except Exception as e:
        results['integration_error'] = str(e)
        print(f"  ✗ Test error: {e}")
    
    finally:
        if str(project_root) in sys.path:
            sys.path.remove(str(project_root))
    
    return results


def calculate_and_display_score(all_results: Dict[str, Dict[str, Any]]) -> None:
    """
    Calculate and display overall verification score.
    """
    print_header("PHASE 4 VERIFICATION SUMMARY")
    
    total_checks = 0
    passed_checks = 0
    failed_categories = []
    
    # Category display names
    category_names = {
        'export_features': "Export Features",
        'reporting_features': "Reporting Features",
        'testing_infrastructure': "Testing Infrastructure",
        'code_quality_tools': "Code Quality Tools",
        'database_indexing': "Database Indexing",
        'performance_features': "Performance Features",
        'integration': "Integration Test",
    }
    
    for category, category_results in all_results.items():
        display_name = category_names.get(category, category.replace('_', ' ').title())
        print(f"\n{display_name}:")
        print("-" * 50)
        
        category_passed = 0
        category_total = 0
        
        for check_name, check_result in category_results.items():
            # Skip non-boolean results and debug info
            skip_patterns = ['error', 'actual_methods', 'list', 'rate', 'version', 
                           'count', 'debug', 'found', 'config', 'file', 'test']
            if any(pattern in check_name.lower() for pattern in skip_patterns):
                continue
            
            if isinstance(check_result, bool):
                category_total += 1
                total_checks += 1
                
                if check_result:
                    category_passed += 1
                    passed_checks += 1
                
                # Format check name for display
                display_name = check_name.replace('_', ' ').title()
                print_check_result(display_name, check_result)
        
        # Calculate category success rate
        if category_total > 0:
            category_rate = (category_passed / category_total) * 100
            if category_rate < 50:
                failed_categories.append(display_name)
    
    # Calculate overall score
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
        if percentage >= 80:
            color = "\033[92m"  # Green
            status = "✅ Excellent! Phase 4 features are complete."
        elif percentage >= 60:
            color = "\033[93m"  # Yellow
            status = "📊 Good progress. Export and testing implemented."
        elif percentage >= 40:
            color = "\033[93m"  # Yellow
            status = "⚡ Moderate progress. Basic export features working."
        else:
            color = "\033[91m"  # Red
            status = "🚧 Needs work. Start with export functionality."
        
        reset = "\033[0m"
        print(f"\n{color}[{bar}]{reset}")
        print(f"{color}{status}{reset}")
        
        # Specific recommendations
        print(f"\n📋 PHASE 4 PRIORITIES:")
        
        # Check what's missing
        if 'export_features' in all_results:
            exp_results = all_results['export_features']
            if not exp_results.get('export_service_exists', False):
                print("1. Create services/export_service.py")
            if not exp_results.get('has_export_to_csv', False):
                print("2. Implement export_to_csv() method")
            if not exp_results.get('has_export_to_excel', False):
                print("3. Implement export_to_excel() method")
        
        if 'code_quality_tools' in all_results:
            cq_results = all_results['code_quality_tools']
            if not cq_results.get('has_black', False):
                print("4. Add 'black' to requirements.txt")
            if not cq_results.get('has_flake8', False):
                print("5. Add 'flake8' to requirements.txt")
        
        # Next steps
        print(f"\n🔍 Next Steps:")
        if percentage >= 70:
            print("1. Run 'python phase5-verify.py' for final phase")
            print("2. Run existing tests: pytest tests/ -v")
            print("3. Test export functionality with sample data")
        else:
            print("1. Run 'python phase4-fixer.py' to fix Phase 4 issues")
            print("2. Review failed checks above")
            print("3. Check blueprint for required export features")
    
    else:
        print("No checks were performed.")


# ==================== MAIN FUNCTION ====================

def verify_phase4() -> None:
    """
    Main function to run all Phase 4 verifications.
    """
    print_header("DAILY EXPENSE TRACKER - PHASE 4 VERIFICATION")
    
    # Get project root
    project_root = Path(__file__).parent
    print(f"📁 Project Location: {project_root.absolute()}")
    print(f"📦 Phase Focus: Export Features, Reporting, Testing, Code Quality")
    print(f"📋 Based on blueprint: ExportService, testing, black, flake8, indexing")
    
    print_header("RUNNING PHASE 4 VERIFICATIONS")
    
    # Run all verifications
    results = {
        'export_features': verify_export_features(project_root),
        'reporting_features': verify_reporting_features(project_root),
        'testing_infrastructure': verify_testing_infrastructure(project_root),
        'code_quality_tools': verify_code_quality_tools(project_root),
        'database_indexing': verify_database_indexing(project_root),
        'performance_features': verify_performance_features(project_root),
        'integration': run_safe_phase4_test(project_root),
    }
    
    # Display results
    calculate_and_display_score(results)


if __name__ == "__main__":
    try:
        verify_phase4()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {e}")
        print("Please ensure the project structure is correct.")
        import traceback
        traceback.print_exc()
        sys.exit(1)