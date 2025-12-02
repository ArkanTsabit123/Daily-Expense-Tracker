# daily-expense-tracker - Deployment Guide

## Deployment Options

### Option 1: Simple Python Script (Recommended for Users)
```bash
# 1. Install Python dependencies
pip install matplotlib pandas openpyxl

# 2. Run the application
python main.py
```

### Option 2: Standalone Executable (No Python Required)

#### Windows (.exe file)
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --name="DailyExpenseTracker" main.py
# Output: dist/DailyExpenseTracker.exe
```

#### macOS (.app bundle)
```bash
# Create macOS application
pyinstaller --windowed --name="daily-expense-tracker" main.py
# Output: dist/daily-expense-tracker.app
```

#### Linux
```bash
# Create Linux executable
pyinstaller --onefile --name="daily-expense-tracker" main.py
# Output: dist/daily-expense-tracker
```

### Option 3: Virtual Environment (Recommended for Developers)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Deployment Package Structure

When distributing the application, include this structure:

```
DailyExpenseTracker-v1.0.0/
├── DailyExpenseTracker.exe    # or main.py for source distribution
├── requirements.txt           # Python dependencies
├── README.txt                # Simple instructions
├── data/                     # Will be created automatically
├── exports/                  # Will be created automatically
└── charts/                   # Will be created automatically
```

## Installation Scripts

### Windows Installation Script (install.bat)
```batch
@echo off
echo Installing daily-expense-tracker...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate and install dependencies
echo Installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist data mkdir data
if not exist exports mkdir exports
if not exist charts mkdir charts

echo.
echo Installation complete!
echo.
echo To run the application:
echo 1. venv\Scripts\activate
echo 2. python main.py
echo.
pause
```

### Mac/Linux Installation Script (install.sh)
```bash
#!/bin/bash
echo "Installing daily-expense-tracker..."

# Check Python 3 installation
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data exports charts

echo ""
echo "Installation complete!"
echo ""
echo "To run the application:"
echo "1. source venv/bin/activate"
echo "2. python main.py"
```

## Python Package Distribution

### Creating a Python Package

Create `setup.py`:
```python
from setuptools import setup, find_packages

setup(
    name="daily-expense-tracker",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python application for tracking daily expenses",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/daily-expense-tracker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "matplotlib>=3.7.0",
        "pandas>=2.0.0",
        "openpyxl>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "expense-tracker=main:main",
        ],
    },
    include_package_data=True,
)
```

### Building and Distributing

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Upload to Test PyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

### Installing from PyPI
```bash
pip install daily-expense-tracker
expense-tracker
```

## Platform-Specific Deployment

### Windows Installer with Inno Setup

1. Download Inno Setup from https://jrsoftware.org/isinfo.php
2. Create `setup.iss` script:
```iss
[Setup]
AppName=daily-expense-tracker
AppVersion=1.0.0
DefaultDirName={pf}\daily-expense-tracker
DefaultGroupName=daily-expense-tracker
OutputDir=installer
OutputBaseFilename=DailyExpenseTrackerSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\DailyExpenseTracker.exe"; DestDir: "{app}"
Source: "requirements.txt"; DestDir: "{app}"
Source: "README.txt"; DestDir: "{app}"
Source: "data\*"; DestDir: "{app}\data"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\daily-expense-tracker"; Filename: "{app}\DailyExpenseTracker.exe"
Name: "{commondesktop}\daily-expense-tracker"; Filename: "{app}\DailyExpenseTracker.exe"
```

3. Compile with ISCC.exe

### Linux .deb Package
```bash
# Install required tools
sudo apt install dh-python

# Create .deb package
python setup.py --command-packages=stdeb.command bdist_deb
# Output: deb_dist/daily-expense-tracker_1.0.0-1_all.deb

# Install the package
sudo dpkg -i deb_dist/daily-expense-tracker_1.0.0-1_all.deb
```

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for matplotlib
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data exports charts

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run application
CMD ["python", "main.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  expense-tracker:
    build: .
    container_name: daily-expense-tracker
    volumes:
      - ./data:/app/data
      - ./exports:/app/exports
      - ./charts:/app/charts
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    stdin_open: true
    tty: true
```

### Docker Commands
```bash
# Build Docker image
docker build -t expense-tracker .

# Run container
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/exports:/app/exports \
  -v $(pwd)/charts:/app/charts \
  expense-tracker

# Using docker-compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Web Deployment Options (Future Enhancements)

### Streamlit Web Application
Create `web_app.py`:
```python
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="daily-expense-tracker", layout="wide")
st.title("daily-expense-tracker - Web Version")

# Add web interface code here
```

Run with:
```bash
pip install streamlit
streamlit run web_app.py
```

### FastAPI Backend + Frontend
Create `api/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="daily-expense-tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Expense(BaseModel):
    date: str
    category: str
    amount: float
    description: str = ""

@app.get("/")
async def root():
    return {"message": "daily-expense-tracker API"}

@app.get("/expenses/")
async def get_expenses():
    # Implement expense retrieval
    return {"expenses": []}
```

Run with:
```bash
pip install fastapi uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Cloud Deployment

### Heroku
Create `Procfile`:
```
web: python main.py
```

Create `runtime.txt`:
```
python-3.11.0
```

Deployment commands:
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-expense-tracker

# Deploy
git push heroku main

# Open app
heroku open
```

### Railway.app
Create `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### PythonAnywhere
1. Upload files via web interface or Git
2. Create virtual environment
3. Install requirements
4. Configure web app or scheduled tasks

## Version Management

### Creating Releases
```bash
# Tag the release
git tag v1.0.0
git push origin v1.0.0

# Create release package
tar -czf DailyExpenseTracker-v1.0.0.tar.gz \
  main.py run.py requirements.txt setup.py \
  config/ models/ services/ utils/ visualization/ \
  docs/ README.md

# Create Windows zip
zip -r DailyExpenseTracker-v1.0.0.zip \
  main.py run.py requirements.txt \
  config/ models/ services/ utils/ visualization/ \
  docs/ README.md
```

### Version Bumping
Update version in:
1. `setup.py` (version field)
2. `pyproject.toml` (if using)
3. Documentation files
4. Main application (optional)

## Database Migration for Updates

Create migration script `migrate_v1_to_v2.py`:
```python
import sqlite3
from pathlib import Path

def migrate():
    db_path = Path("data/expenses.db")
    if not db_path.exists():
        print("Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add new columns
    try:
        cursor.execute("ALTER TABLE expenses ADD COLUMN receipt_path TEXT")
        print("Added receipt_path column")
    except sqlite3.OperationalError:
        print("receipt_path column already exists")
    
    # Update existing data if needed
    # cursor.execute("UPDATE expenses SET column = value WHERE condition")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully")

if __name__ == "__main__":
    migrate()
```

## Security Considerations

### Database Protection
- Store database in `data/` directory
- Add `.gitkeep` but don't commit actual `.db` files
- Consider encryption for sensitive data (future enhancement)

### File Permissions
```bash
# Set appropriate permissions
chmod 700 data/          # Read/write/execute for owner only
chmod 755 exports/ charts/  # Read/execute for others
chmod 644 *.py           # Read for others

# Windows equivalent (using icacls)
icacls data /inheritance:r /grant:r "%USERNAME%:(OI)(CI)F"
```

### Input Validation
- Always validate user input before processing
- Sanitize file paths to prevent directory traversal
- Use parameterized SQL queries to prevent injection

## Deployment Checklist

Before distributing your application:

- [ ] Test on target platform (Windows/macOS/Linux)
- [ ] Verify all dependencies are included
- [ ] Test database creation and migration
- [ ] Verify export functionality works
- [ ] Test chart generation and saving
- [ ] Update version number
- [ ] Update `requirements.txt` with exact versions
- [ ] Create or update documentation
- [ ] Test installation script
- [ ] Create sample data for demonstration
- [ ] Remove any debug or test code
- [ ] Verify no sensitive data is included
- [ ] Check file sizes are reasonable
- [ ] Test upgrade path from previous version

## Post-Deployment Support

### Log Files
Application logs are stored in `logs/` directory:
- `app.log` - General application logs
- `error.log` - Error logs
- `debug.log` - Debug information (when debug mode enabled)

### Troubleshooting Guide

1. **"Module not found" error**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database permission error**
   - Ensure `data/` directory exists and is writable
   - Run as administrator if needed (Windows)

3. **Chart generation fails**
   - Install required system fonts
   - Check write permissions for `charts/` directory

4. **Excel export fails**
   - Ensure openpyxl is installed: `pip install openpyxl`
   - Check available disk space

### Support Channels
1. Application logs in `logs/` directory
2. Console error messages
3. Documentation in `docs/` directory
4. GitHub issues (if using GitHub)

## Quick Deployment Reference

```bash
# For end users (simplest):
pip install matplotlib pandas openpyxl
python main.py

# For developers:
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
python main.py

# For package distribution:
python setup.py sdist
# Upload to PyPI or share .tar.gz file

# For executable distribution:
pyinstaller --onefile --name="DailyExpenseTracker" main.py
# Share dist/DailyExpenseTracker.exe
```

---

*Note: Always test the deployment process thoroughly before distributing to users.*