# !/usr/bin/env python3
"""
Test helper utilities
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_test_expense():
    """Create a test expense dictionary"""
    return {
        "date": "2024-12-01",
        "category": "Food",
        "amount": 50000,
        "description": "Test expense",
    }

def create_test_category():
    """Create a test category dictionary"""
    return {"name": "Test Category", "budget_limit": 100000}
