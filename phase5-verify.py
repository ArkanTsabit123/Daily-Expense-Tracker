"""
PHASE 5 VERIFICATION SCRIPT - FIXED VERSION
Validates all Phase 5 requirements for the Daily Expense Tracker project.
"""

import os
import platform
import re
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


# ==================== VERIFICATION MODULES ====================

def verify_project_organization(project_root: Path) -> Dict[str, bool]:
    """
    Verify project organization completeness (5.1).
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    print("\n📁 Validating project organization...")
    
    # Required directories
    required_directories = [
        "config",
        "models", 
        "services",
        "utils",
        "visualization",
        "tests",
        "data",
        "exports",
        "docs",
        "generate"
    ]
    
    # Required files
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "pyproject.toml",
        "config/database_config.py",
        "models/expense_model.py",
        "models/category_model.py",
        "services/database_service.py",
        "services/expense_service.py",
        "services/export_service.py",
        "utils/validation.py",
        "utils/formatters.py",
        "utils/date_utils.py",
        "visualization/chart_service.py",
        "tests/__init__.py",
        "tests/test_database.py",
        "tests/test_expenses.py",
        "tests/test_export.py",
        "tests/test_validation.py",
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
    
    # Check files
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        results[f'file_{file_path.replace("/", "_")}_exists'] = exists
        if not exists:
            missing_files.append(file_path)
    
    results['all_files_exist'] = len(missing_files) == 0
    
    # Check for additional important files
    additional_checks = {
        'has_license': (project_root / "LICENSE").exists() or (project_root / "LICENSE.txt").exists(),
        'has_setup_py': (project_root / "setup.py").exists(),
        'has_setup_cfg': (project_root / "setup.cfg").exists(),
        'has_dockerfile': (project_root / "Dockerfile").exists() or (project_root / "docker-compose.yml").exists(),
    }
    
    results.update(additional_checks)
    
    return results


def verify_pep8_compliance(project_root: Path) -> Dict[str, bool]:
    """
    Verify PEP 8 compliance (5.2).
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    print("\n📐 Validating PEP 8 compliance...")
    
    # Check if flake8 is available
    flake8_available, flake8_version = run_shell_command(["flake8", "--version"], project_root)
    results['flake8_available'] = flake8_available
    
    if flake8_available:
        # Run flake8 to check code style
        flake8_success, flake8_output = run_shell_command(
            ["flake8", ".", "--count", "--exit-zero"], 
            project_root
        )
        
        # Parse flake8 output
        if flake8_success and flake8_output:
            # Try to get error count
            lines = flake8_output.strip().split('\n')
            if lines:
                # The last line often contains the count
                last_line = lines[-1]
                if last_line.isdigit():
                    error_count = int(last_line)
                else:
                    # Count non-empty lines
                    error_count = len([l for l in lines if l.strip()])
            else:
                error_count = 0
            
            results['flake8_error_count'] = error_count
            results['pep8_compliant'] = error_count == 0
            
            if error_count > 0:
                # Get some example errors
                example_errors = lines[:3] if len(lines) > 3 else lines
                results['flake8_examples'] = example_errors
        else:
            results['pep8_compliant'] = False
            results['flake8_error'] = "Flake8 check failed"
    else:
        results['pep8_compliant'] = False
        results['flake8_missing'] = True
    
    # Check for black formatter (optional but recommended)
    try:
        import black
        results['black_available'] = True
    except ImportError:
        results['black_available'] = False
    
    # Check for isort (import sorting)
    try:
        import isort
        results['isort_available'] = True
    except ImportError:
        results['isort_available'] = False
    
    return results


def verify_code_standards(project_root: Path) -> Dict[str, bool]:
    """
    Verify code standards and optimization (5.3).
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    print("\n🔍 Validating code standards...")
    
    # Find all Python files
    python_files = list(project_root.glob("**/*.py"))
    
    # Filter out virtual environment and cache directories
    filtered_files = []
    for py_file in python_files:
        file_str = str(py_file)
        if any(exclude in file_str for exclude in ['__pycache__', '.venv', 'venv', '.env', 'env']):
            continue
        filtered_files.append(py_file)
    
    results['python_file_count'] = len(filtered_files)
    
    # Check for TODO/FIXME comments
    todo_patterns = [r'#\s*TODO', r'#\s*FIXME', r'#\s*XXX', r'#\s*HACK']
    todo_count = 0
    files_with_todos = []
    
    # Check for print statements in non-test files
    print_count = 0
    files_with_prints = []
    
    # Check for proper docstrings
    files_without_docstrings = []
    
    for py_file in filtered_files:
        content = read_file_with_encoding(py_file)
        if content is None:
            continue
        
        file_name = py_file.name
        
        # Check for TODOs
        for pattern in todo_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                todo_count += 1
                if file_name not in files_with_todos:
                    files_with_todos.append(file_name)
        
        # Check for print statements (excluding test files)
        if 'test' not in file_name.lower() and 'print(' in content:
            print_count += 1
            files_with_prints.append(file_name)
        
        # Check for module docstrings (first line after imports should be a docstring)
        lines = content.split('\n')
        has_docstring = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import') or stripped.startswith('from'):
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                has_docstring = True
                break
            if stripped:  # First non-import, non-empty line
                break
        
        if not has_docstring and file_name != '__init__.py':
            files_without_docstrings.append(file_name)
    
    results['todo_fixme_count'] = todo_count
    results['has_todos'] = todo_count > 0
    results['print_statement_count'] = print_count
    results['has_prints'] = print_count > 0
    results['files_without_docstrings'] = len(files_without_docstrings)
    results['all_files_have_docstrings'] = len(files_without_docstrings) == 0
    
    # Check for proper imports organization
    import_issues = []
    for py_file in filtered_files[:10]:  # Check first 10 files
        content = read_file_with_encoding(py_file)
        if content and 'import' in content:
            # Check for wildcard imports
            if 'from' in content and 'import *' in content:
                import_issues.append(f"{py_file.name}: Wildcard import")
    
    results['import_issues'] = len(import_issues) > 0
    
    return results


def verify_documentation(project_root: Path) -> Dict[str, bool]:
    """
    Verify documentation comprehensiveness (5.4).
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    print("\n📚 Validating documentation...")
    
    # Check README.md
    readme_path = project_root / "README.md"
    results['readme_exists'] = readme_path.exists()
    
    if results['readme_exists']:
        content = read_file_with_encoding(readme_path)
        if content:
            content_lower = content.lower()
            
            # Check for required sections
            required_sections = [
                ("installation", ["install", "setup", "requirements"]),
                ("usage", ["usage", "how to use", "example"]),
                ("features", ["features", "functionality", "capabilities"]),
                ("contributing", ["contributing", "development", "build"]),
                ("license", ["license", "mit", "apache"]),
            ]
            
            for section_name, keywords in required_sections:
                found = any(keyword in content_lower for keyword in keywords)
                results[f'readme_has_{section_name}'] = found
            
            # Check for badges
            has_badges = any(badge in content for badge in ['![']) or 'badge' in content_lower
            results['readme_has_badges'] = has_badges
            
            # Check for screenshots or examples
            has_images = any(img in content for img in ['.png', '.jpg', '.gif', '```python'])
            results['readme_has_examples'] = has_images
        else:
            results['readme_readable'] = False
    else:
        results['readme_readable'] = False
    
    # Check for additional documentation
    docs_dir = project_root / "docs"
    results['docs_dir_exists'] = docs_dir.exists()
    
    if results['docs_dir_exists']:
        doc_files = list(docs_dir.glob("*.md")) + list(docs_dir.glob("*.rst"))
        results['doc_file_count'] = len(doc_files)
        
        # Check for specific documentation files
        specific_docs = {
            'api_docs': any(f.name.lower() in ['api.md', 'api.rst', 'reference.md'] for f in doc_files),
            'contributing_guide': any('contributing' in f.name.lower() for f in doc_files),
            'changelog': any(f.name.lower() in ['changelog.md', 'changes.md', 'history.md'] for f in doc_files),
        }
        results.update(specific_docs)
    
    # Check for docstrings in code
    python_files = list(project_root.glob("**/*.py"))
    filtered_files = [f for f in python_files if not any(
        exclude in str(f) for exclude in ['__pycache__', '.venv', 'venv', '.env']
    )]
    
    modules_with_docstrings = 0
    for py_file in filtered_files[:20]:  # Check first 20 files
        content = read_file_with_encoding(py_file)
        if content and ('\"\"\"' in content or "'''" in content):
            modules_with_docstrings += 1
    
    results['modules_with_docstrings'] = modules_with_docstrings
    results['docstring_coverage'] = modules_with_docstrings / len(filtered_files[:20]) if filtered_files else 0
    
    return results


def verify_test_suite(project_root: Path) -> Dict[str, bool]:
    """
    Verify testing suite (5.5).
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    print("\n🧪 Validating testing suite...")
    
    # Check tests directory
    tests_dir = project_root / "tests"
    results['tests_dir_exists'] = tests_dir.exists()
    
    if results['tests_dir_exists']:
        # Count test files
        test_files = list(tests_dir.glob("test_*.py"))
        results['test_file_count'] = len(test_files)
        
        # Check for specific test files
        required_tests = [
            "test_database.py",
            "test_expenses.py", 
            "test_export.py",
            "test_validation.py",
            "test_visualization.py",
        ]
        
        for test_file in required_tests:
            results[f'has_{test_file}'] = (tests_dir / test_file).exists()
        
        # Check conftest.py
        conftest_path = tests_dir / "conftest.py"
        results['has_conftest'] = conftest_path.exists()
        
        # Check if tests can be run
        try:
            success, output = run_shell_command(["pytest", "--collect-only", "-q"], project_root)
            results['pytest_working'] = success
            if success and output:
                # Count test cases
                test_count = len([line for line in output.split('\n') if line.strip()])
                results['test_case_count'] = test_count
        except Exception:
            results['pytest_working'] = False
        
        # Check for test coverage configuration
        coverage_files = [
            project_root / ".coveragerc",
            project_root / "pyproject.toml",
            project_root / "setup.cfg",
        ]
        
        has_coverage_config = False
        for config_file in coverage_files:
            if config_file.exists():
                content = read_file_with_encoding(config_file)
                if content and 'coverage' in content.lower():
                    has_coverage_config = True
                    break
        
        results['has_coverage_config'] = has_coverage_config
    else:
        results['tests_dir_exists'] = False
    
    return results


def verify_installation_configuration(project_root: Path) -> Dict[str, bool]:
    """
    Verify installation configuration (5.6).
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    print("\n📦 Validating installation configuration...")
    
    # Check required installation files
    required_files = [
        "requirements.txt",
        "pyproject.toml",
        "setup.py",  # Optional but good to have
        "setup.cfg",  # Optional
    ]
    
    for file_name in required_files:
        file_path = project_root / file_name
        exists = file_path.exists()
        results[f'{file_name}_exists'] = exists
        
        if exists and file_name in ['requirements.txt', 'pyproject.toml']:
            content = read_file_with_encoding(file_path)
            if content:
                results[f'{file_name}_readable'] = True
                
                # Check for basic content
                if file_name == 'requirements.txt':
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    results['requirements_count'] = len(lines)
                    
                    # Check for essential dependencies
                    essential_deps = ['pandas', 'matplotlib', 'sqlite3', 'pytest']
                    for dep in essential_deps:
                        results[f'requires_{dep}'] = any(dep in line.lower() for line in lines)
                
                elif file_name == 'pyproject.toml':
                    # Check for basic pyproject.toml structure
                    has_build_system = '[build-system]' in content
                    has_project = '[project]' in content or '[tool.poetry]' in content
                    results['pyproject_has_build_system'] = has_build_system
                    results['pyproject_has_project'] = has_project
            else:
                results[f'{file_name}_readable'] = False
    
    # Check for virtual environment indication
    venv_indicators = [
        project_root / ".venv",
        project_root / "venv",
        project_root / "env",
        project_root / "requirements.txt",
    ]
    
    has_venv = any(indicator.exists() for indicator in venv_indicators)
    results['has_virtualenv'] = has_venv
    
    # Check for .gitignore
    gitignore_path = project_root / ".gitignore"
    results['gitignore_exists'] = gitignore_path.exists()
    
    if results['gitignore_exists']:
        content = read_file_with_encoding(gitignore_path)
        if content:
            # Check for common ignored patterns
            ignore_patterns = ['__pycache__', '.pyc', '.env', 'venv', '.venv', '*.log']
            for pattern in ignore_patterns:
                results[f'gitignore_has_{pattern.replace("*", "star").replace(".", "dot")}'] = pattern in content
    
    return results


def verify_platform_independence(project_root: Path) -> Dict[str, bool]:
    """
    Verify cross-platform independence (5.7).
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    print("\n💻 Validating platform independence...")
    
    # Detect current platform
    current_platform = platform.system()
    results['current_platform'] = current_platform
    
    # Check for platform-specific code
    python_files = list(project_root.glob("**/*.py"))
    filtered_files = [f for f in python_files if not any(
        exclude in str(f) for exclude in ['__pycache__', '.venv', 'venv', '.env']
    )]
    
    platform_patterns = [
        (r'os\.name\s*==', 'os.name check'),
        (r'platform\.system\(\)', 'platform.system() call'),
        (r'sys\.platform', 'sys.platform check'),
        (r'nt\.path', 'Windows NT path'),
        (r'posix\.path', 'POSIX path'),
        (r'C:\\', 'Windows path literal'),
        (r'/home/', 'Linux home path'),
        (r'/Users/', 'macOS home path'),
    ]
    
    platform_issues = []
    for py_file in filtered_files[:30]:  # Check first 30 files
        content = read_file_with_encoding(py_file)
        if content:
            for pattern, description in platform_patterns:
                if re.search(pattern, content):
                    platform_issues.append(f"{py_file.name}: {description}")
    
    results['has_platform_specific_code'] = len(platform_issues) > 0
    results['platform_issue_count'] = len(platform_issues)
    
    # Check for path handling
    path_issues = []
    for py_file in filtered_files[:30]:
        content = read_file_with_encoding(py_file)
        if content:
            # Check for hardcoded paths
            if 'C:\\' in content or '/home/' in content or '/Users/' in content:
                path_issues.append(f"{py_file.name}: Hardcoded path")
            
            # Check for os.path.join usage (good practice)
            if 'os.path.join' in content:
                results['uses_os_path_join'] = True
    
    results['has_hardcoded_paths'] = len(path_issues) > 0
    
    # Check for proper line endings
    crlf_files = []
    for py_file in filtered_files[:20]:
        try:
            with open(py_file, 'rb') as f:
                content = f.read()
                if b'\r\n' in content:  # Windows line endings
                    crlf_files.append(py_file.name)
        except:
            pass
    
    results['has_windows_line_endings'] = len(crlf_files) > 0
    
    return results


def verify_deployment_readiness(project_root: Path) -> Dict[str, bool]:
    """
    Verify deployment preparation (5.8).
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    print("\n🚀 Validating deployment readiness...")
    
    # Check entry points
    entry_points = [
        ("main.py", "main.py exists"),
        ("run.py", "run.py exists"),
    ]
    
    for file_name, check_name in entry_points:
        file_path = project_root / file_name
        exists = file_path.exists()
        results[check_name.replace(" ", "_").lower()] = exists
        
        if exists:
            content = read_file_with_encoding(file_path)
            if content:
                # Check for proper __main__ guard
                has_main_guard = 'if __name__ == "__main__":' in content
                results[f'{file_name}_has_main_guard'] = has_main_guard
                
                # Check for shebang
                has_shebang = content.startswith('#!')
                results[f'{file_name}_has_shebang'] = has_shebang
    
    # Check for packaging files
    packaging_files = [
        "setup.py",
        "setup.cfg",
        "MANIFEST.in",
        "pyproject.toml",
    ]
    
    for file_name in packaging_files:
        file_path = project_root / file_name
        results[f'{file_name}_exists'] = file_path.exists()
    
    # Check for deployment configurations
    deployment_configs = [
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore",
        "requirements-prod.txt",
        "runtime.txt",
    ]
    
    for config_file in deployment_configs:
        file_path = project_root / config_file
        results[f'{config_file}_exists'] = file_path.exists()
    
    # Check for logging configuration
    has_logging = False
    python_files = list(project_root.glob("**/*.py"))
    for py_file in python_files[:20]:
        content = read_file_with_encoding(py_file)
        if content and ('import logging' in content or 'import loguru' in content):
            has_logging = True
            break
    
    results['has_logging'] = has_logging
    
    # Check for error handling
    has_error_handling = False
    for py_file in python_files[:20]:
        content = read_file_with_encoding(py_file)
        if content and ('try:' in content and 'except' in content):
            has_error_handling = True
            break
    
    results['has_error_handling'] = has_error_handling
    
    # Check for configuration management
    config_files = list((project_root / "config").glob("*.py")) if (project_root / "config").exists() else []
    results['has_config_files'] = len(config_files) > 0
    
    return results


def run_comprehensive_integration_test(project_root: Path) -> Dict[str, bool]:
    """
    Run comprehensive integration tests for Phase 5.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Dictionary with verification results
    """
    results = {}
    
    print("\n🔧 Running comprehensive integration tests...")
    
    try:
        # Add project root to Python path
        sys.path.insert(0, str(project_root))
        
        # Test 1: Basic imports
        print("  Testing basic imports...")
        imports_to_test = [
            ("models.expense_model", "Expense"),
            ("models.category_model", "Category"),
            ("services.database_service", "DatabaseService"),
            ("utils.validation", "validate_date"),
            ("utils.formatters", "format_currency"),
        ]
        
        all_imports_ok = True
        for module_path, class_name in imports_to_test:
            try:
                module = __import__(module_path, fromlist=[class_name])
                getattr(module, class_name)
                print(f"    ✓ {module_path}.{class_name}")
            except ImportError as e:
                print(f"    ✗ {module_path}.{class_name}: {e}")
                all_imports_ok = False
        
        results['all_imports_work'] = all_imports_ok
        
        # Test 2: Database connectivity
        print("  Testing database connectivity...")
        try:
            from services.database_service import DatabaseService
            
            db_service = DatabaseService()
            # Try a simple query
            expenses = db_service.get_expenses(limit=5)
            results['database_connectivity'] = expenses is not None
            print(f"    ✓ Database connectivity test passed")
        except Exception as e:
            print(f"    ✗ Database connectivity test failed: {e}")
            results['database_connectivity'] = False
        
        # Test 3: Export functionality
        print("  Testing export functionality...")
        try:
            from services.export_service import ExportService
            
            export_service = ExportService()
            results['export_service_available'] = True
            
            if hasattr(export_service, 'export_to_csv'):
                results['csv_export_available'] = True
                print(f"    ✓ CSV export available")
            
            if hasattr(export_service, 'export_to_excel'):
                results['excel_export_available'] = True
                print(f"    ✓ Excel export available")
                
        except ImportError as e:
            print(f"    ✗ Export service not available: {e}")
            results['export_service_available'] = False
        
        # Test 4: Visualization
        print("  Testing visualization...")
        try:
            from visualization.chart_service import ChartService
            
            chart_service = ChartService()
            results['chart_service_available'] = True
            print(f"    ✓ Chart service available")
        except ImportError as e:
            print(f"    ✗ Chart service not available: {e}")
            results['chart_service_available'] = False
        
        # Test 5: Run a simple test with pytest
        print("  Running test suite...")
        try:
            success, output = run_shell_command(["pytest", "-v", "--tb=short", "tests/test_database.py::test_database_connection"], project_root)
            results['pytest_execution'] = success
            if success:
                print(f"    ✓ Test execution successful")
            else:
                print(f"    ✗ Test execution failed")
        except Exception as e:
            print(f"    ✗ Test execution error: {e}")
            results['pytest_execution'] = False
    
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
    print_header("PHASE 5 VALIDATION SUMMARY")
    
    total_checks = 0
    passed_checks = 0
    critical_checks = 0
    critical_passed = 0
    
    # Define critical checks (must-pass for deployment)
    critical_categories = ['installation_configuration', 'deployment_readiness']
    critical_checks_list = [
        'requirements.txt_exists',
        'pyproject.toml_exists',
        'main.py_exists',
        'main.py_has_main_guard',
        'tests_dir_exists',
        'pytest_working',
    ]
    
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
            
            # Check if this is a critical check
            is_critical = category in critical_categories or check_name in critical_checks_list
            if is_critical:
                critical_checks += 1
                if check_result:
                    critical_passed += 1
            
            # Format check name for display
            display_name = check_name.replace('_', ' ').title()
            
            # Mark critical checks
            if is_critical:
                display_name = f"⚠️  {display_name}"
            
            print_check_result(display_name, check_result)
    
    # Calculate and display score
    if total_checks > 0:
        percentage = (passed_checks / total_checks) * 100
        critical_percentage = (critical_passed / critical_checks * 100) if critical_checks > 0 else 0
        
        print_header("OVERALL STATISTICS")
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {total_checks - passed_checks}")
        print(f"Success Rate: {percentage:.1f}%")
        
        print(f"\nCritical Checks: {critical_checks}")
        print(f"Critical Passed: {critical_passed}")
        print(f"Critical Success Rate: {critical_percentage:.1f}%")
        
        # Visual progress bar
        bar_length = 50
        filled_length = int(bar_length * percentage // 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        # Color code based on percentage
        if percentage >= 90 and critical_percentage >= 90:
            color = "\033[92m"  # Green
            status = "🎉 Excellent! Ready for deployment and portfolio."
        elif percentage >= 70 and critical_percentage >= 80:
            color = "\033[93m"  # Yellow
            status = "📊 Good. Minor improvements needed for production."
        elif percentage >= 50:
            color = "\033[93m"  # Yellow
            status = "⚡ Moderate. Needs significant improvements."
        else:
            color = "\033[91m"  # Red
            status = "🚧 Poor. Major work required."
        
        reset = "\033[0m"
        print(f"\n{color}[{bar}]{reset}")
        print(f"{color}{status}{reset}")
        
        # Recommendations
        print(f"\n📋 DEPLOYMENT CHECKLIST:")
        if critical_percentage < 100:
            print("1. Fix all critical issues (marked with ⚠️)")
        if percentage < 90:
            print("2. Address non-critical issues for better quality")
        print("3. Run comprehensive tests: pytest -v")
        print("4. Update documentation with deployment instructions")
        print("5. Create a release tag in Git")
        
        # Portfolio readiness assessment
        portfolio_ready = percentage >= 80 and critical_percentage >= 90
        
        print(f"\n🎯 PORTFOLIO READINESS:")
        if portfolio_ready:
            print("✅ This project is portfolio-ready!")
            print("   - Good code quality")
            print("   - Comprehensive documentation")
            print("   - Working test suite")
            print("   - Deployment-ready")
        else:
            print("❌ Not portfolio-ready yet.")
            missing = []
            if percentage < 80:
                missing.append(f"Success rate below 80% ({percentage:.1f}%)")
            if critical_percentage < 90:
                missing.append(f"Critical issues not resolved")
            
            print(f"   Missing: {', '.join(missing)}")
    
    else:
        print("No checks were performed.")


# ==================== MAIN FUNCTION ====================

def verify_phase5() -> None:
    """
    Main function to run all Phase 5 verifications.
    """
    print_header("DAILY EXPENSE TRACKER - PHASE 5 VALIDATION")
    
    # Get project root
    project_root = Path(__file__).parent
    print(f"📁 Project Location: {project_root.absolute()}")
    print(f"⚙️  Phase Focus: Code Quality, Documentation, Testing, Deployment")
    print(f"📅 Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print_header("RUNNING PHASE 5 VALIDATIONS")
    
    # Run all verifications
    results = {
        'project_organization': verify_project_organization(project_root),
        'pep8_compliance': verify_pep8_compliance(project_root),
        'code_standards': verify_code_standards(project_root),
        'documentation': verify_documentation(project_root),
        'test_suite': verify_test_suite(project_root),  # Fixed: changed from verify_testing_suite
        'installation_configuration': verify_installation_configuration(project_root),
        'platform_independence': verify_platform_independence(project_root),
        'deployment_readiness': verify_deployment_readiness(project_root),
        'integration_tests': run_comprehensive_integration_test(project_root),
    }
    
    # Display results
    calculate_and_display_score(results)


if __name__ == "__main__":
    try:
        verify_phase5()
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during validation: {e}")
        print("Please ensure the project structure is correct.")
        sys.exit(1)