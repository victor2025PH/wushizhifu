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
        
        # Create group_settings table for group-level markup and address
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id BIGINT NOT NULL UNIQUE,
                group_title TEXT,
                markup REAL DEFAULT 0.0,
                usdt_address TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by BIGINT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_group_settings_group_id 
            ON group_settings(group_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_group_settings_active 
            ON group_settings(is_active)
        """)
        
        # Create transactions table for settlement records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE,
                group_id BIGINT,
                user_id BIGINT NOT NULL,
                username TEXT,
                first_name TEXT,
                cny_amount REAL NOT NULL,
                usdt_amount REAL NOT NULL,
                exchange_rate REAL NOT NULL,
                markup REAL,
                usdt_address TEXT,
                status TEXT DEFAULT 'pending',
                payment_hash TEXT,
                paid_at TIMESTAMP,
                confirmed_at TIMESTAMP,
                cancelled_at TIMESTAMP,
                cancelled_by BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add paid_at column if it doesn't exist (migration for existing databases)
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'paid_at' not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN paid_at TIMESTAMP")
        if 'cancelled_at' not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN cancelled_at TIMESTAMP")
        if 'cancelled_by' not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN cancelled_by BIGINT")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_group_id 
            ON transactions(group_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
            ON transactions(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_created_at 
            ON transactions(created_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_group_date 
            ON transactions(group_id, DATE(created_at))
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_status 
            ON transactions(status)
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
    
    # ========== Group Settings Methods ==========
    
    def get_group_setting(self, group_id: int) -> Optional[dict]:
        """
        Get group-specific settings.
        
        Args:
            group_id: Telegram group ID
            
        Returns:
            Dictionary with group settings or None if not configured
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT group_id, group_title, markup, usdt_address, is_active, 
                   updated_at, updated_by
            FROM group_settings 
            WHERE group_id = ? AND is_active = 1
        """, (group_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'group_id': row['group_id'],
                'group_title': row['group_title'],
                'markup': float(row['markup']) if row['markup'] else 0.0,
                'usdt_address': row['usdt_address'] or '',
                'is_active': bool(row['is_active']),
                'updated_at': row['updated_at'],
                'updated_by': row['updated_by']
            }
        return None
    
    def set_group_markup(self, group_id: int, markup: float, group_title: str = None, updated_by: int = None) -> bool:
        """
        Set group-specific markup.
        
        Args:
            group_id: Telegram group ID
            markup: Markup value
            group_title: Optional group title
            updated_by: Optional user ID who made the update
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO group_settings (group_id, group_title, markup, updated_by, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(group_id) DO UPDATE SET
                    markup = ?,
                    group_title = COALESCE(?, group_title),
                    updated_by = ?,
                    updated_at = CURRENT_TIMESTAMP,
                    is_active = 1
            """, (group_id, group_title, markup, updated_by, markup, group_title, updated_by))
            
            conn.commit()
            logger.info(f"Group {group_id} markup set to {markup}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting group markup: {e}", exc_info=True)
            return False
    
    def set_group_address(self, group_id: int, address: str, group_title: str = None, updated_by: int = None) -> bool:
        """
        Set group-specific USDT address.
        
        Args:
            group_id: Telegram group ID
            address: USDT address
            group_title: Optional group title
            updated_by: Optional user ID who made the update
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO group_settings (group_id, group_title, usdt_address, updated_by, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(group_id) DO UPDATE SET
                    usdt_address = ?,
                    group_title = COALESCE(?, group_title),
                    updated_by = ?,
                    updated_at = CURRENT_TIMESTAMP,
                    is_active = 1
            """, (group_id, group_title, address, updated_by, address, group_title, updated_by))
            
            conn.commit()
            logger.info(f"Group {group_id} address updated")
            return True
            
        except Exception as e:
            logger.error(f"Error setting group address: {e}", exc_info=True)
            return False
    
    def reset_group_settings(self, group_id: int) -> bool:
        """
        Reset group settings to use global defaults (deactivate group-specific settings).
        
        Args:
            group_id: Telegram group ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE group_settings 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE group_id = ?
            """, (group_id,))
            
            conn.commit()
            logger.info(f"Group {group_id} settings reset")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting group settings: {e}", exc_info=True)
            return False
    
    def delete_group_settings(self, group_id: int) -> bool:
        """
        Delete group settings completely.
        
        Args:
            group_id: Telegram group ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM group_settings WHERE group_id = ?", (group_id,))
            conn.commit()
            logger.info(f"Group {group_id} settings deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting group settings: {e}", exc_info=True)
            return False
    
    def get_all_groups(self) -> list:
        """
        Get all configured groups.
        
        Returns:
            List of group dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT group_id, group_title, markup, usdt_address, is_active, updated_at
            FROM group_settings
            WHERE is_active = 1
            ORDER BY updated_at DESC
        """)
        
        rows = cursor.fetchall()
        groups = []
        for row in rows:
            groups.append({
                'group_id': row['group_id'],
                'group_title': row['group_title'],
                'markup': float(row['markup']) if row['markup'] else 0.0,
                'usdt_address': row['usdt_address'] or '',
                'is_active': bool(row['is_active']),
                'updated_at': row['updated_at']
            })
        return groups
    
    # ========== Transaction Methods ==========
    
    def create_transaction(self, group_id: Optional[int], user_id: int, username: str, 
                          first_name: str, cny_amount: float, usdt_amount: float,
                          exchange_rate: float, markup: float, usdt_address: str) -> Optional[str]:
        """
        Create a new transaction record.
        
        Args:
            group_id: Telegram group ID (None for private chat)
            user_id: Telegram user ID
            username: Telegram username
            first_name: User first name
            cny_amount: CNY amount
            usdt_amount: USDT amount
            exchange_rate: Exchange rate used
            markup: Markup applied
            usdt_address: USDT address used
            
        Returns:
            Transaction ID if successful, None otherwise
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Generate transaction ID
            import datetime
            timestamp = datetime.datetime.now()
            transaction_id = f"T{timestamp.strftime('%Y%m%d%H%M%S')}{user_id % 10000:04d}"
            
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_id, group_id, user_id, username, first_name,
                    cny_amount, usdt_amount, exchange_rate, markup, usdt_address, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (transaction_id, group_id, user_id, username or '', first_name or '',
                  cny_amount, usdt_amount, exchange_rate, markup, usdt_address or ''))
            
            conn.commit()
            logger.info(f"Transaction created: {transaction_id}")
            return transaction_id
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}", exc_info=True)
            return None
    
    def get_transactions_by_group(self, group_id: int, date: str = None, limit: int = 20, offset: int = 0) -> list:
        """
        Get transactions for a specific group.
        
        Args:
            group_id: Telegram group ID
            date: Date filter (YYYY-MM-DD format), None for all
            limit: Maximum number of records
            offset: Offset for pagination
            
        Returns:
            List of transaction dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if date:
            cursor.execute("""
                SELECT transaction_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, created_at
                FROM transactions
                WHERE group_id = ? AND DATE(created_at) = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (group_id, date, limit, offset))
        else:
            cursor.execute("""
                SELECT transaction_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, created_at
                FROM transactions
                WHERE group_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (group_id, limit, offset))
        
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            transactions.append({
                'transaction_id': row['transaction_id'],
                'user_id': row['user_id'],
                'username': row['username'],
                'first_name': row['first_name'],
                'cny_amount': float(row['cny_amount']),
                'usdt_amount': float(row['usdt_amount']),
                'exchange_rate': float(row['exchange_rate']),
                'markup': float(row['markup']) if row['markup'] else 0.0,
                'usdt_address': row['usdt_address'],
                'status': row['status'],
                'created_at': row['created_at']
            })
        return transactions
    
    def get_today_transactions_by_group(self, group_id: int) -> list:
        """
        Get today's transactions for a specific group.
        
        Args:
            group_id: Telegram group ID
            
        Returns:
            List of today's transaction dictionaries
        """
        import datetime
        today = datetime.date.today().strftime('%Y-%m-%d')
        return self.get_transactions_by_group(group_id, date=today, limit=1000)
    
    def get_transaction_stats_by_group(self, group_id: int, date: str = None, 
                                       start_date: str = None, end_date: str = None) -> dict:
        """
        Get transaction statistics for a group.
        
        Args:
            group_id: Telegram group ID
            date: Date filter (YYYY-MM-DD format), None for all time
            start_date: Start date filter (YYYY-MM-DD format)
            end_date: End date filter (YYYY-MM-DD format)
            
        Returns:
            Dictionary with statistics
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if date:
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(cny_amount) as total_cny,
                    SUM(usdt_amount) as total_usdt,
                    AVG(cny_amount) as avg_cny,
                    COUNT(DISTINCT user_id) as unique_users,
                    MAX(created_at) as last_active
                FROM transactions
                WHERE group_id = ? AND DATE(created_at) = ?
            """, (group_id, date))
        elif start_date and end_date:
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(cny_amount) as total_cny,
                    SUM(usdt_amount) as total_usdt,
                    AVG(cny_amount) as avg_cny,
                    COUNT(DISTINCT user_id) as unique_users,
                    MAX(created_at) as last_active
                FROM transactions
                WHERE group_id = ? AND DATE(created_at) >= ? AND DATE(created_at) <= ?
            """, (group_id, start_date, end_date))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(cny_amount) as total_cny,
                    SUM(usdt_amount) as total_usdt,
                    AVG(cny_amount) as avg_cny,
                    COUNT(DISTINCT user_id) as unique_users,
                    MAX(created_at) as last_active
                FROM transactions
                WHERE group_id = ?
            """, (group_id,))
        
        row = cursor.fetchone()
        if row and row['count']:
            return {
                'count': int(row['count']),
                'total_cny': float(row['total_cny']) if row['total_cny'] else 0.0,
                'total_usdt': float(row['total_usdt']) if row['total_usdt'] else 0.0,
                'avg_cny': float(row['avg_cny']) if row['avg_cny'] else 0.0,
                'unique_users': int(row['unique_users']),
                'last_active': row['last_active']
            }
        return {'count': 0, 'total_cny': 0.0, 'total_usdt': 0.0, 'avg_cny': 0.0, 'unique_users': 0, 'last_active': None}
    
    def count_transactions_by_group(self, group_id: int, start_date: str = None, end_date: str = None) -> int:
        """
        Count total transactions for a group (for pagination).
        
        Args:
            group_id: Telegram group ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Total count of transactions
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM transactions
                WHERE group_id = ? AND DATE(created_at) >= ? AND DATE(created_at) <= ?
            """, (group_id, start_date, end_date))
        else:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM transactions
                WHERE group_id = ?
            """, (group_id,))
        
        row = cursor.fetchone()
        return int(row['count']) if row else 0
    
    def get_global_stats(self, start_date: str = None, end_date: str = None) -> dict:
        """
        Get global statistics across all groups.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with global statistics
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(cny_amount) as total_cny,
                    SUM(usdt_amount) as total_usdt,
                    COUNT(DISTINCT group_id) as active_groups,
                    COUNT(DISTINCT user_id) as unique_users
                FROM transactions
                WHERE DATE(created_at) >= ? AND DATE(created_at) <= ?
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(cny_amount) as total_cny,
                    SUM(usdt_amount) as total_usdt,
                    COUNT(DISTINCT group_id) as active_groups,
                    COUNT(DISTINCT user_id) as unique_users
                FROM transactions
            """)
        
        row = cursor.fetchone()
        if row and row['count']:
            return {
                'count': int(row['count']),
                'total_cny': float(row['total_cny']) if row['total_cny'] else 0.0,
                'total_usdt': float(row['total_usdt']) if row['total_usdt'] else 0.0,
                'active_groups': int(row['active_groups']),
                'unique_users': int(row['unique_users'])
            }
        return {'count': 0, 'total_cny': 0.0, 'total_usdt': 0.0, 'active_groups': 0, 'unique_users': 0}
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[dict]:
        """
        Get a specific transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction dictionary or None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT transaction_id, group_id, user_id, username, first_name,
                   cny_amount, usdt_amount, exchange_rate, markup,
                   usdt_address, status, payment_hash, paid_at, confirmed_at, 
                   cancelled_at, cancelled_by, created_at
            FROM transactions
            WHERE transaction_id = ?
        """, (transaction_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'transaction_id': row['transaction_id'],
                'group_id': row['group_id'],
                'user_id': row['user_id'],
                'username': row['username'],
                'first_name': row['first_name'],
                'cny_amount': float(row['cny_amount']),
                'usdt_amount': float(row['usdt_amount']),
                'exchange_rate': float(row['exchange_rate']),
                'markup': float(row['markup']) if row['markup'] else 0.0,
                'usdt_address': row['usdt_address'],
                'status': row['status'],
                'payment_hash': row['payment_hash'],
                'paid_at': row['paid_at'],
                'confirmed_at': row['confirmed_at'],
                'cancelled_at': row['cancelled_at'],
                'cancelled_by': row['cancelled_by'],
                'created_at': row['created_at']
            }
        return None
    
    def update_transaction_status(self, transaction_id: str, status: str, payment_hash: str = None, 
                                 cancelled_by: int = None) -> bool:
        """
        Update transaction status.
        
        Args:
            transaction_id: Transaction ID
            status: New status (pending, paid, confirmed, cancelled)
            payment_hash: Optional payment hash
            cancelled_by: Optional user ID who cancelled the transaction
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            if status == 'paid':
                # Mark as paid
                cursor.execute("""
                    UPDATE transactions
                    SET status = ?, payment_hash = ?, paid_at = CURRENT_TIMESTAMP
                    WHERE transaction_id = ?
                """, (status, payment_hash, transaction_id))
            elif status == 'confirmed':
                # Confirm transaction
                cursor.execute("""
                    UPDATE transactions
                    SET status = ?, confirmed_at = CURRENT_TIMESTAMP
                    WHERE transaction_id = ?
                """, (status, transaction_id))
            elif status == 'cancelled':
                # Cancel transaction
                cursor.execute("""
                    UPDATE transactions
                    SET status = ?, cancelled_at = CURRENT_TIMESTAMP, cancelled_by = ?
                    WHERE transaction_id = ?
                """, (status, cancelled_by, transaction_id))
            else:
                # Other status updates
                cursor.execute("""
                    UPDATE transactions
                    SET status = ?, payment_hash = ?
                    WHERE transaction_id = ?
                """, (status, payment_hash, transaction_id))
            
            conn.commit()
            logger.info(f"Transaction {transaction_id} status updated to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating transaction status: {e}", exc_info=True)
            return False
    
    def mark_transaction_paid(self, transaction_id: str, payment_hash: str = None) -> bool:
        """
        Mark transaction as paid.
        
        Args:
            transaction_id: Transaction ID
            payment_hash: Optional payment hash (TXID)
            
        Returns:
            True if successful
        """
        return self.update_transaction_status(transaction_id, 'paid', payment_hash)
    
    def cancel_transaction(self, transaction_id: str, cancelled_by: int) -> bool:
        """
        Cancel a transaction.
        
        Args:
            transaction_id: Transaction ID
            cancelled_by: User ID who cancelled the transaction
            
        Returns:
            True if successful
        """
        return self.update_transaction_status(transaction_id, 'cancelled', cancelled_by=cancelled_by)
    
    def confirm_transaction(self, transaction_id: str) -> bool:
        """
        Confirm a paid transaction (admin only).
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            True if successful
        """
        return self.update_transaction_status(transaction_id, 'confirmed')
    
    def get_pending_transactions(self, group_id: int = None, limit: int = 50) -> list:
        """
        Get pending (not paid) transactions.
        
        Args:
            group_id: Optional group ID filter
            limit: Maximum number of records
            
        Returns:
            List of pending transaction dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if group_id:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, created_at
                FROM transactions
                WHERE group_id = ? AND status = 'pending'
                ORDER BY created_at DESC
                LIMIT ?
            """, (group_id, limit))
        else:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, created_at
                FROM transactions
                WHERE status = 'pending'
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            transactions.append({
                'transaction_id': row['transaction_id'],
                'group_id': row['group_id'],
                'user_id': row['user_id'],
                'username': row['username'],
                'first_name': row['first_name'],
                'cny_amount': float(row['cny_amount']),
                'usdt_amount': float(row['usdt_amount']),
                'exchange_rate': float(row['exchange_rate']),
                'markup': float(row['markup']) if row['markup'] else 0.0,
                'usdt_address': row['usdt_address'],
                'status': row['status'],
                'created_at': row['created_at']
            })
        return transactions
    
    def get_paid_transactions(self, group_id: int = None, limit: int = 50) -> list:
        """
        Get paid transactions waiting for confirmation.
        
        Args:
            group_id: Optional group ID filter
            limit: Maximum number of records
            
        Returns:
            List of paid transaction dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if group_id:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, payment_hash, paid_at, created_at
                FROM transactions
                WHERE group_id = ? AND status = 'paid'
                ORDER BY paid_at DESC
                LIMIT ?
            """, (group_id, limit))
        else:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, payment_hash, paid_at, created_at
                FROM transactions
                WHERE status = 'paid'
                ORDER BY paid_at DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            transactions.append({
                'transaction_id': row['transaction_id'],
                'group_id': row['group_id'],
                'user_id': row['user_id'],
                'username': row['username'],
                'first_name': row['first_name'],
                'cny_amount': float(row['cny_amount']),
                'usdt_amount': float(row['usdt_amount']),
                'exchange_rate': float(row['exchange_rate']),
                'markup': float(row['markup']) if row['markup'] else 0.0,
                'usdt_address': row['usdt_address'],
                'status': row['status'],
                'payment_hash': row['payment_hash'],
                'paid_at': row['paid_at'],
                'created_at': row['created_at']
            })
        return transactions
    
    def get_transactions_by_status(self, status: str, group_id: int = None, limit: int = 50) -> list:
        """
        Get transactions by status.
        
        Args:
            status: Transaction status (pending, paid, confirmed, cancelled)
            group_id: Optional group ID filter
            limit: Maximum number of records
            
        Returns:
            List of transaction dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if group_id:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, payment_hash, paid_at, confirmed_at, 
                       cancelled_at, created_at
                FROM transactions
                WHERE group_id = ? AND status = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (group_id, status, limit))
        else:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, payment_hash, paid_at, confirmed_at,
                       cancelled_at, created_at
                FROM transactions
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (status, limit))
        
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            transactions.append({
                'transaction_id': row['transaction_id'],
                'group_id': row['group_id'],
                'user_id': row['user_id'],
                'username': row['username'],
                'first_name': row['first_name'],
                'cny_amount': float(row['cny_amount']),
                'usdt_amount': float(row['usdt_amount']),
                'exchange_rate': float(row['exchange_rate']),
                'markup': float(row['markup']) if row['markup'] else 0.0,
                'usdt_address': row['usdt_address'],
                'status': row['status'],
                'payment_hash': row['payment_hash'],
                'paid_at': row['paid_at'],
                'confirmed_at': row['confirmed_at'],
                'cancelled_at': row['cancelled_at'],
                'created_at': row['created_at']
            })
        return transactions
    
    # ========== User-level Transaction Methods ==========
    
    def get_transactions_by_user(self, user_id: int, limit: int = 20, offset: int = 0, 
                                 start_date: str = None, end_date: str = None) -> list:
        """
        Get transactions for a specific user (personal bills).
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of records
            offset: Offset for pagination
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            
        Returns:
            List of transaction dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, created_at
                FROM transactions
                WHERE user_id = ? AND DATE(created_at) >= ? AND DATE(created_at) <= ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, start_date, end_date, limit, offset))
        else:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, created_at
                FROM transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
        
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            transactions.append({
                'transaction_id': row['transaction_id'],
                'group_id': row['group_id'],
                'user_id': row['user_id'],
                'username': row['username'],
                'first_name': row['first_name'],
                'cny_amount': float(row['cny_amount']),
                'usdt_amount': float(row['usdt_amount']),
                'exchange_rate': float(row['exchange_rate']),
                'markup': float(row['markup']) if row['markup'] else 0.0,
                'usdt_address': row['usdt_address'],
                'status': row['status'],
                'created_at': row['created_at']
            })
        return transactions
    
    def count_transactions_by_user(self, user_id: int, start_date: str = None, end_date: str = None) -> int:
        """
        Count total transactions for a user (for pagination).
        
        Args:
            user_id: Telegram user ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Total count of transactions
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM transactions
                WHERE user_id = ? AND DATE(created_at) >= ? AND DATE(created_at) <= ?
            """, (user_id, start_date, end_date))
        else:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM transactions
                WHERE user_id = ?
            """, (user_id,))
        
        row = cursor.fetchone()
        return int(row['count']) if row else 0
    
    def get_user_stats(self, user_id: int, date: str = None, 
                      start_date: str = None, end_date: str = None) -> dict:
        """
        Get transaction statistics for a user.
        
        Args:
            user_id: Telegram user ID
            date: Date filter (YYYY-MM-DD format), None for all time
            start_date: Start date filter (YYYY-MM-DD format)
            end_date: End date filter (YYYY-MM-DD format)
            
        Returns:
            Dictionary with statistics
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if date:
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(cny_amount) as total_cny,
                    SUM(usdt_amount) as total_usdt,
                    AVG(cny_amount) as avg_cny,
                    MAX(created_at) as last_active
                FROM transactions
                WHERE user_id = ? AND DATE(created_at) = ?
            """, (user_id, date))
        elif start_date and end_date:
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(cny_amount) as total_cny,
                    SUM(usdt_amount) as total_usdt,
                    AVG(cny_amount) as avg_cny,
                    MAX(created_at) as last_active
                FROM transactions
                WHERE user_id = ? AND DATE(created_at) >= ? AND DATE(created_at) <= ?
            """, (user_id, start_date, end_date))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(cny_amount) as total_cny,
                    SUM(usdt_amount) as total_usdt,
                    AVG(cny_amount) as avg_cny,
                    MAX(created_at) as last_active
                FROM transactions
                WHERE user_id = ?
            """, (user_id,))
        
        row = cursor.fetchone()
        if row and row['count']:
            return {
                'count': int(row['count']),
                'total_cny': float(row['total_cny']) if row['total_cny'] else 0.0,
                'total_usdt': float(row['total_usdt']) if row['total_usdt'] else 0.0,
                'avg_cny': float(row['avg_cny']) if row['avg_cny'] else 0.0,
                'last_active': row['last_active']
            }
        return {'count': 0, 'total_cny': 0.0, 'total_usdt': 0.0, 'avg_cny': 0.0, 'last_active': None}


# Global database instance
db = Database()

