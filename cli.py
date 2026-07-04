# cli.py
"""
Daily Expense Tracker - CLI Version (Upgraded)
Features: 
- Expense & Income Tracking
- Budget Management
- Recurring Expenses
- All Time & Filter Views
- Export to CSV/Excel
- Charts & Analytics
- Data Backup & Restore
"""

import os
import sys
from datetime import datetime
from decimal import Decimal
import logging
import calendar
import sqlite3
import json
import shutil
from typing import Dict, List, Optional, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database_config import DatabaseConfig
from services.expense_service import ExpenseService
from services.export_service import ExportService
from visualization.chart_service import ChartService
from utils.date_utils import get_current_month_year, get_month_name
from utils.formatters import format_category, format_currency, format_date
from utils.validation import validate_amount, validate_date, parse_amount


class ExpenseTrackerApp:
    """
    Main CLI application class for expense tracking
    Upgraded with Income, Budget, Recurring, Backup features
    """
    
    def __init__(self):
        """Initialize the application with services and database"""
        self.expense_service = ExpenseService()
        self.export_service = ExportService()
        self.chart_service = ChartService()
        self.current_month, self.current_year = get_current_month_year()

        # Initialize database
        db_config = DatabaseConfig()
        db_config.initialize_database()
        
        # Initialize additional tables
        self.init_additional_tables()

    def init_additional_tables(self):
        """Initialize additional database tables for new features"""
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        
        # Create expenses table if not exists (with payment_method)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                payment_method TEXT DEFAULT 'Cash',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Incomes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                is_recurring INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                monthly_limit REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Recurring expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recurring_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                frequency TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (expense_id) REFERENCES expenses(id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def clear_screen(self):
        """Clear terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")

    def display_header(self, title):
        """Display formatted header with title"""
        self.clear_screen()
        print("=" * 70)
        print("💵 EXPENSE TRACKER PRO".center(70))
        print(f"📋 {title}".center(70))
        print("=" * 70)
        print()

    def wait_for_enter(self):
        """Wait for user to press Enter"""
        input("\n↵ Press Enter to continue...")

    def print_separator(self, char="=", length=70):
        """Print a separator line"""
        print(char * length)

    # ============================================================
    # DATABASE HELPERS
    # ============================================================

    def get_total_income(self, month=None, year=None, all_time=False) -> float:
        """Get total income for period"""
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        
        if all_time:
            cursor.execute("SELECT SUM(amount) FROM incomes")
        elif month and year:
            cursor.execute(
                "SELECT SUM(amount) FROM incomes WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?",
                (f"{month:02d}", str(year))
            )
        else:
            cursor.execute("SELECT SUM(amount) FROM incomes")
        
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0

    def get_expense_tags(self, expense_id: int) -> List[str]:
        """Get tags for an expense"""
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT tag FROM expense_tags WHERE expense_id = ?", (expense_id,))
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    # ============================================================
    # INCOME FUNCTIONS
    # ============================================================

    def add_income(self):
        """Add new income entry"""
        self.display_header("ADD NEW INCOME")
        
        try:
            # Input date
            while True:
                date_input = input("📅 Date (YYYY-MM-DD) [leave blank for today]: ").strip()
                if not date_input:
                    date_input = datetime.now().strftime("%Y-%m-%d")
                    break
                elif validate_date(date_input):
                    break
                else:
                    print("❌ Invalid date format. Use YYYY-MM-DD")

            # Input source
            source = input("💵 Source (e.g., Salary, Bonus): ").strip()
            if not source:
                print("❌ Source is required!")
                self.wait_for_enter()
                return

            # Input amount
            while True:
                amount_input = input("💰 Amount: Rp ").strip()
                try:
                    amount = float(amount_input.replace(',', ''))
                    if amount > 0:
                        break
                    else:
                        print("❌ Amount must be greater than 0")
                except ValueError:
                    print("❌ Invalid amount format")

            # Input description
            description = input("📝 Description (optional): ").strip()

            # Recurring
            recurring = input("🔄 Recurring income? (y/n): ").lower() == 'y'

            # Confirm
            print("\n📋 Income Summary:")
            print(f"   Date      : {format_date(date_input)}")
            print(f"   Source    : {source}")
            print(f"   Amount    : {format_currency(Decimal(amount))}")
            print(f"   Description: {description or '-'}")
            print(f"   Recurring : {'Yes' if recurring else 'No'}")

            confirm = input("\n✅ Save this income? (y/n): ").lower()

            if confirm == "y":
                conn = sqlite3.connect('expense_tracker.db')
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO incomes (date, source, amount, description, is_recurring) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (date_input, source, amount, description, 1 if recurring else 0)
                )
                conn.commit()
                conn.close()
                print(f"✅ Income added successfully! {source}: {format_currency(Decimal(amount))}")
            else:
                print("❌ Income entry cancelled")

        except KeyboardInterrupt:
            print("\n\n❌ Input cancelled")
        except Exception as e:
            print(f"❌ Error: {e}")

        self.wait_for_enter()

    def view_incomes(self):
        """View all incomes"""
        self.display_header("INCOME HISTORY")
        
        try:
            print("\n🔍 Filter options:")
            print("1. All Time")
            print("2. Specific month")
            print("3. Back")
            
            choice = input("\nSelect (1-3): ").strip()
            
            conn = sqlite3.connect('expense_tracker.db')
            cursor = conn.cursor()
            
            if choice == "1":
                cursor.execute("SELECT * FROM incomes ORDER BY date DESC")
            elif choice == "2":
                year = input(f"Year [{self.current_year}]: ").strip()
                month = input(f"Month (1-12) [{self.current_month}]: ").strip()
                year = int(year) if year.isdigit() else self.current_year
                month = int(month) if month.isdigit() else self.current_month
                cursor.execute(
                    "SELECT * FROM incomes WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ? ORDER BY date DESC",
                    (f"{month:02d}", str(year))
                )
            else:
                conn.close()
                return
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                print("\n📭 No income data found")
                self.wait_for_enter()
                return
            
            total = 0
            print("\n" + "-" * 80)
            print(f"{'ID':>5} {'Date':12} {'Source':20} {'Amount':>15} {'Description':25}")
            print("-" * 80)
            
            for row in rows:
                total += row[3]
                print(
                    f"{row[0]:>5} "
                    f"{format_date(row[1]):12} "
                    f"{row[2]:20} "
                    f"{format_currency(Decimal(row[3])):>15} "
                    f"{row[4][:23] if row[4] else '':25}"
                )
            
            print("-" * 80)
            print(f"{'TOTAL':>5} {'':32} {format_currency(Decimal(total)):>15}")
            print("-" * 80)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.wait_for_enter()

    # ============================================================
    # BUDGET FUNCTIONS
    # ============================================================

    def manage_budgets(self):
        """Manage budgets (create, view, edit, delete)"""
        self.display_header("BUDGET MANAGEMENT")
        
        print("1. View Budgets")
        print("2. Add/Edit Budget")
        print("3. Delete Budget")
        print("4. Back")
        
        choice = input("\nSelect (1-4): ").strip()
        
        if choice == "1":
            self.view_budgets()
        elif choice == "2":
            self.add_edit_budget()
        elif choice == "3":
            self.delete_budget()
        elif choice == "4":
            return
        else:
            print("❌ Invalid selection")
            self.wait_for_enter()

    def view_budgets(self):
        """View all budgets with progress"""
        self.display_header("BUDGET OVERVIEW")
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM budgets")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("\n📭 No budgets set")
            self.wait_for_enter()
            return
        
        # Get current month expenses
        month = datetime.now().month
        year = datetime.now().year
        expenses = self.expense_service.get_expense_history({'month': month, 'year': year})
        
        # Calculate spent per category
        spent = {}
        for exp in expenses:
            spent[exp['category']] = spent.get(exp['category'], 0) + exp['amount']
        
        print("\n📊 BUDGET OVERVIEW")
        print("=" * 70)
        print(f"Period: {get_month_name(month)} {year}")
        print("-" * 70)
        
        for row in rows:
            category = row[1]
            limit = row[2]
            current_spent = spent.get(category, 0)
            remaining = limit - current_spent
            progress = (current_spent / limit * 100) if limit > 0 else 0
            
            # Status
            if progress >= 100:
                status = "⚠️ EXCEEDED"
                color = "🔴"
            elif progress >= 80:
                status = "⚠️ NEAR LIMIT"
                color = "🟡"
            else:
                status = "✅ ON TRACK"
                color = "🟢"
            
            # Progress bar
            bar_length = 30
            filled = int(progress / 100 * bar_length)
            bar = f"{'█' * filled}{'░' * (bar_length - filled)}"
            
            print(f"\n📂 {category}")
            print(f"   Limit : {format_currency(Decimal(limit))}")
            print(f"   Spent : {format_currency(Decimal(current_spent))}")
            print(f"   Left  : {format_currency(Decimal(remaining))}")
            print(f"   [{bar}] {progress:.1f}%  {color} {status}")
        
        print("\n" + "=" * 70)
        self.wait_for_enter()

    def add_edit_budget(self):
        """Add or edit a budget"""
        self.display_header("SET BUDGET")
        
        categories = self.expense_service.get_categories()
        print("Available categories:")
        for i, cat in enumerate(categories, 1):
            print(f" {i}. {cat}")
        
        cat_choice = input("\nSelect category number: ").strip()
        if not cat_choice.isdigit() or not (1 <= int(cat_choice) <= len(categories)):
            print("❌ Invalid category")
            self.wait_for_enter()
            return
        
        category = categories[int(cat_choice) - 1]
        
        # Check if budget exists
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT monthly_limit FROM budgets WHERE category = ?", (category,))
        existing = cursor.fetchone()
        conn.close()
        
        current_limit = existing[0] if existing else 0
        print(f"\nCurrent limit for {category}: {format_currency(Decimal(current_limit)) if current_limit > 0 else 'Not set'}")
        
        limit_input = input("New monthly limit (Rp) [enter to keep current]: ").strip()
        if not limit_input:
            if current_limit > 0:
                print("✅ Budget unchanged")
                self.wait_for_enter()
                return
            else:
                print("❌ Please enter a limit")
                self.wait_for_enter()
                return
        
        try:
            limit = float(limit_input.replace(',', ''))
            if limit <= 0:
                print("❌ Limit must be greater than 0")
                self.wait_for_enter()
                return
        except ValueError:
            print("❌ Invalid amount")
            self.wait_for_enter()
            return
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        if existing:
            cursor.execute("UPDATE budgets SET monthly_limit = ? WHERE category = ?", (limit, category))
            message = f"✅ Budget updated for {category}: {format_currency(Decimal(limit))}"
        else:
            cursor.execute("INSERT INTO budgets (category, monthly_limit) VALUES (?, ?)", (category, limit))
            message = f"✅ Budget created for {category}: {format_currency(Decimal(limit))}"
        conn.commit()
        conn.close()
        
        print(message)
        self.wait_for_enter()

    def delete_budget(self):
        """Delete a budget"""
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT category FROM budgets")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("\n📭 No budgets to delete")
            self.wait_for_enter()
            return
        
        print("\nYour budgets:")
        for i, row in enumerate(rows, 1):
            print(f" {i}. {row[0]}")
        
        choice = input("\nSelect budget to delete (number): ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(rows)):
            print("❌ Invalid selection")
            self.wait_for_enter()
            return
        
        category = rows[int(choice) - 1][0]
        
        confirm = input(f"Delete budget for {category}? (y/n): ").lower()
        if confirm != "y":
            print("❌ Cancelled")
            self.wait_for_enter()
            return
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budgets WHERE category = ?", (category,))
        conn.commit()
        conn.close()
        
        print(f"✅ Budget deleted for {category}")
        self.wait_for_enter()

    # ============================================================
    # RECURRING EXPENSES FUNCTIONS
    # ============================================================

    def manage_recurring(self):
        """Manage recurring expenses"""
        self.display_header("RECURRING EXPENSES")
        
        print("1. View Recurring Expenses")
        print("2. Add Recurring Expense")
        print("3. Edit Recurring Expense")
        print("4. Delete Recurring Expense")
        print("5. Toggle Active/Inactive")
        print("6. Process Recurring Expenses")
        print("7. Back")
        
        choice = input("\nSelect (1-7): ").strip()
        
        if choice == "1":
            self.view_recurring()
        elif choice == "2":
            self.add_recurring()
        elif choice == "3":
            self.edit_recurring()
        elif choice == "4":
            self.delete_recurring()
        elif choice == "5":
            self.toggle_recurring()
        elif choice == "6":
            self.process_recurring()
        elif choice == "7":
            return
        else:
            print("❌ Invalid selection")
            self.wait_for_enter()

    def view_recurring(self):
        """View all recurring expenses"""
        self.display_header("RECURRING EXPENSES LIST")
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recurring_expenses ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("\n📭 No recurring expenses")
            self.wait_for_enter()
            return
        
        print("\n" + "-" * 85)
        print(f"{'ID':>4} {'Category':14} {'Amount':>12} {'Frequency':10} {'Start':12} {'End':12} {'Active':8}")
        print("-" * 85)
        
        for row in rows:
            print(
                f"{row[0]:>4} "
                f"{row[1]:14} "
                f"{format_currency(Decimal(row[2])):>12} "
                f"{row[4]:10} "
                f"{row[5]:12} "
                f"{row[6] if row[6] else 'Never':12} "
                f"{'✅' if row[7] else '❌':>8}"
            )
        
        print("-" * 85)
        self.wait_for_enter()

    def add_recurring(self):
        """Add new recurring expense"""
        self.display_header("ADD RECURRING EXPENSE")
        
        try:
            # Category
            categories = self.expense_service.get_categories()
            print("\nCategories:")
            for i, cat in enumerate(categories, 1):
                print(f" {i}. {cat}")
            
            cat_choice = input("\nSelect category: ").strip()
            if not cat_choice.isdigit() or not (1 <= int(cat_choice) <= len(categories)):
                print("❌ Invalid category")
                self.wait_for_enter()
                return
            category = categories[int(cat_choice) - 1]
            
            # Amount
            while True:
                amount_input = input("💰 Amount: Rp ").strip()
                try:
                    amount = float(amount_input.replace(',', ''))
                    if amount > 0:
                        break
                    else:
                        print("❌ Amount must be greater than 0")
                except ValueError:
                    print("❌ Invalid amount format")
            
            # Description
            description = input("📝 Description (optional): ").strip()
            
            # Frequency
            print("\nFrequency options:")
            print("1. Daily")
            print("2. Weekly")
            print("3. Monthly")
            print("4. Yearly")
            
            freq_choice = input("Select frequency (1-4): ").strip()
            freq_map = {"1": "daily", "2": "weekly", "3": "monthly", "4": "yearly"}
            frequency = freq_map.get(freq_choice, "monthly")
            
            # Start date
            start_date = input("📅 Start Date (YYYY-MM-DD) [leave blank for today]: ").strip()
            if not start_date:
                start_date = datetime.now().strftime("%Y-%m-%d")
            elif not validate_date(start_date):
                print("❌ Invalid date format")
                self.wait_for_enter()
                return
            
            # End date
            end_date = input("📅 End Date (YYYY-MM-DD) [leave blank for never]: ").strip()
            if end_date and not validate_date(end_date):
                print("❌ Invalid date format")
                self.wait_for_enter()
                return
            
            # Confirm
            print("\n📋 Recurring Expense Summary:")
            print(f"   Category  : {category}")
            print(f"   Amount    : {format_currency(Decimal(amount))}")
            print(f"   Description: {description or '-'}")
            print(f"   Frequency : {frequency}")
            print(f"   Start Date: {start_date}")
            print(f"   End Date  : {end_date or 'Never'}")
            
            confirm = input("\n✅ Save? (y/n): ").lower()
            
            if confirm == "y":
                conn = sqlite3.connect('expense_tracker.db')
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO recurring_expenses 
                       (category, amount, description, frequency, start_date, end_date, active) 
                       VALUES (?, ?, ?, ?, ?, ?, 1)""",
                    (category, amount, description, frequency, start_date, end_date if end_date else None)
                )
                conn.commit()
                conn.close()
                print("✅ Recurring expense added successfully!")
            else:
                print("❌ Cancelled")
            
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.wait_for_enter()

    def edit_recurring(self):
        """Edit recurring expense"""
        self.display_header("EDIT RECURRING EXPENSE")
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, amount FROM recurring_expenses ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("\n📭 No recurring expenses to edit")
            self.wait_for_enter()
            return
        
        print("\nYour recurring expenses:")
        for row in rows:
            print(f" {row[0]}. {row[1]} - {format_currency(Decimal(row[2]))}")
        
        choice = input("\nSelect ID to edit: ").strip()
        if not choice.isdigit():
            print("❌ Invalid selection")
            self.wait_for_enter()
            return
        
        rec_id = int(choice)
        
        new_amount = input("New amount (Rp) [enter to keep]: ").strip()
        if new_amount:
            try:
                amount = float(new_amount.replace(',', ''))
                if amount <= 0:
                    print("❌ Amount must be greater than 0")
                    self.wait_for_enter()
                    return
            except ValueError:
                print("❌ Invalid amount")
                self.wait_for_enter()
                return
        else:
            amount = None
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        if amount:
            cursor.execute("UPDATE recurring_expenses SET amount = ? WHERE id = ?", (amount, rec_id))
            print(f"✅ Updated amount to {format_currency(Decimal(amount))}")
        else:
            print("✅ No changes made")
        conn.commit()
        conn.close()
        
        self.wait_for_enter()

    def delete_recurring(self):
        """Delete recurring expense"""
        self.display_header("DELETE RECURRING EXPENSE")
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, amount FROM recurring_expenses ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("\n📭 No recurring expenses to delete")
            self.wait_for_enter()
            return
        
        print("\nYour recurring expenses:")
        for row in rows:
            print(f" {row[0]}. {row[1]} - {format_currency(Decimal(row[2]))}")
        
        choice = input("\nSelect ID to delete: ").strip()
        if not choice.isdigit():
            print("❌ Invalid selection")
            self.wait_for_enter()
            return
        
        confirm = input(f"Delete recurring expense #{choice}? (y/n): ").lower()
        if confirm != "y":
            print("❌ Cancelled")
            self.wait_for_enter()
            return
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recurring_expenses WHERE id = ?", (int(choice),))
        conn.commit()
        conn.close()
        
        print(f"✅ Recurring expense #{choice} deleted")
        self.wait_for_enter()

    def toggle_recurring(self):
        """Toggle recurring expense active status"""
        self.display_header("TOGGLE RECURRING EXPENSE")
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, amount, active FROM recurring_expenses ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("\n📭 No recurring expenses")
            self.wait_for_enter()
            return
        
        print("\nYour recurring expenses:")
        for row in rows:
            status = "✅ Active" if row[3] else "❌ Inactive"
            print(f" {row[0]}. {row[1]} - {format_currency(Decimal(row[2]))} ({status})")
        
        choice = input("\nSelect ID to toggle: ").strip()
        if not choice.isdigit():
            print("❌ Invalid selection")
            self.wait_for_enter()
            return
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT active FROM recurring_expenses WHERE id = ?", (int(choice),))
        current = cursor.fetchone()
        
        if current:
            new_status = 0 if current[0] else 1
            cursor.execute("UPDATE recurring_expenses SET active = ? WHERE id = ?", (new_status, int(choice)))
            conn.commit()
            status_text = "activated" if new_status else "deactivated"
            print(f"✅ Recurring expense #{choice} {status_text}")
        else:
            print("❌ Recurring expense not found")
        
        conn.close()
        self.wait_for_enter()

    def process_recurring(self):
        """Process all active recurring expenses"""
        self.display_header("PROCESS RECURRING EXPENSES")
        
        confirm = input("Process all active recurring expenses? (y/n): ").lower()
        if confirm != "y":
            print("❌ Cancelled")
            self.wait_for_enter()
            return
        
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recurring_expenses WHERE active = 1")
        recurring = cursor.fetchall()
        
        count = 0
        today = datetime.now().strftime("%Y-%m-%d")
        
        for rec in recurring:
            category = rec[1]
            amount = rec[2]
            description = f"[Recurring] {rec[3]}" if rec[3] else f"[Recurring] {category}"
            
            cursor.execute(
                "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
                (today, category, amount, description)
            )
            count += 1
        
        conn.commit()
        conn.close()
        
        if count > 0:
            print(f"✅ {count} recurring expenses processed!")
        else:
            print("ℹ️ No active recurring expenses to process")
        
        self.wait_for_enter()

    # ============================================================
    # BACKUP & RESTORE FUNCTIONS
    # ============================================================

    def backup_data(self):
        """Backup database"""
        self.display_header("BACKUP DATA")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = "backups"
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backup_file = os.path.join(backup_dir, f"expense_backup_{timestamp}.db")
            shutil.copy2("expense_tracker.db", backup_file)
            
            print(f"✅ Database backed up to: {backup_file}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
        
        self.wait_for_enter()

    def restore_data(self):
        """Restore database from backup"""
        self.display_header("RESTORE DATA")
        
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            print("📭 No backups folder found")
            self.wait_for_enter()
            return
        
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        if not backups:
            print("📭 No backup files found")
            self.wait_for_enter()
            return
        
        print("\nAvailable backups:")
        for i, backup in enumerate(sorted(backups, reverse=True), 1):
            print(f" {i}. {backup}")
        
        choice = input("\nSelect backup to restore (number): ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(backups)):
            print("❌ Invalid selection")
            self.wait_for_enter()
            return
        
        backup_file = os.path.join(backup_dir, backups[int(choice) - 1])
        
        confirm = input(f"Restore from {backups[int(choice) - 1]}? (y/n): ").lower()
        if confirm != "y":
            print("❌ Cancelled")
            self.wait_for_enter()
            return
        
        try:
            # Backup current database first
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = os.path.join(backup_dir, f"pre_restore_backup_{timestamp}.db")
            shutil.copy2("expense_tracker.db", current_backup)
            
            # Restore from backup
            shutil.copy2(backup_file, "expense_tracker.db")
            
            print("✅ Database restored successfully!")
        except Exception as e:
            print(f"❌ Restore failed: {e}")
        
        self.wait_for_enter()

    # ============================================================
    # ANALYTICS FUNCTIONS
    # ============================================================

    def show_analytics(self):
        """Show advanced analytics"""
        self.display_header("ADVANCED ANALYTICS")
        
        print("Select analysis type:")
        print("1. Expense Trend")
        print("2. Category Comparison")
        print("3. Monthly Comparison")
        print("4. Back")
        
        choice = input("\nSelect (1-4): ").strip()
        
        if choice == "1":
            self.expense_trend()
        elif choice == "2":
            self.category_comparison()
        elif choice == "3":
            self.monthly_comparison()
        elif choice == "4":
            return
        else:
            print("❌ Invalid selection")
            self.wait_for_enter()

    def expense_trend(self):
        """Show expense trend"""
        self.display_header("EXPENSE TREND")
        
        print("Select period:")
        print("1. Daily")
        print("2. Weekly")
        print("3. Monthly")
        print("4. Yearly")
        
        choice = input("\nSelect (1-4): ").strip()
        period_map = {"1": "daily", "2": "weekly", "3": "monthly", "4": "yearly"}
        period = period_map.get(choice, "monthly")
        
        expenses = self.expense_service.get_expense_history()
        
        if not expenses:
            print("📭 No data available")
            self.wait_for_enter()
            return
        
        # Group by period
        data_by_period = {}
        for exp in expenses:
            date = datetime.strptime(exp['date'], '%Y-%m-%d')
            
            if period == 'daily':
                key = date.strftime('%Y-%m-%d')
            elif period == 'weekly':
                key = f"{date.year}-W{date.strftime('%W')}"
            elif period == 'monthly':
                key = date.strftime('%Y-%m')
            else:  # yearly
                key = str(date.year)
            
            data_by_period[key] = data_by_period.get(key, 0) + exp['amount']
        
        sorted_data = sorted(data_by_period.items())
        
        if not sorted_data:
            print("📭 No data for this period")
            self.wait_for_enter()
            return
        
        print("\n📊 EXPENSE TREND")
        print("=" * 70)
        
        periods = [item[0] for item in sorted_data]
        amounts = [item[1] for item in sorted_data]
        
        total = sum(amounts)
        average = total / len(amounts) if amounts else 0
        highest = max(amounts) if amounts else 0
        lowest = min(amounts) if amounts else 0
        
        print(f"\nPeriod: {period}")
        print(f"Total Expenses: {format_currency(Decimal(total))}")
        print(f"Average: {format_currency(Decimal(average))}")
        print(f"Highest: {format_currency(Decimal(highest))}")
        print(f"Lowest: {format_currency(Decimal(lowest))}")
        
        print("\n📈 Trend:")
        for i, (period_label, amount) in enumerate(sorted_data[:20]):  # Show last 20
            bar_length = int((amount / highest) * 30) if highest > 0 else 0
            bar = f"{'█' * bar_length}"
            print(f"  {period_label:12} {format_currency(Decimal(amount)):>15} {bar}")
        
        if len(sorted_data) > 20:
            print(f"  ... and {len(sorted_data) - 20} more periods")
        
        # Trend analysis
        if len(amounts) > 1:
            trend = amounts[-1] - amounts[0]
            if trend > 0:
                print(f"\n📈 Trend: Increasing (+{format_currency(Decimal(trend))})")
            elif trend < 0:
                print(f"\n📉 Trend: Decreasing ({format_currency(Decimal(trend))})")
            else:
                print("\n➡️ Trend: Stable")
        
        self.wait_for_enter()

    def category_comparison(self):
        """Show category comparison"""
        self.display_header("CATEGORY COMPARISON")
        
        expenses = self.expense_service.get_expense_history()
        
        if not expenses:
            print("📭 No data available")
            self.wait_for_enter()
            return
        
        # Group by category
        breakdown = {}
        for exp in expenses:
            breakdown[exp['category']] = breakdown.get(exp['category'], 0) + exp['amount']
        
        breakdown_list = [{'category': k, 'total': v} for k, v in breakdown.items()]
        breakdown_list.sort(key=lambda x: x['total'], reverse=True)
        
        total = sum(item['total'] for item in breakdown_list)
        
        print("\n📊 CATEGORY BREAKDOWN")
        print("=" * 70)
        print(f"Total Expenses: {format_currency(Decimal(total))}")
        print(f"Categories: {len(breakdown_list)}")
        print("-" * 70)
        
        for item in breakdown_list:
            pct = (item['total'] / total * 100) if total > 0 else 0
            bar_length = int((item['total'] / total) * 30) if total > 0 else 0
            bar = f"{'█' * bar_length}"
            print(f"  {item['category']:20} {format_currency(Decimal(item['total'])):>15} ({pct:>5.1f}%) {bar}")
        
        self.wait_for_enter()

    def monthly_comparison(self):
        """Compare months"""
        self.display_header("MONTHLY COMPARISON")
        
        year = input(f"Year to compare [{self.current_year}]: ").strip()
        year = int(year) if year.isdigit() else self.current_year
        
        months = {}
        for m in range(1, 13):
            month_name = get_month_name(m)
            expenses = self.expense_service.get_expense_history({'month': m, 'year': year})
            total = sum(e['amount'] for e in expenses)
            income = self.get_total_income(m, year)
            net = income - total
            months[m] = {'month': month_name, 'expense': total, 'income': income, 'net': net}
        
        print(f"\n📊 {year} MONTHLY COMPARISON")
        print("=" * 80)
        print(f"{'Month':12} {'Expense':>15} {'Income':>15} {'Net Balance':>15} {'Status':>10}")
        print("-" * 80)
        
        total_expense = 0
        total_income = 0
        
        for m in range(1, 13):
            data = months[m]
            total_expense += data['expense']
            total_income += data['income']
            status = "✅" if data['net'] >= 0 else "❌"
            print(
                f"{data['month']:12} "
                f"{format_currency(Decimal(data['expense'])):>15} "
                f"{format_currency(Decimal(data['income'])):>15} "
                f"{format_currency(Decimal(data['net'])):>15} "
                f"{status:>10}"
            )
        
        print("-" * 80)
        net_total = total_income - total_expense
        status = "✅ SURPLUS" if net_total >= 0 else "❌ DEFICIT"
        print(
            f"{'TOTAL':12} "
            f"{format_currency(Decimal(total_expense)):>15} "
            f"{format_currency(Decimal(total_income)):>15} "
            f"{format_currency(Decimal(net_total)):>15} "
            f"{status:>10}"
        )
        print("=" * 80)
        
        self.wait_for_enter()

    # ============================================================
    # ENHANCED EXPENSE INPUT
    # ============================================================

    def input_expense(self):
        """Add a new expense entry with enhanced features"""
        self.display_header("ADD NEW EXPENSE")

        try:
            # Input date
            while True:
                date_input = input("📅 Date (YYYY-MM-DD) [leave blank for today]: ").strip()
                if not date_input:
                    date_input = datetime.now().strftime("%Y-%m-%d")
                    break
                elif validate_date(date_input):
                    break
                else:
                    print("❌ Invalid date format. Use YYYY-MM-DD")

            # Select category
            categories = self.expense_service.get_categories()
            print("\n📂 Select Category:")
            for i, category in enumerate(categories, 1):
                print(f" {i}. {format_category(category)}")

            while True:
                try:
                    cat_choice = int(input(f"\nSelect category (1-{len(categories)}): "))
                    if 1 <= cat_choice <= len(categories):
                        category = categories[cat_choice - 1]
                        break
                    else:
                        print("❌ Invalid selection")
                except ValueError:
                    print("❌ Please enter a number")

            # Input amount
            while True:
                amount_input = input("💵 Expense Amount: Rp ").strip()
                if validate_amount(amount_input):
                    amount = parse_amount(amount_input)
                    if amount > 0:
                        break
                    else:
                        print("❌ Amount must be greater than 0")
                else:
                    print("❌ Invalid amount")

            # Payment method
            print("\n💳 Payment Method:")
            payment_options = ['Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 'E-Wallet', 'Other']
            for i, method in enumerate(payment_options, 1):
                print(f" {i}. {method}")
            
            pm_choice = input(f"Select payment method (1-{len(payment_options)}): ").strip()
            if pm_choice.isdigit() and 1 <= int(pm_choice) <= len(payment_options):
                payment_method = payment_options[int(pm_choice) - 1]
            else:
                payment_method = 'Cash'

            # Input description
            description = input("📝 Description (optional): ").strip()

            # Tags input
            tags_input = input("🏷️ Tags (comma separated, optional): ").strip()
            tags = [t.strip() for t in tags_input.split(',') if t.strip()] if tags_input else []

            # Confirm entry
            print("\n📋 Expense Summary:")
            print(f"   Date        : {format_date(date_input)}")
            print(f"   Category    : {format_category(category)}")
            print(f"   Amount      : {format_currency(amount)}")
            print(f"   Payment     : {payment_method}")
            print(f"   Description : {description or '-'}")
            print(f"   Tags        : {', '.join(tags) if tags else '-'}")

            confirm = input("\n✅ Save this expense? (y/n): ").lower()

            if confirm == "y":
                conn = sqlite3.connect('expense_tracker.db')
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO expenses (date, category, amount, description, payment_method) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (date_input, category, float(amount), description, payment_method)
                )
                expense_id = cursor.lastrowid
                
                # Add tags
                for tag in tags:
                    cursor.execute(
                        "INSERT INTO expense_tags (expense_id, tag) VALUES (?, ?)",
                        (expense_id, tag)
                    )
                
                conn.commit()
                conn.close()
                print(f"✅ Expense added successfully!")
            else:
                print("❌ Expense entry cancelled")

        except KeyboardInterrupt:
            print("\n\n❌ Input cancelled")
        except Exception as e:
            print(f"❌ Error: {e}")

        self.wait_for_enter()

    # ============================================================
    # ENHANCED VIEW HISTORY
    # ============================================================

    def view_history(self):
        """View expense history with All Time filter support and tags"""
        self.display_header("EXPENSE HISTORY")

        try:
            filters = self.get_filters_from_user()
            if filters is None:
                return

            # Get expenses with filters
            expenses = self.expense_service.get_expense_history(filters)

            if not expenses:
                print("\n📭 No expense data found")
                self.wait_for_enter()
                return

            # Display summary
            total = sum(expense["amount"] for expense in expenses)
            total_income = self.get_total_income(
                filters.get('year'), 
                filters.get('month'), 
                not filters.get('year') and not filters.get('month')
            )
            net_balance = total_income - total
            
            all_time = not filters.get("year") and not filters.get("month")

            if all_time:
                print(f"\n📊 ALL TIME - Total {len(expenses)} transactions")
                print(f"   Total Expense: {format_currency(Decimal(total))}")
                print(f"   Total Income : {format_currency(Decimal(total_income))}")
                print(f"   Net Balance  : {format_currency(Decimal(net_balance))}")
                print(f"   Period       : {expenses[-1]['date']} to {expenses[0]['date']}")
            else:
                year = filters.get("year", self.current_year)
                month = filters.get("month", self.current_month)
                print(f"\n📊 {get_month_name(month)} {year} - Total {len(expenses)} transactions")
                print(f"   Total Expense: {format_currency(Decimal(total))}")
                print(f"   Total Income : {format_currency(Decimal(total_income))}")
                print(f"   Net Balance  : {format_currency(Decimal(net_balance))}")
                if filters.get("category"):
                    print(f"   Category     : {filters['category']}")

            print("\n" + "-" * 95)
            print(f"{'ID':>4} {'Date':12} {'Category':18} {'Amount':>13} {'Payment':12} {'Description':20} {'Tags':10}")
            print("-" * 95)

            for expense in expenses[:50]:  # Show last 50
                tags = self.get_expense_tags(expense['id'])
                tag_str = ', '.join(tags[:2]) + ('...' if len(tags) > 2 else '') if tags else ''
                print(
                    f"{expense['id']:>4} "
                    f"{format_date(expense['date']):12} "
                    f"{format_category(expense['category']):18} "
                    f"{format_currency(Decimal(expense['amount'])):>13} "
                    f"{expense.get('payment_method', 'Cash'):12} "
                    f"{expense['description'][:18]:20} "
                    f"{tag_str:10}"
                )

            if len(expenses) > 50:
                print(f"\n... and {len(expenses) - 50} more transactions")

            print("-" * 95)
            print(f"Total: {format_currency(Decimal(total)):>13}")
            print("-" * 95)

            # Export option
            export = input("\n📤 Export to file? (y/n): ").lower()

            if export == "y":
                format_choice = input("Format (1-CSV, 2-Excel): ").strip()

                if format_choice == "1":
                    filepath = self.export_service.export_to_csv(expenses)
                    print(f"✅ Data exported to: {filepath}")
                elif format_choice == "2":
                    filepath = self.export_service.export_to_excel(expenses)
                    print(f"✅ Data exported to: {filepath}")

        except Exception as e:
            print(f"❌ Error: {e}")

        self.wait_for_enter()

    # ============================================================
    # ENHANCED SUMMARY
    # ============================================================

    def monthly_summary(self):
        """Display monthly summary with All Time support and income"""
        self.display_header("SUMMARY")

        print("\n📊 Select summary type:")
        print("1. All Time (all data)")
        print("2. Specific month")
        print("3. Yearly Summary")
        print("4. Back")

        choice = input("\nSelect (1-4): ").strip()

        try:
            if choice == "1":
                self.show_all_time_summary()
            elif choice == "2":
                self.show_monthly_summary_detail()
            elif choice == "3":
                self.show_yearly_summary()
            elif choice == "4":
                return
            else:
                print("❌ Invalid selection")
                self.wait_for_enter()

        except Exception as e:
            print(f"❌ Error: {e}")

        self.wait_for_enter()

    def show_all_time_summary(self):
        """Show all time summary with income"""
        expenses = self.expense_service.get_expense_history()
        if not expenses:
            print("\n📭 No data available")
            return

        total_expense = sum(e['amount'] for e in expenses)
        total_income = self.get_total_income(all_time=True)
        net_balance = total_income - total_expense
        
        breakdown = {}
        for e in expenses:
            breakdown[e['category']] = breakdown.get(e['category'], 0) + e['amount']
        breakdown_list = [{'category': k, 'total': v} for k, v in breakdown.items()]
        breakdown_list.sort(key=lambda x: x['total'], reverse=True)

        print(f"\n📊 ALL TIME SUMMARY")
        print("=" * 50)
        print(f"Total Expense  : {format_currency(Decimal(total_expense))}")
        print(f"Total Income   : {format_currency(Decimal(total_income))}")
        print(f"Net Balance    : {format_currency(Decimal(net_balance))}")
        print(f"Transactions   : {len(expenses)}")
        print(f"Categories     : {len(breakdown_list)}")
        print(f"Period         : {expenses[-1]['date']} to {expenses[0]['date']}")
        print("=" * 50)

        print("\n📂 Category Breakdown:")
        print("-" * 50)
        for item in breakdown_list:
            pct = (item['total'] / total_expense * 100) if total_expense > 0 else 0
            bar = f"{'█' * int(pct / 100 * 20)}"
            print(
                f"{format_category(item['category']):25} "
                f"{format_currency(Decimal(item['total'])):15} "
                f"({pct:>5.1f}%) {bar}"
            )

        # Export report option
        export_report = input("\n📤 Export full report? (y/n): ").lower()
        if export_report == "y":
            filepath = self.export_service.export_to_csv(expenses)
            print(f"✅ Data exported to: {filepath}")

    def show_monthly_summary_detail(self):
        """Show monthly summary with income"""
        year = input(f"Year [{self.current_year}]: ").strip()
        month = input(f"Month (1-12) [{self.current_month}]: ").strip()

        year = int(year) if year.isdigit() else self.current_year
        month = int(month) if month.isdigit() and 1 <= int(month) <= 12 else self.current_month

        analysis = self.expense_service.get_monthly_analysis(year, month)
        total_income = self.get_total_income(month, year)
        net_balance = total_income - analysis['total_expenses']

        print(f"\n📊 {get_month_name(month)} {year} Expense Summary")
        print("=" * 50)
        print(f"Total Expenses: {format_currency(Decimal(analysis['total_expenses']))}")
        print(f"Total Income  : {format_currency(Decimal(total_income))}")
        print(f"Net Balance   : {format_currency(Decimal(net_balance))}")
        print(f"Categories    : {len(analysis['category_breakdown'])}")

        print("\n📂 Category Breakdown:")
        print("-" * 50)

        for item in analysis["category_breakdown"]:
            percentage = item.get("percentage", 0)
            bar = f"{'█' * int(percentage / 100 * 20)}"
            print(
                f"{format_category(item['category']):25} "
                f"{format_currency(Decimal(item['total'])):15} "
                f"({percentage:>5.1f}%) {bar}"
            )

        # Generate chart option
        generate_chart = input("\n📈 Generate pie chart? (y/n): ").lower()
        if generate_chart == "y":
            try:
                chart_path = self.chart_service.generate_pie_chart(
                    analysis["category_breakdown"], month, year
                )
                print(f"✅ Chart saved to: {chart_path}")
            except Exception as e:
                print(f"❌ Error generating chart: {e}")

        # Export report option
        export_report = input("\n📤 Export full report? (y/n): ").lower()
        if export_report == "y":
            expenses = self.expense_service.get_expense_history(
                {"year": year, "month": month}
            )
            filepath = self.export_service.export_monthly_report(analysis, expenses)
            print(f"✅ Report exported to: {filepath}")

    def show_yearly_summary(self):
        """Show yearly summary"""
        year = input(f"Year [{self.current_year}]: ").strip()
        year = int(year) if year.isdigit() else self.current_year

        print(f"\n📊 {year} YEARLY SUMMARY")
        print("=" * 60)
        print(f"{'Month':12} {'Expense':>15} {'Income':>15} {'Net':>15} {'Status':>10}")
        print("-" * 60)

        total_expense = 0
        total_income = 0

        for m in range(1, 13):
            expenses = self.expense_service.get_expense_history({'month': m, 'year': year})
            month_expense = sum(e['amount'] for e in expenses)
            month_income = self.get_total_income(m, year)
            net = month_income - month_expense
            total_expense += month_expense
            total_income += month_income
            status = "✅" if net >= 0 else "❌"
            
            print(
                f"{get_month_name(m):12} "
                f"{format_currency(Decimal(month_expense)):>15} "
                f"{format_currency(Decimal(month_income)):>15} "
                f"{format_currency(Decimal(net)):>15} "
                f"{status:>10}"
            )

        print("-" * 60)
        net_total = total_income - total_expense
        status = "✅ SURPLUS" if net_total >= 0 else "❌ DEFICIT"
        print(
            f"{'TOTAL':12} "
            f"{format_currency(Decimal(total_expense)):>15} "
            f"{format_currency(Decimal(total_income)):>15} "
            f"{format_currency(Decimal(net_total)):>15} "
            f"{status:>10}"
        )
        print("=" * 60)

    # ============================================================
    # MAIN MENU
    # ============================================================

    def main_menu(self):
        """Display and handle main menu with all features"""
        while True:
            self.display_header("MAIN MENU")

            print("📊 EXPENSE TRACKING")
            print("-" * 40)
            print("1. ➕ Add Expense")
            print("2. 📜 View History (with filters)")
            print("3. 📊 Summary (All Time / Monthly / Yearly)")
            print("4. 📈 Generate Chart")
            
            print("\n💰 FINANCE MANAGEMENT")
            print("-" * 40)
            print("5. 💵 Add Income")
            print("6. 📋 View Income")
            print("7. 🎯 Budget Management")
            print("8. 🔄 Recurring Expenses")
            
            print("\n📊 ANALYTICS & TOOLS")
            print("-" * 40)
            print("9. 📈 Advanced Analytics")
            print("10. 📤 Export Data")
            print("11. 💾 Backup & Restore")
            
            print("\n❌ EXIT")
            print("-" * 40)
            print("12. ❌ Exit")

            choice = input("\nSelect menu (1-12): ").strip()

            if choice == "1":
                self.input_expense()
            elif choice == "2":
                self.view_history()
            elif choice == "3":
                self.monthly_summary()
            elif choice == "4":
                self.generate_chart_menu()
            elif choice == "5":
                self.add_income()
            elif choice == "6":
                self.view_incomes()
            elif choice == "7":
                self.manage_budgets()
            elif choice == "8":
                self.manage_recurring()
            elif choice == "9":
                self.show_analytics()
            elif choice == "10":
                self.export_data_menu()
            elif choice == "11":
                self.backup_restore_menu()
            elif choice == "12":
                print("\n👋 Thank you for using Expense Tracker Pro!")
                break
            else:
                print("❌ Invalid selection")
                self.wait_for_enter()

    def backup_restore_menu(self):
        """Backup and restore menu"""
        self.display_header("BACKUP & RESTORE")
        
        print("1. 📤 Backup Database")
        print("2. 📥 Restore Database")
        print("3. 📋 Export All Data (JSON)")
        print("4. Back")
        
        choice = input("\nSelect (1-4): ").strip()
        
        if choice == "1":
            self.backup_data()
        elif choice == "2":
            self.restore_data()
        elif choice == "3":
            self.export_all_json()
        elif choice == "4":
            return
        else:
            print("❌ Invalid selection")
            self.wait_for_enter()

    def export_all_json(self):
        """Export all data as JSON"""
        self.display_header("EXPORT ALL DATA (JSON)")
        
        try:
            filename = f"expense_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            conn = sqlite3.connect('expense_tracker.db')
            cursor = conn.cursor()
            
            data = {
                'expenses': [],
                'incomes': [],
                'budgets': [],
                'recurring': [],
                'tags': [],
            }
            
            # Expenses
            cursor.execute("SELECT * FROM expenses")
            data['expenses'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Incomes
            cursor.execute("SELECT * FROM incomes")
            data['incomes'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Budgets
            cursor.execute("SELECT * FROM budgets")
            data['budgets'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Recurring
            cursor.execute("SELECT * FROM recurring_expenses")
            data['recurring'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Tags
            cursor.execute("SELECT * FROM expense_tags")
            data['tags'] = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            conn.close()
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"✅ Data exported to: {filename}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
        
        self.wait_for_enter()


def main():
    """Main entry point"""
    app = ExpenseTrackerApp()
    app.main_menu()


if __name__ == "__main__":
    main()