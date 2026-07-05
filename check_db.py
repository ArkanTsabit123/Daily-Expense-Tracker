# check_db.py
"""
Database Checker for Daily Expense Tracker
View all tables, schemas, and data counts
"""

import sqlite3
from pathlib import Path

DB_PATH = "data/expenses.db"


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f" {text}".center(70))
    print("=" * 70)


def get_primary_key(cursor, table_name):
    """Get primary key column name for a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        if col[5] == 1:  # pk flag
            return col[1]
    return "id"  # fallback


def check_database():
    """Check database structure and content"""
    
    if not Path(DB_PATH).exists():
        print(f"❌ Database not found: {DB_PATH}")
        print("📌 Run the application first to create the database")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print_header("DAILY EXPENSE TRACKER - DATABASE CHECK")
    print(f"📁 Database: {DB_PATH}")
    print(f"📅 Check Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ============================================================
    # 1. LIST ALL TABLES
    # ============================================================
    print_header("1. TABLES")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    
    if tables:
        print(f"📋 Total tables: {len(tables)}")
        for table in tables:
            print(f"   📄 {table}")
    else:
        print("❌ No tables found!")
    
    # ============================================================
    # 2. TABLE SCHEMAS
    # ============================================================
    print_header("2. TABLE SCHEMAS")
    
    for table in tables:
        print(f"\n📋 Table: {table}")
        print("-" * 50)
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        print(f"{'Column':<25} {'Type':<15} {'Null':<10} {'Default':<15} {'PK':<5}")
        print("-" * 70)
        for col in columns:
            cid, name, data_type, notnull, default, pk = col
            null_text = "YES" if notnull == 0 else "NO"
            pk_text = "✅" if pk == 1 else ""
            print(f"{name:<25} {data_type:<15} {null_text:<10} {str(default) if default else '-':<15} {pk_text}")
        
        # Count rows
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"\n   📊 Total rows: {count}")
    
    # ============================================================
    # 3. DATA PREVIEW
    # ============================================================
    print_header("3. DATA PREVIEW")
    
    for table in tables:
        print(f"\n📋 {table} (last 5 rows)")
        print("-" * 70)
        
        # Get primary key column
        pk_column = get_primary_key(cursor, table)
        
        try:
            # Try to order by primary key
            cursor.execute(f"SELECT * FROM {table} ORDER BY {pk_column} DESC LIMIT 5")
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            # If no primary key, just get any 5 rows
            cursor.execute(f"SELECT * FROM {table} LIMIT 5")
            rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        if rows:
            # Print headers
            header = " | ".join([f"{col:<15}" for col in columns])
            print(header)
            print("-" * len(header))
            
            # Print rows
            for row in rows:
                row_str = " | ".join([str(val)[:15] if val else "-" for val in row])
                print(row_str)
        else:
            print("   📭 No data")
    
    # ============================================================
    # 4. STATISTICS SUMMARY
    # ============================================================
    print_header("4. STATISTICS SUMMARY")
    
    total_records = 0
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total_records += count
        print(f"   📊 {table:<20} : {count:>6} records")
    
    print("-" * 35)
    print(f"   📊 TOTAL{' '*17}: {total_records:>6} records")
    
    # ============================================================
    # 5. DATABASE SIZE
    # ============================================================
    print_header("5. DATABASE INFO")
    
    db_size = Path(DB_PATH).stat().st_size
    if db_size > 1024 * 1024:
        size_str = f"{db_size / (1024 * 1024):.2f} MB"
    elif db_size > 1024:
        size_str = f"{db_size / 1024:.2f} KB"
    else:
        size_str = f"{db_size} bytes"
    
    print(f"   💾 Database size: {size_str}")
    
    # Get last modified
    import os
    from datetime import datetime
    last_modified = datetime.fromtimestamp(os.path.getmtime(DB_PATH))
    print(f"   🕐 Last modified: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ============================================================
    # 6. INDEXES
    # ============================================================
    print_header("6. INDEXES")
    
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' ORDER BY name;")
    indexes = cursor.fetchall()
    
    if indexes:
        print(f"📋 Total indexes: {len(indexes)}")
        for idx in indexes:
            print(f"   🔍 {idx[0]}")
            if idx[1]:
                print(f"      {idx[1][:60]}...")
    else:
        print("   ℹ️  No indexes found")
    
    # ============================================================
    # 7. SAMPLE DATA (Expenses by Category)
    # ============================================================
    if 'expenses' in tables:
        print_header("7. EXPENSES BY CATEGORY")
        
        cursor.execute("""
            SELECT category, COUNT(*) as count, SUM(amount) as total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        """)
        rows = cursor.fetchall()
        
        if rows:
            print(f"\n{'Category':<20} {'Count':<10} {'Total':<15}")
            print("-" * 50)
            for row in rows:
                print(f"{row[0]:<20} {row[1]:<10} Rp {row[2]:>10,.0f}")
        else:
            print("   📭 No expenses data")
    
    # ============================================================
    # 8. SAMPLE DATA (Incomes by Source)
    # ============================================================
    if 'incomes' in tables:
        print_header("8. INCOMES BY SOURCE")
        
        cursor.execute("""
            SELECT source, COUNT(*) as count, SUM(amount) as total
            FROM incomes
            GROUP BY source
            ORDER BY total DESC
        """)
        rows = cursor.fetchall()
        
        if rows:
            print(f"\n{'Source':<20} {'Count':<10} {'Total':<15}")
            print("-" * 50)
            for row in rows:
                print(f"{row[0]:<20} {row[1]:<10} Rp {row[2]:>10,.0f}")
        else:
            print("   📭 No incomes data")
    
    # ============================================================
    # 9. SUMMARY
    # ============================================================
    print_header("✅ DATABASE CHECK COMPLETE")
    
    # Check if database has minimum data
    if 'expenses' in tables:
        cursor.execute("SELECT COUNT(*) FROM expenses")
        exp_count = cursor.fetchone()[0]
        if exp_count > 0:
            print("✅ Expenses: Have data")
        else:
            print("⚠️  Expenses: Empty (run dummy_data.py to populate)")
    
    if 'incomes' in tables:
        cursor.execute("SELECT COUNT(*) FROM incomes")
        inc_count = cursor.fetchone()[0]
        if inc_count > 0:
            print("✅ Incomes: Have data")
        else:
            print("⚠️  Incomes: Empty (run add_income.py or dummy_data.py)")
    
    if 'budgets' in tables:
        cursor.execute("SELECT COUNT(*) FROM budgets")
        bud_count = cursor.fetchone()[0]
        if bud_count > 0:
            print("✅ Budgets: Have data")
        else:
            print("⚠️  Budgets: Empty (set budgets in application)")
    
    conn.close()


if __name__ == "__main__":
    check_database()