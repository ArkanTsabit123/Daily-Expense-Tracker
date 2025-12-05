#daily-expense-tracker/phase3-verify.py

"""
Phase 3 Verification Script
Verifies the implementation of visualization features, formatters,
date utilities, and main UI updates for the daily-expense-tracker application.
"""

import importlib.util
import sys
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


def check_file_contains_patterns(file_path: Path, patterns: List[str]) -> Dict[str, bool]:
    """
    Check if a file contains specific patterns.
    
    Args:
        file_path: Path to the file to check
        patterns: List of string patterns to search for
        
    Returns:
        Dictionary mapping pattern names to boolean results
    """
    results = {}
    
    if not file_path.exists():
        for pattern in patterns:
            results[pattern] = False
        return results
    
    content = read_file_with_encoding(file_path)
    if content is None:
        for pattern in patterns:
            results[pattern] = False
        return results
    
    for pattern in patterns:
        results[pattern] = pattern in content
    
    return results


# ==================== VERIFICATION MODULES ====================

def verify_visualization_module(project_root: Path) -> Dict[str, bool]:
    """
    Verify visualization module implementation.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check chart service
    chart_service_path = project_root / "visualization" / "chart_service.py"
    results['chart_service_exists'] = chart_service_path.exists()
    
    if results['chart_service_exists']:
        success, module, message = import_module_from_path(chart_service_path, "chart_service")
        results['chart_service_importable'] = success
        
        if success:
            # Check for ChartService class
            if hasattr(module, 'ChartService'):
                results['has_chart_service_class'] = True
                
                # Get the ChartService class
                chart_service_class = module.ChartService
                
                # Check required methods
                required_methods = [
                    "generate_pie_chart",
                    "generate_monthly_trend_chart",
                    "generate_category_trend_chart",
                    "generate_expense_distribution_chart",
                    "save_chart",
                ]
                
                for method in required_methods:
                    results[f'has_{method}'] = hasattr(chart_service_class, method)
            else:
                results['has_chart_service_class'] = False
        else:
            results['import_error'] = message
    
    # Check visualization package structure
    visualization_dir = project_root / "visualization"
    results['visualization_dir_exists'] = visualization_dir.exists()
    
    if results['visualization_dir_exists']:
        init_path = visualization_dir / "__init__.py"
        results['has_init_file'] = init_path.exists()
    
    # Check for common chart types in code
    if chart_service_path.exists():
        content = read_file_with_encoding(chart_service_path)
        if content:
            chart_types = [
                "plot.bar",  # Bar chart
                "plot.pie",  # Pie chart
                "plot.line",  # Line chart
                "figure",  # Matplotlib figure
                "plt.",  # Matplotlib pyplot
            ]
            
            for chart_type in chart_types:
                results[f'uses_{chart_type.replace(".", "_")}'] = chart_type in content
    
    return results


def verify_formatters(project_root: Path) -> Dict[str, bool]:
    """
    Verify formatters module implementation.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check formatters module
    formatters_path = project_root / "utils" / "formatters.py"
    results['formatters_exists'] = formatters_path.exists()
    
    if results['formatters_exists']:
        success, module, message = import_module_from_path(formatters_path, "formatters")
        results['formatters_importable'] = success
        
        if success:
            # Check required functions
            required_functions = [
                "format_currency",
                "format_date",
                "format_category",
                "format_percentage",
                "format_number",
            ]
            
            for func in required_functions:
                results[f'has_{func}'] = hasattr(module, func)
        else:
            results['import_error'] = message
    
    # Check for localization/currency support
    if formatters_path.exists():
        content = read_file_with_encoding(formatters_path)
        if content:
            # Check for common formatting patterns
            formatting_patterns = [
                "locale",  # Localization
                "currency",  # Currency formatting
                "IDR", "Rp",  # Indonesian Rupiah
                "%.2f",  # Decimal formatting
                "strftime",  # Date formatting
            ]
            
            for pattern in formatting_patterns:
                results[f'has_{pattern.lower()}_support'] = pattern in content
    
    return results


def verify_dependencies(project_root: Path) -> Dict[str, bool]:
    """
    Verify required dependencies for Phase 3.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check requirements.txt
    requirements_path = project_root / "requirements.txt"
    results['requirements_exists'] = requirements_path.exists()
    
    if results['requirements_exists']:
        content = read_file_with_encoding(requirements_path)
        if content:
            content_lower = content.lower()
            
            # Check for visualization libraries
            visualization_libs = [
                "matplotlib",
                "seaborn",  # Optional but nice to have
                "plotly",   # Optional
            ]
            
            for lib in visualization_libs:
                results[f'has_{lib}'] = lib in content_lower
                
            # Check version specifications
            results['has_version_specs'] = any(
                char in content for char in ['==', '>=', '<=', '~=']
            )
        else:
            results['read_requirements_error'] = True
    
    # Try to import matplotlib
    try:
        import matplotlib.pyplot as plt
        results['matplotlib_importable'] = True
        
        # Check specific matplotlib components
        results['has_pyplot'] = True
        results['has_figure_class'] = True
    except ImportError:
        results['matplotlib_importable'] = False
        results['has_pyplot'] = False
        results['has_figure_class'] = False
    
    # Try to import pandas (commonly used with matplotlib)
    try:
        import pandas as pd
        results['pandas_importable'] = True
    except ImportError:
        results['pandas_importable'] = False
    
    return results


def verify_date_utilities(project_root: Path) -> Dict[str, bool]:
    """
    Verify date utilities module.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check date utilities module
    date_utils_path = project_root / "utils" / "date_utils.py"
    results['date_utils_exists'] = date_utils_path.exists()
    
    if results['date_utils_exists']:
        success, module, message = import_module_from_path(date_utils_path, "date_utils")
        results['date_utils_importable'] = success
        
        if success:
            # Check required functions
            required_functions = [
                "get_current_month_year",
                "get_month_name",
                "get_month_range",
                "format_date_for_display",
                "parse_date_string",
                "get_previous_month",
                "get_next_month",
            ]
            
            for func in required_functions:
                results[f'has_{func}'] = hasattr(module, func)
        else:
            results['import_error'] = message
    
    # Check for datetime usage patterns
    if date_utils_path.exists():
        content = read_file_with_encoding(date_utils_path)
        if content:
            datetime_patterns = [
                "datetime.date",
                "datetime.datetime",
                "strftime",
                "strptime",
                "timedelta",
            ]
            
            for pattern in datetime_patterns:
                results[f'uses_{pattern.replace(".", "_")}'] = pattern in content
    
    return results


def verify_main_ui_updates(project_root: Path) -> Dict[str, bool]:
    """
    Verify main UI updates for Phase 3 features.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    main_path = project_root / "main.py"
    results['main_file_exists'] = main_path.exists()
    
    if not results['main_file_exists']:
        return results
    
    content = read_file_with_encoding(main_path)
    if content is None:
        return results
    
    # Check imports for Phase 3 features
    required_imports = [
        "visualization.chart_service",
        "utils.formatters",
        "utils.date_utils",
    ]
    
    for import_stmt in required_imports:
        results[f'imports_{import_stmt.replace(".", "_")}'] = import_stmt in content
    
    # Check for new menu options
    menu_patterns = [
        "generate_chart_menu",
        "view_monthly_analysis",
        "show_visualization",
        "chart",
        "visualize",
    ]
    
    for pattern in menu_patterns:
        results[f'has_{pattern}_menu'] = pattern in content.lower()
    
    # Check for chart-related function definitions
    function_patterns = [
        "def generate_chart",
        "def view_monthly_analysis",
        "def show_category_trend",
        "def create_pie_chart",
    ]
    
    for pattern in function_patterns:
        results[f'has_{pattern.split()[1]}'] = pattern in content
    
    # Check for formatter usage
    formatter_calls = [
        "format_currency",
        "format_date",
        "format_category",
    ]
    
    for call in formatter_calls:
        results[f'uses_{call}'] = call in content
    
    return results


def verify_configuration_updates(project_root: Path) -> Dict[str, bool]:
    """
    Verify configuration updates for Phase 3.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    # Check for chart configuration
    config_path = project_root / "config" / "chart_config.py"
    results['chart_config_exists'] = config_path.exists()
    
    if results['chart_config_exists']:
        content = read_file_with_encoding(config_path)
        if content:
            config_patterns = [
                "COLORS",
                "STYLES",
                "FIGURE_SIZE",
                "FONT_SIZE",
                "CHART_TYPES",
            ]
            
            for pattern in config_patterns:
                results[f'has_{pattern.lower()}'] = pattern in content
    
    # Check for export configuration
    export_config_path = project_root / "config" / "export_config.py"
    results['export_config_exists'] = export_config_path.exists()
    
    return results


def run_integration_test(project_root: Path) -> Dict[str, bool]:
    """
    Run an integration test for Phase 3 features.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    try:
        # Add project root to Python path
        sys.path.insert(0, str(project_root))
        
        print(f"\n🔍 Running integration tests...")
        
        # Test 1: Formatters
        try:
            from utils.formatters import format_currency, format_date, format_category
            
            # Test format_currency
            amount = Decimal("50000.75")
            formatted_currency = format_currency(amount)
            results['format_currency_works'] = bool(formatted_currency)
            print(f"  ✓ format_currency({amount}) → {formatted_currency}")
            
            # Test format_date
            test_date = "2024-12-03"
            formatted_date = format_date(test_date)
            results['format_date_works'] = bool(formatted_date)
            print(f"  ✓ format_date('{test_date}') → {formatted_date}")
            
            # Test format_category
            test_category = "Makanan & Minuman"
            formatted_category = format_category(test_category)
            results['format_category_works'] = bool(formatted_category)
            print(f"  ✓ format_category('{test_category}') → {formatted_category}")
            
        except ImportError as e:
            print(f"  ✗ Formatters import failed: {e}")
            results['formatters_integration'] = False
        
        # Test 2: Date Utilities
        try:
            from utils.date_utils import get_current_month_year, get_month_name
            
            month_year = get_current_month_year()
            results['get_current_month_year_works'] = bool(month_year)
            print(f"  ✓ get_current_month_year() → {month_year}")
            
            month_name = get_month_name(1)  # January
            results['get_month_name_works'] = bool(month_name)
            print(f"  ✓ get_month_name(1) → {month_name}")
            
        except ImportError as e:
            print(f"  ✗ Date utilities import failed: {e}")
            results['date_utils_integration'] = False
        
        # Test 3: Chart Service
        try:
            from visualization.chart_service import ChartService
            
            # Create instance
            chart_service = ChartService()
            results['chart_service_instantiation'] = True
            print(f"  ✓ ChartService instantiated successfully")
            
            # Check if methods exist (don't actually generate charts to avoid display issues)
            if hasattr(chart_service, 'generate_pie_chart'):
                results['has_pie_chart_method'] = True
                print(f"  ✓ generate_pie_chart() method exists")
            
            if hasattr(chart_service, 'generate_monthly_trend_chart'):
                results['has_trend_chart_method'] = True
                print(f"  ✓ generate_monthly_trend_chart() method exists")
                
        except ImportError as e:
            print(f"  ✗ Chart service import failed: {e}")
            results['chart_service_integration'] = False
        
        # Test 4: Matplotlib integration
        try:
            import matplotlib
            results['matplotlib_available'] = True
            print(f"  ✓ Matplotlib version: {matplotlib.__version__}")
        except ImportError:
            print(f"  ✗ Matplotlib not available")
            results['matplotlib_available'] = False
    
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
    print_header("PHASE 3 VERIFICATION SUMMARY")
    
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
            status = "🎉 Excellent! Phase 3 visualization features are complete."
        elif percentage >= 70:
            color = "\033[93m"  # Yellow
            status = "📊 Good progress. Review failed checks."
        elif percentage >= 50:
            color = "\033[93m"  # Yellow
            status = "⚡ Halfway there. Focus on visualization module."
        else:
            color = "\033[91m"  # Red
            status = "🚧 Needs work. Start with matplotlib integration."
        
        reset = "\033[0m"
        print(f"\n{color}[{bar}]{reset}")
        print(f"{color}{status}{reset}")
        
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        if percentage < 70:
            print("1. Implement ChartService with visualization methods")
            print("2. Create formatters for currency, dates, and categories")
            print("3. Update main.py with chart menu options")
            print("4. Add matplotlib to requirements.txt")
        
        print(f"\n🎯 Next: Consider adding data export features or advanced analytics.")
    
    else:
        print("No checks were performed.")


# ==================== MAIN FUNCTION ====================

def verify_phase3() -> None:
    """
    Main function to run all Phase 3 verifications.
    """
    print_header("DAILY EXPENSE TRACKER - PHASE 3 VERIFICATION")
    
    # Get project root
    project_root = Path(__file__).parent
    print(f"📁 Project Location: {project_root.absolute()}")
    print(f"📊 Phase Focus: Visualization, Formatters, UI Enhancements")
    
    print_header("RUNNING PHASE 3 VERIFICATIONS")
    
    # Run all verifications
    results = {
        'visualization': verify_visualization_module(project_root),
        'formatters': verify_formatters(project_root),
        'dependencies': verify_dependencies(project_root),
        'date_utilities': verify_date_utilities(project_root),
        'main_ui': verify_main_ui_updates(project_root),
        'configuration': verify_configuration_updates(project_root),
        'integration': run_integration_test(project_root),
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
        sys.exit(1)