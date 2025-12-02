# daily-expense-tracker - Development Cheatsheet

## Project Setup

```bash
# Clone repository
git clone https://github.com/yourusername/daily-expense-tracker.git
cd daily-expense-tracker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 isort
```

## Git Commands

```bash
# Check status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push origin main

# Create new branch
git checkout -b feature/new-feature

# Switch branch
git checkout main

# Merge branch
git merge feature/new-feature

# View commit history
git log --oneline -10

# View changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1
```

## Running the Application

```bash
# Run main application
python main.py

# Run via runner script
python run.py

# Run with debug mode
python main.py --debug

# Run specific month view
python main.py --month 1 --year 2024

# Export data via command line
python main.py --export csv --month 1 --year 2024
```

## Testing Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_database.py -v
python -m pytest tests/test_expenses.py -v
python -m pytest tests/test_export.py -v

# Run with coverage report
python -m pytest --cov=. --cov-report=html

# Run specific test function
python -m pytest tests/test_database.py::TestDatabase::test_add_expense -v

# Run tests with debug output
python -m pytest tests/ -v -s

# Check test discovery
python -m pytest tests/ --collect-only
```

## Code Quality Tools

```bash
# Format code with Black
black .

# Check formatting without changing
black --check .

# Lint code with Flake8
flake8 .

# Lint with specific rules ignored
flake8 --ignore=E501,W503 .

# Sort imports with isort
isort .

# Check import order
isort --check-only .

# Run all quality checks
black . && flake8 . && isort --check-only .
```

## Database Operations

```bash
# Initialize database
python -c "from config.database_config import DatabaseConfig; db = DatabaseConfig(); db.initialize_database()"

# Check database content
python -c "
import sqlite3
conn = sqlite3.connect('data/expenses.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM expenses')
print(f'Total expenses: {cursor.fetchone()[0]}')
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
print('Tables:', [row[0] for row in cursor.fetchall()])
conn.close()
"

# Backup database
cp data/expenses.db data/backups/expenses_backup_$(date +%Y%m%d).db

# Reset database (WARNING: deletes all data)
rm data/expenses.db
```

## Development Utilities

```bash
# Generate project structure
python generate/file_and_folder.py

# View project structure
python generate/structure.py

# Generate sample data (if implemented)
python generate/sample_data.py

# Generate database schema (if implemented)
python generate/database_schema.py

# Generate documentation (if implemented)
python generate/documentation.py
```

## Python Interactive Testing

```python
# Quick test in Python shell
python -c "
from services.expense_service import ExpenseService
service = ExpenseService()
expenses = service.get_expenses()
print(f'Found {len(expenses)} expenses')
"

# Test validation
python -c "
from utils.validation import validate_date, validate_amount
print('Date valid:', validate_date('2024-01-15'))
print('Amount valid:', validate_amount('50000'))
"

# Test formatters
python -c "
from utils.formatters import format_currency
from decimal import Decimal
print('Formatted:', format_currency(Decimal('50000')))
"
```

## File Management

```bash
# Clean test artifacts
rm -rf tests/__pycache__
rm -rf .pytest_cache
rm -rf htmlcov
rm -rf .coverage

# Clean export files
rm -rf exports/*

# Clean chart files
rm -rf charts/*

# Clean log files
rm -rf logs/*

# Remove all generated files (except .gitkeep)
find . -name ".gitkeep" -prune -o -type f -name "*.png" -o -name "*.csv" -o -name "*.xlsx" -o -name "*.log" | xargs rm -f
```

## Package Management

```bash
# Update requirements.txt
pip freeze > requirements.txt

# Install from requirements.txt
pip install -r requirements.txt

# Install specific version
pip install matplotlib==3.7.0

# Upgrade package
pip install --upgrade package-name

# Uninstall package
pip uninstall package-name

# List installed packages
pip list

# Show package info
pip show package-name
```

## Debugging Commands

```bash
# Check Python version
python --version

# Check Python path
python -c "import sys; print(sys.path)"

# Check module availability
python -c "import matplotlib; print('matplotlib:', matplotlib.__version__)"
python -c "import pandas; print('pandas:', pandas.__version__)"
python -c "import sqlite3; print('sqlite3:', sqlite3.sqlite_version)"

# Run with detailed logging
python main.py --debug 2>&1 | tee debug.log

# Check file permissions
ls -la data/ exports/ charts/

# Check disk space
df -h .
```

## Port Management

```bash
# If port conflicts occur (for web version)
# Install kill-port utility
npm install -g kill-port

# Kill specific port
npx kill-port 8000  # Backend port
npx kill-port 3000  # Frontend port
npx kill-port 5432  # Database port

# Alternative: Find and kill process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

## Quick Development Workflow

```bash
# Typical development session
cd daily-expense-tracker
source venv/bin/activate  # or venv\Scripts\activate

# Make changes to code...

# Run tests
python -m pytest tests/ -v

# Format code
black .

# Run application to test
python main.py

# Commit changes
git add .
git commit -m "Description of changes"
git push origin main
```

## Common Error Solutions

```bash
# "Module not found" error
pip install -r requirements.txt

# "Database not found" error
mkdir -p data exports charts
python -c "from config.database_config import DatabaseConfig; db = DatabaseConfig(); db.initialize_database()"

# Permission errors
chmod 755 data exports charts  # Mac/Linux
# or run as administrator (Windows)

# Import errors in tests
export PYTHONPATH=$PWD  # Mac/Linux
set PYTHONPATH=%CD%     # Windows

# Chart generation fails
# Install system dependencies
# Ubuntu/Debian:
sudo apt-get install python3-tk
# Mac:
brew install python-tk
```

## Performance Testing

```bash
# Time application startup
time python main.py --exit

# Profile specific function
python -c "
import cProfile
import pstats
from services.expense_service import ExpenseService

profiler = cProfile.Profile()
profiler.enable()

service = ExpenseService()
service.get_expenses()

profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(10)
"

# Memory usage
python -c "
import tracemalloc
from services.expense_service import ExpenseService

tracemalloc.start()
service = ExpenseService()
expenses = service.get_expenses()
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:5]:
    print(stat)
tracemalloc.stop()
"
```

## Backup and Recovery

```bash
# Create full backup
tar -czf backup_$(date +%Y%m%d).tar.gz \
  main.py run.py requirements.txt \
  config/ models/ services/ utils/ visualization/ tests/ \
  docs/ generate/ \
  data/expenses.db

# Restore from backup
tar -xzf backup_20240115.tar.gz

# Database backup only
cp data/expenses.db data/backups/expenses_$(date +%Y%m%d_%H%M%S).db

# Configuration backup
cp .env .env.backup  # if using environment variables
```

---

## Quick Reference

### Application Options
- `python main.py` - Run application
- `python main.py --debug` - Run with debug logging
- `python main.py --month 1 --year 2024` - View specific month
- `python main.py --export csv` - Export data

### Testing Shortcuts
- `pytest tests/` - Quick test run
- `pytest -k "test_database"` - Run tests with "database" in name
- `pytest --tb=short` - Short traceback format

### Git Shortcuts
- `git commit -am "msg"` - Add and commit tracked files
- `git stash` - Temporarily save changes
- `git stash pop` - Restore stashed changes
- `git log --oneline --graph` - Visual commit history

### Python Shortcuts
- `python -m http.server` - Start simple HTTP server
- `python -m json.tool file.json` - Pretty print JSON
- `python -m pydoc module` - View module documentation

---

*Last updated: January 2024*