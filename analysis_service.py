# services/analysis_service.py (CLEAN VERSION)
"""
Analysis Service for Daily Expense Tracker
Provides advanced analysis functions for expense data.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

from ..models.expense_model import Expense
from .database_service import DatabaseService

class AnalysisService:
    """Service for expense analysis operations"""

    def __init__(self):
        self.db_service = DatabaseService()

    def get_yearly_summary(self, year: int) -> Dict[str, Any]:
        """Get yearly expense summary"""
        monthly_totals = []
        for month in range(1, 13):
            summary = self.db_service.get_monthly_summary(year, month)
            if summary["total_expenses"] > 0:
                monthly_totals.append(
                    {
                        "month": month,
                        "year": year,
                        "total": summary["total_expenses"],
                        "transaction_count": len(
                            self.db_service.get_expenses(month=month, year=year)
                        ),
                    }
                )
        total_year = sum(item["total"] for item in monthly_totals)
        avg_monthly = total_year / len(monthly_totals) if monthly_totals else 0
        return {
            "year": year,
            "total_expenses": total_year,
            "monthly_average": avg_monthly,
            "monthly_breakdown": monthly_totals,
            "most_expensive_month": (
                max(monthly_totals, key=lambda x: x["total"]) if monthly_totals else None
            ),
            "least_expensive_month": (
                min(monthly_totals, key=lambda x: x["total"]) if monthly_totals else None
            ),
        }

    def get_category_trends(self, category: str, months: int = 6) -> List[Dict[str, Any]]:
        """Get category spending trends for the last N months"""
        trends = []
        end_date = datetime.now().date()
        for i in range(months):
            target_date = end_date - timedelta(days=30 * i)
            summary = self.db_service.get_monthly_summary(target_date.year, target_date.month)
            # Find the category in breakdown
            category_total = 0
            for item in summary.get("category_breakdown", []):
                if item["category"] == category:
                    category_total = item["total"]
                    break
            trends.append(
                {
                    "month": target_date.month,
                    "year": target_date.year,
                    "total": category_total,
                    "percentage": (
                        (category_total / summary["total_expenses"] * 100)
                        if summary["total_expenses"] > 0
                        else 0
                    ),
                }
            )
        return trends

    def get_spending_patterns(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Analyze spending patterns between dates"""
        expenses = self.db_service.get_expenses()
        # Filter by date range
        filtered_expenses = [
            exp
            for exp in expenses
            if start_date <= datetime.strptime(exp["date"], "%Y-%m-%d").date() <= end_date
        ]
        if not filtered_expenses:
            return {"message": "No expenses in date range"}
        # Calculate statistics
        amounts = [exp["amount"] for exp in filtered_expenses]
        total = sum(amounts)
        average = total / len(amounts)
        # Find most common day of week
        weekdays = []
        for exp in filtered_expenses:
            exp_date = datetime.strptime(exp["date"], "%Y-%m-%d").date()
            weekdays.append(exp_date.strftime("%A"))
        from collections import Counter

        weekday_counts = Counter(weekdays)
        most_common_day = weekday_counts.most_common(1)[0] if weekday_counts else ("Unknown", 0)
        return {
            "date_range": f"{start_date} to {end_date}",
            "total_expenses": total,
            "transaction_count": len(filtered_expenses),
            "average_per_transaction": average,
            "most_common_day": most_common_day[0],
            "day_frequency": most_common_day[1],
            "category_distribution": self._get_category_distribution(filtered_expenses),
        }

    def _get_category_distribution(self, expenses: List[Dict]) -> Dict[str, float]:
        """Helper to get category distribution"""
        category_totals = {}
        for exp in expenses:
            category = exp["category"]
            amount = exp["amount"]
            category_totals[category] = category_totals.get(category, 0) + amount
        total = sum(category_totals.values())
        # Convert to percentages
        if total > 0:
            return {cat: (amount / total * 100) for cat, amount in category_totals.items()}
        return category_totals
