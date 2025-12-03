#project portofolio/junior project/daily-expense-tracker/services/utils/formatters.py

"""
Formatters Utility
Provides functions to format numbers and strings for display purposes.
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional


def format_currency(amount: Decimal) -> str:
    return f"Rp {amount:,.0f}".replace(",", ".")


def format_date(date_string: str, 
                input_format: str = '%Y-%m-%d',
                output_format: str = '%d/%m/%Y') -> str:
    try:
        date_obj = datetime.strptime(date_string, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_string


def format_category(category: str) -> str:
    icons = {
        'Makanan & Minuman': '🍔',
        'Transportasi': '🚗',
        'Belanja': '🛍️',
        'Hiburan': '🎬',
        'Kesehatan': '🏥',
        'Pendidikan': '📚',
        'Tagihan': '📋',
        'Lain-lain': '📦',
        'Food': '🍔',
        'Transport': '🚗',
        'Shopping': '🛍️',
        'Entertainment': '🎬',
        'Healthcare': '🏥',
        'Education': '📚',
        'Bills': '📋',
        'Others': '📦'
    }
    
    icon = icons.get(category, '📦')
    return f"{icon} {category}"


def format_percentage(value: float) -> str:
    return f"{value:.1f}%"
