#Github\project portofolio\junior project\daily-expense-tracker\config\logging_config.py

"""
Logging Configuration
Sets up logging for the daily-expense-tracker application
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime

class ExpenseTrackerLogger:
    def __init__(self, log_dir=None):
        self.project_root = Path(__file__).parent.parent
        
        if log_dir is None:
            self.log_dir = self.project_root / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        self.log_dir.mkdir(exist_ok=True)
        self._setup_logging()
        self.logger = logging.getLogger("expense_tracker")
    
    def _setup_logging(self):
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(funcName)s - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        log_file = self.log_dir / f"expense_tracker_{datetime.now().strftime('%Y%m')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        error_file = self.log_dir / "errors.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        app_file = self.log_dir / "application.log"
        app_handler = logging.FileHandler(app_file, encoding='utf-8')
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(simple_formatter)
        
        rotating_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "rotating.log",
            maxBytes=5*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        rotating_handler.setLevel(logging.INFO)
        rotating_handler.setFormatter(simple_formatter)
        
        root_logger.setLevel(logging.DEBUG)
        
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(app_handler)
        root_logger.addHandler(rotating_handler)
    
    def log_application_start(self, version="1.0.0"):
        self.logger.info("=" * 60)
        self.logger.info(f"Expense Tracker Application Started")
        self.logger.info(f"Version: {version}")
        self.logger.info(f"Log Directory: {self.log_dir}")
        self.logger.info(f"Python Version: {sys.version}")
        self.logger.info("=" * 60)
    
    def log_application_stop(self):
        self.logger.info("=" * 60)
        self.logger.info("Expense Tracker Application Stopped")
        self.logger.info("=" * 60)
    
    def log_database_operation(self, operation, details):
        self.logger.debug(f"Database {operation}: {details}")
    
    def log_expense_creation(self, expense_data):
        self.logger.info(f"Expense created: {expense_data}")
    
    def log_expense_update(self, expense_id, old_data, new_data):
        self.logger.info(f"Expense {expense_id} updated: from {old_data} to {new_data}")
    
    def log_expense_deletion(self, expense_id):
        self.logger.warning(f"Expense {expense_id} deleted")
    
    def log_error(self, error, context=""):
        self.logger.error(f"{context}: {str(error)}", exc_info=True)
    
    def log_warning(self, warning, context=""):
        self.logger.warning(f"{context}: {warning}")
    
    def get_log_stats(self):
        stats = {
            'log_directory': str(self.log_dir),
            'log_files': [],
            'total_size_bytes': 0
        }
        
        if self.log_dir.exists():
            for log_file in self.log_dir.glob("*.log"):
                file_stat = log_file.stat()
                stats['log_files'].append({
                    'name': log_file.name,
                    'size_bytes': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                })
                stats['total_size_bytes'] += file_stat.st_size
        
        return stats

def setup_simple_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def test_logger():
    print("Testing logger setup...")
    
    logger = ExpenseTrackerLogger()
    
    logger.logger.debug("This is a debug message")
    logger.logger.info("This is an info message")
    logger.logger.warning("This is a warning message")
    logger.logger.error("This is an error message")
    
    logger.log_application_start("1.0.0")
    
    expense_data = {
        "date": "2024-01-15",
        "category": "Food",
        "amount": 25000,
        "description": "Lunch"
    }
    logger.log_expense_creation(expense_data)
    
    try:
        raise ValueError("Test error for logging")
    except ValueError as e:
        logger.log_error(e, "Test error context")
    
    stats = logger.get_log_stats()
    print(f"Log Statistics:")
    print(f"Log Directory: {stats['log_directory']}")
    print(f"Total Size: {stats['total_size_bytes'] / 1024:.2f} KB")
    print(f"Log Files: {len(stats['log_files'])}")
    
    logger.log_application_stop()
    print("Logger test completed")

if __name__ == "__main__":
    test_logger()