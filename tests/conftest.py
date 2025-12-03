#tests/test_expenses.py

"""
Unit tests for ExpenseService class
"""

import pytest
import tempfile
from pathlib import Path

@pytest.fixture(scope="session")
def temp_export_dir():
    """Create temporary export directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def clean_exports_dir():
    """Clean exports directory before test"""
    exports_dir = Path("exports")
    # Remove any test files
    for file in exports_dir.glob("test_*.csv"):
        file.unlink()
    for file in exports_dir.glob("test_*.xlsx"):
        file.unlink()
    yield