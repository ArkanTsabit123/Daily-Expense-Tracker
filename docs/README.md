# Daily Expense Tracker 

A useful Python application for tracking and analyzing daily expenses with data visualization and reporting capabilities. Built with modular architecture following professional software design patterns.

## Features

### Expense Management
- Add expenses with date, category, amount, and description
- View expense history with various filtering options
- Update and delete existing expenses
- Categorize expenses (Food, Transportation, Shopping, etc.)

### Data Analysis & Visualization
- Monthly summaries with total expenses and category breakdowns
- Interactive charts using Matplotlib
- Pie charts for expense distribution visualization
- Monthly trend analysis with line charts

### Export & Reporting
- Export to CSV with proper encoding
- Export to Excel with professional formatting
- Generate useful reports with multiple sheets
- Automatic file management with organized exports

### Advanced Functionality
- Smart filtering by date range, category, and amount
- Input validation with useful error handling
- Currency formatting for Indonesian Rupiah (IDR)
- Date utilities with Indonesian month names

## Project Structure

```
daily-expense-tracker/
├── config/                    # Configuration files
│   ├── __init__.py
│   └── database_config.py    # Database connection & setup
├── models/                    # Data models
│   ├── __init__.py
│   ├── expense_model.py      # Expense data model
│   └── category_model.py     # Category data model
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── database_service.py   # Database operations
│   ├── expense_service.py    # Expense business logic
│   ├── export_service.py     # Export functionality
│   └── analysis_service.py   # Data analysis service
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── validation.py         # Input validation
│   ├── date_utils.py         # Date helper functions
│   ├── formatters.py         # Data formatting
│   └── exceptions.py         # Custom exceptions
├── visualization/             # Chart generation
│   ├── __init__.py
│   └── chart_service.py      # Matplotlib chart generation
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_database.py      # Database tests
│   ├── test_expenses.py      # Expense service tests
│   ├── test_export.py        # Export service tests
│   └── conftest.py           # Test configuration
├── docs/                      # Documentation
│   ├── README.md             # Extended project docs
│   ├── project_plan.md       # Timeline & implementation plan
│   ├── usage.md              # User guide & how-to
│   ├── development.md        # Development setup guide
│   ├── testing.md            # Testing instructions
│   └── deployment.md         # Deployment guide
├── generate/                  # Code generators
│   ├── file_and_folder.py    # Project structure generator
│   ├── structure.py          # Structure viewer
│   ├── sample_data.py        # Sample data generator
│   ├── database_schema.py    # SQL schema generator
│   └── documentation.py      # Documentation generator
├── data/                      # Database storage
├── exports/                   # Export file storage
├── charts/                    # Generated chart storage
├── __init__.py               # Main package
├── main.py                   # Main application entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore                # Git ignore rules
└── pyproject.toml            # Build system configuration
```

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**
   ```bash
   git clone https://github.com/yourusername/daily-expense-tracker.git
   cd daily-expense-tracker
   ```

2. **Set up virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
   
   Or use the runner script:
   ```bash
   python run.py
   ```

## Usage

### Main Menu
```
DAILY EXPENSE TRACKER
============================================================
MAIN MENU
============================================================

Please select an option:
1. Add New Expense
2. View Expense History
3. Monthly Summary
4. Generate Chart
5. Export Data
6. Settings
7. Exit
```

### Adding an Expense
1. Select option 1 from main menu
2. Enter date (YYYY-MM-DD format)
3. Select category from available options
4. Enter amount in Indonesian Rupiah
5. Add optional description
6. Confirm to save

### Viewing Expense History
- View all expenses or filter by:
  - Specific month and year
  - Category
  - Date range
- Export filtered data to CSV or Excel

### Monthly Analysis
- View total expenses for any month
- See category breakdown with percentages
- Generate pie chart visualization
- Export useful monthly report

## Development

### Setting Up Development Environment
```bash
# Clone repository
## 📋 Table of Contents

### 📖 User Documentation
- [User Guide](usage.md) - Complete usage instructions
- [Quick Start](usage.md#quick-start) - Get started in 5 minutes
- [Features Overview](usage.md#features) - All available features
- [FAQ](faq.md) - Frequently asked questions

### 🔧 Developer Documentation
- [Architecture Guide](development.md) - System design and architecture
- [Testing Guide](testing.md) - Testing procedures and setup
- [Deployment Guide](deployment.md) - Deployment instructions
- [API Reference](api.md) - Service and function documentation

### 📊 Project Documentation
- [Project Plan](../project_plan.md) - Development timeline and phases
- [Contributing Guidelines](../CONTRIBUTING.md) - How to contribute to this project
- [License](../LICENSE) - Project license information
- [Changelog](../CHANGELOG.md) - Version history and changes

### 🚀 Quick Links
- [GitHub Repository](https://github.com/ArkanTsabit123/Daily-Expense-Tracker)
- [Issue Tracker](https://github.com/ArkanTsabit123/Daily-Expense-Tracker/issues)
- [Download Latest Release](https://github.com/ArkanTsabit123/Daily-Expense-Tracker/releases)


git clone https://github.com/yourusername/daily-expense-tracker.git
cd daily-expense-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_database.py -v
```

### Code Quality
```bash
# Format code with Black
black .

# Lint code with Flake8
flake8 .

# Sort imports with isort
isort .
```

## Skills Demonstrated

### Core Programming
- Object-Oriented Programming with clean class structure
- Data Modeling with dataclasses and proper validation
- useful Error Handling with try-catch blocks
- Type Hints for better code maintainability

### Database Management
- SQLite Operations with connection management
- Database Design with normalized tables
- Query Optimization with proper indexing and filtering
- Transaction Management for data consistency

### Data Visualization
- Matplotlib Integration for professional charts
- Custom Styling with colors, legends, and annotations
- Chart Export in high-quality formats
- Data Preparation for visualization

### File Handling & Export
- CSV Operations with proper encoding
- Excel Export with pandas and formatting
- File Management with path handling
- Data Serialization for multiple formats

### Software Architecture
- Separation of Concerns with layered architecture
- Modular Design with reusable components
- Configuration Management with external config
- Error Recovery with graceful degradation

## Future Enhancements

1. User Authentication - Multi-user support with login system
2. Budget Planning - Set budget limits per category with alerts
3. Data Backup - Cloud sync and automatic backup functionality
4. Web Interface - Flask/FastAPI web version with REST API
5. Mobile App - Kivy/React Native cross-platform mobile version
6. Advanced Analytics - Machine learning predictions and insights
7. Receipt Scanning - OCR integration for automatic expense entry
8. API Integration - Bank sync for automatic transaction tracking

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Acknowledgments

- Built with Python and modern software engineering practices
- Inspired by personal finance management needs
- Icons and design elements from various open-source resources
