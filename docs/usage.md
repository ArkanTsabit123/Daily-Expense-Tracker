# USAGE GUIDE - Daily Expense Tracker

## QUICK START

### Installation
```bash
# 1. Clone or download the project
git clone https://github.com/yourusername/daily-expense-tracker.git
cd daily-expense-tracker

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python main.py
```

## FIRST TIME SETUP

When you run the application for the first time:
1. Database will be automatically created in `data/expenses.db`
2. Default categories will be added
3. Required directories (`exports/`, `charts/`) will be created

## MAIN MENU

```
============================================================
DAILY EXPENSE TRACKER - MAIN MENU
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

## 1. ADDING EXPENSES

### Step-by-Step Process:
1. Select option 1 from main menu
2. Enter date in YYYY-MM-DD format (or press Enter for today's date)
3. Select category from the list shown
4. Enter amount in Indonesian Rupiah
5. Add optional description
6. Confirm to save

### Example Session:
```
ADD NEW EXPENSE
============================================================

Date (YYYY-MM-DD) [press Enter for today]: 2024-01-15

Select Category:
1. Makanan & Minuman
2. Transportasi
3. Belanja
4. Hiburan
5. Kesehatan
6. Pendidikan
7. Tagihan
8. Lain-lain

Select category (1-8): 1

Amount: Rp 50000

Description (optional): Makan siang di restoran

SUMMARY:
Date: 2024-01-15
Category: Makanan & Minuman
Amount: Rp 50,000
Description: Makan siang di restoran

Save expense? (y/n): y
Expense added successfully!
```

### Accepted Date Formats:
- `2024-01-15` (recommended)
- `15/01/2024`
- `today` or empty for current date
- `yesterday` for previous day

### Accepted Amount Formats:
- `50000` (plain number)
- `50.000` (with thousand separator)
- `50,000` (with comma separator)
- `50 000` (with space separator)
- `50000.50` (with decimal)

## 2. VIEWING EXPENSE HISTORY

### Available Filters:
```
VIEW EXPENSE HISTORY
============================================================
Filter Options:
1. View all expenses
2. Filter by month
3. Filter by category
4. Filter by date range
5. Back to main menu

Select option (1-5):
```

### Example: Filter by Month
```
Select option: 2
Year (YYYY): 2024
Month (1-12): 1

EXPENSES FOR JANUARY 2024
============================================================
Total expenses: 15 transactions
Total amount: Rp 2,500,000

Date        Category            Amount      Description
----------------------------------------------------------
2024-01-15  Makanan & Minuman  Rp 50,000   Makan siang
2024-01-14  Transportasi       Rp 25,000   Bensin
2024-01-13  Belanja            Rp 200,000  Belanja bulanan
2024-01-12  Hiburan            Rp 75,000   Bioskop
2024-01-11  Kesehatan          Rp 150,000  Dokter
...
```

### Exporting Filtered Data:
After viewing expenses, you can export them:
```
Export to file? (y/n): y
Format (1-CSV, 2-Excel): 2
Data exported to: exports/expenses_20240115_143022.xlsx
```

## 3. MONTHLY SUMMARY

### Getting Monthly Analysis:
```
MONTHLY SUMMARY
============================================================
Year [2024]: 2024
Month (1-12) [1]: 1

MONTHLY ANALYSIS - JANUARY 2024
============================================================
Total Expenses: Rp 2,500,000
Transaction Count: 15
Categories Used: 6

CATEGORY BREAKDOWN:
----------------------------------------------------------
Makanan & Minuman     Rp 800,000   (32.0%)
Transportasi          Rp 500,000   (20.0%)
Belanja               Rp 600,000   (24.0%)
Hiburan               Rp 300,000   (12.0%)
Kesehatan             Rp 200,000   (8.0%)
Lain-lain             Rp 100,000   (4.0%)
```

### Generating Charts:
```
Generate chart? (y/n): y
Chart saved to: charts/expense_chart_2024_01.png
```

### Exporting Monthly Report:
```
Export monthly report? (y/n): y
Report exported to: exports/monthly_report_2024_01.xlsx
```

The Excel report contains 3 sheets:
1. **Summary** - Monthly totals and statistics
2. **Per Category** - Detailed category breakdown
3. **Detail Transactions** - All expense records for the month

## 4. GENERATING CHARTS

### Available Chart Types:
```
GENERATE CHART
============================================================
Year [2024]: 2024
Month (1-12) [1]: 1

Generating expense distribution chart...
Chart saved to: charts/expense_chart_2024_01.png

Open chart? (y/n): y
```

### Chart Features:
- Pie chart showing expense distribution by category
- Professional styling with legends and percentages
- High-resolution export (300 DPI)
- Automatic color scheme
- Chart title with total amount

## 5. EXPORTING DATA

### Export Options:
```
EXPORT DATA
============================================================
Export Options:
1. Export all expense data
2. Export monthly report
3. Export category summary
4. Back to main menu

Select option (1-4):
```

### CSV Export:
- Simple comma-separated format
- UTF-8 encoding
- Includes all expense fields
- Can be opened in Excel, Google Sheets, or any text editor

### Excel Export:
- Professional formatting
- Multiple sheets for different data views
- Auto-adjusted column widths
- Date formatting
- Currency formatting

### Export File Locations:
- CSV files: `exports/csv/`
- Excel files: `exports/excel/`
- PDF reports: `exports/pdf/` (future feature)
- Charts: `charts/`

## 6. SETTINGS

### Settings Menu:
```
SETTINGS
============================================================
1. Reset database
2. View system information
3. Backup data
4. Restore from backup
5. Manage categories
6. Back to main menu

Select option (1-6):
```

### Database Reset:
```
WARNING: This will delete all expense data!
Are you sure? (y/n): y
Database reset successfully.
Default categories have been restored.
```

### System Information:
```
SYSTEM INFORMATION
============================================================
Application: Daily Expense Tracker v1.0.0
Python Version: 3.11.0
Database: SQLite 3.37.0
Database Path: data/expenses.db
Exports Directory: exports/
Charts Directory: charts/
Total Expenses: 1,250 records
Database Size: 256 KB
```

### Category Management:
```
MANAGE CATEGORIES
============================================================
Current Categories:
1. Makanan & Minuman
2. Transportasi
3. Belanja
4. Hiburan
5. Kesehatan
6. Pendidikan
7. Tagihan
8. Lain-lain

Options:
1. Add new category
2. Edit existing category
3. Delete category
4. Set budget limits
5. Back to settings
```

## COMMAND LINE ARGUMENTS

Run the application with command line options:

```bash
# Run with specific month view
python main.py --month 1 --year 2024

# Run in export mode
python main.py --export csv --month 1 --year 2024

# Run with debug logging
python main.py --debug

# Show help
python main.py --help
```

## KEYBOARD SHORTCUTS

### Navigation:
- `Ctrl+C` - Cancel current operation
- `Enter` - Use default value
- `q` or `Q` - Quit/Go back

### Date Shortcuts:
- `today` or empty - Current date
- `yesterday` - Previous day
- `-1d` - One day ago
- `-7d` - One week ago

### Category Shortcuts:
- Type category number (1-8)
- Type first few letters of category name
- Use arrow keys to navigate (if supported by terminal)

## DATA MANAGEMENT

### Backup Your Data:
```
SETTINGS > 3. Backup data
Backup saved to: data/backups/expenses_backup_20240115.db
```

### Restore From Backup:
```
SETTINGS > 4. Restore from backup
Available backups:
1. expenses_backup_20240115.db (2024-01-15 14:30)
2. expenses_backup_20240114.db (2024-01-14 10:15)

Select backup to restore: 1
Data restored successfully.
```

### File Locations:
- **Database**: `data/expenses.db`
- **Backups**: `data/backups/`
- **Exports**: `exports/`
- **Charts**: `charts/`
- **Logs**: `logs/`

## TROUBLESHOOTING

### Common Issues:

1. **"Database not found" error**
   ```
   Solution: Make sure you're running from the project root directory
   The 'data/' folder should be in the same directory as main.py
   ```

2. **"Module not found" error**
   ```
   Solution: Install dependencies
   pip install -r requirements.txt
   ```

3. **Permission errors when saving files**
   ```
   Solution: Check write permissions for exports/ and charts/ directories
   Or run as administrator (Windows) / use sudo (Linux/Mac)
   ```

4. **Chart generation fails**
   ```
   Solution: Install matplotlib system dependencies
   # Ubuntu/Debian:
   sudo apt-get install python3-tk
   # Mac:
   brew install python-tk
   ```

### Getting Help:
1. Check the `logs/` directory for error logs
2. Run with debug mode: `python main.py --debug`
3. Review console output for error messages
4. Check file permissions on `data/`, `exports/`, `charts/`

## BEST PRACTICES

1. **Regular Backups**: Use the built-in backup feature weekly
2. **Category Organization**: Use consistent category names
3. **Descriptive Notes**: Add descriptions to expenses for better tracking
4. **Monthly Review**: Use monthly summaries to analyze spending patterns
5. **Export Reports**: Export data before major updates or migrations

## SUPPORT

For issues or questions:
1. Check the documentation in `docs/` directory
2. Review error messages in the console
3. Check the application logs in `logs/` directory
4. Ensure all dependencies are installed correctly

---

*Last Updated: January 2024*
