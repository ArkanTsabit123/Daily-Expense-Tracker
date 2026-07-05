# reset_data.py
"""
Database Reset Utility for Daily Expense Tracker
Completely removes all data and resets the application to fresh state
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

ROOT_DIR = Path(__file__).parent

# Files and folders to reset
FILES_TO_REMOVE = [
    ROOT_DIR / "data" / "expenses.db",
    ROOT_DIR / "expense_tracker.db",
    ROOT_DIR / "sample_expenses.db",
    ROOT_DIR / "test.db",
]

DIRS_TO_CLEAN = [
    ROOT_DIR / "exports",
    ROOT_DIR / "charts",
    ROOT_DIR / "logs",
    ROOT_DIR / "backups",
]

FILE_PATTERNS_TO_REMOVE = [
    "*.db",
    "*.db-journal",
    "*.csv",
    "*.xlsx",
    "*.xls",
    "*.png",
    "*.jpg",
    "*.log",
]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f" {text}".center(70))
    print("=" * 70)


def print_step(text: str):
    """Print step with formatting"""
    print(f"\n🔹 {text}")


def print_success(text: str):
    """Print success message"""
    print(f"   ✅ {text}")


def print_warning(text: str):
    """Print warning message"""
    print(f"   ⚠️  {text}")


def print_error(text: str):
    """Print error message"""
    print(f"   ❌ {text}")


def confirm_action(prompt: str, default: str = "n") -> bool:
    """Ask for user confirmation"""
    choices = "[Y/n]" if default.lower() == "y" else "[y/N]"
    response = input(f"\n{prompt} {choices}: ").strip().lower()
    
    if not response:
        return default.lower() == "y"
    
    return response in ["y", "yes"]


# ============================================================
# MAIN FUNCTIONS
# ============================================================

def close_database_connections():
    """Try to close any open database connections"""
    print_step("Closing database connections...")
    
    # Force garbage collection
    import gc
    gc.collect()
    
    # Try to find and close any sqlite connections
    for obj in gc.get_objects():
        try:
            if isinstance(obj, sqlite3.Connection):
                try:
                    obj.close()
                except:
                    pass
        except:
            pass
    
    print_success("Connections closed")


def remove_files():
    """Remove database files"""
    print_step("Removing database files...")
    
    removed_count = 0
    for file_path in FILES_TO_REMOVE:
        if file_path.exists():
            try:
                file_path.unlink()
                print_success(f"Removed: {file_path}")
                removed_count += 1
            except PermissionError:
                print_error(f"Cannot remove {file_path} - file in use")
            except Exception as e:
                print_error(f"Error removing {file_path}: {e}")
        else:
            print(f"   ℹ️  Not found: {file_path}")
    
    return removed_count


def clean_directories():
    """Clean directories by removing content"""
    print_step("Cleaning directories...")
    
    cleaned_count = 0
    for dir_path in DIRS_TO_CLEAN:
        if dir_path.exists():
            try:
                # Remove all files in directory
                for item in dir_path.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    except PermissionError:
                        print_warning(f"Cannot remove {item} - file in use")
                    except Exception as e:
                        print_warning(f"Error removing {item}: {e}")
                
                print_success(f"Cleaned: {dir_path}/")
                cleaned_count += 1
            except Exception as e:
                print_error(f"Error cleaning {dir_path}: {e}")
        else:
            # Create empty directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ℹ️  Created: {dir_path}/")
    
    return cleaned_count


def remove_patterns():
    """Remove files matching patterns"""
    print_step("Removing files by patterns...")
    
    removed_count = 0
    for pattern in FILE_PATTERNS_TO_REMOVE:
        for file_path in ROOT_DIR.rglob(pattern):
            # Skip if in __pycache__ or venv
            if "__pycache__" in str(file_path) or "venv" in str(file_path) or ".venv" in str(file_path):
                continue
            
            # Skip if in root patterns (already handled)
            if file_path.parent == ROOT_DIR and file_path.name.endswith(".db"):
                continue
            
            try:
                if file_path.is_file():
                    file_path.unlink()
                    removed_count += 1
            except PermissionError:
                print_warning(f"Cannot remove {file_path} - file in use")
            except Exception as e:
                print_warning(f"Error removing {file_path}: {e}")
    
    if removed_count > 0:
        print_success(f"Removed {removed_count} files")


def create_directories():
    """Create necessary directories"""
    print_step("Creating necessary directories...")
    
    directories = [
        ROOT_DIR / "data",
        ROOT_DIR / "exports",
        ROOT_DIR / "charts",
        ROOT_DIR / "logs",
        ROOT_DIR / "backups",
        ROOT_DIR / "screenshots",
    ]
    
    created_count = 0
    for dir_path in directories:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Created: {dir_path}/")
            created_count += 1
        else:
            print(f"   ℹ️  Already exists: {dir_path}/")
    
    return created_count


def initialize_database():
    """Initialize fresh database"""
    print_step("Initializing fresh database...")
    
    try:
        # Import and initialize
        from services.database_service import DatabaseService
        
        db_service = DatabaseService()
        print_success("Database initialized successfully")
        return True
    except ImportError as e:
        print_error(f"Cannot import DatabaseService: {e}")
        return False
    except Exception as e:
        print_error(f"Error initializing database: {e}")
        return False


def show_summary(
    files_removed: int,
    dirs_cleaned: int,
    dirs_created: int,
    db_initialized: bool
):
    """Show reset summary"""
    print_header("RESET COMPLETE")
    
    print(f"\n📊 Reset Summary:")
    print(f"   🗑️  Files removed: {files_removed}")
    print(f"   📁 Directories cleaned: {dirs_cleaned}")
    print(f"   📁 Directories created: {dirs_created}")
    print(f"   💾 Database initialized: {'✅' if db_initialized else '❌'}")
    
    print("\n📋 Next Steps:")
    print("   1. Run 'python utils/dummy_data.py --preview' to generate sample data")
    print("   2. Run 'python gui.py' to launch the application")
    print("   3. Run 'python check_db.py' to verify the database")


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    """Main entry point"""
    print_header("DAILY EXPENSE TRACKER - DATA RESET")
    print(f"📁 Project: {ROOT_DIR}")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n⚠️  WARNING: This will DELETE ALL DATA!")
    print("   - All expenses, incomes, budgets, and tags will be removed")
    print("   - Export files, charts, and logs will be cleaned")
    print("   - Database will be recreated from scratch")
    
    if not confirm_action("Are you sure you want to continue?"):
        print("\n❌ Reset cancelled.")
        sys.exit(0)
    
    print_header("STARTING RESET PROCESS")
    
    # Step 1: Close connections
    close_database_connections()
    
    # Step 2: Remove database files
    files_removed = remove_files()
    
    # Step 3: Clean directories
    dirs_cleaned = clean_directories()
    
    # Step 4: Remove by patterns
    remove_patterns()
    
    # Step 5: Create directories
    dirs_created = create_directories()
    
    # Step 6: Initialize database
    db_initialized = initialize_database()
    
    # Show summary
    show_summary(files_removed, dirs_cleaned, dirs_created, db_initialized)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Reset interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)