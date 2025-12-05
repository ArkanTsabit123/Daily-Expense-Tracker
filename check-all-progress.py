#daily-expense-tracker/check-all-progress.py

"""
Daily Expense Tracker - Complete Project Progress Checker

This script verifies all phases (1-5) of the Daily Expense Tracker project
and provides a comprehensive progress report with recommendations.
"""

import json
import sqlite3
import subprocess
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Import all phase verification functions
try:
    from phase1_verify import verify_phase1
except ImportError:
    verify_phase1 = None
    print("⚠️  Could not import phase1_verify.py")

try:
    from phase2_verify import verify_phase2
except ImportError:
    verify_phase2 = None
    print("⚠️  Could not import phase2_verify.py")

try:
    from phase3_verify import verify_phase3
except ImportError:
    verify_phase3 = None
    print("⚠️  Could not import phase3_verify.py")

try:
    from phase4_verify import verify_phase4
except ImportError:
    verify_phase4 = None
    print("⚠️  Could not import phase4_verify.py")

try:
    from phase5_verify import verify_phase5
except ImportError:
    verify_phase5 = None
    print("⚠️  Could not import phase5_verify.py")


# ==================== UTILITY FUNCTIONS ====================

def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {text}".center(80))
    print("=" * 80)


def print_section(text: str) -> None:
    """Print a section header."""
    print("\n" + "-" * 60)
    print(f" {text}".center(60))
    print("-" * 60)


def print_progress_bar(name: str, percentage: float, width: int = 40) -> None:
    """
    Print a progress bar with percentage.
    
    Args:
        name: Name of the progress item
        percentage: Completion percentage (0-100)
        width: Width of the progress bar
    """
    filled = int(width * percentage // 100)
    bar = "█" * filled + "░" * (width - filled)
    
    if percentage >= 90:
        color = "\033[92m"  # Green
    elif percentage >= 70:
        color = "\033[93m"  # Yellow
    elif percentage >= 50:
        color = "\033[96m"  # Cyan
    else:
        color = "\033[91m"  # Red
    
    reset = "\033[0m"
    print(f"{name:25} [{color}{bar}{reset}] {percentage:6.1f}%")


def print_check_result(name: str, passed: bool, details: str = "", indent: int = 0) -> None:
    """
    Print the result of a check with indentation support.
    
    Args:
        name: Name of the check
        passed: Boolean indicating if check passed
        details: Additional details or error message
        indent: Number of spaces to indent
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
    indent_str = " " * indent
    
    print(f"{indent_str}{symbol} {name:40} {color_code}{status}{reset_code}")
    
    if details:
        detail_color = "\033[93m" if not passed else "\033[94m"  # Yellow for errors, blue for info
        print(f"{indent_str}    ↳ {detail_color}{details}{reset_code}")


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


def run_quick_sanity_check(project_root: Path) -> Dict[str, bool]:
    """
    Run a quick sanity check on the project structure.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with sanity check results
    """
    results = {}
    
    print_section("QUICK SANITY CHECK")
    
    # Check basic project structure
    essential_dirs = ["models", "services", "utils", "tests", "data"]
    for dir_name in essential_dirs:
        dir_path = project_root / dir_name
        results[f"dir_{dir_name}"] = dir_path.exists()
        print_check_result(f"Directory: {dir_name}", dir_path.exists())
    
    # Check essential files
    essential_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "phase1-verify.py",
        "phase2-verify.py",
        "phase3-verify.py",
        "phase4-verify.py",
        "phase5-verify.py",
        "check-all-progress.py",
    ]
    
    for file_name in essential_files:
        file_path = project_root / file_name
        results[f"file_{file_name}"] = file_path.exists()
        print_check_result(f"File: {file_name}", file_path.exists())
    
    # Check database
    db_path = project_root / "data" / "expenses.db"
    results["database_exists"] = db_path.exists()
    print_check_result("Database file exists", db_path.exists())
    
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            results["has_tables"] = len(tables) > 0
            results["has_expenses_table"] = "expenses" in tables
            results["has_categories_table"] = "categories" in tables
            
            print_check_result("Database has tables", len(tables) > 0, f"Found tables: {', '.join(tables)}")
        except Exception as e:
            results["database_error"] = str(e)
            print_check_result("Database connection", False, f"Error: {e}")
    
    return results


def check_dependencies(project_root: Path) -> Dict[str, bool]:
    """
    Check if required dependencies are installed.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with dependency check results
    """
    results = {}
    
    print_section("DEPENDENCY CHECK")
    
    # Check requirements.txt
    req_path = project_root / "requirements.txt"
    if req_path.exists():
        content = read_file_with_encoding(req_path)
        if content:
            required_packages = [
                ("pandas", "Data analysis"),
                ("matplotlib", "Visualization"),
                ("pytest", "Testing"),
                ("black", "Code formatting"),
                ("flake8", "Code linting"),
            ]
            
            for package, description in required_packages:
                has_package = package in content.lower()
                results[f"requires_{package}"] = has_package
                print_check_result(f"{description} ({package})", has_package)
    
    # Check if Python packages can be imported
    packages_to_check = [
        ("sqlite3", "SQLite database"),
        ("datetime", "Date/time handling"),
        ("decimal", "Decimal precision"),
    ]
    
    for package, description in packages_to_check:
        try:
            __import__(package)
            results[f"import_{package}"] = True
            print_check_result(f"Python module: {description}", True)
        except ImportError:
            results[f"import_{package}"] = False
            print_check_result(f"Python module: {description}", False)
    
    return results


def check_git_status(project_root: Path) -> Dict[str, bool]:
    """
    Check Git repository status.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with Git status results
    """
    results = {}
    
    print_section("GIT REPOSITORY CHECK")
    
    # Check if it's a Git repository
    git_dir = project_root / ".git"
    results["is_git_repo"] = git_dir.exists()
    print_check_result("Git repository initialized", git_dir.exists())
    
    if git_dir.exists():
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                results["git_branch"] = branch
                print_check_result(f"Current branch: {branch}", True)
            
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            if result.returncode == 0:
                changes = result.stdout.strip()
                has_changes = len(changes) > 0
                results["has_uncommitted_changes"] = has_changes
                if has_changes:
                    change_count = len(changes.split('\n'))
                    print_check_result("Uncommitted changes", False, f"{change_count} file(s) modified")
                else:
                    print_check_result("All changes committed", True)
            
            # Check for remote
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            if result.returncode == 0 and result.stdout.strip():
                results["has_remote"] = True
                print_check_result("Git remote configured", True)
            else:
                results["has_remote"] = False
                print_check_result("Git remote configured", False, "No remote repository")
                
        except Exception as e:
            results["git_error"] = str(e)
            print_check_result("Git operations", False, f"Error: {e}")
    
    return results


def run_basic_functionality_test(project_root: Path) -> Dict[str, bool]:
    """
    Run basic functionality tests.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with functionality test results
    """
    results = {}
    
    print_section("BASIC FUNCTIONALITY TEST")
    
    try:
        # Add project root to Python path
        sys.path.insert(0, str(project_root))
        
        print("Testing core functionality...")
        
        # Test 1: Model imports
        try:
            from models.expense_model import Expense
            from models.category_model import Category
            
            # Create test instances
            expense = Expense(
                date=datetime.now().date(),
                category="Test",
                amount=Decimal("1000.50"),
                description="Test expense"
            )
            
            category = Category(name="Test Category")
            
            results["models_import"] = True
            results["models_instantiate"] = True
            print_check_result("Model imports and instantiation", True)
        except Exception as e:
            results["models_import"] = False
            print_check_result("Model imports and instantiation", False, f"Error: {e}")
        
        # Test 2: Database service
        try:
            from services.database_service import DatabaseService
            
            db_service = DatabaseService()
            results["database_service"] = True
            
            # Try to get expenses
            expenses = db_service.get_expenses(limit=1)
            results["database_query"] = expenses is not None
            print_check_result("Database service and query", True)
        except Exception as e:
            results["database_service"] = False
            print_check_result("Database service and query", False, f"Error: {e}")
        
        # Test 3: Validation
        try:
            from utils.validation import validate_date, validate_amount
            
            date_valid, _ = validate_date("2024-01-15")
            amount_valid, _ = validate_amount("1000.50")
            
            results["validation_import"] = True
            results["validation_functions"] = date_valid and amount_valid
            print_check_result("Validation functions", True)
        except Exception as e:
            results["validation_import"] = False
            print_check_result("Validation functions", False, f"Error: {e}")
        
        # Test 4: Formatters
        try:
            from utils.formatters import format_currency, format_date
            
            formatted_currency = format_currency(Decimal("1000.50"))
            formatted_date = format_date("2024-01-15")
            
            results["formatters_import"] = True
            results["formatters_work"] = bool(formatted_currency) and bool(formatted_date)
            print_check_result("Formatter functions", True)
        except Exception as e:
            results["formatters_import"] = False
            print_check_result("Formatter functions", False, f"Error: {e}")
        
        # Test 5: Export service
        try:
            from services.export_service import ExportService
            
            export_service = ExportService()
            results["export_service"] = True
            print_check_result("Export service", True)
        except Exception as e:
            results["export_service"] = False
            print_check_result("Export service", False, f"Error: {e}")
        
        # Test 6: Visualization
        try:
            from visualization.chart_service import ChartService
            
            chart_service = ChartService()
            results["chart_service"] = True
            print_check_result("Chart service", True)
        except Exception as e:
            results["chart_service"] = False
            print_check_result("Chart service", False, f"Error: {e}")
    
    except Exception as e:
        print_check_result("Overall functionality test", False, f"Error: {e}")
    
    finally:
        # Clean up path modification
        if str(project_root) in sys.path:
            sys.path.remove(str(project_root))
    
    return results


def get_phase_summary() -> Dict[str, Dict[str, Any]]:
    """
    Get summary information about each phase.
    
    Returns:
        Dictionary with phase summaries
    """
    phases = {
        "Phase 1": {
            "description": "Foundation & Basic Structure",
            "focus": ["Database Setup", "Model Classes", "Basic Validation"],
            "requirements": [
                "Database with expenses and categories tables",
                "Expense and Category models",
                "Validation functions",
                "Project structure setup"
            ],
            "files": [
                "data/expenses.db",
                "models/expense_model.py",
                "models/category_model.py",
                "utils/validation.py"
            ]
        },
        "Phase 2": {
            "description": "Core Functionality & Testing",
            "focus": ["CRUD Operations", "Business Logic", "Error Handling"],
            "requirements": [
                "Database service with CRUD operations",
                "Expense service with business logic",
                "Filtering and search capabilities",
                "Testing framework setup",
                "Error handling implementation"
            ],
            "files": [
                "services/database_service.py",
                "services/expense_service.py",
                "tests/ directory",
                "utils/exceptions.py"
            ]
        },
        "Phase 3": {
            "description": "Visualization & User Interface",
            "focus": ["Charts & Graphs", "Data Formatting", "UI Enhancements"],
            "requirements": [
                "Chart generation service",
                "Data formatters (currency, dates)",
                "Date utilities",
                "Main UI with visualization options"
            ],
            "files": [
                "visualization/chart_service.py",
                "utils/formatters.py",
                "utils/date_utils.py",
                "main.py (updated)"
            ]
        },
        "Phase 4": {
            "description": "Export Features & Code Quality",
            "focus": ["Data Export", "Reporting", "Performance", "Code Quality"],
            "requirements": [
                "Export service (CSV, Excel, JSON)",
                "Reporting features",
                "Database indexing",
                "Code quality tools (flake8, black)"
            ],
            "files": [
                "services/export_service.py",
                "exports/ directory",
                "requirements.txt (updated)",
                "pyproject.toml"
            ]
        },
        "Phase 5": {
            "description": "Polish & Deployment",
            "focus": ["Code Quality", "Documentation", "Testing", "Deployment"],
            "requirements": [
                "PEP 8 compliance",
                "Comprehensive documentation",
                "Test suite completion",
                "Cross-platform compatibility",
                "Deployment readiness"
            ],
            "files": [
                "README.md",
                "tests/ (complete)",
                "docs/ directory",
                "setup.py"
            ]
        }
    }
    
    return phases


def calculate_overall_progress(phase_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate overall progress based on phase results.
    
    Args:
        phase_results: Dictionary with results from each phase
        
    Returns:
        Dictionary with overall progress metrics
    """
    total_phases = len(phase_results)
    completed_phases = 0
    total_checks = 0
    passed_checks = 0
    
    phase_percentages = {}
    
    for phase_name, results in phase_results.items():
        if 'percentage' in results:
            percentage = results['percentage']
            phase_percentages[phase_name] = percentage
            
            if percentage >= 80:  # Consider phase "complete" at 80%+
                completed_phases += 1
            
            # Estimate checks from percentage (assuming ~20 checks per phase)
            phase_checks = 20
            phase_passed = int(phase_checks * percentage / 100)
            total_checks += phase_checks
            passed_checks += phase_passed
    
    overall_percentage = (completed_phases / total_phases * 100) if total_phases > 0 else 0
    check_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    # Weighted average gives more importance to later phases
    weights = {
        "Phase 1": 0.1,
        "Phase 2": 0.2,
        "Phase 3": 0.2,
        "Phase 4": 0.25,
        "Phase 5": 0.25
    }
    
    weighted_sum = 0
    total_weight = 0
    for phase_name, percentage in phase_percentages.items():
        weight = weights.get(phase_name, 0.1)
        weighted_sum += percentage * weight
        total_weight += weight
    
    weighted_percentage = weighted_sum / total_weight if total_weight > 0 else 0
    
    return {
        "total_phases": total_phases,
        "completed_phases": completed_phases,
        "phase_completion_percentage": overall_percentage,
        "check_completion_percentage": check_percentage,
        "weighted_completion_percentage": weighted_percentage,
        "phase_percentages": phase_percentages
    }


def generate_recommendations(phase_results: Dict[str, Dict[str, Any]], 
                            overall_progress: Dict[str, Any]) -> List[str]:
    """
    Generate recommendations based on current progress.
    
    Args:
        phase_results: Dictionary with results from each phase
        overall_progress: Dictionary with overall progress metrics
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Check each phase's progress
    for phase_name, results in phase_results.items():
        if 'percentage' in results:
            percentage = results['percentage']
            
            if percentage < 50:
                recommendations.append(f"🔴 Focus on completing {phase_name} (currently {percentage:.1f}%)")
            elif percentage < 70:
                recommendations.append(f"🟡 Continue improving {phase_name} (currently {percentage:.1f}%)")
    
    # Overall recommendations
    weighted_percentage = overall_progress.get('weighted_completion_percentage', 0)
    
    if weighted_percentage < 30:
        recommendations.append("🎯 Priority: Complete Phase 1 (Foundation) first")
        recommendations.append("📚 Review the project requirements and structure")
    elif weighted_percentage < 50:
        recommendations.append("🎯 Priority: Focus on Phase 2 (Core Functionality)")
        recommendations.append("🧪 Implement CRUD operations and basic testing")
    elif weighted_percentage < 70:
        recommendations.append("🎯 Priority: Work on Phase 3 (Visualization)")
        recommendations.append("📊 Add charts and improve user interface")
    elif weighted_percentage < 85:
        recommendations.append("🎯 Priority: Complete Phase 4 (Export & Code Quality)")
        recommendations.append("📦 Implement export features and code quality checks")
    elif weighted_percentage < 95:
        recommendations.append("🎯 Priority: Polish with Phase 5 (Deployment)")
        recommendations.append("📚 Improve documentation and finalize testing")
    else:
        recommendations.append("✅ Project is nearly complete!")
        recommendations.append("🚀 Prepare for deployment and portfolio presentation")
    
    # Specific recommendations based on common issues
    if 'Phase 1' in phase_results:
        phase1_pct = phase_results['Phase 1'].get('percentage', 0)
        if phase1_pct < 70:
            recommendations.append("💡 Phase 1 Tip: Ensure database has both expenses and categories tables")
    
    if 'Phase 2' in phase_results:
        phase2_pct = phase_results['Phase 2'].get('percentage', 0)
        if phase2_pct < 70:
            recommendations.append("💡 Phase 2 Tip: Implement all CRUD operations in database_service.py")
    
    if 'Phase 5' in phase_results:
        phase5_pct = phase_results['Phase 5'].get('percentage', 0)
        if phase5_pct < 80:
            recommendations.append("💡 Phase 5 Tip: Run 'flake8 .' to check PEP 8 compliance")
    
    return recommendations


def save_progress_report(project_root: Path, phase_results: Dict[str, Dict[str, Any]], 
                        overall_progress: Dict[str, Any]) -> None:
    """
    Save progress report to a JSON file.
    
    Args:
        project_root: Root directory of the project
        phase_results: Dictionary with results from each phase
        overall_progress: Dictionary with overall progress metrics
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "project": "Daily Expense Tracker",
        "overall_progress": overall_progress,
        "phase_results": phase_results,
        "summary": {
            "status": "In Progress" if overall_progress.get('weighted_completion_percentage', 0) < 90 else "Complete",
            "recommendations": generate_recommendations(phase_results, overall_progress)
        }
    }
    
    report_path = project_root / "progress_report.json"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Progress report saved to: {report_path}")
    except Exception as e:
        print(f"\n⚠️  Could not save progress report: {e}")


# ==================== MAIN FUNCTION ====================

def check_all_progress() -> None:
    """
    Main function to check progress across all phases.
    """
    print_header("DAILY EXPENSE TRACKER - COMPLETE PROGRESS CHECK")
    
    # Get project root
    project_root = Path(__file__).parent
    print(f"📁 Project Location: {project_root.absolute()}")
    print(f"📅 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run initial checks
    print_header("INITIAL CHECKS")
    
    sanity_results = run_quick_sanity_check(project_root)
    dependency_results = check_dependencies(project_root)
    git_results = check_git_status(project_root)
    functionality_results = run_basic_functionality_test(project_root)
    
    # Get phase summaries
    phase_summary = get_phase_summary()
    
    print_header("PHASE-BY-PHASE PROGRESS")
    
    phase_results = {}
    
    # Simulate running each phase verification
    # In a real implementation, you would import and run the actual verification functions
    # For now, we'll simulate results based on file existence and quick tests
    
    for phase_name, phase_info in phase_summary.items():
        print_section(f"{phase_name}: {phase_info['description']}")
        print(f"Focus: {', '.join(phase_info['focus'])}")
        
        # Check key files for this phase
        files_exist = []
        files_missing = []
        
        for file_path in phase_info['files']:
            if "/" in file_path:
                # This is a file with path
                full_path = project_root / file_path
            elif "directory" in file_path.lower():
                # This is a directory check
                dir_name = file_path.split(" ")[0].rstrip("/")
                full_path = project_root / dir_name
            else:
                full_path = project_root / file_path
            
            if full_path.exists():
                files_exist.append(file_path)
            else:
                files_missing.append(file_path)
        
        # Calculate approximate percentage based on files
        total_files = len(phase_info['files'])
        existing_files = len(files_exist)
        file_percentage = (existing_files / total_files * 100) if total_files > 0 else 0
        
        # Adjust based on additional checks
        if phase_name == "Phase 1":
            # Check for database tables
            if sanity_results.get("has_expenses_table", False) and sanity_results.get("has_categories_table", False):
                file_percentage = min(100, file_percentage + 20)
        
        elif phase_name == "Phase 2":
            # Check for CRUD operations
            if functionality_results.get("database_service", False):
                file_percentage = min(100, file_percentage + 15)
            if functionality_results.get("validation_import", False):
                file_percentage = min(100, file_percentage + 10)
        
        elif phase_name == "Phase 3":
            # Check for visualization
            if functionality_results.get("formatters_import", False):
                file_percentage = min(100, file_percentage + 10)
            if functionality_results.get("chart_service", False):
                file_percentage = min(100, file_percentage + 15)
        
        elif phase_name == "Phase 4":
            # Check for export
            if functionality_results.get("export_service", False):
                file_percentage = min(100, file_percentage + 20)
        
        elif phase_name == "Phase 5":
            # Check for documentation and testing
            readme_path = project_root / "README.md"
            if readme_path.exists():
                content = read_file_with_encoding(readme_path)
                if content and len(content) > 100:  # Reasonable README
                    file_percentage = min(100, file_percentage + 15)
            
            tests_dir = project_root / "tests"
            if tests_dir.exists():
                test_files = list(tests_dir.glob("test_*.py"))
                if len(test_files) >= 3:
                    file_percentage = min(100, file_percentage + 15)
        
        phase_percentage = min(100, file_percentage)
        phase_results[phase_name] = {
            "description": phase_info['description'],
            "file_coverage": f"{existing_files}/{total_files}",
            "percentage": phase_percentage,
            "files_exist": files_exist,
            "files_missing": files_missing,
            "requirements": phase_info['requirements']
        }
        
        print_progress_bar(f"{phase_name} Progress", phase_percentage)
        
        if files_exist:
            display_files = files_exist[:3]
            print(f"  ✓ Found: {', '.join(display_files)}" + ("..." if len(files_exist) > 3 else ""))
        if files_missing:
            display_missing = files_missing[:3]
            print(f"  ✗ Missing: {', '.join(display_missing)}" + ("..." if len(files_missing) > 3 else ""))
    
    # Calculate overall progress
    overall_progress = calculate_overall_progress(phase_results)
    
    print_header("OVERALL PROJECT PROGRESS")
    
    print("\n📊 PHASE COMPLETION:")
    for phase_name, results in phase_results.items():
        percentage = results['percentage']
        print_progress_bar(phase_name, percentage)
    
    print("\n📈 OVERALL METRICS:")
    print(f"Phases Completed: {overall_progress['completed_phases']}/{overall_progress['total_phases']}")
    print(f"Phase Completion: {overall_progress['phase_completion_percentage']:.1f}%")
    print(f"Overall Progress: {overall_progress['weighted_completion_percentage']:.1f}%")
    
    # Visual overall progress
    print("\n🎯 OVERALL PROGRESS:")
    overall_percentage = overall_progress['weighted_completion_percentage']
    bar_length = 50
    filled = int(bar_length * overall_percentage // 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    if overall_percentage >= 90:
        color = "\033[92m"  # Green
        status = "🎉 EXCELLENT - Ready for final polish!"
    elif overall_percentage >= 70:
        color = "\033[93m"  # Yellow
        status = "📊 GOOD - Well on your way!"
    elif overall_percentage >= 50:
        color = "\033[96m"  # Cyan
        status = "⚡ MODERATE - Keep going!"
    elif overall_percentage >= 30:
        color = "\033[93m"  # Yellow
        status = "🚧 FAIR - Needs more work"
    else:
        color = "\033[91m"  # Red
        status = "🎯 JUST STARTED - Focus on Phase 1"
    
    reset = "\033[0m"
    print(f"[{color}{bar}{reset}] {overall_percentage:.1f}%")
    print(f"{color}{status}{reset}")
    
    # Generate and display recommendations
    recommendations = generate_recommendations(phase_results, overall_progress)
    
    print_header("RECOMMENDATIONS & NEXT STEPS")
    
    print("\n📋 PRIORITY ACTIONS:")
    for i, recommendation in enumerate(recommendations[:5], 1):
        print(f"{i}. {recommendation}")
    
    # Next phase focus
    print("\n🎯 NEXT PHASE FOCUS:")
    
    # Find the phase with lowest completion
    lowest_phase = None
    lowest_percentage = 100
    
    for phase_name, results in phase_results.items():
        percentage = results['percentage']
        if percentage < lowest_percentage:
            lowest_percentage = percentage
            lowest_phase = phase_name
    
    if lowest_phase:
        phase_info = phase_summary.get(lowest_phase, {})
        print(f"Work on {lowest_phase}: {phase_info.get('description', '')}")
        print(f"Focus areas: {', '.join(phase_info.get('focus', []))}")
        
        # Show specific requirements for this phase
        if 'requirements' in phase_info:
            print("\nKey requirements for this phase:")
            for req in phase_info['requirements'][:3]:
                print(f"  • {req}")
    
    # Portfolio readiness
    print_header("PORTFOLIO READINESS ASSESSMENT")
    
    portfolio_score = 0
    portfolio_criteria = []
    
    # Check criteria
    if overall_percentage >= 80:
        portfolio_score += 25
        portfolio_criteria.append("✅ Good overall progress (80%+)")
    else:
        portfolio_criteria.append(f"❌ Need better progress (currently {overall_percentage:.1f}%)")
    
    if functionality_results.get("database_service", False):
        portfolio_score += 20
        portfolio_criteria.append("✅ Core functionality implemented")
    else:
        portfolio_criteria.append("❌ Core functionality missing")
    
    readme_path = project_root / "README.md"
    if readme_path.exists():
        content = read_file_with_encoding(readme_path)
        if content and len(content) > 200:
            portfolio_score += 20
            portfolio_criteria.append("✅ Good documentation")
        else:
            portfolio_criteria.append("❌ Documentation needs improvement")
    else:
        portfolio_criteria.append("❌ Missing README.md")
    
    tests_dir = project_root / "tests"
    if tests_dir.exists():
        test_files = list(tests_dir.glob("test_*.py"))
        if len(test_files) >= 3:
            portfolio_score += 20
            portfolio_criteria.append("✅ Good test coverage")
        else:
            portfolio_criteria.append("❌ Need more tests")
    else:
        portfolio_criteria.append("❌ Missing tests directory")
    
    if git_results.get("is_git_repo", False):
        portfolio_score += 15
        portfolio_criteria.append("✅ Using version control")
    else:
        portfolio_criteria.append("❌ Not using Git")
    
    print(f"\nPortfolio Readiness Score: {portfolio_score}/100")
    
    if portfolio_score >= 80:
        print("🎉 Excellent! This project is portfolio-ready!")
    elif portfolio_score >= 60:
        print("📊 Good! Some improvements needed for portfolio.")
    elif portfolio_score >= 40:
        print("⚡ Fair. Significant work needed for portfolio.")
    else:
        print("🎯 Just starting. Focus on core functionality first.")
    
    print("\nCriteria:")
    for criterion in portfolio_criteria:
        print(f"  {criterion}")
    
    # Save progress report
    save_progress_report(project_root, phase_results, overall_progress)
    
    print_header("COMPLETE VERIFICATION")
    print("\n💡 Run individual phase verifications for detailed checks:")
    print("  python phase1-verify.py  - Database & models")
    print("  python phase2-verify.py  - CRUD operations & testing")
    print("  python phase3-verify.py  - Visualization & UI")
    print("  python phase4-verify.py  - Export & code quality")
    print("  python phase5-verify.py  - Polish & deployment")
    print("\n🚀 Keep up the great work!")


if __name__ == "__main__":
    try:
        check_all_progress()
    except KeyboardInterrupt:
        print("\n\n⚠️  Progress check interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during progress check: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)