"""
PHASE 5 VERIFICATION SCRIPT - FIXED VERSION
Validates all Phase 5 requirements for the Daily Expense Tracker project.
"""

import os
import platform
import re
import subprocess
import sys
import traceback
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


def safe_import_check(project_root: Path, module_path: str) -> Tuple[bool, str]:
    """
    Safely check if a module can be imported without side effects.
    
    Args:
        project_root: Project root directory
        module_path: Module path to check
        
    Returns:
        Tuple of (can_import, error_message)
    """
    try:
        # Check if module file exists first
        file_path = project_root / module_path.replace('.', '/') + '.py'
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        
        # Try to import using importlib (safer)
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            module_path.split('.')[-1],
            str(file_path)
        )
        
        if spec is None:
            return False, "Could not create module spec"
        
        # Just check if we can create the spec, don't actually execute
        return True, "Module can be imported"
        
    except Exception as e:
        return False, f"Import check failed: {e}"


# ==================== VERIFICATION MODULES ====================

def verify_project_organization(project_root: Path) -> Dict[str, Any]:
    """
    Verify project organization completeness (5.1).
    FIXED: Check actual required files, not assumed ones
    """
    results = {}
    
    print("\n📁 Validating project organization...")
    
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
    
    # Optional but recommended files
    optional_files = [
        "models/category_model.py",
        "services/export_service.py",
        "services/analysis_service.py",
        "utils/formatters.py",
        "utils/date_utils.py",
        "utils/exceptions.py",
        "visualization/chart_service.py",
        "tests/test_database.py",
        "tests/test_expenses.py",
        "tests/test_export.py",
        "tests/test_integration.py",
        "tests/conftest.py",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        ".flake8",
        ".coveragerc",
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
    
    # Check optional files
    found_optional = 0
    for file_path in optional_files:
        full_path = project_root / file_path
        if full_path.exists():
            found_optional += 1
            results[f'optional_{file_path.replace("/", "_")}_exists'] = True
        else:
            results[f'optional_{file_path.replace("/", "_")}_exists'] = False
    
    results['optional_files_found'] = found_optional
    results['optional_file_count'] = len(optional_files)
    
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
    Verify PEP 8 compliance (5.2).
    FIXED: Safer, no actual flake8 execution required
    """
    results = {}
    
    print("\n📐 Validating code style...")
    
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
            results['has_isort_config'] = '[tool.isort]' in content or 'tool.isort' in content
    
    # Simple code style checks (without running flake8)
    python_files = list(project_root.glob("**/*.py"))
    python_files = [f for f in python_files if not any(
        exclude in str(f) for exclude in ['__pycache__', '.venv', 'venv', '.env', 'tests/']
    )]
    
    # Check first few files for obvious style issues
    style_issues = []
    files_checked = 0
    
    for py_file in python_files[:10]:  # Check first 10 non-test files
        content = read_file_with_encoding(py_file)
        if content:
            files_checked += 1
            
            # Check for very long lines (>120 chars)
            lines = content.split('\n')
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
            if long_lines:
                style_issues.append(f"{py_file.name}: Long lines at {long_lines[:3]}")
            
            # Check for trailing whitespace
            trailing_ws = [i+1 for i, line in enumerate(lines) if line.rstrip() != line]
            if trailing_ws:
                style_issues.append(f"{py_file.name}: Trailing whitespace at {trailing_ws[:3]}")
    
    results['files_checked_for_style'] = files_checked
    results['style_issues_found'] = len(style_issues)
    results['has_style_issues'] = len(style_issues) > 0
    
    # Check if tools are mentioned in requirements
    req_path = project_root / "requirements.txt"
    if req_path.exists():
        content = read_file_with_encoding(req_path)
        if content:
            content_lower = content.lower()
            results['mentions_black'] = 'black' in content_lower
            results['mentions_flake8'] = 'flake8' in content_lower
            results['mentions_autopep8'] = 'autopep8' in content_lower
    
    return results


def verify_code_standards(project_root: Path) -> Dict[str, Any]:
    """
    Verify code standards and optimization (5.3).
    FIXED: Realistic checks, no over-optimization
    """
    results = {}
    
    print("\n🔍 Validating code standards...")
    
    # Find Python files
    python_files = list(project_root.glob("**/*.py"))
    python_files = [f for f in python_files if not any(
        exclude in str(f) for exclude in ['__pycache__', '.venv', 'venv', '.env']
    )]
    
    # Skip test files for some checks
    non_test_files = [f for f in python_files if 'test' not in f.name.lower()]
    
    results['total_python_files'] = len(python_files)
    results['non_test_files'] = len(non_test_files)
    
    # Check for TODO/FIXME comments
    todo_count = 0
    for py_file in non_test_files[:15]:  # Check first 15 non-test files
        content = read_file_with_encoding(py_file)
        if content:
            if 'TODO' in content or 'FIXME' in content or 'XXX' in content:
                todo_count += 1
    
    results['todo_fixme_count'] = todo_count
    results['has_todos'] = todo_count > 0
    
    # Check for print statements in non-test files
    print_count = 0
    for py_file in non_test_files[:15]:
        content = read_file_with_encoding(py_file)
        if content and 'print(' in content:
            print_count += 1
    
    results['print_statement_count'] = print_count
    results['has_prints_in_code'] = print_count > 0
    
    # Check for basic error handling patterns
    error_handling_files = 0
    for py_file in non_test_files[:15]:
        content = read_file_with_encoding(py_file)
        if content:
            if 'try:' in content and 'except' in content:
                error_handling_files += 1
    
    results['files_with_error_handling'] = error_handling_files
    results['error_handling_coverage'] = error_handling_files / len(non_test_files[:15]) if non_test_files else 0
    
    # Check for type hints
    type_hint_files = 0
    for py_file in non_test_files[:15]:
        content = read_file_with_encoding(py_file)
        if content:
            if '->' in content or ': List[' in content or ': Dict[' in content:
                type_hint_files += 1
    
    results['files_with_type_hints'] = type_hint_files
    
    # Check for proper __init__.py files in packages
    init_files = list(project_root.glob("**/__init__.py"))
    results['init_file_count'] = len(init_files)
    
    # Packages that should have __init__.py
    packages = ['config', 'models', 'services', 'utils', 'visualization', 'tests']
    missing_init = []
    for package in packages:
        init_path = project_root / package / "__init__.py"
        if not init_path.exists():
            missing_init.append(package)
    
    results['all_packages_have_init'] = len(missing_init) == 0
    if missing_init:
        results['packages_missing_init'] = ", ".join(missing_init)
    
    return results


def verify_documentation(project_root: Path) -> Dict[str, Any]:
    """
    Verify documentation comprehensiveness (5.4).
    FIXED: Check actual documentation structure
    """
    results = {}
    
    print("\n📚 Validating documentation...")
    
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
    
    # Check for docs directory
    docs_dir = project_root / "docs"
    results['docs_dir_exists'] = docs_dir.exists()
    
    if results['docs_dir_exists']:
        doc_files = list(docs_dir.glob("*.md"))
        results['doc_file_count'] = len(doc_files)
        
        # Look for specific documentation
        found_docs = []
        for doc_file in doc_files:
            found_docs.append(doc_file.name)
        
        results['found_doc_files'] = ", ".join(found_docs[:5]) if found_docs else "None"
        
        # Check for API documentation
        has_api_docs = any('api' in f.name.lower() or 'reference' in f.name.lower() for f in doc_files)
        results['has_api_docs'] = has_api_docs
    else:
        results['doc_file_count'] = 0
    
    # Check for inline documentation in code
    python_files = list(project_root.glob("**/*.py"))
    python_files = [f for f in python_files if not any(
        exclude in str(f) for exclude in ['__pycache__', '.venv', 'venv', '.env']
    )]
    
    files_with_docstrings = 0
    for py_file in python_files[:20]:  # Check first 20 files
        content = read_file_with_encoding(py_file)
        if content:
            # Check for module docstring (triple quotes at beginning)
            lines = content.split('\n')
            found_docstring = False
            
            for i, line in enumerate(lines[:10]):  # Check first 10 lines
                stripped = line.strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    found_docstring = True
                    break
                if stripped and not stripped.startswith('#') and not stripped.startswith('import'):
                    break  # Reached code without docstring
            
            if found_docstring:
                files_with_docstrings += 1
    
    results['files_with_docstrings'] = files_with_docstrings
    results['total_files_checked'] = min(20, len(python_files))
    
    if python_files:
        results['docstring_percentage'] = (files_with_docstrings / min(20, len(python_files))) * 100
    else:
        results['docstring_percentage'] = 0
    
    return results


def verify_test_suite(project_root: Path) -> Dict[str, Any]:
    """
    Verify testing suite (5.5).
    FIXED: Realistic test checks
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
        
        # Check for coverage configuration
        coverage_configs = [
            project_root / ".coveragerc",
            project_root / "pyproject.toml",
            project_root / "setup.cfg",
        ]
        
        has_coverage_config = False
        for config_file in coverage_configs:
            if config_file.exists():
                content = read_file_with_encoding(config_file)
                if content and 'coverage' in content.lower():
                    has_coverage_config = True
                    break
        
        results['has_coverage_config'] = has_coverage_config
        
        # Try to run a simple test if pytest is available
        try:
            success, _ = run_shell_command(["pytest", "--version"])
            if success and test_files:
                # Run a simple collection test
                success, output = run_shell_command(["pytest", "--collect-only", "-q"], project_root)
                results['pytest_can_collect_tests'] = success
                if success and output:
                    # Count collected tests
                    test_items = [line for line in output.split('\n') if line.strip()]
                    results['collected_test_count'] = len(test_items)
        except:
            results['pytest_can_collect_tests'] = False
    else:
        results['tests_dir_exists'] = False
    
    return results


def verify_installation_configuration(project_root: Path) -> Dict[str, Any]:
    """
    Verify installation configuration (5.6).
    FIXED: Realistic checks
    """
    results = {}
    
    print("\n📦 Validating installation configuration...")
    
    # Core installation files
    core_files = [
        ("requirements.txt", "Dependencies"),
        ("pyproject.toml", "Build configuration"),
        ("setup.py", "Setup script"),
        ("setup.cfg", "Package configuration"),
    ]
    
    for file_name, description in core_files:
        file_path = project_root / file_name
        exists = file_path.exists()
        results[f'{file_name}_exists'] = exists
        
        if exists:
            content = read_file_with_encoding(file_path)
            if content:
                results[f'{file_name}_has_content'] = len(content.strip()) > 0
                
                if file_name == 'requirements.txt':
                    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                    results['dependency_count'] = len(lines)
                    
                    # Check for essential dependencies
                    essential_deps = ['pandas', 'matplotlib', 'openpyxl', 'python-dateutil']
                    for dep in essential_deps:
                        results[f'requires_{dep}'] = any(dep in line.lower() for line in lines)
                
                elif file_name == 'setup.py':
                    # Check for basic setup.py structure
                    has_setup_call = 'setup(' in content
                    results['setup_has_setup_call'] = has_setup_call
            else:
                results[f'{file_name}_has_content'] = False
    
    # Check for virtual environment indication
    venv_dirs = ['.venv', 'venv', 'env']
    has_venv_dir = any((project_root / dir_name).exists() for dir_name in venv_dirs)
    results['has_venv_directory'] = has_venv_dir
    
    # Check .gitignore
    gitignore_path = project_root / ".gitignore"
    results['gitignore_exists'] = gitignore_path.exists()
    
    if results['gitignore_exists']:
        content = read_file_with_encoding(gitignore_path)
        if content:
            # Essential ignore patterns
            essential_ignores = ['__pycache__', '*.pyc', '.env', 'venv/', '.venv/', '*.db', '*.log']
            missing_ignores = []
            
            for pattern in essential_ignores:
                if pattern not in content:
                    missing_ignores.append(pattern)
            
            results['gitignore_complete'] = len(missing_ignores) == 0
            if missing_ignores:
                results['missing_ignores'] = ", ".join(missing_ignores)
    
    # Check for entry points
    entry_points = ['main.py', 'run.py']
    for ep in entry_points:
        ep_path = project_root / ep
        if ep_path.exists():
            content = read_file_with_encoding(ep_path)
            if content:
                results[f'{ep}_has_main_guard'] = 'if __name__ == "__main__":' in content
    
    return results


def verify_platform_independence(project_root: Path) -> Dict[str, Any]:
    """
    Verify cross-platform independence (5.7).
    FIXED: Safe checks
    """
    results = {}
    
    print("\n💻 Validating platform independence...")
    
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
    
    # Check for proper path handling
    uses_os_path = False
    uses_pathlib = False
    
    for py_file in python_files[:20]:
        content = read_file_with_encoding(py_file)
        if content:
            if 'import os.path' in content or 'from os import path' in content:
                uses_os_path = True
            if 'import pathlib' in content or 'from pathlib import' in content:
                uses_pathlib = True
    
    results['uses_os_path'] = uses_os_path
    results['uses_pathlib'] = uses_pathlib
    results['uses_proper_path_handling'] = uses_os_path or uses_pathlib
    
    # Check for hardcoded paths
    hardcoded_paths = []
    for py_file in python_files[:20]:
        content = read_file_with_encoding(py_file)
        if content:
            # Look for absolute paths
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'C:\\' in line or '/home/' in line or '/Users/' in line:
                    hardcoded_paths.append(f"{py_file.name}:{i+1}")
    
    results['has_hardcoded_paths'] = len(hardcoded_paths) > 0
    results['hardcoded_path_count'] = len(hardcoded_paths)
    
    return results


def verify_deployment_readiness(project_root: Path) -> Dict[str, Any]:
    """
    Verify deployment preparation (5.8).
    FIXED: Realistic deployment checks
    """
    results = {}
    
    print("\n🚀 Validating deployment readiness...")
    
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
    
    # Check for packaging files
    packaging_files = ['setup.py', 'setup.cfg', 'pyproject.toml', 'MANIFEST.in']
    packaging_files_found = 0
    
    for pkg_file in packaging_files:
        if (project_root / pkg_file).exists():
            packaging_files_found += 1
            results[f'has_{pkg_file}'] = True
        else:
            results[f'has_{pkg_file}'] = False
    
    results['packaging_files_found'] = packaging_files_found
    results['has_packaging_files'] = packaging_files_found > 0
    
    # Check for logging configuration
    config_dir = project_root / "config"
    if config_dir.exists():
        config_files = list(config_dir.glob("*.py"))
        has_logging_config = any('log' in f.name.lower() for f in config_files)
        results['has_logging_config'] = has_logging_config
    
    # Check for error handling in main.py
    main_path = project_root / "main.py"
    if main_path.exists():
        content = read_file_with_encoding(main_path)
        if content:
            results['main_has_error_handling'] = 'try:' in content and 'except' in content
            results['main_has_logging'] = 'logging' in content or 'import log' in content
    
    # Check for environment configuration
    env_files = ['.env', '.env.example', 'config/.env']
    env_files_found = 0
    for env_file in env_files:
        if (project_root / env_file).exists():
            env_files_found += 1
    
    results['env_files_found'] = env_files_found
    results['has_env_config'] = env_files_found > 0
    
    # Check for database backup/restore
    services_dir = project_root / "services"
    if services_dir.exists():
        service_files = list(services_dir.glob("*.py"))
        has_backup = any('backup' in f.name.lower() or 'export' in f.name.lower() for f in service_files)
        results['has_backup_feature'] = has_backup
    
    return results


def run_safe_integration_checks(project_root: Path) -> Dict[str, Any]:
    """
    Run SAFE integration checks for Phase 5.
    No dangerous imports or executions.
    """
    results = {}
    
    print("\n🔧 Running safe integration checks...")
    
    checks_passed = 0
    checks_run = 0
    
    # Check 1: Project structure
    print("  Checking project structure...")
    required_paths = [
        ("main.py", "Main application"),
        ("requirements.txt", "Dependencies"),
        (".gitignore", "Git ignore rules"),
        ("config/database_config.py", "Database config"),
        ("data/", "Data directory"),
        ("exports/", "Exports directory"),
    ]
    
    for path_name, description in required_paths:
        checks_run += 1
        if '/' in path_name and path_name.endswith('/'):
            # Directory
            exists = (project_root / path_name.rstrip('/')).exists()
        else:
            # File
            exists = (project_root / path_name).exists()
        
        if exists:
            checks_passed += 1
            print(f"    ✓ {description}")
        else:
            print(f"    ⚠ {description} not found")
    
    # Check 2: Can run basic Python
    print("  Checking Python environment...")
    checks_run += 1
    try:
        # Just check Python version, don't run any code
        import sys
        version = sys.version_info
        results['python_version'] = f"{version.major}.{version.minor}.{version.micro}"
        checks_passed += 1
        print(f"    ✓ Python {results['python_version']}")
    except:
        print("    ⚠ Could not check Python version")
    
    # Check 3: Dependencies
    print("  Checking dependencies...")
    req_path = project_root / "requirements.txt"
    if req_path.exists():
        checks_run += 1
        content = read_file_with_encoding(req_path)
        if content and len([l for l in content.split('\n') if l.strip()]) > 0:
            checks_passed += 1
            print("    ✓ requirements.txt has content")
        else:
            print("    ⚠ requirements.txt is empty")
    else:
        checks_run += 1
        print("    ⚠ requirements.txt not found")
    
    # Check 4: Tests
    print("  Checking tests...")
    tests_dir = project_root / "tests"
    if tests_dir.exists():
        checks_run += 1
        test_files = list(tests_dir.glob("test_*.py"))
        if len(test_files) > 0:
            checks_passed += 1
            print(f"    ✓ Found {len(test_files)} test files")
        else:
            print("    ⚠ No test files found")
    else:
        checks_run += 1
        print("    ⚠ tests directory not found")
    
    # Check 5: Documentation
    print("  Checking documentation...")
    checks_run += 1
    readme_path = project_root / "README.md"
    if readme_path.exists():
        content = read_file_with_encoding(readme_path)
        if content and len(content.strip()) > 100:
            checks_passed += 1
            print("    ✓ README.md has substantial content")
        else:
            print("    ⚠ README.md is minimal")
    else:
        print("    ⚠ README.md not found")
    
    # Calculate success rate
    if checks_run > 0:
        results['integration_success_rate'] = (checks_passed / checks_run) * 100
    results['integration_checks_passed'] = checks_passed
    results['integration_checks_run'] = checks_run
    
    print(f"\n  📊 Integration checks: {checks_passed}/{checks_run} passed")
    
    return results


def calculate_and_display_score(all_results: Dict[str, Dict[str, Any]]) -> None:
    """
    Calculate and display overall verification score.
    """
    print_header("PHASE 5 VERIFICATION SUMMARY")
    
    total_checks = 0
    passed_checks = 0
    
    # Category display names
    category_names = {
        'project_organization': "Project Organization",
        'pep8_compliance': "Code Style & PEP 8",
        'code_standards': "Code Standards",
        'documentation': "Documentation",
        'test_suite': "Testing Suite",
        'installation_configuration': "Installation Configuration",
        'platform_independence': "Platform Independence",
        'deployment_readiness': "Deployment Readiness",
        'integration': "Integration Checks",
    }
    
    for category, category_results in all_results.items():
        display_name = category_names.get(category, category.replace('_', ' ').title())
        print(f"\n{display_name}:")
        print("-" * 50)
        
        category_passed = 0
        category_total = 0
        
        for check_name, check_result in category_results.items():
            # Skip non-boolean results and debug info
            skip_patterns = ['error', 'missing', 'count', 'percentage', 'rate', 
                           'version', 'found', 'list', 'examples', 'issues']
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
            status = "✅ Excellent! Project is portfolio-ready."
        elif percentage >= 60:
            color = "\033[93m"  # Yellow
            status = "📊 Good. Minor improvements needed."
        elif percentage >= 40:
            color = "\033[93m"  # Yellow
            status = "⚡ Moderate. Several areas need work."
        else:
            color = "\033[91m"  # Red
            status = "🚧 Needs significant work before deployment."
        
        reset = "\033[0m"
        print(f"\n{color}[{bar}]{reset}")
        print(f"{color}{status}{reset}")
        
        # Recommendations based on score
        print(f"\n📋 RECOMMENDATIONS:")
        
        if percentage >= 80:
            print("1. Create a final release tag")
            print("2. Update CHANGELOG.md with final version")
            print("3. Create deployment package (PyInstaller/wheel)")
            print("4. Add to your portfolio with screenshots")
        elif percentage >= 60:
            print("1. Fix critical issues (marked with ❌)")
            print("2. Improve documentation with examples")
            print("3. Add more test coverage")
            print("4. Run phase5-fixer.py for automated fixes")
        else:
            print("1. Address all failed checks above")
            print("2. Run phase5-fixer.py")
            print("3. Review project structure against blueprint")
            print("4. Ensure all Phase 1-4 requirements are met")
        
        print(f"\n🎯 PROJECT STATUS:")
        if percentage >= 80:
            print("✅ READY FOR DEPLOYMENT & PORTFOLIO")
        elif percentage >= 60:
            print("⚠️  NEARLY READY - Minor fixes needed")
        else:
            print("❌ NOT READY - Significant work required")
    
    else:
        print("No checks were performed.")


# ==================== MAIN FUNCTION ====================

def verify_phase5() -> None:
    """
    Main function to run all Phase 5 verifications.
    """
    print_header("DAILY EXPENSE TRACKER - PHASE 5 VERIFICATION")
    print("FINAL POLISH & DEPLOYMENT READINESS CHECK")
    
    # Get project root
    project_root = Path(__file__).parent
    print(f"📁 Project Location: {project_root.absolute()}")
    print(f"⚙️  Phase Focus: Code Quality, Documentation, Testing, Deployment")
    print(f"📅 Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print_header("RUNNING PHASE 5 VERIFICATIONS")
    print("This may take a moment...")
    
    # Run all verifications
    results = {
        'project_organization': verify_project_organization(project_root),
        'pep8_compliance': verify_pep8_compliance(project_root),
        'code_standards': verify_code_standards(project_root),
        'documentation': verify_documentation(project_root),
        'test_suite': verify_test_suite(project_root),
        'installation_configuration': verify_installation_configuration(project_root),
        'platform_independence': verify_platform_independence(project_root),
        'deployment_readiness': verify_deployment_readiness(project_root),
        'integration': run_safe_integration_checks(project_root),
    }
    
    # Display results
    calculate_and_display_score(results)


if __name__ == "__main__":
    try:
        verify_phase5()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {e}")
        print("Please ensure the project structure is correct.")
        traceback.print_exc()
        sys.exit(1)