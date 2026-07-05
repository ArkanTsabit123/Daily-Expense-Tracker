# daily_expense_tracker/services/export_service.py

"""
Export Service for Daily Expense Tracker
Handles CSV, Excel exports and comprehensive reporting
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment


class ExportService:
    """Service for exporting expense data to various formats"""
    
    def __init__(self):
        """Initialize export service with export directory"""
        self.export_dir = Path(__file__).parent.parent / "exports"
        self.export_dir.mkdir(exist_ok=True)

    def export_to_csv(self, expenses: List[Dict], filename: Optional[str] = None) -> str:
        """
        Export expenses data to CSV format.
        
        Args:
            expenses: List of expense dictionaries
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expenses_export_{timestamp}.csv"

        filepath = self.export_dir / filename

        if not expenses:
            # Create empty CSV with headers
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["No data to export"])
            return str(filepath)

        # Get all possible keys from all expenses
        all_keys = set()
        for expense in expenses:
            all_keys.update(expense.keys())
        fieldnames = sorted(all_keys)

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(expenses)

        return str(filepath)

    def export_to_excel(self, expenses: List[Dict], filename: Optional[str] = None) -> str:
        """
        Export expenses data to Excel format with formatting.
        
        Args:
            expenses: List of expense dictionaries
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expenses_export_{timestamp}.xlsx"

        filepath = self.export_dir / filename

        if not expenses:
            # Create empty Excel with message
            df = pd.DataFrame({"Message": ["No data to export"]})
            df.to_excel(filepath, index=False)
            return str(filepath)

        # Convert to DataFrame
        df = pd.DataFrame(expenses)

        # Format date columns
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        # Export to Excel with formatting
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Expenses", index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets["Expenses"]
            
            # Style for header
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="2E86C1", end_color="2E86C1", fill_type="solid")
            
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
        """
        Export comprehensive monthly report with multiple sheets.
        
        Args:
            monthly_data: Dictionary with monthly summary data
            expenses: List of expense dictionaries for the month
            
        Returns:
            Path to the exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monthly_report_{monthly_data.get('year', '')}_{monthly_data.get('month', ''):02d}_{timestamp}.xlsx"
        filepath = self.export_dir / filename

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            # Sheet 1: Summary
            summary_data = {
                "Metric": [
                    "Month-Year",
                    "Total Expenses",
                    "Number of Transactions",
                    "Categories Covered",
                ],
                "Value": [
                    f"{monthly_data.get('month', '')}/{monthly_data.get('year', '')}",
                    f"Rp {monthly_data.get('total_expenses', 0):,.0f}",
                    len(expenses),
                    len(monthly_data.get("category_breakdown", [])),
                ],
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

            # Sheet 2: Category Breakdown
            if "category_breakdown" in monthly_data and monthly_data["category_breakdown"]:
                category_df = pd.DataFrame(monthly_data["category_breakdown"])
                category_df.to_excel(writer, sheet_name="Per Kategori", index=False)

            # Sheet 3: Transaction Details
            if expenses:
                expenses_df = pd.DataFrame(expenses)
                if "date" in expenses_df.columns:
                    expenses_df["date"] = pd.to_datetime(expenses_df["date"]).dt.strftime("%Y-%m-%d")
                expenses_df.to_excel(writer, sheet_name="Detail Transaksi", index=False)

            # Auto-adjust column widths for all sheets
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
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


# Optional: Simple test function
def test_export():
    """Test export functionality with sample data"""
    sample_expenses = [
        {
            "id": 1,
            "date": "2024-01-15",
            "category": "Food",
            "amount": 50000,
            "description": "Lunch",
        },
        {
            "id": 2,
            "date": "2024-01-16",
            "category": "Transport",
            "amount": 20000,
            "description": "Gojek",
        },
    ]
    
    service = ExportService()
    
    # Test CSV export
    csv_path = service.export_to_csv(sample_expenses)
    print(f"✅ CSV exported to: {csv_path}")
    
    # Test Excel export
    excel_path = service.export_to_excel(sample_expenses)
    print(f"✅ Excel exported to: {excel_path}")
    
    # Test monthly report
    monthly_data = {
        "year": 2024,
        "month": 1,
        "total_expenses": 70000,
        "category_breakdown": [
            {"category": "Food", "total": 50000, "percentage": 71.4},
            {"category": "Transport", "total": 20000, "percentage": 28.6},
        ],
    }
    report_path = service.export_monthly_report(monthly_data, sample_expenses)
    print(f"✅ Monthly report exported to: {report_path}")


if __name__ == "__main__":
    test_export()