# dashboard.py
"""
Daily Expense Tracker - Dashboard Version
Modern interface with instant statistics and charts
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
from datetime import datetime
import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.database_service import DatabaseService
from services.expense_service import ExpenseService

# Try to import matplotlib for charts
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use('TkAgg')
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class DashboardApp:
    """Main Dashboard Application"""

    def __init__(self, root):
        """Initialize the dashboard application"""
        self.root = root
        self.root.title("💰 Expense Dashboard")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)
        self.root.configure(bg='#0f0f23')

        # Initialize services
        self.db_service = DatabaseService()
        self.expense_service = ExpenseService(self.db_service)

        # Current filter
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year

        # Setup
        self.setup_fonts()
        self.build_ui()
        self.refresh_dashboard()

    def setup_fonts(self):
        """Configure application fonts"""
        self.fonts = {
            'title': ('Segoe UI', 22, 'bold'),
            'subtitle': ('Segoe UI', 12),
            'button': ('Segoe UI', 10, 'bold'),
            'body': ('Segoe UI', 10),
            'heading': ('Segoe UI', 11, 'bold'),
            'stats': ('Segoe UI', 28, 'bold'),
            'small': ('Segoe UI', 9)
        }

    def build_ui(self):
        """Build dashboard user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#0f0f23')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ============================================================
        # TOP BAR
        # ============================================================
        top_bar = tk.Frame(main_frame, bg='#1a1a2e', height=70)
        top_bar.pack(fill=tk.X, pady=(0, 15))
        top_bar.pack_propagate(False)

        # Logo + Title
        title_label = tk.Label(
            top_bar,
            text="💰 Expense Dashboard",
            font=self.fonts['title'],
            bg='#1a1a2e',
            fg='#f39c12'
        )
        title_label.pack(side=tk.LEFT, padx=20)

        # Right side - Month selector
        control_frame = tk.Frame(top_bar, bg='#1a1a2e')
        control_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(
            control_frame,
            text="Month:",
            font=self.fonts['body'],
            bg='#1a1a2e',
            fg='#bdc3c7'
        ).pack(side=tk.LEFT, padx=5)

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
        month_spin.pack(side=tk.LEFT, padx=5)

        tk.Label(
            control_frame,
            text="Year:",
            font=self.fonts['body'],
            bg='#1a1a2e',
            fg='#bdc3c7'
        ).pack(side=tk.LEFT, padx=5)

        self.year_var = tk.StringVar(value=str(self.current_year))
        year_spin = tk.Spinbox(
            control_frame,
            from_=2020, to=2030,
            textvariable=self.year_var,
            width=5,
            font=self.fonts['body'],
            bg='#0f3460',
            fg='#ecf0f1',
            relief=tk.FLAT,
            command=self.refresh_dashboard
        )
        year_spin.pack(side=tk.LEFT, padx=5)

        # ============================================================
        # STATS CARDS
        # ============================================================
        stats_frame = tk.Frame(main_frame, bg='#0f0f23')
        stats_frame.pack(fill=tk.X, pady=(0, 15))

        stats_data = [
            ("💰 Total Expenses", "total", "#2ecc71"),
            ("📊 Categories", "categories", "#3498db"),
            ("📈 Avg per Day", "avg", "#9b59b6"),
            ("🏆 Top Category", "top", "#e67e22")
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
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)

            tk.Label(
                card,
                text=label,
                font=self.fonts['subtitle'],
                bg='#1a1a2e',
                fg='#bdc3c7'
            ).pack(pady=(10, 0))

            value_label = tk.Label(
                card,
                text="Rp 0",
                font=self.fonts['stats'],
                bg='#1a1a2e',
                fg=color
            )
            value_label.pack(pady=(5, 10))
            self.stats_labels[key] = value_label

        # ============================================================
        # MAIN CONTENT - Chart + Table
        # ============================================================
        content_frame = tk.Frame(main_frame, bg='#0f0f23')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left: Chart
        chart_frame = tk.Frame(content_frame, bg='#1a1a2e')
        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(
            chart_frame,
            text="📊 Expenses by Category",
            font=self.fonts['heading'],
            bg='#1a1a2e',
            fg='#ecf0f1'
        ).pack(anchor='w', pady=(5, 5))

        self.chart_container = tk.Frame(chart_frame, bg='#1a1a2e')
        self.chart_container.pack(fill=tk.BOTH, expand=True)

        # Right: Recent Expenses Table
        table_frame = tk.Frame(content_frame, bg='#1a1a2e')
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(
            table_frame,
            text="📜 Recent Expenses",
            font=self.fonts['heading'],
            bg='#1a1a2e',
            fg='#ecf0f1'
        ).pack(anchor='w', pady=(5, 5))

        # Treeview for expenses
        columns = ('ID', 'Date', 'Category', 'Amount', 'Description')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=12,
            style='Custom.Treeview'
        )

        # Configure treeview style
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
            self.tree.heading(col, text=col, anchor='center')
            width = 60 if col == 'ID' else 100 if col == 'Date' else 120 if col == 'Category' else 120 if col == 'Amount' else 150
            self.tree.column(col, width=width, anchor='center')

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ============================================================
        # BOTTOM: Actions + Status
        # ============================================================
        action_frame = tk.Frame(main_frame, bg='#0f0f23')
        action_frame.pack(fill=tk.X, pady=(15, 0))

        # Action buttons
        actions = [
            ("➕ Add", self.open_add_expense, '#2ecc71'),
            ("📤 Export", self.export_data, '#1abc9c'),
            ("🔄 Refresh", self.refresh_dashboard, '#3498db'),
            ("📊 All History", self.view_full_history, '#9b59b6')
        ]

        for text, command, color in actions:
            btn = tk.Button(
                action_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=self.fonts['button'],
                padx=25,
                pady=8,
                relief=tk.FLAT,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Status bar
        status_frame = tk.Frame(main_frame, bg='#1a1a2e', height=30)
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

        # ============================================================
        # RIGHT CLICK MENU
        # ============================================================
        self.context_menu = tk.Menu(self.root, tearoff=0, bg='#1a1a2e', fg='#ecf0f1')
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_selected)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Show right-click context menu"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def delete_selected(self):
        """Delete selected expense"""
        selected = self.tree.selection()
        if not selected:
            return

        if not messagebox.askyesno("Confirm Delete", "Delete selected expense?"):
            return

        for item in selected:
            expense_id = self.tree.item(item)['values'][0]
            result = self.expense_service.delete_expense(expense_id)
            if result['success']:
                self.log_output(f"✅ Deleted expense #{expense_id}", 'success')

        self.refresh_dashboard()

    def log_output(self, message, tag=None):
        """Update status bar"""
        self.status_label.config(text=message)

    def refresh_dashboard(self):
        """Refresh all dashboard components"""
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
        except ValueError:
            month = self.current_month
            year = self.current_year

        self.current_month = month
        self.current_year = year

        # Get data
        filters = {'month': month, 'year': year}
        expenses = self.expense_service.get_expense_history(filters)
        analysis = self.expense_service.get_monthly_analysis(year, month)

        # Update stats
        total = analysis.get('total_expenses', 0)
        categories = analysis.get('category_breakdown', [])
        num_categories = len(categories)

        # Calculate average per day
        import calendar
        days_in_month = calendar.monthrange(year, month)[1]
        avg = total / days_in_month if days_in_month > 0 else 0

        # Top category
        top_category = categories[0]['category'] if categories else '-'
        top_amount = categories[0]['total'] if categories else 0
        top_label = f"{top_category} (Rp {top_amount:,.0f})" if top_category != '-' else '-'

        self.stats_labels['total'].config(text=f"Rp {total:,.0f}")
        self.stats_labels['categories'].config(text=str(num_categories))
        self.stats_labels['avg'].config(text=f"Rp {avg:,.0f}")
        self.stats_labels['top'].config(text=top_label)

        # Update treeview
        self.tree.delete(*self.tree.get_children())
        for exp in expenses[:50]:  # Show last 50
            self.tree.insert('', tk.END, values=(
                exp['id'],
                exp['date'],
                exp['category'],
                f"Rp {exp['amount']:,.0f}",
                exp.get('description', '')[:20]
            ))

        # Update chart
        self.update_chart(categories, month, year)

        # Update status
        self.status_label.config(text=f"✅ Showing {len(expenses)} expenses for {month:02d}/{year}")

    def update_chart(self, categories, month, year):
        """Update pie chart"""
        # Clear previous chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        if not MATPLOTLIB_AVAILABLE or not categories:
            label = tk.Label(
                self.chart_container,
                text="📭 No data to display\n\nAdd some expenses to see the chart!",
                font=self.fonts['body'],
                bg='#1a1a2e',
                fg='#bdc3c7'
            )
            label.pack(expand=True)
            return

        # Create figure
        fig, ax = plt.subplots(figsize=(5, 4), facecolor='#1a1a2e')

        # Data
        labels = [item['category'] for item in categories]
        sizes = [item['total'] for item in categories]
        colors = ['#2ecc71', '#3498db', '#9b59b6', '#e67e22', '#1abc9c', '#e74c3c', '#f39c12', '#2c3e50'][:len(labels)]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'color': 'white', 'fontsize': 9}
        )

        ax.set_title(f'Expenses - {month:02d}/{year}', color='white', fontsize=12)

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def open_add_expense(self):
        """Open dialog to add expense"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Add Expense")
        dialog.geometry("450x420")
        dialog.resizable(False, False)
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()

        # Header
        tk.Label(
            dialog,
            text="➕ Add New Expense",
            font=('Segoe UI', 18, 'bold'),
            bg='#1a1a2e',
            fg='#f39c12'
        ).pack(pady=(20, 10))

        # Form
        form = tk.Frame(dialog, bg='#16213e', padx=25, pady=20)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        entries = {}

        fields = [
            ("📅 Date (YYYY-MM-DD):", "date", datetime.now().strftime("%Y-%m-%d")),
            ("📂 Category:", "category", "Food"),
            ("💰 Amount:", "amount", ""),
            ("📝 Description:", "desc", "")
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
                    insertbackground='#f39c12'
                )
                entry.insert(0, default)
                entry.grid(row=i, column=1, padx=5, pady=8, sticky='w')

            entries[key] = entry

        def submit():
            date_str = entries['date'].get().strip()
            category = entries['category'].get().strip()
            amount_str = entries['amount'].get().strip()
            description = entries['desc'].get().strip()

            if not date_str or not category or not amount_str:
                messagebox.showerror("Error", "📌 All fields except description are required!")
                return

            result = self.expense_service.create_expense(
                date_str=date_str,
                category=category,
                amount_str=amount_str,
                description=description
            )

            if result['success']:
                messagebox.showinfo("Success", f"✅ {result['message']}")
                dialog.destroy()
                self.refresh_dashboard()
                self.status_label.config(text=f"✅ Added expense: {category} - Rp {amount_str}")
            else:
                messagebox.showerror("Error", f"❌ {result['error']}")

        # Buttons
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

    def view_full_history(self):
        """Open full history in new window"""
        history_window = tk.Toplevel(self.root)
        history_window.title("📜 Full Expense History")
        history_window.geometry("800x500")
        history_window.configure(bg='#0f0f23')

        tk.Label(
            history_window,
            text="📜 Full Expense History",
            font=('Segoe UI', 18, 'bold'),
            bg='#0f0f23',
            fg='#f39c12'
        ).pack(pady=10)

        # Treeview
        columns = ('ID', 'Date', 'Category', 'Amount', 'Description', 'Created')
        tree = ttk.Treeview(
            history_window,
            columns=columns,
            show='headings',
            height=20,
            style='Custom.Treeview'
        )

        style = ttk.Style()
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
            tree.heading(col, text=col, anchor='center')
            width = 60 if col == 'ID' else 100 if col == 'Date' else 120 if col == 'Category' else 120 if col == 'Amount' else 150 if col == 'Description' else 150
            tree.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        expenses = self.expense_service.get_expense_history()
        total = 0
        for exp in expenses:
            total += exp['amount']
            tree.insert('', tk.END, values=(
                exp['id'],
                exp['date'],
                exp['category'],
                f"Rp {exp['amount']:,.0f}",
                exp.get('description', '')[:30],
                exp.get('created_at', '')[:10]
            ))

        # Total footer
        footer = tk.Frame(history_window, bg='#0f0f23')
        footer.pack(fill=tk.X, pady=10)
        tk.Label(
            footer,
            text=f"📊 Total: {len(expenses)} expenses | Rp {total:,.0f}",
            font=('Segoe UI', 12, 'bold'),
            bg='#0f0f23',
            fg='#2ecc71'
        ).pack()

    def export_data(self):
        """Export data to CSV"""
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Error", "❌ Pandas not installed")
            return

        expenses = self.expense_service.get_expense_history()
        if not expenses:
            messagebox.showinfo("Info", "📭 No expenses to export")
            return

        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date'])

        filename = f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            df.to_csv(filename, index=False)
            messagebox.showinfo("Success", f"✅ Exported to {filename}")
            self.status_label.config(text=f"📤 Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Export failed: {e}")


def main():
    """Run the dashboard"""
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()