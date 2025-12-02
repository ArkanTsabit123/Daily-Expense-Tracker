# TESTING GUIDE - Daily Expense Tracker

## RUNNING TESTS

### Quick Test Commands
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_database.py -v
python -m pytest tests/test_expenses.py -v  
python -m pytest tests/test_export.py -v

# Run with coverage report
python -m pytest --cov=. --cov-report=html

# Run specific test function
python -m pytest tests/test_database.py::TestDatabase::test_add_expense -v
```

## TEST COVERAGE

### Database Tests (tests/test_database.py)
```python
# Tests included:
- Database connection setup
- CRUD operations (Create, Read, Update, Delete)
- Filtering and searching
- Monthly summaries
- Category management
```

### Expense Service Tests (tests/test_expenses.py)
```python
# Tests included:
- Expense validation
- Business logic
- Date filtering
- Amount calculations
- Error handling
```

### Export Service Tests (tests/test_export.py)
```python
# Tests included:
- CSV export functionality
- Excel export with formatting
- Report generation
- File handling
```

## TEST FIXTURES

Sample test data is automatically generated for:
- 50 random expense records
- Multiple categories
- Realistic date ranges (last 3 months)
- Varying amounts

## RUNNING MANUAL TESTS

```python
# Quick manual test from Python shell
python -c "
from services.expense_service import ExpenseService
service = ExpenseService()
expenses = service.get_expenses()
print(f'Found {len(expenses)} expenses')
"
```

## TESTING SCENARIOS

### 1. Database Operations
```bash
# Test database connection
python tests/test_database.py -k "test_connection"

# Test CRUD operations
python tests/test_database.py -k "test_crud"
```

### 2. Business Logic
```bash
# Test expense validation
python tests/test_expenses.py -k "test_validation"

# Test monthly analysis
python tests/test_expenses.py -k "test_monthly_analysis"
```

### 3. Export Functionality
```bash
# Test CSV export
python tests/test_export.py -k "test_csv_export"

# Test Excel export
python tests/test_export.py -k "test_excel_export"
```

## DEBUGGING TESTS

```bash
# Run tests with debug output
python -m pytest tests/ -v -s

# Run single test with debug
python -m pytest tests/test_database.py::TestDatabase::test_add_expense -v -s

# Check test discovery
python -m pytest tests/ --collect-only
```

## CODE QUALITY CHECKS

```bash
# Run linter
python -m flake8 .

# Check code formatting
python -m black --check .

# Sort imports
python -m isort --check-only .
```

## TEST CLEANUP

```bash
# Clean test artifacts
rm -rf tests/__pycache__
rm -rf .pytest_cache
rm -rf htmlcov
rm -rf .coverage

# Remove test databases
rm -f test_expenses.db
```

## CONTINUOUS INTEGRATION

### GitHub Actions (.github/workflows/test.yml)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ -v
```

---

# USAGE GUIDE - Daily Expense Tracker

## QUICK START

### Installation
```bash
# Method 1: From source
git clone https://github.com/yourusername/daily-expense-tracker.git
cd daily-expense-tracker
pip install -r requirements.txt
python main.py

# Method 2: Using virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py
```

### First Run
```
DAILY EXPENSE TRACKER
============================================================
MAIN MENU
============================================================

1. Add New Expense
2. View Expense History
3. Monthly Summary
4. Generate Chart
5. Export Data
6. Settings
7. Exit

Select option (1-7):
```

## ADDING EXPENSES

### Step-by-Step:
1. Select Option 1 from main menu
2. Enter date (YYYY-MM-DD format) or press Enter for today
3. Select category from list:
   ```
   1. Makanan & Minuman
   2. Transportasi
   3. Belanja
   4. Hiburan
   5. Kesehatan
   6. Pendidikan
   7. Tagihan
   8. Lain-lain
   ```
4. Enter amount (example: `50000` or `50.000`)
5. Add optional description
6. Confirm to save

### Examples:
```
Tanggal: 2024-01-15
Kategori: Makanan & Minuman
Jumlah: Rp 50.000
Keterangan: Makan siang di restoran
```

## VIEWING EXPENSES

### Option 2: View Expense History
```
Filter Options:
1. View all
2. Filter by month
3. Filter by category
4. Filter by month and category
```

### View All Expenses:
```
Total 25 transactions: Rp 3.500.000
--------------------------------------------------
Date        Category            Amount      Description
--------------------------------------------------
15/01/2024  Makanan & Minuman  Rp 50.000   Makan siang
14/01/2024  Transportasi       Rp 25.000   Bensin
13/01/2024  Belanja            Rp 200.000  Belanja bulanan
...
```

## MONTHLY ANALYSIS

### Option 3: Monthly Summary
```
Ringkasan Pengeluaran Januari 2024
======================================
Total Expenses: Rp 3.500.000
Category Count : 8

Breakdown per Category:
--------------------------------------------------
Makanan & Minuman     Rp 800.000   (22.9%)
Transportasi          Rp 500.000   (14.3%)
Belanja              Rp 1.000.000 (28.6%)
Hiburan              Rp 300.000   (8.6%)
Kesehatan            Rp 400.000   (11.4%)
Pendidikan           Rp 250.000   (7.1%)
Tagihan              Rp 200.000   (5.7%)
Lain-lain            Rp 50.000    (1.4%)
```

### Generate Chart:
```
Generate pie chart? (y/n): y
Chart saved to: charts/expense_chart_2024_01.png
```

## EXPORTING DATA

### Option 5: Export Data
```
Export Options:
1. Export transaction data
2. Export monthly report

Format (1-CSV, 2-Excel): 2
Data exported to: exports/monthly_report_2024_01.xlsx
```

### Excel Report Contains:
1. Summary Sheet: Monthly totals and statistics
2. Per Category Sheet: Category breakdown with percentages
3. Detail Transactions Sheet: All expense records

## SETTINGS & MAINTENANCE

### Option 6: Settings
```
SETTINGS
1. Reset database
2. View system info
3. Back up data
4. Back to main menu
```

### Database Reset:
```
WARNING: This will delete all data! Continue? (y/n): y
Database reset successfully
```

## TIPS & SHORTCUTS

### Date Formats Accepted:
- `2024-01-15` (recommended)
- `15/01/2024`
- `today` or empty for current date

### Amount Formats Accepted:
- `50000`
- `50.000`
- `50,000`
- `50 000`

### Category Aliases:
- `food`, `makanan` -> Makanan & Minuman
- `transport`, `transportasi` -> Transportasi
- `shop`, `belanja` -> Belanja

## TROUBLESHOOTING

### Common Issues:

1. Database not found error:
   - Run from project root directory
   - Ensure data/ directory exists
   - Check file permissions

2. Import errors:
   - Make sure requirements are installed
   - Check Python version (3.8+ required)

3. Chart generation fails:
   - Install required system fonts
   - Check write permissions for charts/ directory

### Getting Help:
- Check logs in logs/ directory
- Run with debug flag: `python main.py --debug`
- Review error messages in console output
