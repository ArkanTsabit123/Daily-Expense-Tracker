#  tests/test_database.py

"""
Unit tests for database service and models
"""

import pytest
from datetime import date
from decimal import Decimal
from services.database_service import DatabaseService


@pytest.fixture
def db_service():
    """Fixture untuk DatabaseService dengan database in-memory"""
    service = DatabaseService(":memory:")
    yield service
    service.close()


def test_add_expense(db_service):
    """Test menambah expense"""
    class TestExpense:
        def __init__(self):
            self.date = date(2026, 7, 5)
            self.category = "Makanan"
            self.amount = Decimal("50000")
            self.description = "Makan siang"
    
    expense_id = db_service.add_expense(TestExpense())
    assert expense_id > 0
    
    expenses = db_service.get_expenses()
    assert len(expenses) == 1
    assert expenses[0]['amount'] == 50000
    assert expenses[0]['category'] == "Makanan"


def test_get_expenses(db_service):
    """Test mengambil expenses dengan filter"""
    class TestExpense:
        def __init__(self, date_val, amount, category, desc):
            self.date = date_val
            self.category = category
            self.amount = Decimal(str(amount))
            self.description = desc
    
    db_service.add_expense(TestExpense(date(2026, 7, 1), 10000, "Food", "Test 1"))
    db_service.add_expense(TestExpense(date(2026, 7, 5), 20000, "Transport", "Test 2"))
    db_service.add_expense(TestExpense(date(2026, 8, 1), 15000, "Food", "Test 3"))
    
    # Test semua expenses
    all_expenses = db_service.get_expenses()
    assert len(all_expenses) == 3
    
    # Test filter by month
    expenses = db_service.get_expenses(month=7, year=2026)
    assert len(expenses) == 2
    
    # Test filter by category
    expenses = db_service.get_expenses(category="Food")
    assert len(expenses) == 2


def test_get_expense_by_id(db_service):
    """Test mengambil expense berdasarkan ID"""
    class TestExpense:
        def __init__(self):
            self.date = date(2026, 7, 5)
            self.category = "Hiburan"
            self.amount = Decimal("30000")
            self.description = "Nonton film"
    
    expense_id = db_service.add_expense(TestExpense())
    expense = db_service.get_expense(expense_id)
    
    assert expense is not None
    assert expense['amount'] == 30000
    assert expense['category'] == "Hiburan"
    
    not_found = db_service.get_expense(9999)
    assert not_found is None


def test_update_expense(db_service):
    """Test update expense"""
    class TestExpense:
        def __init__(self, desc):
            self.date = date(2026, 7, 5)
            self.category = "Minuman"
            self.amount = Decimal("10000")
            self.description = desc
    
    expense_id = db_service.add_expense(TestExpense("Kopi"))
    
    # Update
    updated = db_service.update_expense(expense_id, TestExpense("Kopi Update"))
    assert updated is True
    
    # Verifikasi
    expense = db_service.get_expense(expense_id)
    assert expense['description'] == "Kopi Update"


def test_delete_expense(db_service):
    """Test delete expense"""
    class TestExpense:
        def __init__(self):
            self.date = date(2026, 7, 5)
            self.category = "Lainnya"
            self.amount = Decimal("20000")
            self.description = "Test delete"
    
    expense_id = db_service.add_expense(TestExpense())
    
    deleted = db_service.delete_expense(expense_id)
    assert deleted is True
    
    expense = db_service.get_expense(expense_id)
    assert expense is None


def test_get_monthly_summary(db_service):
    """Test monthly summary"""
    class TestExpense:
        def __init__(self, date_val, amount, category):
            self.date = date_val
            self.category = category
            self.amount = Decimal(str(amount))
            self.description = ""
    
    db_service.add_expense(TestExpense(date(2026, 7, 1), 10000, "Food"))
    db_service.add_expense(TestExpense(date(2026, 7, 5), 20000, "Transport"))
    db_service.add_expense(TestExpense(date(2026, 7, 10), 15000, "Food"))
    
    summary = db_service.get_monthly_summary(2026, 7)
    assert summary['total_expenses'] == 45000
    assert len(summary['category_breakdown']) == 2


def test_execute_query(db_service):
    """Test execute_query method"""
    class TestExpense:
        def __init__(self, category, amount):
            self.date = date(2026, 7, 1)
            self.category = category
            self.amount = Decimal(str(amount))
            self.description = "Test"
    
    db_service.add_expense(TestExpense("Food", 10000))
    db_service.add_expense(TestExpense("Transport", 20000))
    
    results = db_service.execute_query(
        "SELECT category, SUM(amount) as total FROM expenses GROUP BY category"
    )
    assert len(results) == 2