# Buat folder docs jika belum ada
mkdir docs 2>nul

# Buat file api.md
cat > docs/api.md << 'EOF'
# API Documentation

## Database Service

### `DatabaseService`
Main service for database operations.

#### Methods
- `add_expense(data: Dict) -> int`: Add new expense
- `get_expenses(filters: Dict) -> List[Dict]`: Get expenses with filters
- `update_expense(expense_id: int, data: Dict) -> bool`: Update expense
- `delete_expense(expense_id: int) -> bool`: Delete expense

## Expense Service

### `ExpenseService`
Business logic layer.

#### Methods
- `create_expense(data: Dict) -> int`: Create expense with validation
- `get_expense_history(filters: Dict) -> List[Dict]`: Get expense history
- `get_monthly_analysis(year: int, month: int) -> Dict`: Get monthly analysis
- `get_categories() -> List[str]`: Get all categories

## Export Service

### `ExportService`
Export data to various formats.

#### Methods
- `export_to_csv(expenses: List[Dict], filename: str = None) -> str`: Export to CSV
- `export_to_excel(expenses: List[Dict], filename: str = None) -> str`: Export to Excel
- `export_monthly_report(monthly_data: Dict, expenses: List[Dict]) -> str`: Export report

## Utility Modules

### Validation (`utils/validation.py`)
- `validate_date(date_str: str) -> bool`: Validate date format
- `validate_amount(amount_str: str) -> bool`: Validate amount format

### Formatters (`utils/formatters.py`)
- `format_currency(amount: Decimal) -> str`: Format as currency (Rp)
- `format_date(date_obj: date) -> str`: Format date
- `format_category(category: str) -> str`: Format category with icon

### Date Utilities (`utils/date_utils.py`)
- `get_current_month_year() -> Tuple[int, int]`: Get current month/year
- `get_month_name(month: int, language: str = "id") -> str`: Get month name
- `get_previous_month_year(month: int, year: int) -> Tuple[int, int]`: Get previous month/year
- `get_next_month_year(month: int, year: int) -> Tuple[int, int]`: Get next month/year
- `get_month_range(year: int, month: int) -> Tuple[date, date]`: Get month date range
EOF