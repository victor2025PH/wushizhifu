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
        
        # Create user_settings table for user preferences and onboarding
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id BIGINT PRIMARY KEY,
                onboarding_completed BOOLEAN DEFAULT 0,
                last_active_at TIMESTAMP,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create price_history table for price tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                base_price REAL NOT NULL,
                final_price REAL NOT NULL,
                markup REAL DEFAULT 0.0,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_history_created_at 
            ON price_history(created_at)
        """)
        
        # Create price_alerts table for user price alerts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT NOT NULL,
                alert_type TEXT NOT NULL,
                threshold_value REAL NOT NULL,
                comparison_operator TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                notification_count INTEGER DEFAULT 0,
                last_notified_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id 
            ON price_alerts(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_alerts_active 
            ON price_alerts(is_active)
        """)
        
        # Create settlement_templates table for quick settlement templates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settlement_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT,
                template_name TEXT NOT NULL,
                template_value TEXT NOT NULL,
                template_type TEXT NOT NULL,
                is_preset BOOLEAN DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, template_name)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_settlement_templates_user_id 
            ON settlement_templates(user_id)
        """)
        
        # Insert default preset templates if not exists
        default_templates = [
            ('1000', 'amount', '常用金额模板'),
            ('5000', 'amount', '常用金额模板'),
            ('10000', 'amount', '常用金额模板'),
            ('20000', 'amount', '常用金额模板'),
            ('50000', 'amount', '常用金额模板'),
            ('20000-200', 'formula', '常用算式模板'),
            ('50000-500', 'formula', '常用算式模板'),
            ('100000-1000', 'formula', '常用算式模板')
        ]
        
        for value, t_type, name in default_templates:
            cursor.execute("""
                INSERT OR IGNORE INTO settlement_templates 
                (user_id, template_name, template_value, template_type, is_preset)
                VALUES (NULL, ?, ?, ?, 1)
            """, (name, value, t_type))
        
        # Create usdt_addresses table for multiple address management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usdt_addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id BIGINT,
                address TEXT NOT NULL,
                label TEXT,
                is_default BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                usage_count INTEGER DEFAULT 0,
                last_used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by BIGINT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_usdt_addresses_group_id 
            ON usdt_addresses(group_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_usdt_addresses_active 
            ON usdt_addresses(is_active)
        """)
        
        # Create operation_logs table for audit trail
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                user_id BIGINT NOT NULL,
                username TEXT,
                first_name TEXT,
                target_type TEXT,
                target_id TEXT,
                description TEXT,
                old_value TEXT,
                new_value TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_operation_logs_user_id 
            ON operation_logs(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_operation_logs_type 
            ON operation_logs(operation_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at 
            ON operation_logs(created_at)
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
    
    def get_transactions_by_group(self, group_id: int, date: str = None, 
                                 start_date: str = None, end_date: str = None,
                                 status: str = None, min_amount: float = None, max_amount: float = None,
                                 user_id: int = None, limit: int = 20, offset: int = 0) -> list:
        """
        Get transactions for a specific group with advanced filtering.
        
        Args:
            group_id: Telegram group ID
            date: Date filter (YYYY-MM-DD format), None for all
            start_date: Start date filter (YYYY-MM-DD format)
            end_date: End date filter (YYYY-MM-DD format)
            status: Status filter (pending, paid, confirmed, cancelled)
            min_amount: Minimum CNY amount filter
            max_amount: Maximum CNY amount filter
            user_id: Optional user ID filter
            limit: Maximum number of records
            offset: Offset for pagination
            
        Returns:
            List of transaction dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Build query dynamically based on filters
        query = """
            SELECT transaction_id, group_id, user_id, username, first_name,
                   cny_amount, usdt_amount, exchange_rate, markup,
                   usdt_address, status, payment_hash, paid_at, confirmed_at,
                   cancelled_at, created_at
            FROM transactions
            WHERE group_id = ?
        """
        params = [group_id]
        
        # Date filters
        if date:
            query += " AND DATE(created_at) = ?"
            params.append(date)
        elif start_date and end_date:
            query += " AND DATE(created_at) >= ? AND DATE(created_at) <= ?"
            params.extend([start_date, end_date])
        
        # Status filter
        if status:
            query += " AND status = ?"
            params.append(status)
        
        # Amount filters
        if min_amount is not None:
            query += " AND cny_amount >= ?"
            params.append(min_amount)
        if max_amount is not None:
            query += " AND cny_amount <= ?"
            params.append(max_amount)
        
        # User filter
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, tuple(params))
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
    
    def count_transactions_by_group(self, group_id: int, start_date: str = None, end_date: str = None,
                                    status: str = None, min_amount: float = None, max_amount: float = None,
                                    user_id: int = None) -> int:
        """
        Count total transactions for a group with filters (for pagination).
        
        Args:
            group_id: Telegram group ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            status: Optional status filter
            min_amount: Optional minimum CNY amount filter
            max_amount: Optional maximum CNY amount filter
            user_id: Optional user ID filter
            
        Returns:
            Total count of transactions
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) as count FROM transactions WHERE group_id = ?"
        params = [group_id]
        
        if start_date and end_date:
            query += " AND DATE(created_at) >= ? AND DATE(created_at) <= ?"
            params.extend([start_date, end_date])
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if min_amount is not None:
            query += " AND cny_amount >= ?"
            params.append(min_amount)
        
        if max_amount is not None:
            query += " AND cny_amount <= ?"
            params.append(max_amount)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        cursor.execute(query, tuple(params))
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
    
    # ========== User Settings Methods ==========
    
    def get_user_setting(self, user_id: int, key: str = None) -> Optional[dict]:
        """
        Get user setting(s).
        
        Args:
            user_id: Telegram user ID
            key: Optional setting key (if None, returns all settings)
            
        Returns:
            Dictionary with user settings or None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, onboarding_completed, last_active_at, preferences
            FROM user_settings
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        if row:
            import json
            prefs = {}
            if row['preferences']:
                try:
                    prefs = json.loads(row['preferences'])
                except:
                    pass
            
            return {
                'user_id': row['user_id'],
                'onboarding_completed': bool(row['onboarding_completed']),
                'last_active_at': row['last_active_at'],
                'preferences': prefs
            }
        
        return None
    
    def is_onboarding_completed(self, user_id: int) -> bool:
        """
        Check if user has completed onboarding.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if onboarding completed
        """
        setting = self.get_user_setting(user_id)
        return setting['onboarding_completed'] if setting else False
    
    def mark_onboarding_completed(self, user_id: int) -> bool:
        """
        Mark user onboarding as completed.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_settings (user_id, onboarding_completed, last_active_at)
                VALUES (?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    onboarding_completed = 1,
                    last_active_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id,))
            
            conn.commit()
            logger.info(f"User {user_id} onboarding marked as completed")
            return True
            
        except Exception as e:
            logger.error(f"Error marking onboarding completed: {e}", exc_info=True)
            return False
    
    def update_user_last_active(self, user_id: int) -> bool:
        """
        Update user last active timestamp.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_settings (user_id, last_active_at)
                VALUES (?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    last_active_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating user last active: {e}", exc_info=True)
            return False
    
    def set_user_preference(self, user_id: int, key: str, value: any) -> bool:
        """
        Set user preference.
        
        Args:
            user_id: Telegram user ID
            key: Preference key
            value: Preference value
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Get existing preferences
            setting = self.get_user_setting(user_id)
            prefs = setting['preferences'] if setting else {}
            
            # Update preference
            import json
            prefs[key] = value
            
            cursor.execute("""
                INSERT INTO user_settings (user_id, preferences, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    preferences = ?,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, json.dumps(prefs), json.dumps(prefs)))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error setting user preference: {e}", exc_info=True)
            return False
    
    # ========== Operation Logs Methods ==========
    
    def log_operation(self, operation_type: str, user_id: int, username: str = None,
                     first_name: str = None, target_type: str = None, target_id: str = None,
                     description: str = None, old_value: str = None, new_value: str = None,
                     ip_address: str = None) -> bool:
        """
        Log an operation for audit trail.
        
        Args:
            operation_type: Type of operation (e.g., 'set_markup', 'set_address', 'confirm_transaction')
            user_id: User ID who performed the operation
            username: Username
            first_name: First name
            target_type: Type of target (e.g., 'group', 'transaction', 'global')
            target_id: ID of target (e.g., group_id, transaction_id)
            description: Operation description
            old_value: Old value (for updates)
            new_value: New value (for updates)
            ip_address: Optional IP address
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO operation_logs (
                    operation_type, user_id, username, first_name,
                    target_type, target_id, description,
                    old_value, new_value, ip_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                operation_type, user_id, username or '', first_name or '',
                target_type or '', target_id or '', description or '',
                old_value or '', new_value or '', ip_address or ''
            ))
            
            conn.commit()
            logger.debug(f"Operation logged: {operation_type} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging operation: {e}", exc_info=True)
            return False
    
    def get_operation_logs(self, operation_type: str = None, user_id: int = None,
                          target_type: str = None, target_id: str = None,
                          start_date: str = None, end_date: str = None,
                          limit: int = 100, offset: int = 0) -> list:
        """
        Get operation logs with filters.
        
        Args:
            operation_type: Optional operation type filter
            user_id: Optional user ID filter
            target_type: Optional target type filter
            target_id: Optional target ID filter
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            limit: Maximum number of records
            offset: Offset for pagination
            
        Returns:
            List of operation log dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM operation_logs WHERE 1=1"
        params = []
        
        if operation_type:
            query += " AND operation_type = ?"
            params.append(operation_type)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if target_type:
            query += " AND target_type = ?"
            params.append(target_type)
        
        if target_id:
            query += " AND target_id = ?"
            params.append(target_id)
        
        if start_date and end_date:
            query += " AND DATE(created_at) >= ? AND DATE(created_at) <= ?"
            params.extend([start_date, end_date])
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        logs = []
        for row in rows:
            logs.append({
                'id': row['id'],
                'operation_type': row['operation_type'],
                'user_id': row['user_id'],
                'username': row['username'],
                'first_name': row['first_name'],
                'target_type': row['target_type'],
                'target_id': row['target_id'],
                'description': row['description'],
                'old_value': row['old_value'],
                'new_value': row['new_value'],
                'ip_address': row['ip_address'],
                'created_at': row['created_at']
            })
        return logs
    
    def count_operation_logs(self, operation_type: str = None, user_id: int = None,
                            target_type: str = None, start_date: str = None,
                            end_date: str = None) -> int:
        """
        Count operation logs with filters.
        
        Args:
            operation_type: Optional operation type filter
            user_id: Optional user ID filter
            target_type: Optional target type filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Total count of logs
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) as count FROM operation_logs WHERE 1=1"
        params = []
        
        if operation_type:
            query += " AND operation_type = ?"
            params.append(operation_type)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if target_type:
            query += " AND target_type = ?"
            params.append(target_type)
        
        if start_date and end_date:
            query += " AND DATE(created_at) >= ? AND DATE(created_at) <= ?"
            params.extend([start_date, end_date])
        
        cursor.execute(query, tuple(params))
        row = cursor.fetchone()
        return int(row['count']) if row else 0
    
    # ========== Price History Methods ==========
    
    def save_price_history(self, base_price: float, final_price: float, markup: float, source: str = 'binance_p2p') -> bool:
        """
        Save price to history table.
        
        Args:
            base_price: Base price from API
            final_price: Final price (base + markup)
            markup: Markup applied
            source: Price source (binance_p2p, coingecko, etc.)
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO price_history (base_price, final_price, markup, source)
                VALUES (?, ?, ?, ?)
            """, (base_price, final_price, markup, source))
            
            conn.commit()
            logger.debug(f"Price history saved: {final_price} (base: {base_price}, markup: {markup})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving price history: {e}", exc_info=True)
            return False
    
    def get_price_history(self, hours: int = 24, limit: int = 100) -> list:
        """
        Get price history for the last N hours.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of records
            
        Returns:
            List of price history dictionaries
        """
        import datetime
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Calculate start time
        start_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            SELECT base_price, final_price, markup, source, created_at
            FROM price_history
            WHERE created_at >= ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (start_str, limit))
        
        rows = cursor.fetchall()
        history = []
        for row in rows:
            history.append({
                'base_price': float(row['base_price']),
                'final_price': float(row['final_price']),
                'markup': float(row['markup']) if row['markup'] else 0.0,
                'source': row['source'],
                'created_at': row['created_at']
            })
        
        return history
    
    def get_price_stats(self, hours: int = 24) -> dict:
        """
        Get price statistics for the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with statistics (count, min, max, avg)
        """
        import datetime
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Calculate start time
        start_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                MIN(final_price) as min_final,
                MAX(final_price) as max_final,
                AVG(final_price) as avg_final
            FROM price_history
            WHERE created_at >= ?
        """, (start_str,))
        
        row = cursor.fetchone()
        if row and row['count']:
            return {
                'count': int(row['count']),
                'min_final': float(row['min_final']) if row['min_final'] else 0.0,
                'max_final': float(row['max_final']) if row['max_final'] else 0.0,
                'avg_final': float(row['avg_final']) if row['avg_final'] else 0.0
            }
        
        return {'count': 0, 'min_final': 0.0, 'max_final': 0.0, 'avg_final': 0.0}
    
    # ========== Price Alert Methods ==========
    
    def get_user_alerts(self, user_id: int, active_only: bool = False) -> list:
        """
        Get price alerts for a user.
        
        Args:
            user_id: Telegram user ID
            active_only: If True, only return active alerts
            
        Returns:
            List of alert dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("""
                SELECT id, user_id, alert_type, threshold_value, comparison_operator,
                       is_active, notification_count, last_notified_at, created_at
                FROM price_alerts
                WHERE user_id = ? AND is_active = 1
                ORDER BY created_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT id, user_id, alert_type, threshold_value, comparison_operator,
                       is_active, notification_count, last_notified_at, created_at
                FROM price_alerts
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
        
        rows = cursor.fetchall()
        alerts = []
        for row in rows:
            alerts.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'alert_type': row['alert_type'],
                'threshold_value': float(row['threshold_value']),
                'comparison_operator': row['comparison_operator'],
                'is_active': bool(row['is_active']),
                'notification_count': int(row['notification_count']),
                'last_notified_at': row['last_notified_at'],
                'created_at': row['created_at']
            })
        
        return alerts
    
    def get_active_alerts(self) -> list:
        """
        Get all active price alerts.
        
        Returns:
            List of active alert dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, alert_type, threshold_value, comparison_operator,
                   is_active, notification_count, last_notified_at, created_at
            FROM price_alerts
            WHERE is_active = 1
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        alerts = []
        for row in rows:
            alerts.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'alert_type': row['alert_type'],
                'threshold_value': float(row['threshold_value']),
                'comparison_operator': row['comparison_operator'],
                'is_active': bool(row['is_active']),
                'notification_count': int(row['notification_count']),
                'last_notified_at': row['last_notified_at'],
                'created_at': row['created_at']
            })
        
        return alerts
    
    def create_price_alert(self, user_id: int, alert_type: str, threshold_value: float, 
                          comparison_operator: str = '>') -> bool:
        """
        Create a new price alert.
        
        Args:
            user_id: Telegram user ID
            alert_type: Alert type (price_above, price_below)
            threshold_value: Price threshold
            comparison_operator: Comparison operator (>, >=, <, <=)
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO price_alerts (user_id, alert_type, threshold_value, comparison_operator)
                VALUES (?, ?, ?, ?)
            """, (user_id, alert_type, threshold_value, comparison_operator))
            
            conn.commit()
            logger.info(f"Price alert created for user {user_id}: {alert_type} {comparison_operator} {threshold_value}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating price alert: {e}", exc_info=True)
            return False


# Global database instance
db = Database()

