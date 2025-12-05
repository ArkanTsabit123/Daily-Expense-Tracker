#root/run.py
"""
Daily Expense Tracker - Alternative Entry Point
"""

import os
import sys

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import main

    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Error: {e}")
    print("\nMake sure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
