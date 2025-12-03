#tests/test_integration.py

"""
Integration tests for export functionality
"""

import pytest
from services.expense_service import ExpenseService
from services.export_service import ExportService

class TestIntegration:
    """End-to-end integration tests"""
    
    @pytest.fixture
    def expense_service(self):
        return ExpenseService()
    
    @pytest.fixture
    def export_service(self):
        return ExportService()
    
    def test_complete_workflow(self, expense_service, export_service):
        """Test complete workflow: add expense -> get history -> export"""
        # Add test expense
        result = expense_service.create_expense(
            "2024-12-01",
            "Food",
            "50000",
            "Test integration"
        )
        assert result['success'] == True
        
        # Get history
        expenses = expense_service.get_expense_history()
        assert len(expenses) > 0
        
        # Export to CSV
        filepath = export_service.export_to_csv(expenses, "test_integration.csv")
        assert "test_integration.csv" in filepath
        
        # Clean up
        import os
        if os.path.exists(filepath):
            os.remove(filepath)