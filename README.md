Here's the repaired README.md with corrections and improvements:

```markdown
# Daily Expense Tracker 

A Python application for tracking daily expenses with data visualization and reporting capabilities.

## 📋 Features

### 📊 Core Features
- **Expense Management**: Add, view, update, delete expenses
- **Monthly Analysis**: Category breakdowns with percentages
- **Data Visualization**: Pie charts for expense distribution
- **Export Functionality**: CSV and Excel reports

### 🛠️ Technical Features
- **Layered Architecture**: Models-Services-Utils separation
- **Database**: SQLite with indexing for performance
- **Testing**: Comprehensive pytest test suite
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
python main.py
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
├── 📁 tests/                   # Test files
├── main.py                     # Main application & menu
├── requirements.txt            # Dependencies
├── run.py                      # Application entry point
└── README.md                   # Documentation
```

## 🎮 Usage

### Main Menu Options
1. **➕ Add Expense** - Record new expenses with category selection
2. **📜 View History** - Browse expense history with filtering options
3. **📊 Monthly Summary** - View monthly breakdowns and generate charts
4. **📈 Generate Chart** - Create visual representations of spending
5. **📤 Export Data** - Export to CSV or Excel formats
6. **❌ Exit** - Exit the application

### Example Usage
```bash
# Run the application
python main.py

# Or use the entry point
python run.py
```

## 🗄️ Database Schema

The application uses SQLite with two main tables:

### Expenses Table
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Categories Table
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    budget_limit DECIMAL(10,2) DEFAULT NULL
);
```

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

## 📊 Output Examples

### Generated Charts
- **Pie Charts**: Expense distribution by category
- **Trend Charts**: Monthly spending patterns

### Export Formats
- **CSV**: Comma-separated values for spreadsheet import
- **Excel**: Formatted multi-sheet reports with auto-adjusting columns

## 📦 Dependencies

### Core Requirements
```
matplotlib==3.7.1        # Data visualization
pandas==2.0.3           # Data processing and Excel export
openpyxl==3.1.2         # Excel file manipulation
python-dateutil==2.8.2  # Date parsing utilities
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
2. **Budget Planning** - Set monthly budgets with notifications
3. **Data Backup** - Automated cloud sync and local backups
4. **Web Interface** - Flask/FastAPI web application
5. **Mobile App** - Cross-platform mobile version
6. **Receipt Scanning** - OCR integration for automatic entry
7. **Bank Integration** - API connections for auto-import
8. **Advanced Analytics** - Predictive spending insights

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository** (click Fork button on GitHub)
2. **Create a descriptive feature branch**:

   git checkout -b feature/feature-name
   # Examples: feature/add-dark-mode, fix/export-bug, docs/update-readme

3. **Commit your changes with a clear message**:

   git commit -m 'Add: Monthly budget tracking feature'

4. **Push to your branch**:

   git push origin feature/feature-name

5. **Open a Pull Request** on the original repository

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

## ❓ Support

For issues or questions:
1. Check the existing documentation
2. Review the code comments
3. Create an issue in the [GitHub repository](https://github.com/ArkanTsabit123/Daily-Expense-Tracker/issues)
4. Contact: aarkantsabit@gmail.com

---

**Happy Tracking!** ⭐
```
