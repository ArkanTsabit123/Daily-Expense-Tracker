# Development Guide

## Development Environment Setup

### Prerequisites
- Python 3.8 or higher
- Git
- pip (Python package manager)

### Setting Up Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/daily-expense-tracker.git
cd daily-expense-tracker
```

2. **Create virtual environment**
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
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 isort
```

4. **Initialize the project**
```bash
# Initialize database (optional - will be created on first run)
python -c "from config.database_config import DatabaseConfig; db = DatabaseConfig(); db.initialize_database()"
```

## Project Architecture

### Layered Architecture
The application follows a layered architecture:

```
Presentation Layer (CLI)
    ↓
Business Logic Layer (Services)
    ↓
Data Access Layer (Database Service)
    ↓
Database Layer (SQLite)
```

### Key Components

1. **Models** (`models/`): Data structures and validation
2. **Services** (`services/`): Business logic and operations
3. **Utils** (`utils/`): Helper functions and utilities
4. **Visualization** (`visualization/`): Chart generation
5. **Config** (`config/`): Configuration management
6. **Tests** (`tests/`): Test suite

## Coding Standards

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Keep functions small and focused (single responsibility)

### Naming Conventions
- **Classes**: PascalCase (e.g., `ExpenseService`)
- **Functions/Methods**: snake_case (e.g., `calculate_total`)
- **Variables**: snake_case (e.g., `expense_amount`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_CATEGORIES`)
- **Files**: snake_case (e.g., `expense_service.py`)

### Import Organization
1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
import os
from datetime import datetime
from typing import List, Dict

import pandas as pd
import matplotlib.pyplot as plt

from models.expense_model import Expense
from services.database_service import DatabaseService
```

## Development Workflow

### 1. Creating New Features

1. **Create a feature branch**
```bash
git checkout -b feature/add-export-feature
```

2. **Implement the feature**
   - Write code following coding standards
   - Add tests for new functionality
   - Update documentation if needed

3. **Run tests**
```bash
python -m pytest tests/ -v
```

4. **Format and lint code**
```bash
black .
flake8 .
isort .
```

5. **Commit changes**
```bash
git add .
git commit -m "FEAT: Add export functionality with Excel formatting"
```

### 2. Adding New Dependencies

1. **Add to requirements.txt**
```bash
# Install the package
pip install package-name

# Add to requirements.txt
pip freeze | grep package-name >> requirements.txt
```

2. **Update setup.py** (if applicable)
```python
install_requires=[
    'existing-package>=1.0.0',
    'package-name>=1.0.0',  # New dependency
],
```

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_database.py -v

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test function
python -m pytest tests/test_database.py::TestDatabase::test_add_expense -v
```

### Writing Tests

1. **Test Structure**
```python
def test_function_name():
    # Arrange
    # Set up test data and conditions
    
    # Act
    # Execute the function being tested
    
    # Assert
    # Verify the results
```

2. **Example Test**
```python
def test_add_expense():
    # Arrange
    service = ExpenseService()
    expense_data = {
        'date': '2024-01-15',
        'category': 'Food',
        'amount': '50000',
        'description': 'Lunch'
    }
    
    # Act
    result = service.create_expense(**expense_data)
    
    # Assert
    assert result['success'] == True
    assert 'expense_id' in result
```

### Test Fixtures

Sample test data is provided in `tests/fixtures/`:
- Sample expense records
- Test database setup
- Mock data for different scenarios

## Database Development

### Schema Changes

1. **Create migration script** in `scripts/migrations/`
```python
# scripts/migrations/v1_1_add_receipt_column.py
import sqlite3
from pathlib import Path

def migrate():
    db_path = Path("data/expenses.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        ALTER TABLE expenses 
        ADD COLUMN receipt_path TEXT
    """)
    
    conn.commit()
    conn.close()
```

2. **Run migration**
```bash
python scripts/migrations/v1_1_add_receipt_column.py
```

### Database Backup
```bash
# Manual backup
python scripts/backup_database.py

# Restore from backup
python scripts/restore_database.py --backup-file data/backups/backup_20240115.db
```

## Code Quality Tools

### Black (Code Formatter)
```bash
# Format all code
black .

# Check formatting without changing
black --check .
```

### Flake8 (Linter)
```bash
# Run linter
flake8 .

# Specific rules to ignore
flake8 --ignore=E501,W503 .
```

### isort (Import Sorter)
```bash
# Sort imports
isort .

# Check import order
isort --check-only .
```

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## Debugging

### Logging
The application uses Python's built-in logging module:

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Debug information")
    logger.info("General information")
    logger.warning("Warning message")
    logger.error("Error occurred")
```

### Debug Mode
Run the application in debug mode:
```bash
python main.py --debug
```

### Common Debugging Commands
```bash
# Check database content
python -c "
import sqlite3
conn = sqlite3.connect('data/expenses.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM expenses')
print(f'Total expenses: {cursor.fetchone()[0]}')
conn.close()
"

# Check module imports
python -c "import sys; print(sys.path)"
```

## Performance Optimization

### Database Optimization
1. **Use indexes** for frequently queried columns
2. **Batch operations** for bulk inserts/updates
3. **Connection pooling** for frequent database access

### Memory Optimization
1. **Use generators** for large datasets
2. **Clear cache** when processing large files
3. **Close file handles** and database connections properly

## Documentation

### Code Documentation
- Write docstrings for all public functions and classes
- Use type hints
- Include examples in docstrings where helpful

### API Documentation
If adding API endpoints, document them in `docs/api.md`:
```markdown
## Expense Endpoints

### POST /expenses/
Add a new expense.

**Request Body:**
```json
{
    "date": "2024-01-15",
    "category": "Food",
    "amount": 50000,
    "description": "Lunch"
}
```

**Response:**
```json
{
    "success": true,
    "expense_id": 123,
    "message": "Expense added successfully"
}
```
```

## Deployment Preparation

### Version Bumping
1. Update version in `pyproject.toml` or `setup.py`
2. Update CHANGELOG.md
3. Tag the release
```bash
git tag v1.1.0
git push origin v1.1.0
```

### Building Packages
```bash
# Build source distribution
python setup.py sdist

# Build wheel distribution
python setup.py bdist_wheel

# Build executable (Windows)
pyinstaller --onefile --name="DailyExpenseTracker" main.py
```

## Troubleshooting

### Common Issues

1. **Import errors**
   - Check PYTHONPATH
   - Verify virtual environment is activated
   - Check __init__.py files exist in packages

2. **Database connection issues**
   - Verify data/ directory exists
   - Check file permissions
   - Ensure no other process is using the database

3. **Chart generation failures**
   - Install required system fonts
   - Check matplotlib backend configuration
   - Verify write permissions for charts/ directory

### Getting Help
1. Check application logs in `logs/`
2. Run tests to identify issues
3. Use debug mode for detailed output
4. Check existing issues on GitHub

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

---

