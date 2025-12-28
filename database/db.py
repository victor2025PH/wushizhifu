"""
Database connection and initialization
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses botA's database.
        """
        if db_path is None:
            # Use botA's database to ensure consistency
            # Default to botA/wushipay.db if it exists, otherwise root wushipay.db
            botA_db = Path(__file__).parent.parent / "botA" / "wushipay.db"
            root_db = Path(__file__).parent.parent / "wushipay.db"
            
            if botA_db.exists():
                self.db_path = str(botA_db)
                logger.info(f"Using Bot A database: {self.db_path}")
            elif root_db.exists():
                self.db_path = str(root_db)
                logger.info(f"Using root database: {self.db_path}")
            else:
                # Default to botA path for new installations
                self.db_path = str(botA_db)
                logger.info(f"Creating new database at: {self.db_path}")
        else:
            self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
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
    
    def execute(self, query: str, params: tuple = ()):
        """
        Execute a query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Cursor object
        """
        conn = self.connect()
        return conn.execute(query, params)
    
    def executemany(self, query: str, params_list: list):
        """
        Execute a query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Cursor object
        """
        conn = self.connect()
        return conn.executemany(query, params_list)
    
    def commit(self):
        """Commit current transaction"""
        if self.conn:
            self.conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return self.connect()


# Global database instance
db = Database()

