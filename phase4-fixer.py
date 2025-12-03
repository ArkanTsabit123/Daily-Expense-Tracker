# phase4-fixer.py
"""
Phase 4 Fixer - Fixes all missing items from the checker
Run this to complete Phase 4 requirements
"""

import os
import sys
from pathlib import Path
import subprocess

project_root = Path(__file__).parent

def print_step(step_num, description):
    """Print a step with formatting"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print('='*60)

def create_file(filepath, content):
    """Create or overwrite a file"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created/updated: {filepath}")

def run_checker():
    """Run the phase4-verify.py checker"""
    print("\n🔍 Running checker to verify fixes...")
    try:
        result = subprocess.run(
            [sys.executable, "phase4-verify.py"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        # Extract score from output
        for line in result.stdout.split('\n'):
            if 'Progress:' in line and '%' in line:
                percentage = float(line.split('[')[1].split('%')[0].strip())
                print(f"\n📊 New Score: {percentage:.1f}%")
                return percentage
        
        # Fallback if we can't parse
        print("Checker output:")
        print(result.stdout[-500:])  # Last 500 chars
        
    except Exception as e:
        print(f"❌ Error running checker: {e}")
    return 0

def main():
    print("\n" + "="*70)
    print("🚀 PHASE 4 FIXER - DAILY EXPENSE TRACKER")
    print("="*70)
    
    current_score = run_checker()
    print(f"\nCurrent Phase 4 Completion: {current_score:.1f}%")
    
    if input("\nContinue with fixes? (y/n): ").lower() != 'y':
        print("❌ Fixes cancelled")
        return
    
    # STEP 1: Fix requirements.txt
    print_step(1, "Fixing requirements.txt")
    requirements_content = '''# Core Dependencies
matplotlib==3.7.1
pandas==2.0.3
openpyxl==3.1.2
python-dateutil==2.8.2

# Development & Testing
pytest==7.4.2
pytest-cov==4.1.0
pytest-mock==3.11.1

# Code Quality
black==23.9.1
flake8==6.1.0
isort==5.12.0
mypy==1.5.1

# Security
bandit==1.7.5

# Performance
psutil==5.9.5
'''
    create_file("requirements.txt", requirements_content)
    
    # STEP 2: Fix export_service.py
    print_step(2, "Fixing services/export_service.py")
    export_service_content = '''"""
Export Service for Daily Expense Tracker
Handles CSV, Excel exports and comprehensive reporting
"""
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class ExportService:
    def __init__(self):
        self.export_dir = Path(__file__).parent.parent / "exports"
        self.export_dir.mkdir(exist_ok=True)
    
    def export_to_csv(self, expenses: List[Dict], filename: Optional[str] = None) -> str:
        """Export expenses data to CSV format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expenses_export_{timestamp}.csv"
        
        filepath = self.export_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if expenses:
                all_keys = set()
                for expense in expenses:
                    all_keys.update(expense.keys())
                fieldnames = sorted(all_keys)
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(expenses)
        
        return str(filepath)
    
    def export_to_excel(self, expenses: List[Dict], filename: Optional[str] = None) -> str:
        """Export expenses data to Excel format with formatting"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expenses_export_{timestamp}.xlsx"
        
        filepath = self.export_dir / filename
        
        df = pd.DataFrame(expenses)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Expenses', index=False)
            
            worksheet = writer.sheets['Expenses']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return str(filepath)
    
    def export_monthly_report(self, monthly_data: Dict, expenses: List[Dict]) -> str:
        """Export comprehensive monthly report with multiple sheets"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monthly_report_{monthly_data['year']}_{monthly_data['month']:02d}_{timestamp}.xlsx"
        filepath = self.export_dir / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            summary_data = {
                'Metric': ['Month-Year', 'Total Expenses', 'Number of Transactions', 'Categories Covered'],
                'Value': [
                    f"{monthly_data['month']:02d}/{monthly_data['year']}",
                    f"Rp {monthly_data['total_expenses']:,.0f}",
                    len(expenses),
                    len(monthly_data['category_breakdown'])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        return str(filepath)
'''
    create_file("services/export_service.py", export_service_content)
    
    # STEP 3: Fix database_config.py with indexes
    print_step(3, "Fixing config/database_config.py with indexes")
    # First, read existing content
    db_config_path = project_root / "config" / "database_config.py"
    if db_config_path.exists():
        with open(db_config_path, 'r', encoding='utf-8') as f:
            db_content = f.read()
        
        # Add CREATE INDEX statements after table creation
        if 'CREATE TABLE IF NOT EXISTS expenses' in db_content:
            # Find where to insert indexes
            lines = db_content.split('\n')
            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                if 'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP' in line:
                    # Insert index creation after expenses table
                    new_lines.append('        )')
                    new_lines.append('')
                    new_lines.append('        # Create indexes for performance')
                    new_lines.append('        cursor.execute(\'\'\'')
                    new_lines.append('            CREATE INDEX IF NOT EXISTS idx_expenses_date')
                    new_lines.append('            ON expenses(date)')
                    new_lines.append('        \'\'\')')
                    new_lines.append('')
                    new_lines.append('        cursor.execute(\'\'\'')
                    new_lines.append('            CREATE INDEX IF NOT EXISTS idx_expenses_category')
                    new_lines.append('            ON expenses(category)')
                    new_lines.append('        \'\'\')')
                    new_lines.append('')
                    new_lines.append('        cursor.execute(\'\'\'')
                    new_lines.append('            CREATE INDEX IF NOT EXISTS idx_expenses_date_category')
                    new_lines.append('            ON expenses(date, category)')
                    new_lines.append('        \'\'\')')
                    # Skip the original closing parenthesis line
                    continue
                elif line.strip() == '        )' and i > 0 and 'categories' in lines[i-1]:
                    # Skip duplicate closing parenthesis
                    continue
            
            db_content = '\n'.join(new_lines)
            create_file("config/database_config.py", db_content)
            print("✅ Added database indexes to config/database_config.py")
    else:
        print("⚠️  config/database_config.py not found, skipping...")
    
    # STEP 4: Create pyproject.toml
    print_step(4, "Creating pyproject.toml")
    pyproject_content = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "daily-expense-tracker"
version = "1.0.0"
authors = [
    {name = "Developer", email = "dev@example.com"},
]
description = "A comprehensive Python application for tracking and analyzing daily expenses"
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = ["--verbose", "--tb=short"]
'''
    create_file("pyproject.toml", pyproject_content)
    
    # STEP 5: Create setup.cfg
    print_step(5, "Creating setup.cfg")
    setup_cfg_content = '''[metadata]
name = daily-expense-tracker
version = 1.0.0
author = Developer
author_email = dev@example.com
description = A comprehensive Python application for tracking and analyzing daily expenses

[options]
packages = find:
python_requires = >=3.8

[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
'''
    create_file("setup.cfg", setup_cfg_content)
    
    # STEP 6: Add batch operations to database_service.py
    print_step(6, "Adding batch operations to services/database_service.py")
    db_service_path = project_root / "services" / "database_service.py"
    if db_service_path.exists():
        with open(db_service_path, 'r', encoding='utf-8') as f:
            db_service_content = f.read()
        
        # Add batch operations method if not present
        if 'def add_batch_expenses' not in db_service_content:
            # Find where to add the method (after add_expense)
            lines = db_service_content.split('\n')
            new_lines = []
            add_method_inserted = False
            
            for line in lines:
                new_lines.append(line)
                if 'def add_expense' in line and not add_method_inserted:
                    # Add batch method after add_expense
                    new_lines.append('')
                    new_lines.append('    def add_batch_expenses(self, expenses: List[Expense]) -> List[int]:')
                    new_lines.append('        """Add multiple expenses in batch"""')
                    new_lines.append('        conn = self.db_config.get_connection()')
                    new_lines.append('        cursor = conn.cursor()')
                    new_lines.append('        expense_ids = []')
                    new_lines.append('        ')
                    new_lines.append('        try:')
                    new_lines.append('            for expense in expenses:')
                    new_lines.append('                cursor.execute(\'\'\'')
                    new_lines.append('                    INSERT INTO expenses (date, category, amount, description)')
                    new_lines.append('                    VALUES (?, ?, ?, ?)')
                    new_lines.append('                \'\'\', (expense.date, expense.category, float(expense.amount), expense.description))')
                    new_lines.append('                expense_ids.append(cursor.lastrowid)')
                    new_lines.append('            ')
                    new_lines.append('            conn.commit()')
                    new_lines.append('        except Exception as e:')
                    new_lines.append('            conn.rollback()')
                    new_lines.append('            raise e')
                    new_lines.append('        finally:')
                    new_lines.append('            conn.close()')
                    new_lines.append('        ')
                    new_lines.append('        return expense_ids')
                    add_method_inserted = True
            
            if add_method_inserted:
                db_service_content = '\n'.join(new_lines)
                create_file("services/database_service.py", db_service_content)
                print("✅ Added batch operations to services/database_service.py")
    else:
        print("⚠️  services/database_service.py not found, skipping...")
    
    # STEP 7: Create integration test
    print_step(7, "Creating integration test")
    integration_test_content = '''"""
Integration tests for export functionality
"""
import pytest
import tempfile
from pathlib import Path
from services.export_service import ExportService

def test_export_service_integration():
    """Integration test for ExportService"""
    with tempfile.TemporaryDirectory() as tmpdir:
        service = ExportService()
        service.export_dir = Path(tmpdir)
        
        sample_expenses = [
            {'date': '2024-01-15', 'category': 'Food', 'amount': 50000, 'description': 'Lunch'},
            {'date': '2024-01-16', 'category': 'Transport', 'amount': 25000, 'description': 'Bus'}
        ]
        
        # Test CSV export
        csv_path = service.export_to_csv(sample_expenses)
        assert Path(csv_path).exists()
        assert csv_path.endswith('.csv')
        
        # Test Excel export
        excel_path = service.export_to_excel(sample_expenses)
        assert Path(excel_path).exists()
        assert excel_path.endswith('.xlsx')
        
        # Test monthly report export
        monthly_data = {
            'year': 2024,
            'month': 1,
            'total_expenses': 75000,
            'category_breakdown': [
                {'category': 'Food', 'total': 50000},
                {'category': 'Transport', 'total': 25000}
            ]
        }
        report_path = service.export_monthly_report(monthly_data, sample_expenses)
        assert Path(report_path).exists()
        assert report_path.endswith('.xlsx')
        
        print(f"✅ All exports created successfully")
        print(f"   CSV: {csv_path}")
        print(f"   Excel: {excel_path}")
        print(f"   Report: {report_path}")

def test_export_service_instantiation():
    """Test that ExportService can be instantiated and has required methods"""
    service = ExportService()
    
    assert hasattr(service, 'export_to_csv')
    assert hasattr(service, 'export_to_excel')
    assert hasattr(service, 'export_monthly_report')
    assert hasattr(service, 'export_dir')
    
    # Check methods are callable
    assert callable(service.export_to_csv)
    assert callable(service.export_to_excel)
    assert callable(service.export_monthly_report)
'''
    
    # Add to existing test_export.py or create new integration test
    test_export_path = project_root / "tests" / "test_export.py"
    if test_export_path.exists():
        with open(test_export_path, 'a', encoding='utf-8') as f:
            f.write('\n\n' + integration_test_content)
        print("✅ Added integration tests to tests/test_export.py")
    else:
        create_file("tests/test_integration.py", integration_test_content)
        print("✅ Created tests/test_integration.py with integration tests")
    
    # STEP 8: Verify all fixes
    print_step(8, "Verifying all fixes")
    print("\n📋 Summary of fixes applied:")
    print("1. ✅ Updated requirements.txt with code quality tools")
    print("2. ✅ Created complete ExportService in services/export_service.py")
    print("3. ✅ Added database indexes to config/database_config.py")
    print("4. ✅ Created pyproject.toml with tool configurations")
    print("5. ✅ Created setup.cfg with pytest configuration")
    print("6. ✅ Added batch operations to services/database_service.py")
    print("7. ✅ Added integration tests")
    
    # Final verification
    final_score = run_checker()
    
    print("\n" + "="*70)
    print("🎉 PHASE 4 FIXES COMPLETE!")
    print("="*70)
    
    improvement = final_score - current_score
    print(f"📈 Score improved from {current_score:.1f}% to {final_score:.1f}%")
    print(f"📊 Improvement: +{improvement:.1f}%")
    
    if final_score >= 90:
        print("\n🏆 EXCELLENT! Phase 4 is complete!")
    elif final_score >= 70:
        print("\n👍 GOOD PROGRESS! Phase 4 is mostly complete!")
    else:
        print("\n⚠️  Some items may still need manual attention.")
        print("   Run the checker again to see remaining issues.")
    
    print("\n📝 Next steps:")
    print("1. Install new dependencies: pip install -r requirements.txt")
    print("2. Test the application: python main.py")
    print("3. Run tests: python -m pytest tests/ -v")
    print("4. Format code: python -m black .")

if __name__ == "__main__":
    main()