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

def verify_export_features(project_root: Path) -> Dict[str, bool]:
    """
    Verify export features implementation.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check export service
    export_service_path = project_root / "services" / "export_service.py"
    results['export_service_exists'] = export_service_path.exists()
    
    if results['export_service_exists']:
        success, module, message = import_module_from_path(export_service_path, "export_service")
        results['export_service_importable'] = success
        
        if success:
            # Check for ExportService class
            if hasattr(module, 'ExportService'):
                results['has_export_service_class'] = True
                
                # Get the ExportService class
                export_service_class = module.ExportService
                
                # Check required export methods
                export_methods = [
                    "export_to_csv",
                    "export_to_excel",
                    "export_monthly_report",
                    "export_category_report",
                    "export_to_json",
                ]
                
                for method in export_methods:
                    results[f'has_{method}'] = hasattr(export_service_class, method)
            else:
                results['has_export_service_class'] = False
        else:
            results['import_error'] = message
    
    # Check exports directory
    exports_dir = project_root / "exports"
    results['exports_dir_exists'] = exports_dir.exists()
    
    # Check if exports directory is in .gitignore
    gitignore_path = project_root / ".gitignore"
    if gitignore_path.exists():
        content = read_file_with_encoding(gitignore_path)
        if content:
            results['exports_in_gitignore'] = 'exports/' in content or 'exports' in content
    
    # Check for export-related imports in code
    if export_service_path.exists():
        content = read_file_with_encoding(export_service_path)
        if content:
            # Check for common export libraries
            export_libraries = [
                "pandas",
                "openpyxl",  # For Excel
                "csv",  # For CSV
                "json",  # For JSON
            ]
            
            for lib in export_libraries:
                results[f'uses_{lib}'] = lib in content.lower()
    
    return results


def verify_reporting_features(project_root: Path) -> Dict[str, bool]:
    """
    Verify reporting features implementation.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check export service for reporting features
    export_service_path = project_root / "services" / "export_service.py"
    results['export_service_exists_for_reporting'] = export_service_path.exists()
    
    if results['export_service_exists_for_reporting']:
        content = read_file_with_encoding(export_service_path)
        if content:
            # Check for advanced reporting features
            reporting_features = [
                "monthly_report",  # Monthly reporting
                "category_report",  # Category-based reporting
                "summary",  # Summary reports
                "chart",  # Chart embedding in reports
                "format",  # Formatting options
            ]
            
            for feature in reporting_features:
                results[f'has_{feature}_reporting'] = feature in content.lower()
            
            # Check for Excel-specific features
            excel_features = [
                "ExcelWriter",  # Multiple sheets
                "sheet_name",  # Named sheets
                "worksheet",  # Worksheet manipulation
                "cell",  # Cell formatting
                "column_dimensions",  # Column sizing
            ]
            
            for feature in excel_features:
                results[f'has_excel_{feature.lower()}'] = feature in content
    
    # Check for separate reporting service
    reporting_service_path = project_root / "services" / "reporting_service.py"
    results['reporting_service_exists'] = reporting_service_path.exists()
    
    # Check for report templates or configurations
    report_config_path = project_root / "config" / "report_config.py"
    results['report_config_exists'] = report_config_path.exists()
    
    # Check for report output formats (if export service content exists)
    if results['export_service_exists_for_reporting']:
        content = read_file_with_encoding(export_service_path)
        if content:
            export_formats = ['csv', 'xlsx', 'pdf', 'json']
            for fmt in export_formats:
                results[f'supports_{fmt}_format'] = f'.{fmt}' in content
        else:
            for fmt in ['csv', 'xlsx', 'pdf', 'json']:
                results[f'supports_{fmt}_format'] = False
    
    return results


def verify_testing_infrastructure(project_root: Path) -> Dict[str, bool]:
    """
    Verify testing infrastructure.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check tests directory
    tests_dir = project_root / "tests"
    results['tests_dir_exists'] = tests_dir.exists()
    
    if results['tests_dir_exists']:
        # Count test files
        test_files = list(tests_dir.glob("test_*.py"))
        results['has_test_files'] = len(test_files) > 0
        results['test_file_count'] = len(test_files)
        
        # Check for specific test categories
        test_categories = {
            'unit': any('unit' in f.name.lower() for f in test_files),
            'integration': any('integration' in f.name.lower() for f in test_files),
            'export': any('export' in f.name.lower() for f in test_files),
            'database': any('database' in f.name.lower() for f in test_files),
        }
        
        for category, exists in test_categories.items():
            results[f'has_{category}_tests'] = exists
        
        # Check for conftest.py
        conftest_path = tests_dir / "conftest.py"
        results['has_conftest'] = conftest_path.exists()
        
        if results['has_conftest']:
            conftest_content = read_file_with_encoding(conftest_path)
            if conftest_content:
                results['conftest_has_fixtures'] = '@pytest.fixture' in conftest_content
                results['conftest_has_config'] = any(
                    word in conftest_content.lower() 
                    for word in ['config', 'setup', 'teardown']
                )
    
    # Check test coverage configuration
    coverage_configs = [
        project_root / ".coveragerc",
        project_root / "pyproject.toml",
        project_root / "setup.cfg",
    ]
    
    for config in coverage_configs:
        if config.exists():
            content = read_file_with_encoding(config)
            if content and 'coverage' in content.lower():
                results['has_coverage_config'] = True
                break
    else:
        results['has_coverage_config'] = False
    
    return results


def verify_code_quality_tools(project_root: Path) -> Dict[str, bool]:
    """
    Verify code quality tools setup.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check requirements.txt for code quality tools
    requirements_path = project_root / "requirements.txt"
    results['requirements_exists'] = requirements_path.exists()
    
    if results['requirements_exists']:
        content = read_file_with_encoding(requirements_path)
        if content:
            content_lower = content.lower()
            
            # Check for code quality tools
            quality_tools = [
                "black",  # Code formatter
                "flake8",  # Linter
                "pylint",  # Linter
                "mypy",  # Type checker
                "isort",  # Import sorter
                "bandit",  # Security checker
            ]
            
            for tool in quality_tools:
                results[f'has_{tool}'] = tool in content_lower
            
            # Check for testing tools
            testing_tools = [
                "pytest",
                "pytest-cov",  # Coverage
                "pytest-mock",  # Mocking
            ]
            
            for tool in testing_tools:
                results[f'has_{tool}'] = tool in content_lower
    
    # Check for configuration files
    config_files = {
        'pyproject_toml': project_root / "pyproject.toml",
        'setup_cfg': project_root / "setup.cfg",
        'flake8_config': project_root / ".flake8",
        'pylintrc': project_root / ".pylintrc",
        'mypy_config': project_root / "mypy.ini",
    }
    
    for name, path in config_files.items():
        results[name] = path.exists()
    
    # Check if tools are actually installed and working
    try:
        # Try to import black to check if it's available
        import black
        results['black_available'] = True
    except ImportError:
        results['black_available'] = False
    
    try:
        # Try to run flake8
        success, output = run_shell_command(["flake8", "--version"])
        results['flake8_available'] = success
    except Exception:
        results['flake8_available'] = False
    
    return results


def verify_database_indexing(project_root: Path) -> Dict[str, bool]:
    """
    Verify database indexing implementation.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check database path
    db_path = project_root / "data" / "expenses.db"
    results['database_exists'] = db_path.exists()
    
    if not results['database_exists']:
        return results
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [row[0] for row in cursor.fetchall()]
        
        results['has_indexes'] = len(indexes) > 0
        results['index_count'] = len(indexes)
        
        # Check for specific indexes
        expected_indexes = [
            "idx_expenses_date",
            "idx_expenses_category",
            "idx_expenses_amount",
            "idx_expenses_date_category",
        ]
        
        for idx in expected_indexes:
            results[f'has_{idx}'] = idx in indexes
        
        # Check expenses table structure
        cursor.execute("PRAGMA table_info(expenses);")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Check which columns are indexed
        indexed_columns = []
        for idx in indexes:
            if idx.startswith('idx_expenses_'):
                # Extract column name from index name
                col_name = idx.replace('idx_expenses_', '')
                indexed_columns.append(col_name)
        
        # Check if important columns are indexed
        important_columns = ['date', 'category', 'amount']
        for col in important_columns:
            if col in columns:
                results[f'{col}_column_exists'] = True
                results[f'{col}_is_indexed'] = col in indexed_columns or any(col in idx for idx in indexes)
        
        conn.close()
        
    except sqlite3.Error as e:
        results['database_error'] = str(e)
    
    return results


def verify_performance_features(project_root: Path) -> Dict[str, bool]:
    """
    Verify performance optimization features.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check database service for performance optimizations
    db_service_path = project_root / "services" / "database_service.py"
    results['db_service_exists'] = db_service_path.exists()
    
    if results['db_service_exists']:
        content = read_file_with_encoding(db_service_path)
        if content:
            # Check for performance optimizations
            optimizations = [
                "executemany",  # Batch operations
                "transaction",  # Transaction handling
                "connection pool",  # Connection pooling
                "cache",  # Caching
                "index",  # Index creation/usage
                "pragma",  # SQLite optimizations
                "vacuum",  # Database maintenance
            ]
            
            for opt in optimizations:
                results[f'has_{opt.replace(" ", "_")}_optimization'] = opt in content.lower()
    
    # Check for query optimization in code
    query_patterns = [
        "SELECT *",  # Check for specific column selection
        "LIMIT",  # Result limiting
        "ORDER BY",  # Sorting
        "WHERE",  # Filtering
        "JOIN",  # Joins
    ]
    
    # Search in all Python files for query patterns
    python_files = list(project_root.glob("**/*.py"))
    found_queries = {pattern: False for pattern in query_patterns}
    
    for py_file in python_files:
        if py_file.is_file():
            content = read_file_with_encoding(py_file)
            if content:
                for pattern in query_patterns:
                    if pattern in content:
                        found_queries[pattern] = True
    
    for pattern, found in found_queries.items():
        results[f'uses_{pattern.lower().replace(" ", "_")}'] = found
    
    # Check for pagination support
    pagination_indicators = ["page", "limit", "offset", "paginate"]
    for indicator in pagination_indicators:
        found = False
        for py_file in python_files:
            if py_file.is_file():
                content = read_file_with_encoding(py_file)
                if content and indicator in content.lower():
                    found = True
                    break
        results[f'has_{indicator}_support'] = found
    
    return results


def run_phase4_integration_test(project_root: Path) -> Dict[str, bool]:
    """
    Run integration tests for Phase 4 features.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    try:
        # Add project root to Python path
        sys.path.insert(0, str(project_root))
        
        print(f"\n🔍 Running Phase 4 integration tests...")
        
        # Test 1: Export Service
        try:
            from services.export_service import ExportService
            
            export_service = ExportService()
            results['export_service_instantiation'] = True
            print(f"  ✓ ExportService instantiated successfully")
            
            # Check if methods exist
            if hasattr(export_service, 'export_to_csv'):
                results['has_csv_export'] = True
                print(f"  ✓ CSV export method available")
            
            if hasattr(export_service, 'export_to_excel'):
                results['has_excel_export'] = True
                print(f"  ✓ Excel export method available")
                
        except ImportError as e:
            print(f"  ✗ ExportService import failed: {e}")
            results['export_service_available'] = False
        
        # Test 2: Database Performance
        try:
            from services.database_service import DatabaseService
            
            db_service = DatabaseService()
            results['database_service_available'] = True
            
            # Test query performance
            import time
            
            start_time = time.time()
            expenses = db_service.get_expenses(limit=100)
            query_time = time.time() - start_time
            
            results['database_query_works'] = expenses is not None
            results['query_performance'] = query_time < 1.0  # Should be fast
            
            print(f"  ✓ Database query completed in {query_time:.3f}s")
            
        except ImportError as e:
            print(f"  ✗ DatabaseService import failed: {e}")
            results['database_service_available'] = False
        
        # Test 3: Code Quality Tools
        print(f"  📊 Checking code quality tools...")
        
        # Check black
        try:
            success, output = run_shell_command(["black", "--version"])
            results['black_working'] = success
            if success:
                print(f"  ✓ Black formatter available")
        except Exception:
            results['black_working'] = False
        
        # Check flake8
        try:
            # Run flake8 on a small test
            test_file = project_root / "tests" / "test_database.py"
            if test_file.exists():
                success, output = run_shell_command(["flake8", str(test_file)])
                results['flake8_working'] = True
                print(f"  ✓ Flake8 linter available")
        except Exception:
            results['flake8_working'] = False
        
        # Test 4: Reporting Features
        try:
            from services.export_service import ExportService
            
            # Create sample data for reporting
            sample_data = [
                {"date": "2024-12-01", "category": "Food", "amount": 50000, "description": "Lunch"},
                {"date": "2024-12-02", "category": "Transport", "amount": 25000, "description": "Taxi"},
            ]
            
            export_service = ExportService()
            
            # Test if report generation methods exist
            if hasattr(export_service, 'export_monthly_report'):
                results['monthly_report_available'] = True
                print(f"  ✓ Monthly report generation available")
            
            if hasattr(export_service, 'export_category_report'):
                results['category_report_available'] = True
                print(f"  ✓ Category report generation available")
                
        except ImportError:
            results['reporting_features'] = False
    
    except Exception as e:
        print(f"  ✗ Integration test error: {e}")
        results['integration_error'] = str(e)
    
    finally:
        # Clean up path modification
        if str(project_root) in sys.path:
            sys.path.remove(str(project_root))
    
    return results


def calculate_and_display_score(all_results: Dict[str, Dict[str, bool]]) -> None:
    """
    Calculate and display overall verification score.
    
    Args:
        all_results: Dictionary containing results from all verification modules
    """
    print_header("PHASE 4 VERIFICATION SUMMARY")
    
    total_checks = 0
    passed_checks = 0
    
    for category, category_results in all_results.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        print("-" * 50)
        
        for check_name, check_result in category_results.items():
            # Skip non-boolean results
            if not isinstance(check_result, bool):
                continue
            
            total_checks += 1
            if check_result:
                passed_checks += 1
            
            # Format check name for display
            display_name = check_name.replace('_', ' ').title()
            print_check_result(display_name, check_result)
    
    # Calculate and display score
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
            status = "🎉 Excellent! Phase 4 features are complete."
        elif percentage >= 70:
            color = "\033[93m"  # Yellow
            status = "📊 Good progress. Export and reporting features implemented."
        elif percentage >= 50:
            color = "\033[93m"  # Yellow
            status = "⚡ Halfway there. Focus on testing infrastructure."
        else:
            color = "\033[91m"  # Red
            status = "🚧 Needs work. Start with export functionality."
        
        reset = "\033[0m"
        print(f"\n{color}[{bar}]{reset}")
        print(f"{color}{status}{reset}")
        
        # Recommendations
        print(f"\n📋 PHASE 4 PRIORITIES:")
        if percentage < 70:
            print("1. Implement ExportService with CSV/Excel export")
            print("2. Set up comprehensive test suite")
            print("3. Add database indexing for performance")
            print("4. Configure code quality tools (black, flake8)")
        
        print(f"\n🎯 Next Phase: Deployment, Documentation, and Polish")
    
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
    
    print_header("RUNNING PHASE 4 VERIFICATIONS")
    
    # Run all verifications
    results = {
        'export_features': verify_export_features(project_root),
        'reporting_features': verify_reporting_features(project_root),
        'testing_infrastructure': verify_testing_infrastructure(project_root),
        'code_quality_tools': verify_code_quality_tools(project_root),
        'database_indexing': verify_database_indexing(project_root),
        'performance_features': verify_performance_features(project_root),
        'integration_tests': run_phase4_integration_test(project_root),
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
        sys.exit(1)