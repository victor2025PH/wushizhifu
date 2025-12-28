"""
Database module for OTC Group Management Bot
Handles SQLite database operations for admin_markup and usdt_address
"""
import sqlite3
import os
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Database connection and operations manager"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Default: use current directory or create in bot directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "otc_bot.db")
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables if they don't exist"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Create settings table for admin_markup and usdt_address
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Initialize default values if not exists
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value) 
            VALUES ('admin_markup', '0.0')
        """)
        
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value) 
            VALUES ('usdt_address', '')
        """)
        
        conn.commit()
        logger.info("Database initialized successfully")
    
    def connect(self) -> sqlite3.Connection:
        """
        Create database connection.
        
        Returns:
            SQLite connection object
        """
        if self.conn is None:
            # Ensure directory exists
            db_dir = Path(self.db_path).parent
            if db_dir and not db_dir.exists():
                db_dir.mkdir(parents=True, exist_ok=True)
            
            self.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Connected to database: {self.db_path}")
        
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")
    
    def get_admin_markup(self) -> float:
        """
        Get admin markup (floating point added to exchange rate).
        
        Returns:
            Admin markup as float (default: 0.0)
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = 'admin_markup'")
        row = cursor.fetchone()
        
        if row:
            try:
                return float(row['value'])
            except (ValueError, TypeError):
                logger.warning("Invalid admin_markup value, using default 0.0")
                return 0.0
        
        return 0.0
    
    def set_admin_markup(self, markup: float) -> bool:
        """
        Set admin markup value.
        
        Args:
            markup: Floating point value to add to exchange rate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE settings 
                SET value = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE key = 'admin_markup'
            """, (str(markup),))
            
            if cursor.rowcount == 0:
                # Insert if doesn't exist
                cursor.execute("""
                    INSERT INTO settings (key, value) 
                    VALUES ('admin_markup', ?)
                """, (str(markup),))
            
            conn.commit()
            logger.info(f"Admin markup updated to: {markup}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting admin_markup: {e}")
            return False
    
    def get_usdt_address(self) -> str:
        """
        Get USDT receiving wallet address.
        
        Returns:
            USDT wallet address (default: empty string)
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = 'usdt_address'")
        row = cursor.fetchone()
        
        if row:
            return row['value'] or ''
        
        return ''
    
    def set_usdt_address(self, address: str) -> bool:
        """
        Set USDT receiving wallet address.
        
        Args:
            address: USDT wallet address string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE settings 
                SET value = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE key = 'usdt_address'
            """, (address,))
            
            if cursor.rowcount == 0:
                # Insert if doesn't exist
                cursor.execute("""
                    INSERT INTO settings (key, value) 
                    VALUES ('usdt_address', ?)
                """, (address,))
            
            conn.commit()
            logger.info(f"USDT address updated: {address[:10]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error setting usdt_address: {e}")
            return False
    
    def get_all_settings(self) -> dict:
        """
        Get all settings as a dictionary.
        
        Returns:
            Dictionary with all settings
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        
        settings = {}
        for row in rows:
            settings[row['key']] = row['value']
        
        return settings


# Global database instance
db = Database()

