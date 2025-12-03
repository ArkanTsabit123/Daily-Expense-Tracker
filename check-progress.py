# check-all-phases.py
"""
Comprehensive progress checker for ALL phases (1-5)
"""

from pathlib import Path
import os
import sys

def check_file_content(file_path, min_size=50):
    """Check if a file exists and has meaningful content"""
    path = Path(file_path)
    if not path.exists():
        return False, "❌ Missing"
    
    size = path.stat().st_size
    if size == 0:
        return False, "📄 Empty"
    elif size < min_size:
        return False, f"📄 Small ({size}b)"
    else:
        return True, f"✅ ({size}b)"

def check_phase1():
    """Check Phase 1: Foundation & Setup"""
    print("\n" + "=" * 60)
    print("PHASE 1: Foundation & Setup")
    print("=" * 60)
    
    phase1_files = [
        # Project structure
        ("__init__.py", 1, "Project root init"),
        ("main.py", 300, "Main application"),
        ("main.py", 50, "Application runner"),
        ("requirements.txt", 50, "Dependencies"),
        (".gitignore", 50, "Git ignore file"),
        
        # Config
        ("config/__init__.py", 1, "Config package"),
        ("config/database_config.py", 500, "Database config"),
        
        # Models
        ("models/__init__.py", 1, "Models package"),
        ("models/expense_model.py", 100, "Expense model"),
        ("models/category_model.py", 50, "Category model"),
        
        # Utils
        ("utils/__init__.py", 1, "Utils package"),
        ("utils/validation.py", 100, "Validation utils"),
        
        # Data directory
        ("data/.gitkeep", 1, "Data directory"),
    ]
    
    completed = 0
    for file_path, min_size, description in phase1_files:
        has_content, message = check_file_content(file_path, min_size)
        status = "✅" if has_content else "❌"
        print(f"{status} {description:25} {message}")
        if has_content:
            completed += 1
    
    percentage = (completed / len(phase1_files)) * 100
    print(f"\n📊 Phase 1: {completed}/{len(phase1_files)} ({percentage:.0f}%)")
    return completed, len(phase1_files)

def check_phase2():
    """Check Phase 2: Core & Testing"""
    print("\n" + "=" * 60)
    print("PHASE 2: Core & Testing")
    print("=" * 60)
    
    phase2_files = [
        # Services
        ("services/__init__.py", 1, "Services package"),
        ("services/database_service.py", 500, "Database service"),
        ("services/expense_service.py", 300, "Expense service"),
        
        # More utils
        ("utils/date_utils.py", 50, "Date utilities"),
        ("utils/exceptions.py", 50, "Custom exceptions"),
        
        # Tests
        ("tests/__init__.py", 1, "Tests package"),
        ("tests/test_database.py", 100, "Database tests"),
        ("tests/test_expenses.py", 100, "Expense tests"),
        
        # Test data generation
        ("generate/sample_data.py", 50, "Sample data generator"),
    ]
    
    completed = 0
    for file_path, min_size, description in phase2_files:
        has_content, message = check_file_content(file_path, min_size)
        status = "✅" if has_content else "❌"
        print(f"{status} {description:25} {message}")
        if has_content:
            completed += 1
    
    percentage = (completed / len(phase2_files)) * 100
    print(f"\n📊 Phase 2: {completed}/{len(phase2_files)} ({percentage:.0f}%)")
    return completed, len(phase2_files)

def check_phase3():
    """Check Phase 3: Visualization & UI"""
    print("\n" + "=" * 60)
    print("PHASE 3: Visualization & UI")
    print("=" * 60)
    
    phase3_files = [
        # Visualization
        ("visualization/__init__.py", 1, "Visualization package"),
        ("visualization/chart_service.py", 300, "Chart service"),
        
        # More utils
        ("utils/formatters.py", 100, "Formatting utilities"),
        
        # UI enhancements (check main.py for features)
        ("main.py", 800, "Main app with UI menus"),
        
        # Charts directory
        ("charts/.gitkeep", 1, "Charts directory"),
    ]
    
    completed = 0
    for file_path, min_size, description in phase3_files:
        has_content, message = check_file_content(file_path, min_size)
        status = "✅" if has_content else "❌"
        print(f"{status} {description:25} {message}")
        if has_content:
            completed += 1
    
    # Check for specific features in main.py
    main_features = []
    if Path("main.py").exists():
        with open("main.py", 'r') as f:
            content = f.read()
            main_features = [
                ("Has chart menu", 'generate_chart_menu' in content),
                ("Has export menu", 'export_data_menu' in content),
                ("Has monthly analysis", 'monthly_summary' in content),
            ]
    
    print("\n🔍 Main Application Features:")
    for feature, exists in main_features:
        status = "✅" if exists else "❌"
        print(f"  {status} {feature}")
        if exists:
            completed += 0.5  # Half points for features
    
    total_items = len(phase3_files) + len(main_features) * 0.5
    percentage = (completed / total_items) * 100 if total_items > 0 else 0
    print(f"\n📊 Phase 3: {completed:.1f}/{total_items:.1f} ({percentage:.0f}%)")
    return completed, total_items

def check_phase4():
    """Check Phase 4: Export & Quality"""
    print("\n" + "=" * 60)
    print("PHASE 4: Export & Quality")
    print("=" * 60)
    
    phase4_files = [
        # Export functionality
        ("services/export_service.py", 200, "Export service"),
        ("services/analysis_service.py", 50, "Analysis service"),
        
        # Export directories
        ("exports/.gitkeep", 1, "Exports directory"),
        
        # Additional tests
        ("tests/test_export.py", 100, "Export tests"),
        ("tests/conftest.py", 50, "Test config"),
        
        # Code quality tools
        (".flake8", 10, "Flake8 config"),
        ("pyproject.toml", 100, "Project config"),
        ("setup.cfg", 50, "Setup config"),
        
        # Additional utils
        ("utils/__init__.py", 1, "Utils package complete"),
    ]
    
    completed = 0
    for file_path, min_size, description in phase4_files:
        has_content, message = check_file_content(file_path, min_size)
        status = "✅" if has_content else "❌"
        print(f"{status} {description:25} {message}")
        if has_content:
            completed += 1
    
    # Check for integration tests
    integration_tests = False
    if Path("tests/test_integration.py").exists():
        with open("tests/test_integration.py", 'r') as f:
            if 'def test_' in f.read():
                integration_tests = True
                print("✅ Integration tests       ✅ Present")
                completed += 1
            else:
                print("❌ Integration tests       ❌ No tests")
    else:
        print("❌ Integration tests       ❌ Missing")
    
    percentage = (completed / len(phase4_files) + 1) * 100  # +1 for integration tests
    print(f"\n📊 Phase 4: {completed}/{len(phase4_files) + 1} ({percentage:.0f}%)")
    return completed, len(phase4_files) + 1

def check_phase5():
    """Check Phase 5: Polish & Deployment"""
    print("\n" + "=" * 60)
    print("PHASE 5: Polish & Deployment")
    print("=" * 60)
    
    phase5_files = [
        # Documentation
        ("README.md", 500, "Main README"),
        ("docs/README.md", 100, "Docs README"),
        ("docs/usage.md", 100, "Usage documentation"),
        
        # Deployment files
        ("setup.py", 100, "Setup script"),
        ("MANIFEST.in", 10, "Package manifest"),
        
        # Additional polish
        ("CONTRIBUTING.md", 50, "Contributing guidelines"),
        ("LICENSE", 500, "License file"),
    ]
    
    completed = 0
    for file_path, min_size, description in phase5_files:
        has_content, message = check_file_content(file_path, min_size)
        status = "✅" if has_content else "❌"
        print(f"{status} {description:25} {message}")
        if has_content:
            completed += 1
    
    # Check for additional polish features
    polish_features = []
    
    # Check if README has installation instructions
    if Path("README.md").exists():
        with open("README.md", 'r') as f:
            content = f.read().lower()
            polish_features = [
                ("README has installation", 'install' in content),
                ("README has usage examples", 'usage' in content or 'example' in content),
                ("README has features list", 'feature' in content or '## feature' in content),
            ]
    
    print("\n🔍 Documentation Quality:")
    for feature, exists in polish_features:
        status = "✅" if exists else "❌"
        print(f"  {status} {feature}")
        if exists:
            completed += 0.33  # One third point per feature
    
    total_items = len(phase5_files) + len(polish_features) * 0.33
    percentage = (completed / total_items) * 100 if total_items > 0 else 0
    print(f"\n📊 Phase 5: {completed:.1f}/{total_items:.1f} ({percentage:.0f}%)")
    return completed, total_items

def check_functionality():
    """Test if key functionality works"""
    print("\n" + "=" * 60)
    print("FUNCTIONALITY TESTS")
    print("=" * 60)
    
    tests = []
    
    try:
        # Test 1: Can import database config
        from config.database_config import DatabaseConfig
        db = DatabaseConfig()
        tests.append(("Database config imports", True))
    except Exception as e:
        tests.append(("Database config imports", False))
    
    try:
        # Test 2: Can import export service
        from services.export_service import ExportService
        tests.append(("Export service imports", True))
    except Exception as e:
        tests.append(("Export service imports", False))
    
    try:
        # Test 3: Can import chart service
        from visualization.chart_service import ChartService
        tests.append(("Chart service imports", True))
    except Exception as e:
        tests.append(("Chart service imports", False))
    
    try:
        # Test 4: Can import expense service
        from services.expense_service import ExpenseService
        tests.append(("Expense service imports", True))
    except Exception as e:
        tests.append(("Expense service imports", False))
    
    # Display results
    for test, passed in tests:
        status = "✅" if passed else "❌"
        print(f"{status} {test}")
    
    passed = sum(1 for _, p in tests if p)
    percentage = (passed / len(tests)) * 100
    print(f"\n📊 Imports working: {passed}/{len(tests)} ({percentage:.0f}%)")
    
    return passed, len(tests)

def main():
    print("DAILY EXPENSE TRACKER - COMPREHENSIVE PROGRESS CHECK")
    print("=" * 60)
    print("Checking ALL phases (1-5)...\n")
    
    # Check each phase
    phase1_completed, phase1_total = check_phase1()
    phase2_completed, phase2_total = check_phase2()
    phase3_completed, phase3_total = check_phase3()
    phase4_completed, phase4_total = check_phase4()
    phase5_completed, phase5_total = check_phase5()
    
    # Check functionality
    func_passed, func_total = check_functionality()
    
    # Summary
    print("\n" + "=" * 60)
    print("OVERALL PROJECT SUMMARY")
    print("=" * 60)
    
    phases = [
        ("Phase 1: Foundation", phase1_completed, phase1_total),
        ("Phase 2: Core & Testing", phase2_completed, phase2_total),
        ("Phase 3: Visualization", phase3_completed, phase3_total),
        ("Phase 4: Export & Quality", phase4_completed, phase4_total),
        ("Phase 5: Polish & Deployment", phase5_completed, phase5_total),
    ]
    
    total_completed = 0
    total_items = 0
    
    print("\n📈 PHASE PROGRESS:")
    for name, completed, total in phases:
        percentage = (completed / total) * 100 if total > 0 else 0
        bar_length = 30
        filled = int(percentage / 100 * bar_length)
        bar = f"{'█' * filled}{'░' * (bar_length - filled)}"
        
        print(f"{name:25} [{bar}] {percentage:5.1f}% ({completed:.1f}/{total:.1f})")
        
        total_completed += completed
        total_items += total
    
    # Overall percentage
    overall_percentage = (total_completed / total_items) * 100 if total_items > 0 else 0
    
    print("\n" + "=" * 60)
    print("📊 OVERALL COMPLETION:")
    print(f"   Total: {total_completed:.1f}/{total_items:.1f} items")
    print(f"   Percentage: {overall_percentage:.1f}%")
    
    # Functionality status
    func_percentage = (func_passed / func_total) * 100
    print(f"\n🔧 FUNCTIONALITY: {func_passed}/{func_total} imports working ({func_percentage:.0f}%)")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDATIONS:")
    
    if overall_percentage < 40:
        print("1. Focus on completing Phases 1-3 first")
        print("2. Ensure core functionality works")
        print("3. Run: python check-progress.py for detailed Phase 4 check")
    elif overall_percentage < 70:
        print("1. Complete Phase 4 (Export & Quality)")
        print("2. Run tests: pytest tests/ -v")
        print("3. Verify all imports work correctly")
    elif overall_percentage < 90:
        print("1. Focus on Phase 5 (Polish & Deployment)")
        print("2. Improve documentation")
        print("3. Add final polish and testing")
    else:
        print("1. You're almost done! Final polish needed.")
        print("2. Update README with screenshots and examples")
        print("3. Run final comprehensive tests")
        print("4. Prepare for deployment/portfolio showcase")
    
    print(f"\n2. Current overall status: {overall_percentage:.1f}% complete")
    print("3. Next focus: {'Phase 5' if overall_percentage > 70 else 'Phase 4'}")
    print("4. Run: git status to see all modified files")

if __name__ == "__main__":
    # Add project root to path for imports
    sys.path.insert(0, str(Path(__file__).parent))
    main()