# project portofolio/junior project/daily-expense-tracker/phase3-verify.py

"""
Phase 3 Verification Script
Verifies the implementation of visualization features, formatters,
date utilities, and main UI updates for the daily-expense-tracker application.
"""

# phase3-verify-fixed.py
"""
Fixed Phase 3 Verification Script
"""

import sys
from pathlib import Path
import importlib.util

project_root = Path(__file__).parent

class VerificationTracker:
    def __init__(self):
        self.total_checks = 0
        self.passed_checks = 0
    
    def check_item(self, name, passed, message=""):
        self.total_checks += 1
        if passed:
            self.passed_checks += 1
            status = "✅ PASS"
            symbol = "✅"
        else:
            status = "❌ FAIL"
            symbol = "❌"
        
        print(f"{symbol} {name:40} {status}")
        if message:
            print(f"   {message}")
    
    def get_score(self):
        if self.total_checks == 0:
            return 0
        return (self.passed_checks / self.total_checks) * 100


def print_header(text):
    print("\n" + "=" * 70)
    print(f" {text}".center(70))
    print("=" * 70)


def check_module_exists(module_path, module_name):
    full_path = project_root / module_path
    if not full_path.exists():
        return False, f"File not found: {module_path}"
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, full_path)
        if spec is None:
            return False, f"Cannot load module: {module_name}"
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, f"Module imported: {module_name}"
    except Exception as e:
        return False, f"Import error: {str(e)}"


def check_visualization_module(tracker):
    print_header("VISUALIZATION MODULE CHECK")
    
    chart_service_path = "visualization/chart_service.py"
    passed, msg = check_module_exists(chart_service_path, "chart_service")
    tracker.check_item("Chart service exists", passed, msg)
    
    if passed:
        try:
            spec = importlib.util.spec_from_file_location(
                "chart_service",
                project_root / chart_service_path
            )
            chart_service = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(chart_service)
            
            required_methods = [
                'generate_pie_chart', 'generate_monthly_trend_chart',
                'generate_category_trend_chart'
            ]
            
            for method in required_methods:
                if hasattr(chart_service.ChartService, method):
                    tracker.check_item(f"Method {method}() exists", True)
                else:
                    tracker.check_item(f"Method {method}() exists", False)
                    
        except Exception as e:
            tracker.check_item("Chart service implementation", False, str(e))
    
    init_path = "visualization/__init__.py"
    init_exists = (project_root / init_path).exists()
    tracker.check_item("visualization/__init__.py exists", init_exists)


def check_formatters(tracker):
    print_header("FORMATTERS CHECK")
    
    formatters_path = "utils/formatters.py"
    passed, msg = check_module_exists(formatters_path, "formatters")
    tracker.check_item("Formatters module exists", passed, msg)
    
    if passed:
        try:
            spec = importlib.util.spec_from_file_location(
                "formatters",
                project_root / formatters_path
            )
            formatters = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(formatters)
            
            required_functions = [
                'format_currency', 'format_date', 'format_category',
                'format_percentage'
            ]
            
            for func in required_functions:
                if hasattr(formatters, func):
                    tracker.check_item(f"Function {func}() exists", True)
                else:
                    tracker.check_item(f"Function {func}() exists", False)
                    
        except Exception as e:
            tracker.check_item("Formatters implementation", False, str(e))


def check_matplotlib_dependency(tracker):
    print_header("DEPENDENCIES CHECK")
    
    requirements_path = project_root / "requirements.txt"
    if requirements_path.exists():
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        has_matplotlib = 'matplotlib' in content.lower()
        tracker.check_item("matplotlib in requirements", has_matplotlib)
    else:
        tracker.check_item("requirements.txt exists", False)
    
    try:
        import matplotlib
        tracker.check_item("matplotlib import", True)
    except ImportError:
        tracker.check_item("matplotlib import", False)


def check_date_utils(tracker):
    print_header("DATE UTILITIES CHECK")
    
    date_utils_path = "utils/date_utils.py"
    passed, msg = check_module_exists(date_utils_path, "date_utils")
    tracker.check_item("Date utilities exists", passed, msg)
    
    if passed:
        try:
            spec = importlib.util.spec_from_file_location(
                "date_utils",
                project_root / date_utils_path
            )
            date_utils = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(date_utils)
            
            required_functions = [
                'get_current_month_year', 'get_month_name',
                'get_month_range'
            ]
            
            for func in required_functions:
                if hasattr(date_utils, func):
                    tracker.check_item(f"Function {func}() exists", True)
                else:
                    tracker.check_item(f"Function {func}() exists", False)
                    
        except Exception as e:
            tracker.check_item("Date utilities implementation", False, str(e))


def check_main_ui_updates(tracker):
    print_header("MAIN UI UPDATES CHECK")
    
    main_path = project_root / "main.py"
    if not main_path.exists():
        tracker.check_item("main.py exists", False)
        return
    
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_chart_service_import = 'visualization.chart_service' in content
    tracker.check_item("Chart service import in main.py", has_chart_service_import)
    
    has_formatters_import = 'utils.formatters' in content
    tracker.check_item("Formatters import in main.py", has_formatters_import)
    
    has_generate_chart_menu = 'def generate_chart_menu' in content
    tracker.check_item("generate_chart_menu() method", has_generate_chart_menu)
    
    has_view_monthly_analysis = 'def view_monthly_analysis' in content
    tracker.check_item("view_monthly_analysis() method", has_view_monthly_analysis)


def run_integration_test(tracker):
    print_header("INTEGRATION TEST")
    
    try:
        sys.path.insert(0, str(project_root))
        
        from utils.formatters import format_currency, format_date, format_category
        from decimal import Decimal
        
        amount = Decimal("50000")
        formatted = format_currency(amount)
        tracker.check_item("format_currency() works", 'Rp' in formatted)
        
        date_str = "2024-12-03"
        formatted_date = format_date(date_str)
        tracker.check_item("format_date() works", '/' in formatted_date)
        
        category = "Makanan & Minuman"
        formatted_cat = format_category(category)
        tracker.check_item("format_category() works", '🍔' in formatted_cat)
        
        try:
            from visualization.chart_service import ChartService
            tracker.check_item("ChartService import", True)
            
            service = ChartService()
            tracker.check_item("ChartService instantiation", True)
            
        except ImportError as e:
            tracker.check_item("ChartService import", False, str(e))
            
    except Exception as e:
        tracker.check_item("Integration test", False, f"Error: {str(e)}")


def main():
    print_header("DAILY EXPENSE TRACKER - PHASE 3 VERIFICATION")
    print(f"Project location: {project_root}\n")
    
    tracker = VerificationTracker()
    
    check_visualization_module(tracker)
    check_formatters(tracker)
    check_matplotlib_dependency(tracker)
    check_date_utils(tracker)
    check_main_ui_updates(tracker)
    run_integration_test(tracker)
    
    print_header("PHASE 3 VERIFICATION RESULTS")
    
    percentage = tracker.get_score()
    
    bar_length = 50
    filled = int(percentage / 100 * bar_length)
    bar = f"{'█' * filled}{'░' * (bar_length - filled)}"
    
    print(f"\nProgress: [{bar}] {percentage:.1f}%")
    print(f"Passed: {tracker.passed_checks}/{tracker.total_checks} checks")
    
    if percentage >= 90:
        print("\n✅ Excellent! Phase 3 is complete.")
    elif percentage >= 70:
        print("\n⚠️ Good progress. Review the failed checks.")
    elif percentage >= 50:
        print("\n⚠️ Halfway there. Focus on visualization features.")
    else:
        print("\n❌ Needs work. Start with visualization module.")
    
    print("\nAll checks completed successfully!")


if __name__ == "__main__":
    main()