# 📝 **README.md - Complete Single File**

```markdown
# 💰 Daily Expense Tracker

A comprehensive Python application for tracking daily expenses with advanced features including income tracking, budget management, recurring expenses, and data visualization.

## 📋 Features

### 📊 Core Features
- **Expense Management**: Add, view, update, delete expenses with categories
- **Income Tracking**: Record and manage multiple income sources
- **Budget Management**: Set monthly budgets per category with progress tracking
- **Recurring Expenses**: Automate recurring bills and subscriptions
- **Monthly Analysis**: Category breakdowns with percentages and trends
- **Data Visualization**: Pie charts and trend charts for expense distribution
- **Export Functionality**: CSV, Excel, and JSON export options
- **Data Backup & Restore**: Local backup system with restore capability
- **Tags & Labels**: Add custom tags to expenses for better organization
- **Payment Methods**: Track payment methods (Cash, Credit Card, E-Wallet, etc.)

### 🎨 User Interfaces
- **CLI Version**: Full-featured command-line interface with all features
- **GUI Version**: Modern graphical interface with real-time dashboard
- **Dashboard**: Real-time stats with total expense, income, and net balance
- **Interactive Charts**: Pie charts and trend visualizations

### 🛠️ Technical Features
- **Layered Architecture**: Models-Services-Utils separation
- **Database**: SQLite with indexing for performance
- **Multiple Interfaces**: CLI and GUI in one application
- **Code Quality**: Black formatting, Flake8 linting

## 🚀 Quick Start

### Installation
```bash
# 1. Clone repository
git clone https://github.com/ArkanTsabit123/Daily-Expense-Tracker.git
cd Daily-Expense-Tracker

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run application
# Choose interface:
python run.py          # Launcher (choose CLI or GUI)
python cli.py          # CLI version only
python gui.py          # GUI version only
```

## 📁 Project Structure

```
Daily-Expense-Tracker/
├── 📁 config/
│   └── database_config.py      # Database configuration
├── 📁 models/
│   └── expense_model.py        # Data models
├── 📁 services/
│   ├── database_service.py     # Database operations layer
│   ├── expense_service.py      # Business logic layer
│   └── export_service.py       # Export functionality
├── 📁 utils/
│   ├── validation.py           # Input validation
│   ├── date_utils.py           # Date helper functions
│   └── formatters.py           # Data formatting
├── 📁 visualization/
│   └── chart_service.py        # Chart generation
├── 📁 backups/                 # Database backups (auto-created)
├── 📁 tests/                   # Test files
├── cli.py                      # CLI application (full features)
├── gui.py                      # GUI application (full features)
├── run.py                      # Application launcher
├── main.py                     # Original main application
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

## 🎮 Usage

### CLI Version

Run the CLI application:
```bash
python cli.py
```

**Main Menu Options:**
```
📊 EXPENSE TRACKING
1. ➕ Add Expense
2. 📜 View History
3. 📊 Summary
4. 📈 Generate Chart

💰 FINANCE MANAGEMENT
5. 💵 Add Income
6. 📋 View Income
7. 🎯 Budget Management
8. 🔄 Recurring Expenses

📊 ANALYTICS & TOOLS
9. 📈 Advanced Analytics
10. 📤 Export Data
11. 💾 Backup & Restore

❌ EXIT
12. ❌ Exit
```

### GUI Version

Run the GUI application:
```bash
python gui.py
```

**GUI Features:**
- **Dashboard**: Real-time expense, income, and net balance stats
- **Budget Tab**: Set and track monthly budgets with progress bars
- **Income Tab**: Record and manage income sources
- **Recurring Tab**: Manage recurring expenses
- **Analytics Tab**: Advanced charts and trend analysis
- **Settings Tab**: Backup, restore, and export options

### Example Usage

**Add an expense:**
```bash
python cli.py
> Select option 1 (Add Expense)
> Date: 2026-07-02
> Category: Food
> Amount: 50000
> Description: Lunch
> Payment Method: Cash
> Tags: lunch, work
```

**Add income:**
```bash
> Select option 5 (Add Income)
> Date: 2026-07-01
> Source: Salary
> Amount: 5000000
> Description: July salary
> Recurring: Yes
```

## 🗄️ Database Schema

The application uses SQLite with the following tables:

### Expenses Table
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    payment_method TEXT DEFAULT 'Cash',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Incomes Table
```sql
CREATE TABLE incomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    source TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    is_recurring INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Budgets Table
```sql
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL UNIQUE,
    monthly_limit REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Recurring Expenses Table
```sql
CREATE TABLE recurring_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    frequency TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Tags Table
```sql
CREATE TABLE expense_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (expense_id) REFERENCES expenses(id)
);
```

## 📊 Output Examples

### CLI Screenshot
```
📊 ALL TIME SUMMARY
==================================================
Total Expense  : Rp 5,000,000
Total Income   : Rp 8,000,000
Net Balance    : Rp 3,000,000
Transactions   : 45
Categories     : 6
Period         : 2026-01-01 to 2026-07-02
==================================================

📂 Category Breakdown:
--------------------------------------------------
Food                    Rp 2,000,000 (40.0%) ████████
Transport               Rp 1,000,000 (20.0%) ████
Bills                   Rp 1,500,000 (30.0%) ██████
Entertainment           Rp   500,000 (10.0%) ██
```

### GUI Features
- Real-time dashboard with stats cards
- Interactive pie charts
- Budget progress bars with color indicators
- Search and filter functionality
- Export buttons for CSV/Excel

## 🧪 Development

### Running Tests
```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_database.py -v
```

### Code Quality
```bash
# Format code with Black
black .

# Check code style with Flake8
flake8 .

# Run type checking (optional)
mypy .
```

## 📦 Dependencies

### Core Requirements
```
matplotlib==3.7.1        # Data visualization
pandas==2.0.3           # Data processing and Excel export
openpyxl==3.1.2         # Excel file manipulation
python-dateutil==2.8.2  # Date parsing utilities
tkinter                 # GUI framework (built-in with Python)
```

### Development Dependencies
```
pytest==7.4.3           # Testing framework
black==23.9.1           # Code formatting
flake8==6.1.0           # Code linting
```

## 🔮 Future Enhancements

### Planned Features
1. **User Authentication** - Multi-user support with login system
2. **Cloud Sync** - Automatic backup to cloud services
3. **Web Interface** - Flask/FastAPI web application
4. **Mobile App** - Cross-platform mobile version
5. **Receipt Scanning** - OCR integration for automatic entry
6. **Bank Integration** - API connections for auto-import
7. **Advanced Analytics** - Predictive spending insights
8. **Multiple Currency** - Support for different currencies
9. **Dark/Light Theme** - Toggle between themes in GUI
10. **Export Filtering** - Export specific date ranges or categories

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a descriptive feature branch**:
   ```bash
   git checkout -b feature/feature-name
   ```
3. **Commit your changes with a clear message**:
   ```bash
   git commit -m 'Add: feature description'
   ```
4. **Push to your branch**:
   ```bash
   git push origin feature/feature-name
   ```
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation accordingly
- Use descriptive commit messages
- Ensure your code passes all existing tests

## 📄 License

This project is available for educational and personal use. Commercial use requires permission.

## 🙏 Acknowledgments

- Built as a portfolio project to demonstrate Python development skills
- Inspired by the need for personal finance management tools
- Uses open-source libraries: Matplotlib, Pandas, OpenPyXL
- SQLite for lightweight local database storage

## ❓ Support

For issues or questions:
1. Check the existing documentation
2. Review the code comments
3. Create an issue in the [GitHub repository](https://github.com/ArkanTsabit123/Daily-Expense-Tracker/issues)
4. Contact: aarkantsabit@gmail.com

---

**Happy Tracking!** ⭐
```

