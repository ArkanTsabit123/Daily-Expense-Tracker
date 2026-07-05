# gui.py
"""
Daily Expense Tracker - Complete GUI
All Features: Dashboard + Budget Management + Income Tracking + Backup + Analytics + More
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font, filedialog, simpledialog
from datetime import datetime, timedelta
import os
import sys
import calendar
import json
import shutil
import sqlite3
from decimal import Decimal
from typing import List, Dict, Optional

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.database_service import DatabaseService
from services.expense_service import ExpenseService

# Database path constant
DB_PATH = "data/expenses.db"

# Try to import matplotlib
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use('TkAgg')
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Try to import pandas
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ExpenseTrackerGUI:
    """Complete GUI Application with All Features"""

    def __init__(self, root):
        """Initialize the GUI application"""
        self.root = root
        self.root.title("💰 Daily Expense Tracker Pro")
        self.root.geometry("1400x850")
        self.root.resizable(True, True)
        self.root.configure(bg='#0f0f23')

        # Initialize services
        self.db_service = DatabaseService()
        self.expense_service = ExpenseService(self.db_service)
        
        # Initialize database tables for new features
        self.init_additional_tables()

        # Current filter
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.filter_category = None
        
        # Sorting state
        self.sort_column = None
        self.sort_reverse = False
        self.current_expenses = []
        self.filtered_expenses = []
        
        # Data stores
        self.incomes = []
        self.budgets = {}
        self.recurring_expenses = []

        # Setup
        self.setup_fonts()
        self.build_ui()
        self.refresh_dashboard()
        self.load_budgets()
        self.load_incomes()
        self.load_recurring_expenses()

    def init_additional_tables(self):
        """Initialize additional database tables"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create expenses table FIRST if it doesn't exist
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
        
        # Create incomes table
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
        
        # Create budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                monthly_limit REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create recurring expenses table
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
        
        # Create tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (expense_id) REFERENCES expenses(id)
            )
        ''')
        
        # Now check if payment_method column exists in expenses table
        cursor.execute("PRAGMA table_info(expenses)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'payment_method' not in columns:
            try:
                cursor.execute("ALTER TABLE expenses ADD COLUMN payment_method TEXT DEFAULT 'Cash'")
            except sqlite3.OperationalError:
                pass  # Column might already exist
        
        conn.commit()
        conn.close()

    def setup_fonts(self):
        """Configure application fonts"""
        self.fonts = {
            'title': ('Segoe UI', 20, 'bold'),
            'subtitle': ('Segoe UI', 12),
            'button': ('Segoe UI', 10, 'bold'),
            'body': ('Segoe UI', 10),
            'heading': ('Segoe UI', 11, 'bold'),
            'stats': ('Segoe UI', 22, 'bold'),
            'number': ('Segoe UI', 18, 'bold'),
            'small': ('Segoe UI', 8)
        }

    def build_ui(self):
        """Build main user interface"""
        # Main container with notebook (tabs)
        self.main_container = tk.Frame(self.root, bg='#0f0f23')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Dashboard
        self.dashboard_tab = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(self.dashboard_tab, text="📊 Dashboard")
        self.build_dashboard_tab()
        
        # Tab 2: Budget Management
        self.budget_tab = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(self.budget_tab, text="💰 Budget")
        self.build_budget_tab()
        
        # Tab 3: Income Tracking
        self.income_tab = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(self.income_tab, text="💵 Income")
        self.build_income_tab()
        
        # Tab 4: Recurring Expenses
        self.recurring_tab = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(self.recurring_tab, text="🔄 Recurring")
        self.build_recurring_tab()
        
        # Tab 5: Analytics
        self.analytics_tab = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(self.analytics_tab, text="📈 Analytics")
        self.build_analytics_tab()
        
        # Tab 6: Settings
        self.settings_tab = tk.Frame(self.notebook, bg='#0f0f23')
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        self.build_settings_tab()

    # ============================================================
    # TAB 1: DASHBOARD
    # ============================================================

    def build_dashboard_tab(self):
        """Build the dashboard tab"""
        tab = self.dashboard_tab
        
        # Top bar with controls
        top_bar = tk.Frame(tab, bg='#1a1a2e', height=60)
        top_bar.pack(fill=tk.X, pady=(0, 10))
        top_bar.pack_propagate(False)
        
        title_label = tk.Label(
            top_bar,
            text="💰 Expense Dashboard",
            font=self.fonts['title'],
            bg='#1a1a2e',
            fg='#f39c12'
        )
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Controls
        control_frame = tk.Frame(top_bar, bg='#1a1a2e')
        control_frame.pack(side=tk.RIGHT, padx=15)
        
        # All Time Checkbox
        self.all_time_var = tk.IntVar(value=0)
        all_time_check = tk.Checkbutton(
            control_frame,
            text="📅 All Time",
            variable=self.all_time_var,
            command=self.refresh_dashboard,
            bg='#1a1a2e',
            fg='#ecf0f1',
            selectcolor='#1a1a2e',
            font=self.fonts['body']
        )
        all_time_check.pack(side=tk.LEFT, padx=10)
        
        # Month
        tk.Label(control_frame, text="Month:", font=self.fonts['body'], bg='#1a1a2e', fg='#bdc3c7').pack(side=tk.LEFT, padx=3)
        self.month_var = tk.StringVar(value=str(self.current_month))
        month_spin = tk.Spinbox(
            control_frame,
            from_=1, to=12,
            textvariable=self.month_var,
            width=3,
            font=self.fonts['body'],
            bg='#0f3460',
            fg='#ecf0f1',
            relief=tk.FLAT,
            command=self.refresh_dashboard
        )
        month_spin.pack(side=tk.LEFT, padx=3)
        
        # Year
        tk.Label(control_frame, text="Year:", font=self.fonts['body'], bg='#1a1a2e', fg='#bdc3c7').pack(side=tk.LEFT, padx=3)
        self.year_var = tk.StringVar(value=str(self.current_year))
        year_spin = tk.Spinbox(
            control_frame,
            from_=2020, to=2035,
            textvariable=self.year_var,
            width=5,
            font=self.fonts['body'],
            bg='#0f3460',
            fg='#ecf0f1',
            relief=tk.FLAT,
            command=self.refresh_dashboard
        )
        year_spin.pack(side=tk.LEFT, padx=3)
        
        # Category filter
        tk.Label(control_frame, text="Category:", font=self.fonts['body'], bg='#1a1a2e', fg='#bdc3c7').pack(side=tk.LEFT, padx=3)
        self.category_var = tk.StringVar(value="All")
        cat_dropdown = ttk.Combobox(
            control_frame,
            textvariable=self.category_var,
            values=['All', 'Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Health', 'Education', 'Other'],
            width=10,
            font=self.fonts['body']
        )
        cat_dropdown.pack(side=tk.LEFT, padx=3)
        cat_dropdown.bind('<<ComboboxSelected>>', lambda e: self.refresh_dashboard())
        
        # Stats cards
        stats_frame = tk.Frame(tab, bg='#0f0f23')
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        stats_data = [
            ("💰 Total Expense", "total", "#e74c3c"),
            ("💵 Total Income", "income", "#2ecc71"),
            ("💎 Net Balance", "balance", "#f39c12"),
            ("📊 Categories", "categories", "#3498db"),
            ("📈 Avg/Day", "avg", "#9b59b6"),
            ("🏆 Top Category", "top", "#e67e22"),
            ("📝 Transactions", "count", "#1abc9c")
        ]
        
        self.stats_labels = {}
        
        for i, (label, key, color) in enumerate(stats_data):
            card = tk.Frame(
                stats_frame,
                bg='#1a1a2e',
                relief=tk.FLAT,
                bd=0,
                highlightbackground=color,
                highlightthickness=2
            )
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=3, pady=3)
            
            tk.Label(
                card,
                text=label,
                font=self.fonts['subtitle'],
                bg='#1a1a2e',
                fg='#bdc3c7'
            ).pack(pady=(5, 0))
            
            value_label = tk.Label(
                card,
                text="Rp 0",
                font=self.fonts['stats'],
                bg='#1a1a2e',
                fg=color
            )
            value_label.pack(pady=(2, 5))
            self.stats_labels[key] = value_label
        
        # Main content: Chart + Table
        content_frame = tk.Frame(tab, bg='#0f0f23')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left: Chart
        chart_frame = tk.Frame(content_frame, bg='#1a1a2e')
        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        chart_header = tk.Frame(chart_frame, bg='#1a1a2e')
        chart_header.pack(fill=tk.X, pady=5)
        
        tk.Label(
            chart_header,
            text="📊 Expenses by Category",
            font=self.fonts['heading'],
            bg='#1a1a2e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT)
        
        self.chart_container = tk.Frame(chart_frame, bg='#1a1a2e')
        self.chart_container.pack(fill=tk.BOTH, expand=True)
        
        # Right: Table
        table_frame = tk.Frame(content_frame, bg='#1a1a2e')
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Table Header with Search
        table_header = tk.Frame(table_frame, bg='#1a1a2e')
        table_header.pack(fill=tk.X, pady=5)
        
        tk.Label(
            table_header,
            text="📜 Recent Expenses",
            font=self.fonts['heading'],
            bg='#1a1a2e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT)
        
        # Search Box
        search_frame = tk.Frame(table_header, bg='#1a1a2e')
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(
            search_frame,
            text="🔍",
            font=self.fonts['body'],
            bg='#1a1a2e',
            fg='#bdc3c7'
        ).pack(side=tk.LEFT, padx=2)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.apply_search())
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=self.fonts['body'],
            width=20,
            bg='#0f3460',
            fg='#ecf0f1',
            relief=tk.FLAT,
            insertbackground='#f39c12'
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        
        clear_search_btn = tk.Button(
            search_frame,
            text="✕",
            command=self.clear_search,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 8, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=5,
            pady=1
        )
        clear_search_btn.pack(side=tk.LEFT, padx=2)
        
        # Add & Edit buttons
        add_btn = tk.Button(
            table_header,
            text="➕ Add",
            command=self.open_add_expense,
            bg='#2ecc71',
            fg='white',
            font=self.fonts['small'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=10
        )
        add_btn.pack(side=tk.RIGHT, padx=2)
        
        edit_btn = tk.Button(
            table_header,
            text="✏️ Edit",
            command=self.open_edit_expense,
            bg='#f39c12',
            fg='white',
            font=self.fonts['small'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=10
        )
        edit_btn.pack(side=tk.RIGHT, padx=2)
        
        # Treeview with expanded columns
        columns = ('ID', 'Date', 'Category', 'Amount', 'Payment', 'Description', 'Tags')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=12,
            style='Custom.Treeview'
        )
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Custom.Treeview',
                        background='#0f3460',
                        foreground='#ecf0f1',
                        fieldbackground='#0f3460',
                        rowheight=28)
        style.configure('Custom.Treeview.Heading',
                        background='#1a1a2e',
                        foreground='#f39c12',
                        font=('Segoe UI', 10, 'bold'))
        
        for col in columns:
            self.tree.heading(col, text=col, anchor='center', 
                            command=lambda c=col: self.sort_by_column(c))
            widths = {'ID': 40, 'Date': 90, 'Category': 100, 'Amount': 110, 
                     'Payment': 100, 'Description': 130, 'Tags': 100}
            self.tree.column(col, width=widths.get(col, 100), anchor='center')
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind events
        self.tree.bind("<Double-1>", lambda e: self.open_edit_expense())
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
        
        # Right-click menu
        self.context_menu = tk.Menu(self.root, tearoff=0, bg='#1a1a2e', fg='#ecf0f1')
        self.context_menu.add_command(label="✏️ Edit", command=self.open_edit_expense)
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🏷️ Add Tag", command=self.add_tag_to_expense)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Bottom action bar
        action_frame = tk.Frame(tab, bg='#0f0f23')
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        actions = [
            ("➕ Add Expense", self.open_add_expense, '#2ecc71'),
            ("💵 Add Income", self.open_add_income, '#3498db'),
            ("✏️ Edit Expense", self.open_edit_expense, '#f39c12'),
            ("🗑️ Delete", self.delete_selected, '#e74c3c'),
            ("📤 Export CSV", self.export_data, '#1abc9c'),
            ("📤 Export Excel", self.export_excel, '#1abc9c'),
            ("📊 Summary", self.show_monthly_summary, '#9b59b6'),
            ("🔄 Refresh", self.refresh_dashboard, '#3498db'),
        ]
        
        for text, command, color in actions:
            btn = tk.Button(
                action_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=self.fonts['button'],
                padx=15,
                pady=6,
                relief=tk.FLAT,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=3)
        
        # Status bar
        status_frame = tk.Frame(tab, bg='#1a1a2e', height=28)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="✅ Ready",
            anchor='w',
            bg='#1a1a2e',
            fg='#bdc3c7',
            font=self.fonts['body'],
            padx=10
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.search_count_label = tk.Label(
            status_frame,
            text="",
            anchor='e',
            bg='#1a1a2e',
            fg='#f39c12',
            font=self.fonts['body'],
            padx=10
        )
        self.search_count_label.pack(side=tk.RIGHT)

    # ============================================================
    # TAB 2: BUDGET MANAGEMENT
    # ============================================================

    def build_budget_tab(self):
        """Build the budget management tab"""
        tab = self.budget_tab
        
        # Header
        header = tk.Frame(tab, bg='#0f0f23')
        header.pack(fill=tk.X, pady=10)
        
        tk.Label(
            header,
            text="💰 Budget Management",
            font=self.fonts['title'],
            bg='#0f0f23',
            fg='#f39c12'
        ).pack(side=tk.LEFT, padx=20)
        
        # Add budget button
        add_budget_btn = tk.Button(
            header,
            text="➕ Add Budget",
            command=self.open_add_budget,
            bg='#2ecc71',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        add_budget_btn.pack(side=tk.RIGHT, padx=20)
        
        # Budget list frame
        list_frame = tk.Frame(tab, bg='#1a1a2e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for budgets
        columns = ('Category', 'Monthly Limit', 'Current Spent', 'Remaining', 'Progress', 'Status')
        self.budget_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=15,
            style='Custom.Treeview'
        )
        
        for col in columns:
            self.budget_tree.heading(col, text=col, anchor='center')
            widths = {'Category': 150, 'Monthly Limit': 140, 'Current Spent': 140,
                     'Remaining': 140, 'Progress': 150, 'Status': 100}
            self.budget_tree.column(col, width=widths.get(col, 120), anchor='center')
        
        self.budget_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.budget_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.budget_tree.configure(yscrollcommand=scrollbar.set)
        
        # Budget action buttons
        action_frame = tk.Frame(tab, bg='#0f0f23')
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            action_frame,
            text="✏️ Edit Budget",
            command=self.open_edit_budget,
            bg='#f39c12',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            action_frame,
            text="🗑️ Delete Budget",
            command=self.delete_budget,
            bg='#e74c3c',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🔄 Refresh",
            command=self.load_budgets,
            bg='#3498db',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    # ============================================================
    # TAB 3: INCOME TRACKING
    # ============================================================

    def build_income_tab(self):
        """Build the income tracking tab"""
        tab = self.income_tab
        
        # Header
        header = tk.Frame(tab, bg='#0f0f23')
        header.pack(fill=tk.X, pady=10)
        
        tk.Label(
            header,
            text="💵 Income Tracking",
            font=self.fonts['title'],
            bg='#0f0f23',
            fg='#2ecc71'
        ).pack(side=tk.LEFT, padx=20)
        
        # Summary stats
        self.income_stats_frame = tk.Frame(header, bg='#0f0f23')
        self.income_stats_frame.pack(side=tk.RIGHT, padx=20)
        
        self.total_income_label = tk.Label(
            self.income_stats_frame,
            text="Total Income: Rp 0",
            font=self.fonts['heading'],
            bg='#0f0f23',
            fg='#2ecc71'
        )
        self.total_income_label.pack(side=tk.LEFT, padx=15)
        
        # Add income button
        add_income_btn = tk.Button(
            header,
            text="➕ Add Income",
            command=self.open_add_income,
            bg='#2ecc71',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        add_income_btn.pack(side=tk.RIGHT, padx=20)
        
        # Income list
        list_frame = tk.Frame(tab, bg='#1a1a2e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Date', 'Source', 'Amount', 'Description', 'Recurring')
        self.income_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=15,
            style='Custom.Treeview'
        )
        
        for col in columns:
            self.income_tree.heading(col, text=col, anchor='center')
            widths = {'ID': 50, 'Date': 100, 'Source': 150, 'Amount': 140,
                     'Description': 200, 'Recurring': 80}
            self.income_tree.column(col, width=widths.get(col, 120), anchor='center')
        
        self.income_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.income_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.income_tree.configure(yscrollcommand=scrollbar.set)
        
        # Income action buttons
        action_frame = tk.Frame(tab, bg='#0f0f23')
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            action_frame,
            text="✏️ Edit",
            command=self.open_edit_income,
            bg='#f39c12',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            action_frame,
            text="🗑️ Delete",
            command=self.delete_income,
            bg='#e74c3c',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🔄 Refresh",
            command=self.load_incomes,
            bg='#3498db',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    # ============================================================
    # TAB 4: RECURRING EXPENSES
    # ============================================================

    def build_recurring_tab(self):
        """Build the recurring expenses tab"""
        tab = self.recurring_tab
        
        # Header
        header = tk.Frame(tab, bg='#0f0f23')
        header.pack(fill=tk.X, pady=10)
        
        tk.Label(
            header,
            text="🔄 Recurring Expenses",
            font=self.fonts['title'],
            bg='#0f0f23',
            fg='#9b59b6'
        ).pack(side=tk.LEFT, padx=20)
        
        # Add recurring button
        add_recurring_btn = tk.Button(
            header,
            text="➕ Add Recurring",
            command=self.open_add_recurring,
            bg='#9b59b6',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        add_recurring_btn.pack(side=tk.RIGHT, padx=20)
        
        # Recurring list
        list_frame = tk.Frame(tab, bg='#1a1a2e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Category', 'Amount', 'Description', 'Frequency', 'Start Date', 'End Date', 'Active')
        self.recurring_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=15,
            style='Custom.Treeview'
        )
        
        for col in columns:
            self.recurring_tree.heading(col, text=col, anchor='center')
            widths = {'ID': 40, 'Category': 120, 'Amount': 120, 'Description': 150,
                     'Frequency': 100, 'Start Date': 100, 'End Date': 100, 'Active': 80}
            self.recurring_tree.column(col, width=widths.get(col, 100), anchor='center')
        
        self.recurring_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.recurring_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recurring_tree.configure(yscrollcommand=scrollbar.set)
        
        # Recurring action buttons
        action_frame = tk.Frame(tab, bg='#0f0f23')
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            action_frame,
            text="✏️ Edit",
            command=self.open_edit_recurring,
            bg='#f39c12',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            action_frame,
            text="🗑️ Delete",
            command=self.delete_recurring,
            bg='#e74c3c',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🔄 Toggle Active",
            command=self.toggle_recurring,
            bg='#3498db',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="⚡ Process Now",
            command=self.process_recurring_expenses,
            bg='#e67e22',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    # ============================================================
    # TAB 5: ANALYTICS
    # ============================================================

    def build_analytics_tab(self):
        """Build the analytics tab"""
        tab = self.analytics_tab
        
        # Header
        header = tk.Frame(tab, bg='#0f0f23')
        header.pack(fill=tk.X, pady=10)
        
        tk.Label(
            header,
            text="📈 Advanced Analytics",
            font=self.fonts['title'],
            bg='#0f0f23',
            fg='#3498db'
        ).pack(side=tk.LEFT, padx=20)
        
        # Analytics period selector
        period_frame = tk.Frame(header, bg='#0f0f23')
        period_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            period_frame,
            text="Period:",
            font=self.fonts['body'],
            bg='#0f0f23',
            fg='#bdc3c7'
        ).pack(side=tk.LEFT, padx=5)
        
        self.analytics_period_var = tk.StringVar(value="monthly")
        period_options = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        period_dropdown = ttk.Combobox(
            period_frame,
            textvariable=self.analytics_period_var,
            values=period_options,
            width=10,
            font=self.fonts['body']
        )
        period_dropdown.pack(side=tk.LEFT, padx=5)
        period_dropdown.bind('<<ComboboxSelected>>', lambda e: self.generate_analytics())
        
        tk.Button(
            period_frame,
            text="📊 Generate",
            command=self.generate_analytics,
            bg='#3498db',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=10)
        
        # Main analytics content
        content_frame = tk.Frame(tab, bg='#0f0f23')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Charts
        chart_container = tk.Frame(content_frame, bg='#1a1a2e')
        chart_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.analytics_chart_container = tk.Frame(chart_container, bg='#1a1a2e')
        self.analytics_chart_container.pack(fill=tk.BOTH, expand=True)
        
        # Right: Summary stats
        stats_container = tk.Frame(content_frame, bg='#1a1a2e', width=350)
        stats_container.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        stats_container.pack_propagate(False)
        
        # Scrolled text for stats
        self.analytics_stats = scrolledtext.ScrolledText(
            stats_container,
            bg='#0f3460',
            fg='#ecf0f1',
            font=self.fonts['body'],
            wrap=tk.WORD,
            padx=10,
            pady=10,
            height=20
        )
        self.analytics_stats.pack(fill=tk.BOTH, expand=True)

    # ============================================================
    # TAB 6: SETTINGS
    # ============================================================

    def build_settings_tab(self):
        """Build the settings tab"""
        tab = self.settings_tab
        
        # Backup section
        backup_frame = tk.Frame(tab, bg='#1a1a2e', padx=20, pady=20)
        backup_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(
            backup_frame,
            text="💾 Backup & Restore",
            font=self.fonts['heading'],
            bg='#1a1a2e',
            fg='#f39c12'
        ).pack(anchor='w', pady=5)
        
        backup_btn_frame = tk.Frame(backup_frame, bg='#1a1a2e')
        backup_btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            backup_btn_frame,
            text="📤 Backup Database",
            command=self.backup_database,
            bg='#2ecc71',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            backup_btn_frame,
            text="📥 Restore Database",
            command=self.restore_database,
            bg='#3498db',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            backup_btn_frame,
            text="📋 Export All Data (JSON)",
            command=self.export_all_data_json,
            bg='#9b59b6',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        # CSV Import section
        import_frame = tk.Frame(tab, bg='#1a1a2e', padx=20, pady=20)
        import_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(
            import_frame,
            text="📥 Import Data",
            font=self.fonts['heading'],
            bg='#1a1a2e',
            fg='#f39c12'
        ).pack(anchor='w', pady=5)
        
        import_btn_frame = tk.Frame(import_frame, bg='#1a1a2e')
        import_btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            import_btn_frame,
            text="📄 Import CSV",
            command=self.import_csv_data,
            bg='#1abc9c',
            fg='white',
            font=self.fonts['button'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        # App info
        info_frame = tk.Frame(tab, bg='#1a1a2e', padx=20, pady=20)
        info_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(
            info_frame,
            text="ℹ️ Application Info",
            font=self.fonts['heading'],
            bg='#1a1a2e',
            fg='#f39c12'
        ).pack(anchor='w', pady=5)
        
        info_text = """
        📊 Daily Expense Tracker Pro v2.0
        
        Features:
        ✅ Expense Tracking with Categories
        ✅ Budget Management with Alerts
        ✅ Income Tracking
        ✅ Recurring Expenses
        ✅ Advanced Analytics
        ✅ Data Backup & Restore
        ✅ CSV Import/Export
        ✅ Excel Export
        ✅ Search & Filter
        ✅ Tags & Labels
        ✅ Payment Methods
        
        Database: SQLite
        Charts: Matplotlib
        Reports: Pandas
        """
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=self.fonts['body'],
            bg='#1a1a2e',
            fg='#bdc3c7',
            justify=tk.LEFT
        )
        info_label.pack(anchor='w', pady=10)

    # ============================================================
    # INCOME FUNCTIONS
    # ============================================================

    def open_add_income(self):
        """Open add income dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("💵 Add Income")
        dialog.geometry("450x420")
        dialog.resizable(False, False)
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="💵 Add New Income",
            font=('Segoe UI', 18, 'bold'),
            bg='#1a1a2e',
            fg='#2ecc71'
        ).pack(pady=(15, 10))
        
        form = tk.Frame(dialog, bg='#16213e', padx=25, pady=15)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        entries = {}
        fields = [
            ("📅 Date (YYYY-MM-DD):", "date", datetime.now().strftime("%Y-%m-%d")),
            ("💵 Source:", "source", ""),
            ("💰 Amount:", "amount", ""),
            ("📝 Description:", "desc", ""),
            ("🔄 Recurring:", "recurring", "No"),
        ]
        
        for i, (label, key, default) in enumerate(fields):
            tk.Label(
                form,
                text=label,
                font=('Segoe UI', 11),
                bg='#16213e',
                fg='#ecf0f1'
            ).grid(row=i, column=0, padx=5, pady=8, sticky='w')
            
            if key == "recurring":
                entry = ttk.Combobox(
                    form,
                    values=['No', 'Yes'],
                    font=('Segoe UI', 11),
                    width=25
                )
                entry.set('No')
                entry.grid(row=i, column=1, padx=5, pady=8, sticky='w')
            else:
                entry = tk.Entry(
                    form,
                    font=('Segoe UI', 11),
                    width=27,
                    relief=tk.FLAT,
                    bg='#0f3460',
                    fg='#ecf0f1',
                    insertbackground='#2ecc71'
                )
                entry.insert(0, default)
                entry.grid(row=i, column=1, padx=5, pady=8, sticky='w')
            entries[key] = entry
        
        def submit():
            date_str = entries['date'].get().strip()
            source = entries['source'].get().strip()
            amount_str = entries['amount'].get().strip()
            desc = entries['desc'].get().strip()
            is_recurring = 1 if entries['recurring'].get() == 'Yes' else 0
            
            if not date_str or not source or not amount_str:
                messagebox.showerror("Error", "Date, Source, and Amount are required!")
                return
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount format!")
                return
            
            # Simpan ke database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO incomes (date, source, amount, description, is_recurring) 
                   VALUES (?, ?, ?, ?, ?)""",
                (date_str, source, amount, desc, is_recurring)
            )
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"✅ Income added successfully!\n{source}: Rp {amount:,.0f}")
            dialog.destroy()
            
            # Refresh semua tampilan
            self.load_incomes()
            self.refresh_dashboard()
            self.status_label.config(text=f"✅ Added income: {source} - Rp {amount:,.0f}")
        
        btn_frame = tk.Frame(dialog, bg='#1a1a2e')
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="💾 Save Income",
            command=submit,
            bg='#2ecc71',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            padx=40,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 12),
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)

    def get_total_income(self, month=None, year=None, all_time=False):
        """Get total income for period"""
        conn = sqlite3.connect(DB_PATH)
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

    def load_incomes(self):
        """Load and display incomes"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incomes ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()
        
        self.income_tree.delete(*self.income_tree.get_children())
        total = 0
        
        for row in rows:
            total += row[3]
            self.income_tree.insert('', tk.END, values=(
                row[0], row[1], row[2], f"Rp {row[3]:,.0f}", 
                row[4][:25] if row[4] else '', 'Yes' if row[5] else 'No'
            ))
        
        self.total_income_label.config(text=f"Total Income: Rp {total:,.0f}")
        return total

    def open_edit_income(self):
        """Edit selected income"""
        selected = self.income_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an income to edit")
            return
        
        values = self.income_tree.item(selected[0])['values']
        income_id = values[0]
        
        new_amount = simpledialog.askstring(
            "Edit Income",
            f"Enter new amount for income #{income_id}:",
            initialvalue=values[3].replace('Rp ', '').replace(',', '')
        )
        
        if new_amount:
            try:
                amount = float(new_amount)
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE incomes SET amount = ? WHERE id = ?", (amount, income_id))
                conn.commit()
                conn.close()
                self.load_incomes()
                self.refresh_dashboard()
                messagebox.showinfo("Success", "✅ Income updated!")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount!")

    def delete_income(self):
        """Delete selected income"""
        selected = self.income_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an income to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Delete selected income?"):
            return
        
        values = self.income_tree.item(selected[0])['values']
        income_id = values[0]
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM incomes WHERE id = ?", (income_id,))
        conn.commit()
        conn.close()
        
        self.load_incomes()
        self.refresh_dashboard()
        self.status_label.config(text=f"✅ Deleted income #{income_id}")

    # ============================================================
    # BUDGET FUNCTIONS
    # ============================================================

    def load_budgets(self):
        """Load and display budgets"""
        self.budget_tree.delete(*self.budget_tree.get_children())
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM budgets")
        rows = cursor.fetchall()
        conn.close()
        
        # Get current month expenses
        month = datetime.now().month
        year = datetime.now().year
        expenses = self.expense_service.get_expense_history({'month': month, 'year': year})
        
        # Calculate spent per category
        spent = {}
        for exp in expenses:
            spent[exp['category']] = spent.get(exp['category'], 0) + exp['amount']
        
        for row in rows:
            category = row[1]
            limit = row[2]
            current_spent = spent.get(category, 0)
            remaining = limit - current_spent
            progress = (current_spent / limit * 100) if limit > 0 else 0
            
            # Status
            if progress >= 100:
                status = "⚠️ Exceeded"
                status_color = '#e74c3c'
            elif progress >= 80:
                status = "⚠️ Near Limit"
                status_color = '#e67e22'
            else:
                status = "✅ On Track"
                status_color = '#2ecc71'
            
            # Create progress bar visual
            bar_length = 20
            filled = int(progress / 100 * bar_length)
            progress_bar = f"{'█' * filled}{'░' * (bar_length - filled)}"
            
            self.budget_tree.insert('', tk.END, values=(
                category,
                f"Rp {limit:,.0f}",
                f"Rp {current_spent:,.0f}",
                f"Rp {remaining:,.0f}",
                f"{progress_bar} {progress:.1f}%",
                status
            ), tags=(status_color,))
        
        # Color tags for status
        self.budget_tree.tag_configure('#2ecc71', foreground='#2ecc71')
        self.budget_tree.tag_configure('#e67e22', foreground='#e67e22')
        self.budget_tree.tag_configure('#e74c3c', foreground='#e74c3c')

    def open_add_budget(self):
        """Open add budget dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("💰 Add Budget")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="💰 Set Budget",
            font=('Segoe UI', 18, 'bold'),
            bg='#1a1a2e',
            fg='#f39c12'
        ).pack(pady=(15, 10))
        
        form = tk.Frame(dialog, bg='#16213e', padx=25, pady=15)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Category
        tk.Label(form, text="Category:", font=('Segoe UI', 11), bg='#16213e', fg='#ecf0f1').grid(row=0, column=0, padx=5, pady=8, sticky='w')
        category_entry = ttk.Combobox(
            form,
            values=['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Health', 'Education', 'Other'],
            font=('Segoe UI', 11),
            width=25
        )
        category_entry.set('Food')
        category_entry.grid(row=0, column=1, padx=5, pady=8, sticky='w')
        
        # Monthly Limit
        tk.Label(form, text="Monthly Limit (Rp):", font=('Segoe UI', 11), bg='#16213e', fg='#ecf0f1').grid(row=1, column=0, padx=5, pady=8, sticky='w')
        limit_entry = tk.Entry(form, font=('Segoe UI', 11), width=27, relief=tk.FLAT, bg='#0f3460', fg='#ecf0f1', insertbackground='#f39c12')
        limit_entry.grid(row=1, column=1, padx=5, pady=8, sticky='w')
        
        def submit():
            category = category_entry.get().strip()
            limit_str = limit_entry.get().strip()
            
            if not category or not limit_str:
                messagebox.showerror("Error", "All fields are required!")
                return
            
            try:
                limit = float(limit_str)
                if limit <= 0:
                    messagebox.showerror("Error", "Limit must be greater than 0!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid limit format!")
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if budget exists
            cursor.execute("SELECT id FROM budgets WHERE category = ?", (category,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("UPDATE budgets SET monthly_limit = ? WHERE category = ?", (limit, category))
                message = "Budget updated!"
            else:
                cursor.execute("INSERT INTO budgets (category, monthly_limit) VALUES (?, ?)", (category, limit))
                message = "Budget created!"
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"✅ {message}")
            dialog.destroy()
            self.load_budgets()
        
        btn_frame = tk.Frame(dialog, bg='#1a1a2e')
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="💾 Save",
            command=submit,
            bg='#2ecc71',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            padx=40,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 12),
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)

    def open_edit_budget(self):
        """Edit selected budget"""
        selected = self.budget_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a budget to edit")
            return
        
        values = self.budget_tree.item(selected[0])['values']
        category = values[0]
        current_limit = float(values[1].replace('Rp ', '').replace(',', ''))
        
        new_limit = simpledialog.askstring(
            "Edit Budget",
            f"Edit budget for {category}:",
            initialvalue=str(current_limit)
        )
        
        if new_limit:
            try:
                limit = float(new_limit)
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE budgets SET monthly_limit = ? WHERE category = ?", (limit, category))
                conn.commit()
                conn.close()
                self.load_budgets()
                messagebox.showinfo("Success", "✅ Budget updated!")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount!")

    def delete_budget(self):
        """Delete selected budget"""
        selected = self.budget_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a budget to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Delete this budget?"):
            return
        
        values = self.budget_tree.item(selected[0])['values']
        category = values[0]
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM budgets WHERE category = ?", (category,))
        conn.commit()
        conn.close()
        
        self.load_budgets()
        messagebox.showinfo("Success", "✅ Budget deleted!")

    # ============================================================
    # RECURRING EXPENSES FUNCTIONS
    # ============================================================

    def open_add_recurring(self):
        """Open add recurring expense dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔄 Add Recurring Expense")
        dialog.geometry("450x450")
        dialog.resizable(False, False)
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="🔄 Recurring Expense",
            font=('Segoe UI', 18, 'bold'),
            bg='#1a1a2e',
            fg='#9b59b6'
        ).pack(pady=(15, 10))
        
        form = tk.Frame(dialog, bg='#16213e', padx=25, pady=15)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        entries = {}
        fields = [
            ("📂 Category:", "category", "Food"),
            ("💰 Amount:", "amount", ""),
            ("📝 Description:", "desc", ""),
            ("📅 Start Date:", "start_date", datetime.now().strftime("%Y-%m-%d")),
            ("📅 End Date (optional):", "end_date", ""),
        ]
        
        for i, (label, key, default) in enumerate(fields):
            tk.Label(
                form,
                text=label,
                font=('Segoe UI', 11),
                bg='#16213e',
                fg='#ecf0f1'
            ).grid(row=i, column=0, padx=5, pady=8, sticky='w')
            
            if key == "category":
                entry = ttk.Combobox(
                    form,
                    values=['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Health', 'Education', 'Other'],
                    font=('Segoe UI', 11),
                    width=25
                )
                entry.set('Food')
                entry.grid(row=i, column=1, padx=5, pady=8, sticky='w')
            else:
                entry = tk.Entry(
                    form,
                    font=('Segoe UI', 11),
                    width=27,
                    relief=tk.FLAT,
                    bg='#0f3460',
                    fg='#ecf0f1',
                    insertbackground='#9b59b6'
                )
                entry.insert(0, default)
                entry.grid(row=i, column=1, padx=5, pady=8, sticky='w')
            entries[key] = entry
        
        # Frequency
        tk.Label(form, text="Frequency:", font=('Segoe UI', 11), bg='#16213e', fg='#ecf0f1').grid(row=5, column=0, padx=5, pady=8, sticky='w')
        frequency_var = tk.StringVar(value="monthly")
        frequency_dropdown = ttk.Combobox(
            form,
            textvariable=frequency_var,
            values=['daily', 'weekly', 'monthly', 'yearly'],
            font=('Segoe UI', 11),
            width=25
        )
        frequency_dropdown.grid(row=5, column=1, padx=5, pady=8, sticky='w')
        
        def submit():
            category = entries['category'].get().strip()
            amount_str = entries['amount'].get().strip()
            description = entries['desc'].get().strip()
            start_date = entries['start_date'].get().strip()
            end_date = entries['end_date'].get().strip()
            frequency = frequency_var.get()
            
            if not category or not amount_str or not start_date:
                messagebox.showerror("Error", "Category, Amount, and Start Date are required!")
                return
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount format!")
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO recurring_expenses 
                   (category, amount, description, frequency, start_date, end_date, active) 
                   VALUES (?, ?, ?, ?, ?, ?, 1)""",
                (category, amount, description, frequency, start_date, end_date if end_date else None)
            )
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "✅ Recurring expense added!")
            dialog.destroy()
            self.load_recurring_expenses()
        
        btn_frame = tk.Frame(dialog, bg='#1a1a2e')
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="💾 Save",
            command=submit,
            bg='#9b59b6',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            padx=40,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 12),
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)

    def load_recurring_expenses(self):
        """Load and display recurring expenses"""
        self.recurring_tree.delete(*self.recurring_tree.get_children())
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recurring_expenses ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            self.recurring_tree.insert('', tk.END, values=(
                row[0], row[1], f"Rp {row[2]:,.0f}", row[3][:20] if row[3] else '',
                row[4], row[5], row[6] if row[6] else 'Never', '✅' if row[7] else '❌'
            ))

    def open_edit_recurring(self):
        """Edit selected recurring expense"""
        selected = self.recurring_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a recurring expense to edit")
            return
        
        values = self.recurring_tree.item(selected[0])['values']
        recurring_id = values[0]
        
        new_amount = simpledialog.askstring(
            "Edit Recurring",
            f"Enter new amount for recurring #{recurring_id}:",
            initialvalue=values[2].replace('Rp ', '').replace(',', '')
        )
        
        if new_amount:
            try:
                amount = float(new_amount)
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE recurring_expenses SET amount = ? WHERE id = ?", (amount, recurring_id))
                conn.commit()
                conn.close()
                self.load_recurring_expenses()
                messagebox.showinfo("Success", "✅ Recurring expense updated!")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount!")

    def delete_recurring(self):
        """Delete selected recurring expense"""
        selected = self.recurring_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a recurring expense to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Delete this recurring expense?"):
            return
        
        values = self.recurring_tree.item(selected[0])['values']
        recurring_id = values[0]
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recurring_expenses WHERE id = ?", (recurring_id,))
        conn.commit()
        conn.close()
        
        self.load_recurring_expenses()
        messagebox.showinfo("Success", "✅ Recurring expense deleted!")

    def toggle_recurring(self):
        """Toggle active status of recurring expense"""
        selected = self.recurring_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a recurring expense to toggle")
            return
        
        values = self.recurring_tree.item(selected[0])['values']
        recurring_id = values[0]
        current_active = values[7] == '✅'
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE recurring_expenses SET active = ? WHERE id = ?", (0 if current_active else 1, recurring_id))
        conn.commit()
        conn.close()
        
        self.load_recurring_expenses()
        status = "activated" if not current_active else "deactivated"
        messagebox.showinfo("Success", f"✅ Recurring expense {status}!")

    def process_recurring_expenses(self):
        """Process all active recurring expenses"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all active recurring expenses
        cursor.execute("SELECT * FROM recurring_expenses WHERE active = 1")
        recurring = cursor.fetchall()
        
        count = 0
        today = datetime.now().strftime("%Y-%m-%d")
        
        for rec in recurring:
            # Simple logic: process all that are active
            category = rec[1]
            amount = rec[2]
            description = f"[Recurring] {rec[3]}" if rec[3] else f"[Recurring] {category}"
            
            # Add expense
            cursor.execute(
                "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
                (today, category, amount, description)
            )
            count += 1
        
        conn.commit()
        conn.close()
        
        if count > 0:
            messagebox.showinfo("Success", f"✅ {count} recurring expenses processed!")
            self.refresh_dashboard()
            self.load_budgets()
        else:
            messagebox.showinfo("Info", "No recurring expenses to process")

    # ============================================================
    # TAGS FUNCTIONS
    # ============================================================

    def get_expense_tags(self, expense_id):
        """Get tags for an expense"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT tag FROM expense_tags WHERE expense_id = ?", (expense_id,))
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def add_tag_to_expense(self):
        """Add tag to selected expense"""
        expense_id = self.get_selected_id()
        if expense_id is None:
            messagebox.showinfo("Info", "Please select an expense to tag")
            return
        
        tag = simpledialog.askstring("Add Tag", "Enter tag name:")
        if not tag:
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expense_tags (expense_id, tag) VALUES (?, ?)", (expense_id, tag))
        conn.commit()
        conn.close()
        
        self.refresh_dashboard()
        messagebox.showinfo("Success", f"✅ Tag '{tag}' added!")

    # ============================================================
    # EXPENSE CRUD
    # ============================================================

    def open_add_expense(self):
        """Open enhanced add expense dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Add Expense")
        dialog.geometry("500x480")
        dialog.resizable(False, False)
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="➕ Add New Expense",
            font=('Segoe UI', 18, 'bold'),
            bg='#1a1a2e',
            fg='#f39c12'
        ).pack(pady=(15, 10))
        
        form = tk.Frame(dialog, bg='#16213e', padx=25, pady=15)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        entries = {}
        fields = [
            ("📅 Date (YYYY-MM-DD):", "date", datetime.now().strftime("%Y-%m-%d")),
            ("📂 Category:", "category", "Food"),
            ("💰 Amount:", "amount", ""),
            ("💳 Payment Method:", "payment", "Cash"),
            ("📝 Description:", "desc", ""),
            ("🏷️ Tags (comma separated):", "tags", ""),
        ]
        
        for i, (label, key, default) in enumerate(fields):
            tk.Label(
                form,
                text=label,
                font=('Segoe UI', 11),
                bg='#16213e',
                fg='#ecf0f1'
            ).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            
            if key == "category":
                entry = ttk.Combobox(
                    form,
                    values=['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Health', 'Education', 'Other'],
                    font=('Segoe UI', 11),
                    width=25
                )
                entry.set('Food')
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            elif key == "payment":
                entry = ttk.Combobox(
                    form,
                    values=['Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 'E-Wallet', 'Other'],
                    font=('Segoe UI', 11),
                    width=25
                )
                entry.set('Cash')
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            else:
                entry = tk.Entry(
                    form,
                    font=('Segoe UI', 11),
                    width=27,
                    relief=tk.FLAT,
                    bg='#0f3460',
                    fg='#ecf0f1',
                    insertbackground='#f39c12'
                )
                entry.insert(0, default)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            entries[key] = entry
        
        def submit():
            date_str = entries['date'].get().strip()
            category = entries['category'].get().strip()
            amount_str = entries['amount'].get().strip()
            payment = entries['payment'].get().strip()
            desc = entries['desc'].get().strip()
            tags_str = entries['tags'].get().strip()
            
            if not date_str or not category or not amount_str:
                messagebox.showerror("Error", "Date, Category, and Amount are required!")
                return
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount format!")
                return
            
            # Create expense
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO expenses (date, category, amount, description, payment_method) 
                   VALUES (?, ?, ?, ?, ?)""",
                (date_str, category, amount, desc, payment)
            )
            expense_id = cursor.lastrowid
            conn.commit()
            
            # Add tags
            if tags_str:
                tags = [t.strip() for t in tags_str.split(',') if t.strip()]
                for tag in tags:
                    cursor.execute(
                        "INSERT INTO expense_tags (expense_id, tag) VALUES (?, ?)",
                        (expense_id, tag)
                    )
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "✅ Expense added successfully!")
            dialog.destroy()
            self.refresh_dashboard()
            self.load_budgets()
        
        btn_frame = tk.Frame(dialog, bg='#1a1a2e')
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="💾 Save",
            command=submit,
            bg='#2ecc71',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            padx=40,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 12),
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)

    def open_edit_expense(self):
        """Open edit expense dialog"""
        expense_id = self.get_selected_id()
        if expense_id is None:
            messagebox.showinfo("Info", "Please select an expense to edit")
            return
        
        # Get expense data
        expenses = self.expense_service.get_expense_history()
        expense = next((e for e in expenses if e['id'] == expense_id), None)
        if not expense:
            messagebox.showerror("Error", "Expense not found")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Edit Expense")
        dialog.geometry("500x480")
        dialog.resizable(False, False)
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="✏️ Edit Expense",
            font=('Segoe UI', 18, 'bold'),
            bg='#1a1a2e',
            fg='#f39c12'
        ).pack(pady=(15, 10))
        
        form = tk.Frame(dialog, bg='#16213e', padx=25, pady=15)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        entries = {}
        fields = [
            ("📅 Date (YYYY-MM-DD):", "date", expense['date']),
            ("📂 Category:", "category", expense['category']),
            ("💰 Amount:", "amount", str(expense['amount'])),
            ("💳 Payment Method:", "payment", expense.get('payment_method', 'Cash')),
            ("📝 Description:", "desc", expense.get('description', '')),
            ("🏷️ Tags (comma separated):", "tags", ', '.join(self.get_expense_tags(expense_id))),
        ]
        
        for i, (label, key, default) in enumerate(fields):
            tk.Label(
                form,
                text=label,
                font=('Segoe UI', 11),
                bg='#16213e',
                fg='#ecf0f1'
            ).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            
            if key == "category":
                entry = ttk.Combobox(
                    form,
                    values=['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Health', 'Education', 'Other'],
                    font=('Segoe UI', 11),
                    width=25
                )
                entry.set(default)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            elif key == "payment":
                entry = ttk.Combobox(
                    form,
                    values=['Cash', 'Credit Card', 'Debit Card', 'Bank Transfer', 'E-Wallet', 'Other'],
                    font=('Segoe UI', 11),
                    width=25
                )
                entry.set(default)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            else:
                entry = tk.Entry(
                    form,
                    font=('Segoe UI', 11),
                    width=27,
                    relief=tk.FLAT,
                    bg='#0f3460',
                    fg='#ecf0f1',
                    insertbackground='#f39c12'
                )
                entry.insert(0, default)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            entries[key] = entry
        
        def submit():
            date_str = entries['date'].get().strip()
            category = entries['category'].get().strip()
            amount_str = entries['amount'].get().strip()
            payment = entries['payment'].get().strip()
            desc = entries['desc'].get().strip()
            tags_str = entries['tags'].get().strip()
            
            if not date_str or not category or not amount_str:
                messagebox.showerror("Error", "Date, Category, and Amount are required!")
                return
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount format!")
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Update expense
            cursor.execute(
                """UPDATE expenses 
                   SET date = ?, category = ?, amount = ?, description = ?, payment_method = ?
                   WHERE id = ?""",
                (date_str, category, amount, desc, payment, expense_id)
            )
            
            # Update tags
            cursor.execute("DELETE FROM expense_tags WHERE expense_id = ?", (expense_id,))
            
            if tags_str:
                tags = [t.strip() for t in tags_str.split(',') if t.strip()]
                for tag in tags:
                    cursor.execute(
                        "INSERT INTO expense_tags (expense_id, tag) VALUES (?, ?)",
                        (expense_id, tag)
                    )
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "✅ Expense updated!")
            dialog.destroy()
            self.refresh_dashboard()
            self.load_budgets()
        
        btn_frame = tk.Frame(dialog, bg='#1a1a2e')
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="💾 Update",
            command=submit,
            bg='#f39c12',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            padx=40,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 12),
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)

    def delete_selected(self):
        """Delete selected expense"""
        expense_id = self.get_selected_id()
        if expense_id is None:
            messagebox.showinfo("Info", "Please select an expense to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", f"Delete expense #{expense_id}?"):
            return
        
        # Delete tags first
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expense_tags WHERE expense_id = ?", (expense_id,))
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()
        
        self.status_label.config(text=f"✅ Deleted expense #{expense_id}")
        self.refresh_dashboard()
        self.load_budgets()

    def get_selected_id(self):
        """Get selected expense ID from treeview"""
        selected = self.tree.selection()
        if selected:
            return int(self.tree.item(selected[0])['values'][0])
        return None

    def show_context_menu(self, event):
        """Show right-click context menu"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    # ============================================================
    # SEARCH & SORT FUNCTIONS
    # ============================================================

    def apply_search(self):
        """Apply search filter"""
        search_term = self.search_var.get().strip().lower()
        
        if not search_term:
            self.filtered_expenses = self.current_expenses.copy()
            self.search_count_label.config(text="")
        else:
            self.filtered_expenses = []
            for exp in self.current_expenses:
                searchable_fields = [
                    str(exp.get('id', '')),
                    exp.get('date', ''),
                    exp.get('category', ''),
                    str(exp.get('amount', '')),
                    exp.get('description', '').lower(),
                    exp.get('payment_method', '').lower()
                ]
                
                formatted_amount = f"Rp {exp.get('amount', 0):,.0f}".lower()
                searchable_fields.append(formatted_amount)
                
                tags = self.get_expense_tags(exp['id'])
                searchable_fields.extend([t.lower() for t in tags])
                
                if any(search_term in field for field in searchable_fields if field):
                    self.filtered_expenses.append(exp)
            
            count = len(self.filtered_expenses)
            total = len(self.current_expenses)
            if count == 0:
                self.search_count_label.config(text="🔍 No results found", fg='#e74c3c')
            else:
                self.search_count_label.config(text=f"🔍 {count} of {total} found", fg='#2ecc71')
        
        self.populate_treeview(self.filtered_expenses)

    def clear_search(self):
        """Clear search box"""
        self.search_var.set("")
        self.search_count_label.config(text="")
        self.filtered_expenses = self.current_expenses.copy()
        self.populate_treeview(self.filtered_expenses)
        self.status_label.config(text="✅ Search cleared")

    def sort_by_column(self, column):
        """Sort treeview by column"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        items = [(self.tree.set(child, column), child) for child in self.tree.get_children('')]
        
        if column == 'Amount':
            items.sort(key=lambda x: float(x[0].replace('Rp ', '').replace(',', '')), reverse=self.sort_reverse)
        elif column == 'ID':
            items.sort(key=lambda x: int(x[0]), reverse=self.sort_reverse)
        else:
            items.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)

        for index, (_, child) in enumerate(items):
            self.tree.move(child, '', index)

        self.update_status()

    def update_status(self):
        """Update status bar"""
        sort_info = ""
        if self.sort_column:
            direction = "↑" if not self.sort_reverse else "↓"
            sort_info = f" | Sorted: {self.sort_column} {direction}"
            
        search_info = ""
        search_term = self.search_var.get().strip()
        if search_term:
            search_info = f" | Searching: '{search_term}'"
        
        self.status_label.config(text=f"✅ Ready{sort_info}{search_info}")

    # ============================================================
    # DASHBOARD REFRESH
    # ============================================================

    def refresh_dashboard(self):
        """Refresh all dashboard components"""
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            category = self.category_var.get()
            all_time = self.all_time_var.get() == 1

            if category == 'All':
                category = None
        except ValueError:
            month = self.current_month
            year = self.current_year
            all_time = False

        self.current_month = month
        self.current_year = year
        self.filter_category = category

        # Get expense data
        if all_time:
            filters = {}
            if category:
                filters['category'] = category
            expenses = self.expense_service.get_expense_history(filters)
        else:
            filters = {'month': month, 'year': year}
            if category:
                filters['category'] = category
            expenses = self.expense_service.get_expense_history(filters)

        # Store for sorting and searching
        self.current_expenses = expenses
        self.filtered_expenses = expenses.copy()

        # Calculate expense stats
        total_expense = sum(e['amount'] for e in expenses)
        categories = list(set(e['category'] for e in expenses))

        # Calculate total income
        total_income = self.get_total_income(month, year, all_time)
        
        # Calculate net balance
        net_balance = total_income - total_expense

        # Calculate average per day
        if expenses and not all_time:
            days = calendar.monthrange(year, month)[1]
            avg = total_expense / days if days > 0 else 0
        elif expenses and all_time:
            dates = [datetime.strptime(e['date'], '%Y-%m-%d') for e in expenses]
            if dates:
                min_date = min(dates)
                max_date = max(dates)
                days = (max_date - min_date).days + 1
                avg = total_expense / days if days > 0 else 0
            else:
                avg = 0
        else:
            avg = 0

        # Calculate category breakdown
        breakdown = {}
        for e in expenses:
            breakdown[e['category']] = breakdown.get(e['category'], 0) + e['amount']
        breakdown_list = [{'category': k, 'total': v} for k, v in breakdown.items()]
        breakdown_list.sort(key=lambda x: x['total'], reverse=True)
        top = breakdown_list[0] if breakdown_list else {'category': '-', 'total': 0}

        # Update stats labels
        self.stats_labels['total'].config(text=f"Rp {total_expense:,.0f}")
        self.stats_labels['income'].config(text=f"Rp {total_income:,.0f}")
        
        # Net balance with color
        balance_color = '#2ecc71' if net_balance >= 0 else '#e74c3c'
        self.stats_labels['balance'].config(text=f"Rp {net_balance:,.0f}", fg=balance_color)
        
        self.stats_labels['categories'].config(text=str(len(categories)))
        self.stats_labels['avg'].config(text=f"Rp {avg:,.0f}")
        self.stats_labels['top'].config(text=f"{top['category']} (Rp {top['total']:,.0f})" if top['category'] != '-' else '-')
        self.stats_labels['count'].config(text=str(len(expenses)))

        # Apply search if there's a search term
        search_term = self.search_var.get().strip()
        if search_term:
            self.apply_search()
        else:
            self.populate_treeview(expenses)
            self.search_count_label.config(text="")

        # Update chart
        self.update_chart(breakdown_list, month, year, all_time)

        # Update status
        self.update_status()

    def populate_treeview(self, expenses):
        """Populate treeview with expense data"""
        self.tree.delete(*self.tree.get_children())
        
        for exp in expenses[:50]:
            # Get tags for this expense
            tags = self.get_expense_tags(exp['id'])
            tag_str = ', '.join(tags) if tags else ''
            
            self.tree.insert('', tk.END, values=(
                exp['id'],
                exp['date'],
                exp['category'],
                f"Rp {exp['amount']:,.0f}",
                exp.get('payment_method', 'Cash'),
                exp.get('description', '')[:20],
                tag_str
            ))

        if self.sort_column and expenses:
            self.sort_by_column(self.sort_column)

    def update_chart(self, categories, month, year, all_time=False):
        """Update pie chart"""
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        if not MATPLOTLIB_AVAILABLE or not categories:
            label = tk.Label(
                self.chart_container,
                text="📭 No data\n\nAdd expenses to see chart!",
                font=self.fonts['body'],
                bg='#1a1a2e',
                fg='#bdc3c7'
            )
            label.pack(expand=True)
            return

        fig, ax = plt.subplots(figsize=(5, 4), facecolor='#1a1a2e')

        labels = [item['category'] for item in categories]
        sizes = [item['total'] for item in categories]
        colors = ['#2ecc71', '#3498db', '#9b59b6', '#e67e22', '#1abc9c', '#e74c3c', '#f39c12', '#2c3e50'][:len(labels)]

        if all_time:
            title = 'All Time Expenses'
        else:
            title = f'Expenses - {month:02d}/{year}'

        ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'color': 'white', 'fontsize': 9}
        )
        ax.set_title(title, color='white', fontsize=12)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ============================================================
    # EXPORT FUNCTIONS
    # ============================================================

    def export_data(self):
        """Export to CSV"""
        if not PANDAS_AVAILABLE:
            messagebox.showerror("Error", "Pandas not installed!")
            return
        
        expenses = self.expense_service.get_expense_history()
        if not expenses:
            messagebox.showinfo("Info", "No expenses to export")
            return
        
        # Add payment methods and tags to export
        for exp in expenses:
            exp['payment_method'] = exp.get('payment_method', 'Cash')
            tags = self.get_expense_tags(exp['id'])
            exp['tags'] = ', '.join(tags)
        
        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date'])
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"✅ Exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Export failed: {e}")

    def export_excel(self):
        """Export to Excel"""
        if not PANDAS_AVAILABLE:
            messagebox.showerror("Error", "Pandas not installed!")
            return
        
        expenses = self.expense_service.get_expense_history()
        if not expenses:
            messagebox.showinfo("Info", "No expenses to export")
            return
        
        # Add payment methods and tags
        for exp in expenses:
            exp['payment_method'] = exp.get('payment_method', 'Cash')
            tags = self.get_expense_tags(exp['id'])
            exp['tags'] = ', '.join(tags)
        
        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date'])
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if filename:
            try:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Expenses')
                    
                    # Add budgets sheet
                    conn = sqlite3.connect(DB_PATH)
                    budgets_df = pd.read_sql_query("SELECT * FROM budgets", conn)
                    budgets_df.to_excel(writer, index=False, sheet_name='Budgets')
                    conn.close()
                    
                    # Add incomes sheet
                    conn = sqlite3.connect(DB_PATH)
                    incomes_df = pd.read_sql_query("SELECT * FROM incomes", conn)
                    incomes_df.to_excel(writer, index=False, sheet_name='Incomes')
                    conn.close()
                
                messagebox.showinfo("Success", f"✅ Exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Export failed: {e}")

    def import_csv_data(self):
        """Import data from CSV"""
        if not PANDAS_AVAILABLE:
            messagebox.showerror("Error", "Pandas not installed!")
            return
        
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            df = pd.read_csv(filename)
            
            # Check required columns
            required = ['date', 'category', 'amount']
            if not all(col in df.columns for col in required):
                messagebox.showerror("Error", f"CSV must contain columns: {', '.join(required)}")
                return
            
            count = 0
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                try:
                    date = row['date']
                    category = row['category']
                    amount = float(row['amount'])
                    description = row.get('description', '')
                    payment_method = row.get('payment_method', 'Cash')
                    
                    cursor.execute(
                        """INSERT INTO expenses (date, category, amount, description, payment_method) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (date, category, amount, description, payment_method)
                    )
                    count += 1
                except Exception as e:
                    print(f"Error importing row: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"✅ {count} records imported successfully!")
            self.refresh_dashboard()
            self.load_budgets()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Import failed: {e}")

    # ============================================================
    # BACKUP & RESTORE FUNCTIONS
    # ============================================================

    def backup_database(self):
        """Backup the database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = "backups"
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backup_file = os.path.join(backup_dir, f"expense_backup_{timestamp}.db")
            shutil.copy2(DB_PATH, backup_file)
            
            messagebox.showinfo("Success", f"✅ Database backed up to:\n{backup_file}")
            self.status_label.config(text=f"📤 Backup created: {os.path.basename(backup_file)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Backup failed: {e}")

    def restore_database(self):
        """Restore database from backup"""
        filename = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        if not messagebox.askyesno(
            "Confirm Restore",
            "This will overwrite your current database!\nAre you sure?"
        ):
            return
        
        try:
            # Backup current database first
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = f"backups/pre_restore_backup_{timestamp}.db"
            shutil.copy2(DB_PATH, current_backup)
            
            # Restore from backup
            shutil.copy2(filename, DB_PATH)
            
            messagebox.showinfo("Success", "✅ Database restored successfully!")
            self.refresh_dashboard()
            self.load_budgets()
            self.load_incomes()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Restore failed: {e}")

    def export_all_data_json(self):
        """Export all data as JSON"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"expense_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if not filename:
                return
            
            # Export all data
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get all data
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
            
            # Write JSON
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            messagebox.showinfo("Success", f"✅ Data exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Export failed: {e}")

    # ============================================================
    # ANALYTICS FUNCTIONS
    # ============================================================

    def generate_analytics(self):
        """Generate advanced analytics"""
        for widget in self.analytics_chart_container.winfo_children():
            widget.destroy()
        
        period = self.analytics_period_var.get()
        
        # Get all expenses
        expenses = self.expense_service.get_expense_history()
        
        if not expenses:
            label = tk.Label(
                self.analytics_chart_container,
                text="📭 No data for analytics",
                font=self.fonts['body'],
                bg='#1a1a2e',
                fg='#bdc3c7'
            )
            label.pack(expand=True)
            self.analytics_stats.delete(1.0, tk.END)
            self.analytics_stats.insert(tk.END, "No data available")
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
            elif period == 'quarterly':
                quarter = (date.month - 1) // 3 + 1
                key = f"{date.year}-Q{quarter}"
            else:  # yearly
                key = str(date.year)
            
            if key not in data_by_period:
                data_by_period[key] = 0
            data_by_period[key] += exp['amount']
        
        # Sort by date
        sorted_data = sorted(data_by_period.items())
        
        if not sorted_data:
            label = tk.Label(
                self.analytics_chart_container,
                text="📭 No data for this period",
                font=self.fonts['body'],
                bg='#1a1a2e',
                fg='#bdc3c7'
            )
            label.pack(expand=True)
            return
        
        # Generate chart
        if MATPLOTLIB_AVAILABLE:
            fig, ax = plt.subplots(figsize=(6, 4), facecolor='#1a1a2e')
            
            periods = [item[0] for item in sorted_data]
            amounts = [item[1] for item in sorted_data]
            
            ax.plot(periods, amounts, marker='o', color='#2ecc71', linewidth=2, markersize=8)
            ax.fill_between(periods, amounts, alpha=0.3, color='#2ecc71')
            ax.set_title(f'Expense Trend ({period})', color='white', fontsize=12)
            ax.set_xlabel('Period', color='white', fontsize=10)
            ax.set_ylabel('Amount (Rp)', color='white', fontsize=10)
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.2, color='white')
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self.analytics_chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Update stats
        self.analytics_stats.delete(1.0, tk.END)
        stats_text = f"📊 ANALYTICS SUMMARY\n"
        stats_text += "=" * 40 + "\n\n"
        stats_text += f"Period: {period}\n"
        stats_text += f"Total Periods: {len(sorted_data)}\n"
        stats_text += f"Total Expenses: Rp {sum(amounts):,.0f}\n"
        
        if amounts:
            stats_text += f"Average per Period: Rp {sum(amounts)/len(amounts):,.0f}\n"
            stats_text += f"Highest: Rp {max(amounts):,.0f} ({sorted_data[amounts.index(max(amounts))][0]})\n"
            stats_text += f"Lowest: Rp {min(amounts):,.0f} ({sorted_data[amounts.index(min(amounts))][0]})\n"
            
            # Trend
            if len(amounts) > 1:
                trend = amounts[-1] - amounts[0]
                if trend > 0:
                    stats_text += f"\n📈 Trend: Increasing (+Rp {trend:,.0f})"
                elif trend < 0:
                    stats_text += f"\n📉 Trend: Decreasing (-Rp {abs(trend):,.0f})"
                else:
                    stats_text += f"\n➡️ Trend: Stable"
        
        self.analytics_stats.insert(tk.END, stats_text)

    def show_monthly_summary(self):
        """Show monthly summary dialog"""
        month = self.current_month
        year = self.current_year
        all_time = self.all_time_var.get() == 1
        
        if all_time:
            expenses = self.expense_service.get_expense_history()
            total = sum(e['amount'] for e in expenses)
            breakdown = {}
            for e in expenses:
                breakdown[e['category']] = breakdown.get(e['category'], 0) + e['amount']
            breakdown_list = [{'category': k, 'total': v} for k, v in breakdown.items()]
            breakdown_list.sort(key=lambda x: x['total'], reverse=True)
            
            total_income = self.get_total_income(all_time=True)
            net_balance = total_income - total

            msg = f"📊 ALL TIME SUMMARY\n"
            msg += "=" * 40 + "\n"
            msg += f"Total Expenses: Rp {total:,.0f}\n"
            msg += f"Total Income: Rp {total_income:,.0f}\n"
            msg += f"Net Balance: Rp {net_balance:,.0f}\n"
            msg += f"Categories: {len(breakdown_list)}\n"
            msg += f"Transactions: {len(expenses)}\n"
            msg += "-" * 40 + "\n"
            msg += "Category Breakdown:\n"
            for item in breakdown_list:
                pct = (item['total'] / total * 100) if total > 0 else 0
                msg += f"  {item['category']:<14} Rp {item['total']:>10,.0f} ({pct:>5.1f}%)\n"
        else:
            analysis = self.expense_service.get_monthly_analysis(year, month)
            total_income = self.get_total_income(month, year)
            net_balance = total_income - analysis['total_expenses']
            
            msg = f"📊 MONTHLY SUMMARY - {month:02d}/{year}\n"
            msg += "=" * 40 + "\n"
            msg += f"Total Expenses: Rp {analysis['total_expenses']:,.0f}\n"
            msg += f"Total Income: Rp {total_income:,.0f}\n"
            msg += f"Net Balance: Rp {net_balance:,.0f}\n"
            msg += f"Categories: {len(analysis['category_breakdown'])}\n"
            msg += "-" * 40 + "\n"
            msg += "Category Breakdown:\n"
            for item in analysis['category_breakdown']:
                pct = item.get('percentage', 0)
                msg += f"  {item['category']:<14} Rp {item['total']:>10,.0f} ({pct:>5.1f}%)\n"
        
        messagebox.showinfo("Summary", msg)


def main():
    """Run the GUI application"""
    root = tk.Tk()
    app = ExpenseTrackerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()