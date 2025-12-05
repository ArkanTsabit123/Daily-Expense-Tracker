# tests/test_export.py

"""
Integration tests for export functionality
"""
import tempfile
from pathlib import Path

import pytest

from services.export_service import ExportService

def test_export_service_integration():
    """Integration test for ExportService"""
    with tempfile.TemporaryDirectory() as tmpdir:
        service = ExportService()
        service.export_dir = Path(tmpdir)
        sample_expenses = [
            {
                "date": "2024-01-15",
                "category": "Food",
                "amount": 50000,
                "description": "Lunch",
            },
            {
                "date": "2024-01-16",
                "category": "Transport",
                "amount": 25000,
                "description": "Bus",
            },
        ]
        # Test CSV export
        csv_path = service.export_to_csv(sample_expenses)
        assert Path(csv_path).exists()
        assert csv_path.endswith(".csv")
        # Test Excel export
        excel_path = service.export_to_excel(sample_expenses)
        assert Path(excel_path).exists()
        assert excel_path.endswith(".xlsx")
        # Test monthly report export
        monthly_data = {
            "year": 2024,
            "month": 1,
            "total_expenses": 75000,
            "category_breakdown": [
                {"category": "Food", "total": 50000},
                {"category": "Transport", "total": 25000},
            ],
        }
        report_path = service.export_monthly_report(monthly_data, sample_expenses)
        assert Path(report_path).exists()
        assert report_path.endswith(".xlsx")
        print("✅ All exports created successfully")
        print(f"   CSV: {csv_path}")
        print(f"   Excel: {excel_path}")
        print(f"   Report: {report_path}")

def test_export_service_instantiation():
    """Test that ExportService can be instantiated and has required methods"""
    service = ExportService()
    assert hasattr(service, "export_to_csv")
    assert hasattr(service, "export_to_excel")
    assert hasattr(service, "export_monthly_report")
    assert hasattr(service, "export_dir")
    # Check methods are callable
    assert callable(service.export_to_csv)
    assert callable(service.export_to_excel)
    assert callable(service.export_monthly_report)
