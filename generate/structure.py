# project portofolio/junior projects/daily-expense-tracker/generate/structure.py

"""
View daily-expense-tracker - Project Structure
"""

def show_structure():
    print("daily-expense-tracker - Project Structure")
    print("=" * 60)

    structure = """
    daily-expense-tracker/
    ├── config/                    # Configuration files
    │   ├── __init__.py           # Package initialization
    │   └── database_config.py    # Database connection & setup
    ├── models/                    # Data models
    │   ├── __init__.py           # Models package
    │   ├── expense_model.py      # Expense data model
    │   └── category_model.py     # Category data model
    ├── generate/                  # Code generators
    │   ├── file_and_folder.py    # Project structure generator
    │   ├── structure.py          # Structure viewer
    │   ├── sample_data.py        # Sample data generator
    │   ├── database_schema.py    # SQL schema generator
    │   └── documentation.py      # Documentation generator
    ├── docs/                      # Project documentation
    │   ├── README.md             # Extended project docs
    │   ├── project_plan.md       # Timeline & implementation plan
    │   ├── usage.md              # User guide & how-to
    │   ├── development.md        # Development setup guide
    │   ├── testing.md            # Testing instructions
    │   └── deployment.md         # Deployment guide
    ├── services/                  # Business logic layer
    │   ├── __init__.py           # Services package
    │   ├── database_service.py   # Database operations
    │   ├── expense_service.py    # Expense business logic
    │   ├── export_service.py     # Export functionality
    │   └── analysis_service.py   # Data analysis service
    ├── utils/                     # Utility functions
    │   ├── __init__.py           # Utils package
    │   ├── validation.py         # Input validation
    │   ├── date_utils.py         # Date helper functions
    │   ├── formatters.py         # Data formatting
    │   └── exceptions.py         # Custom exceptions
    ├── visualization/             # Chart generation
    │   ├── __init__.py           # Visualization package
    │   └── chart_service.py      # Matplotlib chart generation
    ├── tests/                     # Test suite
    │   ├── __init__.py           # Tests package
    │   ├── test_database.py      # Database tests
    │   ├── test_expenses.py      # Expense service tests
    │   ├── test_export.py        # Export service tests
    │   └── conftest.py           # Test configuration
    ├── data/                      # Database storage
    ├── exports/                   # Export file storage
    ├── charts/                    # Generated chart storage
    ├── __init__.py               # Main package
    ├── main.py                   # Main application entry point
    ├── run.py                    # Application runner
    ├── requirements.txt          # Python dependencies
    ├── README.md                 # Project README
    ├── .gitignore                # Git ignore rules
    └── pyproject.toml            # Build system configuration
    """
    print(structure)
    print("=" * 60)
    print("Structure: 11 directories, 44 files")
    print("(Includes 3 .gitkeep files for empty directories)")

if __name__ == "__main__":
    show_structure()
