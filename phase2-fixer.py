#daily-expense-tracker/phase2-fixer.py

"""
This module applies fixes for phase 2 issues in the daily-expense-tracker project.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent

def fix_database_config_connection():
    config_path = project_root / "config" / "database_config.py"
    if not config_path.exists():
        print("database_config.py not found")
        return False
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "@contextmanager" in content and "def get_connection(self)" in content:
        lines = content.split("\n")
        method_start = -1
        for i, line in enumerate(lines):
            if "def get_connection(self)" in line:
                method_start = i
                break
        if method_start == -1:
            print("get_connection method not found")
            return False
        method_end = method_start
        for i in range(method_start + 1, len(lines)):
            if lines[i].strip() == "" or (lines[i].startswith("    ") and "def " in lines[i]):
                method_end = i
                break
            if i == len(lines) - 1:
                method_end = len(lines)
        new_method = """    def get_connection(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise"""
        for i in range(method_start - 1, max(-1, method_start - 3), -1):
            if "@contextmanager" in lines[i]:
                lines[i] = ""
                break
        lines = lines[:method_start] + [new_method] + lines[method_end:]
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("Fixed get_connection() in database_config.py")
        return True
    print("get_connection() already fixed")
    return True

def fix_validation_parse_amount():
    validation_path = project_root / "utils" / "validation.py"
    if not validation_path.exists():
        print("validation.py not found")
        return False
    with open(validation_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "def parse_amount" not in content:
        print("parse_amount() not found")
        return False
    lines = content.split("\n")
    fixed_lines = []
    parse_amount_func = """def parse_amount(amount_string: str) -> Decimal:
    try:
        cleaned = re.sub(r'[^\\d.,]', '', amount_string)
        cleaned = cleaned.replace(',', '.')
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return Decimal('0')"""
    in_parse_amount = False
    parse_amount_start = -1
    for i, line in enumerate(lines):
        if "def parse_amount" in line:
            in_parse_amount = True
            parse_amount_start = i
            fixed_lines.append(parse_amount_func)
        elif in_parse_amount and line.strip() == "" and i > parse_amount_start:
            in_parse_amount = False
            fixed_lines.append(line)
        elif not in_parse_amount:
            fixed_lines.append(line)
    if parse_amount_start != -1:
        with open(validation_path, "w", encoding="utf-8") as f:
            f.write("\n".join(fixed_lines))
        print("Fixed parse_amount() function")
        return True
    return False

def verify_fixes():
    print("\nRunning verification tests...")
    test_results = []
    try:
        sys.path.insert(0, str(project_root))
        from config.database_config import DatabaseConfig

        db_config = DatabaseConfig()
        conn = db_config.get_connection()
        if hasattr(conn, "cursor"):
            print("Database connection test passed")
            test_results.append(True)
            conn.close()
        else:
            test_results.append(False)
    except Exception as e:
        print(f"Database connection test failed: {e}")
        test_results.append(False)
    try:
        from utils.validation import parse_amount

        parse_amount("50000")
        print("Validation parse_amount test passed")
        test_results.append(True)
    except Exception as e:
        print(f"Validation parse_amount test failed: {e}")
        test_results.append(False)
    try:
        from services.database_service import DatabaseService

        DatabaseService()
        print("Database service import test passed")
        test_results.append(True)
    except Exception as e:
        print(f"Database service import test failed: {e}")
        test_results.append(False)
    return all(test_results)

def main():
    print("=" * 60)
    print("Phase 2 Fixer")
    print("=" * 60)
    print("/n1. Fixing database_config.py...")
    fix_database_config_connection()
    print("/n2. Fixing validation.py...")
    fix_validation_parse_amount()
    print("\n3. Verifying fixes...")
    if verify_fixes():
        print("\n" + "=" * 60)
        print("All fixes applied successfully")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Some fixes may need manual review")
        print("=" * 60)
    print("/nRun: python phase2-verify.py")

if __name__ == "__main__":
    main()
