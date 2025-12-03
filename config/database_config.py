#Github\project portofolio\junior project\daily-expense-tracker\config\database_config.py

"""
Database Configuration for daily-expense-tracker
Handles SQLite database setup and connection management
"""

import sqlite3
import logging
import shutil
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    def __init__(self, db_name: str = "expenses.db"):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.db_path = self.data_dir / db_name
        
        self.data_dir.mkdir(exist_ok=True)
        logger.info(f"Database path: {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    @contextmanager
    def get_connection_context(self):
        """Context manager version for use with 'with' statement"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def initialize_database(self) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    budget_limit DECIMAL(10,2) DEFAULT NULL CHECK (budget_limit >= 0),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category)')
            
            default_categories = [
                ('Makanan & Minuman', 0, 'Pengeluaran untuk makanan dan minuman'),
                ('Transportasi', 0, 'Biaya transportasi'),
                ('Belanja', 0, 'Belanja kebutuhan sehari-hari'),
                ('Hiburan', 0, 'Pengeluaran hiburan dan rekreasi'),
                ('Kesehatan', 0, 'Biaya kesehatan dan obat-obatan'),
                ('Pendidikan', 0, 'Biaya pendidikan dan kursus'),
                ('Tagihan', 0, 'Pembayaran tagihan rutin'),
                ('Lain-lain', 0, 'Pengeluaran lainnya')
            ]
            
            for category in default_categories:
                cursor.execute(
                    '''INSERT OR IGNORE INTO categories (name, budget_limit, description) 
                       VALUES (?, ?, ?)''',
                    category
                )
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            return False
    
    def backup_database(self, backup_name: str = None) -> bool:
        if not self.db_path.exists():
            logger.warning("Database file does not exist")
            return False
        
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"expenses_backup_{timestamp}.db"
        
        backup_path = self.data_dir / backup_name
        
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def get_database_info(self) -> dict:
        info = {
            'path': str(self.db_path),
            'exists': self.db_path.exists(),
            'size_bytes': 0,
            'tables': []
        }
        
        if self.db_path.exists():
            info['size_bytes'] = self.db_path.stat().st_size
            
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                info['tables'] = [table['name'] for table in tables]
                
                for table in info['tables']:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    count = cursor.fetchone()['count']
                    info[f'{table}_count'] = count
                
                conn.close()
                    
            except sqlite3.Error as e:
                logger.error(f"Error getting database info: {e}")
        
        return info


def test_database():
    print("Testing database configuration...")
    
    db_config = DatabaseConfig("test_expenses.db")
    
    if db_config.initialize_database():
        print("Database initialized successfully")
    else:
        print("Database initialization failed")
        return
    
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        print(f"Found {len(tables)} tables")
        
        for table in tables:
            print(f"  - {table['name']}")
            
    except Exception as e:
        print(f"Connection test failed: {e}")
    
    info = db_config.get_database_info()
    print(f"Database Information:")
    print(f"  Path: {info['path']}")
    print(f"  Size: {info['size_bytes'] / 1024:.2f} KB")
    print(f"  Tables: {', '.join(info['tables'])}")
    
    if db_config.backup_database():
        print("Backup created successfully")


if __name__ == "__main__":
    test_database()