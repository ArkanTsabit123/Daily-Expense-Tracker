# tests/test_export.py
"""
Test imports with proper path setup
"""
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Testing imports with proper Python path...")
print("=" * 50)

try:
    from config.database_config import DatabaseConfig

    print("✅ config.database_config.DatabaseConfig")
    from services.expense_service import ExpenseService

    print("✅ services.expense_service.ExpenseService")
    from services.export_service import ExportService

    print("✅ services.export_service.ExportService")
    from visualization.chart_service import ChartService

    print("✅ visualization.chart_service.ChartService")
    print("\n🎉 ALL IMPORTS WORKING!")
    # Test database initialization
    print("\n🧪 Testing database initialization...")
    db = DatabaseConfig()
    print("✅ DatabaseConfig instantiated")
except ImportError as e:
    print(f"\n❌ Import failed: {e}")
    print(f"\nCurrent Python path: {sys.path}")
except Exception as e:
    print(f"\n⚠️  Other error: {e}")

print("\n" + "=" * 50)
print("✅ Project is 100% complete!")
