"""
Export Service for Daily Expense Tracker
Handles CSV, Excel exports and comprehensive reporting
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

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

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
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

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Expenses", index=False)

            worksheet = writer.sheets["Expenses"]
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
        filename = (
            f"monthly_report_{monthly_data['year']}_{monthly_data['month']:02d}_{timestamp}.xlsx"
        )
        filepath = self.export_dir / filename

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            summary_data = {
                "Metric": [
                    "Month-Year",
                    "Total Expenses",
                    "Number of Transactions",
                    "Categories Covered",
                ],
                "Value": [
                    f"{monthly_data['month']:02d}/{monthly_data['year']}",
                    f"Rp {monthly_data['total_expenses']:,.0f}",
                    len(expenses),
                    len(monthly_data["category_breakdown"]),
                ],
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

        return str(filepath)

# services/export_service.py
from typing import Dict, List

class ExportService:
    def __init__(self):
        self.export_dir = Path(__file__).parent.parent / "exports"
        self.export_dir.mkdir(exist_ok=True)

    def export_to_csv(self, expenses: List[Dict], filename: str = None) -> str:
        """Export data to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expenses_export_{timestamp}.csv"

        filepath = self.export_dir / filename

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            if expenses:
                fieldnames = expenses[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(expenses)

        return str(filepath)

    def export_to_excel(self, expenses: List[Dict], filename: str = None) -> str:
        """Export data to Excel"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expenses_export_{timestamp}.xlsx"

        filepath = self.export_dir / filename

        # Convert to DataFrame
        df = pd.DataFrame(expenses)

        # Format date columns
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        # Export to Excel
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Expenses", index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets["Expenses"]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = max_length + 2
                worksheet.column_dimensions[column_letter].width = adjusted_width

        return str(filepath)

    def export_monthly_report(self, monthly_data: Dict, expenses: List[Dict]) -> str:
        """Export comprehensive monthly report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monthly_report_{monthly_data['year']}_{monthly_data['month']}_{timestamp}.xlsx"
        filepath = self.export_dir / filename

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            # Sheet 1: Summary
            summary_data = {
                "Bulan": [f"{monthly_data['month']}/{monthly_data['year']}"],
                "Total Pengeluaran": [monthly_data["total_expenses"]],
                "Jumlah Transaksi": [len(expenses)],
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Ringkasan", index=False)

            # Sheet 2: Category Breakdown
            if "category_breakdown" in monthly_data:
                category_df = pd.DataFrame(monthly_data["category_breakdown"])
                category_df.to_excel(writer, sheet_name="Per Kategori", index=False)

            # Sheet 3: Transaction Details
            expenses_df = pd.DataFrame(expenses)
            if "date" in expenses_df.columns:
                expenses_df["date"] = pd.to_datetime(expenses_df["date"]).dt.strftime("%Y-%m-%d")
            expenses_df.to_excel(writer, sheet_name="Detail Transaksi", index=False)

        return str(filepath)
