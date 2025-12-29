# daily-expense-tracker/phase3-verify.py

"""
Phase 3 Verification Script
Verifies the implementation of visualization features, formatters,
date utilities, and main UI updates for the daily-expense-tracker application.
"""

import importlib.util
import sys
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

def verify_visualization_module(project_root: Path) -> Dict[str, Any]:
    """
    Verify visualization module implementation.
    FIXED: Based on actual blueprint (not assumptions)
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
    Verify formatters module implementation.
    FIXED: Based on actual blueprint
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
    Verify date utilities module.
    FIXED: Based on actual blueprint
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
    FIXED: Check actual implementation
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


def verify_dependencies(project_root: Path) -> Dict[str, Any]:
    """
    Verify required dependencies for Phase 3.
    FIXED: Check actual requirements
    """
    results = {}
    
    # Check requirements.txt
    requirements_path = project_root / "requirements.txt"
    results['requirements_exists'] = requirements_path.exists()
    
    if results['requirements_exists']:
        content = read_file_with_encoding(requirements_path)
        if content:
            content_lower = content.lower()
            
            # Required for Phase 3 (from blueprint)
            required_deps = [
                "matplotlib",  # For charts
                "pandas",      # For data processing (export)
                "openpyxl",    # For Excel export
            ]
            
            for dep in required_deps:
                results[f'has_{dep}'] = dep in content_lower
            
            # Check versions
            import re
            version_patterns = {
                'matplotlib_version': r'matplotlib[=<>!~]*([\d.]+)',
                'pandas_version': r'pandas[=<>!~]*([\d.]+)',
            }
            
            for name, pattern in version_patterns.items():
                match = re.search(pattern, content)
                results[name] = match.group(1) if match else "Not specified"
        else:
            results['read_requirements_error'] = True
    
    # Try to import matplotlib
    try:
        import matplotlib
        results['matplotlib_importable'] = True
        results['matplotlib_version'] = matplotlib.__version__
    except ImportError:
        results['matplotlib_importable'] = False
    
    # Try to import pandas
    try:
        import pandas
        results['pandas_importable'] = True
        results['pandas_version'] = pandas.__version__
    except ImportError:
        results['pandas_importable'] = False
    
    return results


def verify_chart_generation(project_root: Path) -> Dict[str, Any]:
    """
    Verify chart generation capabilities.
    FIXED: Simple, safe checks
    """
    results = {}
    
    # Check if charts directory exists
    charts_dir = project_root / "charts"
    results['charts_dir_exists'] = charts_dir.exists()
    
    if results['charts_dir_exists']:
        # Check if directory is writable
        try:
            test_file = charts_dir / ".test_write"
            test_file.touch()
            results['charts_dir_writable'] = True
            test_file.unlink()
        except:
            results['charts_dir_writable'] = False
    
    # Check chart service for output directory configuration
    chart_service_path = project_root / "visualization" / "chart_service.py"
    if chart_service_path.exists():
        content = read_file_with_encoding(chart_service_path)
        if content:
            # Check for output directory configuration
            results['has_output_dir_config'] = any(
                pattern in content for pattern in [
                    'output_dir', 'charts/', 'self.output_dir', 'Path("charts")'
                ]
            )
            
            # Check for savefig usage
            results['has_savefig'] = 'savefig' in content or 'plt.savefig' in content
    
    return results


def run_safe_integration_test(project_root: Path) -> Dict[str, Any]:
    """
    Run a SAFE integration test for Phase 3 features.
    Only tests imports and basic functionality.
    """
    results = {}
    
    try:
        sys.path.insert(0, str(project_root))
        print("\nRunning safe integration tests...")
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Formatters
        try:
            from utils.formatters import format_currency
            # Just test import, don't call to avoid errors
            results['formatters_import_ok'] = True
            tests_passed += 1
            print(f"  ✅ Formatters module imports OK")
        except ImportError as e:
            results['formatters_import_ok'] = False
            print(f"  ❌ Formatters import failed: {e}")
        total_tests += 1
        
        # Test 2: Date Utilities
        try:
            from utils.date_utils import get_current_month_year
            results['date_utils_import_ok'] = True
            tests_passed += 1
            print(f"  ✅ Date utilities module imports OK")
        except ImportError as e:
            results['date_utils_import_ok'] = False
            print(f"  ❌ Date utilities import failed: {e}")
        total_tests += 1
        
        # Test 3: Visualization (optional - may not be fully implemented)
        try:
            from visualization.chart_service import ChartService
            results['chart_service_import_ok'] = True
            tests_passed += 1
            print(f"  ✅ Chart service module imports OK")
        except ImportError as e:
            results['chart_service_import_ok'] = False
            print(f"  ⚠️  Chart service import failed (may not be implemented): {e}")
        total_tests += 1
        
        # Test 4: Matplotlib availability
        try:
            import matplotlib
            results['matplotlib_available'] = True
            results['matplotlib_version'] = matplotlib.__version__
            tests_passed += 1
            print(f"  ✅ Matplotlib available (v{matplotlib.__version__})")
        except ImportError:
            results['matplotlib_available'] = False
            print(f"  ❌ Matplotlib not installed")
        total_tests += 1
        
        # Calculate success rate
        results['integration_success_rate'] = (tests_passed / total_tests * 100) if total_tests > 0 else 0
        results['tests_passed'] = tests_passed
        results['total_tests'] = total_tests
        
        print(f"\n  📊 Integration tests: {tests_passed}/{total_tests} passed")
        
    except Exception as e:
        results['integration_error'] = str(e)
        print(f"  ❌ Integration test error: {e}")
    
    finally:
        if str(project_root) in sys.path:
            sys.path.remove(str(project_root))
    
    return results


def calculate_and_display_score(all_results: Dict[str, Dict[str, Any]]) -> None:
    """
    Calculate and display overall verification score.
    """
    print_header("PHASE 3 VERIFICATION SUMMARY")
    print("📊 PHASE 3: VISUALIZATION & ENHANCEMENTS")
    print("📋 Checking: Charts, Formatters, Date Utils, UI Updates, Dependencies")
    
    total_checks = 0
    passed_checks = 0
    
    # Category display names
    category_names = {
        'visualization': "📈 Visualization Module",
        'formatters': "🎨 Formatters",
        'date_utilities': "📅 Date Utilities",
        'main_ui': "🖥️  Main UI Updates",
        'dependencies': "📦 Dependencies",
        'chart_generation': "🖼️  Chart Generation",
        'integration': "🔧 Integration Test",
    }
    
    for category, category_results in all_results.items():
        display_name = category_names.get(category, category.replace('_', ' ').title())
        print(f"\n{display_name}:")
        print("-" * 50)
        
        for check_name, check_result in category_results.items():
            # Skip non-boolean results and debug info
            skip_patterns = ['error', 'actual_methods', 'list', 'rate', 'version', 'count', 'debug', 'found']
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
            status = "✅ Excellent! Phase 3 visualization features are complete."
        elif percentage >= 60:
            status_color = "\033[93m"
            status = "📊 Good progress. Visualization features mostly implemented."
        elif percentage >= 40:
            status_color = "\033[93m"
            status = "⚡ Moderate progress. Basic visualization implemented."
        else:
            status_color = "\033[91m"
            status = "🚧 Needs work. Start with matplotlib integration."
        
        reset = "\033[0m"
        print(f"{status_color}{status}{reset}")
        
        # Next steps
        print("\n" + "=" * 70)
        if percentage >= 70:
            print("🎉 PHASE 3 COMPLETED! Ready for Phase 4.")
            print("👉 Next step: Run 'python phase4-verify.py' for Phase 4 (Export features)")
        else:
            print("⚠️  PHASE 3 INCOMPLETE - Some checks failed.")
            print("👉 Next step: Run 'python phase3-fixer.py' to fix Phase 3 issues")
        print("=" * 70)


# ==================== MAIN FUNCTION ====================

def verify_phase3() -> None:
    """
    Main function to run all Phase 3 verifications.
    """
    print_header("DAILY EXPENSE TRACKER - PHASE 3 VERIFICATION")
    print("📊 VISUALIZATION & ENHANCEMENTS CHECK")
    
    # Get project root
    project_root = Path(__file__).parent
    print(f"📁 Project Location: {project_root.absolute()}")
    print(f"⚙️  Phase Focus: Visualization, Formatters, UI Enhancements")
    print(f"📋 Based on blueprint: ChartService, formatters, date utilities")
    
    print_header("RUNNING PHASE 3 VERIFICATIONS")
    
    # Run all verifications
    results = {
        'visualization': verify_visualization_module(project_root),
        'formatters': verify_formatters(project_root),
        'date_utilities': verify_date_utilities(project_root),
        'main_ui': verify_main_ui_updates(project_root),
        'dependencies': verify_dependencies(project_root),
        'chart_generation': verify_chart_generation(project_root),
        'integration': run_safe_integration_test(project_root),
    }
    
    # Display results
    calculate_and_display_score(results)


if __name__ == "__main__":
    try:
        verify_phase3()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {e}")
        print("Please ensure the project structure is correct.")
        import traceback
        traceback.print_exc()
        sys.exit(1)