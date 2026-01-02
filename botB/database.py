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
            db_path: Path to SQLite database file. If None, uses shared database (wushipay.db).
        """
        if db_path is None:
            # Use shared database (same as BotA and Miniapp)
            # Use wushipay.db in project root directory
            root_dir = Path(__file__).parent.parent
            root_db = root_dir / "wushipay.db"
            db_path = str(root_db)
            logger.info(f"Using shared database: {db_path}")
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
                group_id BIGINT NOT NULL,
                address TEXT NOT NULL,
                label TEXT,
                qr_code_file_id TEXT,
                is_default BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                needs_confirmation BOOLEAN DEFAULT 0,
                pending_confirmation BOOLEAN DEFAULT 0,
                confirmed_by BIGINT,
                confirmed_at TIMESTAMP,
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
        
        # Migrate existing table: add new columns if they don't exist
        try:
            # Check if qr_code_file_id column exists
            cursor.execute("PRAGMA table_info(usdt_addresses)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'qr_code_file_id' not in columns:
                cursor.execute("ALTER TABLE usdt_addresses ADD COLUMN qr_code_file_id TEXT")
                logger.info("Added qr_code_file_id column to usdt_addresses")
            
            if 'needs_confirmation' not in columns:
                cursor.execute("ALTER TABLE usdt_addresses ADD COLUMN needs_confirmation BOOLEAN DEFAULT 0")
                logger.info("Added needs_confirmation column to usdt_addresses")
            
            if 'pending_confirmation' not in columns:
                cursor.execute("ALTER TABLE usdt_addresses ADD COLUMN pending_confirmation BOOLEAN DEFAULT 0")
                logger.info("Added pending_confirmation column to usdt_addresses")
            
            if 'confirmed_by' not in columns:
                cursor.execute("ALTER TABLE usdt_addresses ADD COLUMN confirmed_by BIGINT")
                logger.info("Added confirmed_by column to usdt_addresses")
            
            if 'confirmed_at' not in columns:
                cursor.execute("ALTER TABLE usdt_addresses ADD COLUMN confirmed_at TIMESTAMP")
                logger.info("Added confirmed_at column to usdt_addresses")
            
            # Handle existing NULL group_id records (migration from old global addresses)
            # Set them to a special group_id or delete them (user should re-add)
            cursor.execute("SELECT COUNT(*) FROM usdt_addresses WHERE group_id IS NULL")
            null_count = cursor.fetchone()[0]
            if null_count > 0:
                logger.warning(f"Found {null_count} addresses with NULL group_id. These will be deleted as global addresses are no longer supported.")
                cursor.execute("DELETE FROM usdt_addresses WHERE group_id IS NULL")
                logger.info(f"Deleted {null_count} addresses with NULL group_id")
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error migrating usdt_addresses table: {e}", exc_info=True)
            conn.rollback()
        
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
        
        # Create otc_transactions table for settlement records (renamed to avoid conflict with BotA's transactions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otc_transactions (
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
        cursor.execute("PRAGMA table_info(otc_transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'paid_at' not in columns:
            cursor.execute("ALTER TABLE otc_transactions ADD COLUMN paid_at TIMESTAMP")
        if 'cancelled_at' not in columns:
            cursor.execute("ALTER TABLE otc_transactions ADD COLUMN cancelled_at TIMESTAMP")
        if 'cancelled_by' not in columns:
            cursor.execute("ALTER TABLE otc_transactions ADD COLUMN cancelled_by BIGINT")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_otc_transactions_group_id 
            ON otc_transactions(group_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_otc_transactions_user_id 
            ON otc_transactions(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_otc_transactions_created_at 
            ON otc_transactions(created_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_otc_transactions_group_date 
            ON otc_transactions(group_id, DATE(created_at))
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_otc_transactions_status 
            ON otc_transactions(status)
        """)
        
        # Create customer_service_accounts table for managing customer service accounts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_service_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                display_name TEXT,
                status TEXT DEFAULT 'available',
                weight INTEGER DEFAULT 5,
                max_concurrent INTEGER DEFAULT 50,
                current_count INTEGER DEFAULT 0,
                total_served INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer_service_accounts_username 
            ON customer_service_accounts(username)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer_service_accounts_status 
            ON customer_service_accounts(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer_service_accounts_active 
            ON customer_service_accounts(is_active)
        """)
        
        # Create customer_service_assignments table for tracking assignments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_service_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                service_account TEXT NOT NULL,
                assignment_method TEXT,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                completed_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer_service_assignments_user_id 
            ON customer_service_assignments(user_id)
        """)
        
        # Create groups table for group management (if not exists from Bot A)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                group_id BIGINT PRIMARY KEY,
                group_title VARCHAR(255),
                verification_enabled BOOLEAN DEFAULT 0,
                verification_type VARCHAR(20) DEFAULT 'none',
                welcome_message TEXT,
                rules_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_groups_verification_enabled 
            ON groups(verification_enabled)
        """)
        
        # Create group_members table for tracking group members
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(group_id),
                UNIQUE(group_id, user_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_group_members_group_id 
            ON group_members(group_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_group_members_user_id 
            ON group_members(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_group_members_status 
            ON group_members(status)
        """)
        
        # Create sensitive_words table for filtering
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensitive_words (
                word_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id BIGINT,
                word VARCHAR(255) NOT NULL,
                action VARCHAR(20) DEFAULT 'warn',
                added_by BIGINT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (group_id) REFERENCES groups(group_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sensitive_words_group_id 
            ON sensitive_words(group_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sensitive_words_word 
            ON sensitive_words(word)
        """)
        
        # Create verification_questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_questions (
                question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id BIGINT,
                question_text TEXT NOT NULL,
                question_type VARCHAR(20) NOT NULL DEFAULT 'single_choice',
                correct_answer TEXT NOT NULL,
                options TEXT,
                difficulty VARCHAR(20) DEFAULT 'medium',
                hint TEXT,
                max_attempts INTEGER DEFAULT 3,
                time_limit INTEGER DEFAULT 300,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(group_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_verification_questions_group_id 
            ON verification_questions(group_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_verification_questions_active 
            ON verification_questions(is_active)
        """)
        
        # Create verification_records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                verification_type VARCHAR(50) NOT NULL,
                ai_score INTEGER,
                question_id INTEGER,
                user_answer TEXT,
                is_correct BOOLEAN,
                result VARCHAR(20) NOT NULL,
                attempt_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(group_id),
                FOREIGN KEY (question_id) REFERENCES verification_questions(question_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_verification_records_group_user 
            ON verification_records(group_id, user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_verification_records_result 
            ON verification_records(result)
        """)
        
        # Create verification_configs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_configs (
                config_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id BIGINT UNIQUE NOT NULL,
                verification_mode VARCHAR(20) DEFAULT 'question',
                auto_approve_threshold INTEGER DEFAULT 80,
                question_threshold_min INTEGER DEFAULT 60,
                question_threshold_max INTEGER DEFAULT 80,
                manual_threshold_min INTEGER DEFAULT 40,
                manual_threshold_max INTEGER DEFAULT 60,
                auto_reject_threshold INTEGER DEFAULT 40,
                enable_time_strategy BOOLEAN DEFAULT 0,
                question_selection_mode VARCHAR(20) DEFAULT 'random',
                welcome_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(group_id)
            )
        """)
        
        # Initialize default questions if not exists
        cursor.execute("SELECT COUNT(*) FROM verification_questions WHERE group_id IS NULL")
        if cursor.fetchone()[0] == 0:
            default_questions = [
                ('伍拾支付的主要功能是什么？', 'fill_blank', '支付|转账|USDT|数字资产', 'easy', '提示：我们是一个支付平台', 3, 300),
                ('USDT是什么？', 'fill_blank', 'USDT|泰达币|稳定币', 'easy', '提示：一种数字货币', 3, 300),
                ('本群是否允许发送广告？', 'true_false', '否|不允许|禁止|不', 'medium', '请查看群组规则', 3, 300),
                ('请回答：3+5=？', 'fill_blank', '8|八', 'easy', '简单的数学题', 3, 180),
            ]
            cursor.executemany("""
                INSERT INTO verification_questions 
                (group_id, question_text, question_type, correct_answer, difficulty, hint, max_attempts, time_limit)
                VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)
            """, default_questions)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer_service_assignments_service_account 
            ON customer_service_assignments(service_account)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customer_service_assignments_status 
            ON customer_service_assignments(status)
        """)
        
        # Initialize default customer service account if none exists
        cursor.execute("SELECT COUNT(*) FROM customer_service_accounts")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("""
                INSERT INTO customer_service_accounts (username, display_name, status, weight, max_concurrent, is_active)
                VALUES ('wushizhifu_jianglai', '客服账号1', 'available', 5, 50, 1)
            """)
        
        # Create users table (if not exists from Bot A)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                language_code VARCHAR(10),
                is_premium BOOLEAN DEFAULT 0,
                vip_level INTEGER DEFAULT 0,
                total_transactions INTEGER DEFAULT 0,
                total_amount DECIMAL(15,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active'
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username 
            ON users(username)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_status 
            ON users(status)
        """)
        
        # Create transactions table (if not exists from Bot A)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT NOT NULL,
                order_id VARCHAR(64) UNIQUE NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                payment_channel VARCHAR(20) NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                fee DECIMAL(15,2) DEFAULT 0,
                actual_amount DECIMAL(15,2) NOT NULL,
                currency VARCHAR(10) DEFAULT 'CNY',
                status VARCHAR(20) NOT NULL,
                description TEXT,
                payer_info VARCHAR(255),
                payee_info VARCHAR(255),
                qr_code_url TEXT,
                payment_url TEXT,
                callback_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                paid_at TIMESTAMP,
                expired_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
            ON transactions(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_status 
            ON transactions(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_created_at 
            ON transactions(created_at)
        """)
        
        # Create admins table (if not exists from Bot A)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT UNIQUE NOT NULL,
                role VARCHAR(20) DEFAULT 'admin',
                status VARCHAR(20) DEFAULT 'active',
                added_by BIGINT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admins_user_id 
            ON admins(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admins_status 
            ON admins(status)
        """)
        
        # Create referral_codes table (if not exists from Bot A)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referral_codes (
                user_id BIGINT PRIMARY KEY,
                referral_code VARCHAR(50) UNIQUE NOT NULL,
                total_invites INTEGER DEFAULT 0,
                successful_invites INTEGER DEFAULT 0,
                total_rewards DECIMAL(15,2) DEFAULT 0,
                lottery_entries INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create referrals table (if not exists from Bot A)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id BIGINT NOT NULL,
                referred_id BIGINT NOT NULL,
                referral_code VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                first_transaction_at TIMESTAMP,
                reward_amount DECIMAL(15,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                FOREIGN KEY (referred_id) REFERENCES users(user_id),
                UNIQUE(referred_id)
            )
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
    
    def ensure_group_exists(self, group_id: int, group_title: str = None) -> bool:
        """
        Ensure group record exists in database (auto-create if not exists).
        This is called automatically when bot receives messages from groups to track all groups.
        
        Args:
            group_id: Telegram group ID
            group_title: Optional group title
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Check if group already exists
            cursor.execute("""
                SELECT id FROM group_settings WHERE group_id = ?
            """, (group_id,))
            
            if cursor.fetchone():
                # Group exists, just update title if provided and different
                if group_title:
                    cursor.execute("""
                        UPDATE group_settings 
                        SET group_title = COALESCE(?, group_title),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE group_id = ? AND (group_title IS NULL OR group_title != ?)
                    """, (group_title, group_id, group_title))
                    conn.commit()
                return True
            
            # Group doesn't exist, create it
            cursor.execute("""
                INSERT INTO group_settings (group_id, group_title, is_active, created_at, updated_at)
                VALUES (?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (group_id, group_title))
            
            conn.commit()
            logger.debug(f"Auto-created group record: {group_id} - {group_title or 'Unknown'}")
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring group exists: {e}", exc_info=True)
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
        Get all groups with transactions (active groups).
        Combines data from group_settings and transactions tables.
        
        Returns:
            List of group dictionaries with title, settings, and stats
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get all unique group_ids from transactions, ordered by latest transaction time
        cursor.execute("""
            SELECT group_id
            FROM otc_transactions
            WHERE group_id IS NOT NULL
            GROUP BY group_id
            ORDER BY MAX(created_at) DESC
        """)
        
        transaction_groups = cursor.fetchall()
        group_ids = [row[0] for row in transaction_groups]
        
        # Get configured groups
        cursor.execute("""
            SELECT group_id, group_title, markup, usdt_address, is_active, updated_at
            FROM group_settings
            WHERE is_active = 1
        """)
        
        configured_groups = {}
        for row in cursor.fetchall():
            configured_groups[row['group_id']] = {
                'group_id': row['group_id'],
                'group_title': row['group_title'],
                'markup': float(row['markup']) if row['markup'] else 0.0,
                'usdt_address': row['usdt_address'] or '',
                'is_active': bool(row['is_active']),
                'updated_at': row['updated_at'],
                'is_configured': True
            }
        
        # Get transaction stats for each group
        cursor.execute("""
            SELECT 
                group_id,
                COUNT(*) as tx_count,
                MAX(created_at) as last_active
            FROM otc_transactions
            WHERE group_id IS NOT NULL
            GROUP BY group_id
        """)
        
        group_stats = {}
        for row in cursor.fetchall():
            group_stats[row['group_id']] = {
                'tx_count': int(row['tx_count']),
                'last_active': row['last_active']
            }
        
        # Combine all groups
        all_groups = []
        
        # Add configured groups
        for group_id, group_data in configured_groups.items():
            stats = group_stats.get(group_id, {'tx_count': 0, 'last_active': None})
            group_data.update(stats)
            all_groups.append(group_data)
        
        # Add groups with transactions but no configuration
        for group_id in group_ids:
            if group_id not in configured_groups:
                stats = group_stats.get(group_id, {'tx_count': 0, 'last_active': None})
                all_groups.append({
                    'group_id': group_id,
                    'group_title': None,  # Will try to get from Bot API
                    'markup': 0.0,
                    'usdt_address': '',
                    'is_active': True,
                    'updated_at': stats.get('last_active'),
                    'is_configured': False,
                    'tx_count': stats.get('tx_count', 0),
                    'last_active': stats.get('last_active')
                })
        
        # Sort by last_active (most recent first)
        all_groups.sort(key=lambda x: x.get('last_active') or '', reverse=True)
        
        return all_groups
    
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
                INSERT INTO otc_transactions (
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
            FROM otc_transactions
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
                FROM otc_transactions
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
                FROM otc_transactions
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
                FROM otc_transactions
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
        
        query = "SELECT COUNT(*) as count FROM otc_transactions WHERE group_id = ?"
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
                FROM otc_transactions
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
                FROM otc_transactions
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
            FROM otc_transactions
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
                    UPDATE otc_transactions
                    SET status = ?, payment_hash = ?, paid_at = CURRENT_TIMESTAMP
                    WHERE transaction_id = ?
                """, (status, payment_hash, transaction_id))
            elif status == 'confirmed':
                # Confirm transaction
                cursor.execute("""
                    UPDATE otc_transactions
                    SET status = ?, confirmed_at = CURRENT_TIMESTAMP
                    WHERE transaction_id = ?
                """, (status, transaction_id))
            elif status == 'cancelled':
                # Cancel transaction
                cursor.execute("""
                    UPDATE otc_transactions
                    SET status = ?, cancelled_at = CURRENT_TIMESTAMP, cancelled_by = ?
                    WHERE transaction_id = ?
                """, (status, cancelled_by, transaction_id))
            else:
                # Other status updates
                cursor.execute("""
                    UPDATE otc_transactions
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
                FROM otc_transactions
                WHERE group_id = ? AND status = 'pending'
                ORDER BY created_at DESC
                LIMIT ?
            """, (group_id, limit))
        else:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, created_at
                FROM otc_transactions
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
                FROM otc_transactions
                WHERE group_id = ? AND status = 'paid'
                ORDER BY paid_at DESC
                LIMIT ?
            """, (group_id, limit))
        else:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, payment_hash, paid_at, created_at
                FROM otc_transactions
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
                FROM otc_transactions
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
                FROM otc_transactions
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
                FROM otc_transactions
                WHERE user_id = ? AND DATE(created_at) >= ? AND DATE(created_at) <= ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, start_date, end_date, limit, offset))
        else:
            cursor.execute("""
                SELECT transaction_id, group_id, user_id, username, first_name,
                       cny_amount, usdt_amount, exchange_rate, markup,
                       usdt_address, status, created_at
                FROM otc_transactions
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
                FROM otc_transactions
                WHERE user_id = ? AND DATE(created_at) >= ? AND DATE(created_at) <= ?
            """, (user_id, start_date, end_date))
        else:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM otc_transactions
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
                FROM otc_transactions
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
                FROM otc_transactions
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
                FROM otc_transactions
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
    
    # ========== USDT Address Management Methods ==========
    
    def get_usdt_addresses(self, group_id: int, active_only: bool = True) -> list:
        """
        Get USDT addresses for a group.
        
        Args:
            group_id: Group ID (required, no global addresses)
            active_only: If True, only return active and confirmed addresses
            
        Returns:
            List of address dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("""
                SELECT id, group_id, address, label, qr_code_file_id, is_default, is_active,
                       needs_confirmation, pending_confirmation, confirmed_by, confirmed_at,
                       usage_count, last_used_at, created_at, created_by
                FROM usdt_addresses
                WHERE group_id = ? AND is_active = 1 AND pending_confirmation = 0
                ORDER BY is_default DESC, usage_count DESC, created_at DESC
            """, (group_id,))
        else:
            cursor.execute("""
                SELECT id, group_id, address, label, qr_code_file_id, is_default, is_active,
                       needs_confirmation, pending_confirmation, confirmed_by, confirmed_at,
                       usage_count, last_used_at, created_at, created_by
                FROM usdt_addresses
                WHERE group_id = ?
                ORDER BY pending_confirmation DESC, is_default DESC, usage_count DESC, created_at DESC
            """, (group_id,))
        
        rows = cursor.fetchall()
        addresses = []
        for row in rows:
            addresses.append({
                'id': row['id'],
                'group_id': row['group_id'],
                'address': row['address'],
                'label': row['label'],
                'qr_code_file_id': row['qr_code_file_id'],
                'is_default': bool(row['is_default']),
                'is_active': bool(row['is_active']),
                'needs_confirmation': bool(row['needs_confirmation']) if row['needs_confirmation'] is not None else False,
                'pending_confirmation': bool(row['pending_confirmation']) if row['pending_confirmation'] is not None else False,
                'confirmed_by': row['confirmed_by'],
                'confirmed_at': row['confirmed_at'],
                'usage_count': int(row['usage_count']) if row['usage_count'] else 0,
                'last_used_at': row['last_used_at'],
                'created_at': row['created_at'],
                'created_by': row['created_by']
            })
        return addresses
    
    def get_active_address(self, group_id: int, strategy: str = 'default') -> Optional[dict]:
        """
        Get an active and confirmed address using the specified strategy.
        
        Args:
            group_id: Group ID (required)
            strategy: Selection strategy ('default', 'round_robin', 'random')
            
        Returns:
            Address dictionary or None
        """
        addresses = self.get_usdt_addresses(group_id=group_id, active_only=True)
        
        if not addresses:
            return None
        
        if strategy == 'default':
            # Return default address if exists, otherwise first one
            for addr in addresses:
                if addr['is_default']:
                    return addr
            return addresses[0] if addresses else None
        
        elif strategy == 'round_robin':
            # Return address with least usage
            return min(addresses, key=lambda x: x['usage_count'])
        
        elif strategy == 'random':
            # Return random address
            import random
            return random.choice(addresses) if addresses else None
        
        else:
            # Default to first address
            return addresses[0] if addresses else None
    
    def add_usdt_address(self, group_id: int, address: str, label: str = None, 
                        qr_code_file_id: str = None, is_default: bool = False, 
                        needs_confirmation: bool = True, created_by: int = None) -> Optional[int]:
        """
        Add a new USDT address.
        
        Args:
            group_id: Group ID (required)
            address: USDT address
            label: Optional label for the address
            qr_code_file_id: Optional Telegram file ID for QR code
            is_default: Whether this should be the default address
            needs_confirmation: Whether this address needs confirmation (default True)
            created_by: Optional user ID who created this address
            
        Returns:
            Address ID if successful, None otherwise
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # If setting as default, unset other defaults for the same group
            if is_default:
                cursor.execute("""
                    UPDATE usdt_addresses 
                    SET is_default = 0 
                    WHERE group_id = ?
                """, (group_id,))
            
            # Set pending_confirmation if needs_confirmation is True
            pending_confirmation = 1 if needs_confirmation else 0
            
            cursor.execute("""
                INSERT INTO usdt_addresses (group_id, address, label, qr_code_file_id, is_default, 
                                          needs_confirmation, pending_confirmation, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (group_id, address, label or '未命名地址', qr_code_file_id, 
                  1 if is_default else 0, 1 if needs_confirmation else 0, 
                  pending_confirmation, created_by))
            
            address_id = cursor.lastrowid
            conn.commit()
            logger.info(f"USDT address added (id: {address_id}, group_id: {group_id}, label: {label})")
            return address_id
            
        except Exception as e:
            logger.error(f"Error adding USDT address: {e}", exc_info=True)
            return None
    
    def increment_address_usage(self, address_id: int) -> bool:
        """
        Increment usage count for an address.
        
        Args:
            address_id: Address ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE usdt_addresses 
                SET usage_count = usage_count + 1,
                    last_used_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (address_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing address usage: {e}", exc_info=True)
            return False
    
    def update_usdt_address(self, address_id: int, address: str = None, label: str = None, 
                           qr_code_file_id: str = None, is_default: bool = None, 
                           is_active: bool = None, needs_confirmation: bool = None) -> bool:
        """
        Update an existing USDT address.
        
        Args:
            address_id: Address ID
            address: Optional new address
            label: Optional new label
            qr_code_file_id: Optional new QR code file ID
            is_default: Optional default status
            is_active: Optional active status
            needs_confirmation: Optional needs confirmation flag (if True, sets pending_confirmation=1)
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if address is not None:
                updates.append("address = ?")
                params.append(address)
            
            if label is not None:
                updates.append("label = ?")
                params.append(label)
            
            if qr_code_file_id is not None:
                updates.append("qr_code_file_id = ?")
                params.append(qr_code_file_id)
            
            if is_default is not None:
                updates.append("is_default = ?")
                params.append(1 if is_default else 0)
                
                # If setting as default, unset other defaults for same group
                if is_default:
                    cursor.execute("""
                        SELECT group_id FROM usdt_addresses WHERE id = ?
                    """, (address_id,))
                    row = cursor.fetchone()
                    if row:
                        group_id = row['group_id']
                        cursor.execute("""
                            UPDATE usdt_addresses 
                            SET is_default = 0 
                            WHERE group_id = ? AND id != ?
                        """, (group_id, address_id))
            
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            
            if needs_confirmation is not None:
                updates.append("needs_confirmation = ?")
                params.append(1 if needs_confirmation else 0)
                # If needs confirmation, set pending_confirmation
                if needs_confirmation:
                    updates.append("pending_confirmation = 1")
                    updates.append("confirmed_by = NULL")
                    updates.append("confirmed_at = NULL")
            
            if not updates:
                return True
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(address_id)
            
            query = f"UPDATE usdt_addresses SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, tuple(params))
            
            conn.commit()
            logger.info(f"USDT address {address_id} updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating USDT address: {e}", exc_info=True)
            return False
    
    def delete_usdt_address(self, address_id: int) -> bool:
        """
        Delete a USDT address.
        
        Args:
            address_id: Address ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM usdt_addresses WHERE id = ?", (address_id,))
            conn.commit()
            
            logger.info(f"USDT address {address_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting USDT address: {e}", exc_info=True)
            return False
    
    def get_address_by_id(self, address_id: int) -> Optional[dict]:
        """
        Get address details by ID.
        
        Args:
            address_id: Address ID
            
        Returns:
            Address dictionary or None
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, group_id, address, label, qr_code_file_id, is_default, is_active,
                       needs_confirmation, pending_confirmation, confirmed_by, confirmed_at,
                       usage_count, last_used_at, created_at, created_by
                FROM usdt_addresses
                WHERE id = ?
            """, (address_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'id': row['id'],
                'group_id': row['group_id'],
                'address': row['address'],
                'label': row['label'],
                'qr_code_file_id': row['qr_code_file_id'],
                'is_default': bool(row['is_default']),
                'is_active': bool(row['is_active']),
                'needs_confirmation': bool(row['needs_confirmation']) if row['needs_confirmation'] is not None else False,
                'pending_confirmation': bool(row['pending_confirmation']) if row['pending_confirmation'] is not None else False,
                'confirmed_by': row['confirmed_by'],
                'confirmed_at': row['confirmed_at'],
                'usage_count': int(row['usage_count']) if row['usage_count'] else 0,
                'last_used_at': row['last_used_at'],
                'created_at': row['created_at'],
                'created_by': row['created_by']
            }
            
        except Exception as e:
            logger.error(f"Error getting address by ID: {e}", exc_info=True)
            return None
    
    def confirm_address(self, address_id: int, confirmed_by: int) -> bool:
        """
        Confirm an address.
        
        Args:
            address_id: Address ID
            confirmed_by: User ID who confirmed the address
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE usdt_addresses 
                SET pending_confirmation = 0,
                    confirmed_by = ?,
                    confirmed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (confirmed_by, address_id))
            
            conn.commit()
            logger.info(f"Address {address_id} confirmed by user {confirmed_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error confirming address: {e}", exc_info=True)
            return False
    
    def update_address_qr_code(self, address_id: int, qr_code_file_id: str) -> bool:
        """
        Update QR code file ID for an address.
        
        Args:
            address_id: Address ID
            qr_code_file_id: Telegram file ID for QR code
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE usdt_addresses 
                SET qr_code_file_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (qr_code_file_id, address_id))
            
            conn.commit()
            logger.info(f"QR code updated for address {address_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating QR code: {e}", exc_info=True)
            return False
    
    # ========== Template Methods ==========
    
    def get_templates(self, user_id: Optional[int] = None, template_type: str = None, limit: Optional[int] = None) -> list:
        """
        Get templates for a user or all preset templates.
        
        Args:
            user_id: Optional user ID (None for preset templates only)
            template_type: Optional template type filter ('amount' or 'formula')
            limit: Optional limit on number of templates to return
            
        Returns:
            List of template dictionaries (sorted by is_preset DESC, usage_count DESC)
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM settlement_templates WHERE 1=1"
        params = []
        
        if user_id is None:
            # Get preset templates only (user_id IS NULL)
            query += " AND user_id IS NULL"
        else:
            # Get user's templates
            query += " AND user_id = ?"
            params.append(user_id)
        
        if template_type:
            query += " AND template_type = ?"
            params.append(template_type)
        
        # Order: preset first, then by usage count (most used first), then by creation time
        query += " ORDER BY is_preset DESC, usage_count DESC, created_at DESC"
        
        # Add limit if specified
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        templates = []
        for row in rows:
            templates.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'template_name': row['template_name'],
                'template_value': row['template_value'],
                'template_type': row['template_type'],
                'is_preset': bool(row['is_preset']),
                'usage_count': int(row['usage_count']) if row['usage_count'] else 0,
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        return templates
    
    def create_template(self, user_id: int, template_name: str, template_value: str, 
                       template_type: str) -> bool:
        """
        Create a new template.
        
        Args:
            user_id: User ID (required for user templates)
            template_name: Template name/label
            template_value: Template value (amount or formula)
            template_type: Template type ('amount' or 'formula')
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO settlement_templates (user_id, template_name, template_value, template_type)
                VALUES (?, ?, ?, ?)
            """, (user_id, template_name, template_value, template_type))
            
            conn.commit()
            logger.info(f"Template created for user {user_id}: {template_name} = {template_value}")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"Template already exists for user {user_id}: {template_name}")
            return False
        except Exception as e:
            logger.error(f"Error creating template: {e}", exc_info=True)
            return False
    
    def update_template(self, template_id: int, template_name: str = None, 
                       template_value: str = None) -> bool:
        """
        Update an existing template.
        
        Args:
            template_id: Template ID
            template_name: Optional new template name
            template_value: Optional new template value
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if template_name is not None:
                updates.append("template_name = ?")
                params.append(template_name)
            
            if template_value is not None:
                updates.append("template_value = ?")
                params.append(template_value)
            
            if not updates:
                return True
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(template_id)
            
            query = f"UPDATE settlement_templates SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, tuple(params))
            
            conn.commit()
            logger.info(f"Template {template_id} updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating template: {e}", exc_info=True)
            return False
    
    def delete_template(self, template_id: int) -> bool:
        """
        Delete a template (only user templates, not preset).
        
        Args:
            template_id: Template ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Only allow deleting user templates (not preset)
            cursor.execute("""
                DELETE FROM settlement_templates 
                WHERE id = ? AND (is_preset = 0 OR is_preset IS NULL)
            """, (template_id,))
            
            conn.commit()
            logger.info(f"Template {template_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting template: {e}", exc_info=True)
            return False
    
    def increment_template_usage(self, template_id: int) -> bool:
        """
        Increment usage count for a template.
        
        Args:
            template_id: Template ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE settlement_templates 
                SET usage_count = usage_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (template_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing template usage: {e}", exc_info=True)
            return False
    
    def get_template(self, template_id: int) -> Optional[dict]:
        """
        Get template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Template dictionary or None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM settlement_templates WHERE id = ?
        """, (template_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'template_name': row['template_name'],
                'template_value': row['template_value'],
                'template_type': row['template_type'],
                'is_preset': bool(row['is_preset']),
                'usage_count': int(row['usage_count']) if row['usage_count'] else 0,
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None
    
    # ========== Customer Service Management Methods ==========
    
    def add_customer_service_account(self, username: str, display_name: str = None, 
                                     weight: int = 5, max_concurrent: int = 50) -> bool:
        """
        Add a new customer service account.
        
        Args:
            username: Service account username (without @)
            display_name: Display name (optional)
            weight: Weight for assignment (1-10, default 5)
            max_concurrent: Maximum concurrent customers (default 50)
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO customer_service_accounts 
                (username, display_name, status, weight, max_concurrent, is_active)
                VALUES (?, ?, 'available', ?, ?, 1)
            """, (username, display_name or username, weight, max_concurrent))
            
            conn.commit()
            logger.info(f"Customer service account added: {username}")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"Customer service account already exists: {username}")
            return False
        except Exception as e:
            logger.error(f"Error adding customer service account: {e}", exc_info=True)
            return False
    
    def get_customer_service_accounts(self, active_only: bool = True) -> list:
        """
        Get all customer service accounts.
        
        Args:
            active_only: Only return active accounts
            
        Returns:
            List of account dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("""
                SELECT * FROM customer_service_accounts 
                WHERE is_active = 1
                ORDER BY weight DESC, current_count ASC, created_at ASC
            """)
        else:
            cursor.execute("""
                SELECT * FROM customer_service_accounts 
                ORDER BY is_active DESC, weight DESC, current_count ASC
            """)
        
        accounts = []
        for row in cursor.fetchall():
            accounts.append({
                'id': row['id'],
                'username': row['username'],
                'display_name': row['display_name'] or row['username'],
                'status': row['status'],
                'weight': int(row['weight']),
                'max_concurrent': int(row['max_concurrent']),
                'current_count': int(row['current_count']),
                'total_served': int(row['total_served']),
                'is_active': bool(row['is_active']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        return accounts
    
    def get_customer_service_account(self, account_id: int = None, username: str = None) -> Optional[dict]:
        """
        Get customer service account by ID or username.
        
        Args:
            account_id: Account ID
            username: Account username
            
        Returns:
            Account dictionary or None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if account_id:
            cursor.execute("SELECT * FROM customer_service_accounts WHERE id = ?", (account_id,))
        elif username:
            cursor.execute("SELECT * FROM customer_service_accounts WHERE username = ?", (username,))
        else:
            return None
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'username': row['username'],
                'display_name': row['display_name'] or row['username'],
                'status': row['status'],
                'weight': int(row['weight']),
                'max_concurrent': int(row['max_concurrent']),
                'current_count': int(row['current_count']),
                'total_served': int(row['total_served']),
                'is_active': bool(row['is_active']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None
    
    def update_customer_service_account(self, account_id: int, display_name: str = None,
                                        weight: int = None, max_concurrent: int = None,
                                        status: str = None) -> bool:
        """
        Update customer service account.
        
        Args:
            account_id: Account ID
            display_name: New display name
            weight: New weight
            max_concurrent: New max concurrent
            status: New status (available/offline/busy/disabled)
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if display_name is not None:
                updates.append("display_name = ?")
                params.append(display_name)
            if weight is not None:
                updates.append("weight = ?")
                params.append(weight)
            if max_concurrent is not None:
                updates.append("max_concurrent = ?")
                params.append(max_concurrent)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(account_id)
            
            cursor.execute(f"""
                UPDATE customer_service_accounts 
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            
            conn.commit()
            logger.info(f"Customer service account {account_id} updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating customer service account: {e}", exc_info=True)
            return False
    
    def toggle_customer_service_account(self, account_id: int) -> bool:
        """
        Toggle customer service account active status.
        
        Args:
            account_id: Account ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE customer_service_accounts 
                SET is_active = NOT is_active,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (account_id,))
            
            conn.commit()
            
            # Get new status
            cursor.execute("SELECT is_active FROM customer_service_accounts WHERE id = ?", (account_id,))
            is_active = bool(cursor.fetchone()['is_active'])
            logger.info(f"Customer service account {account_id} toggled to {'active' if is_active else 'inactive'}")
            return True
            
        except Exception as e:
            logger.error(f"Error toggling customer service account: {e}", exc_info=True)
            return False
    
    def delete_customer_service_account(self, account_id: int) -> bool:
        """
        Delete customer service account.
        
        Args:
            account_id: Account ID
            
        Returns:
            True if successful
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM customer_service_accounts WHERE id = ?", (account_id,))
            
            conn.commit()
            logger.info(f"Customer service account {account_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting customer service account: {e}", exc_info=True)
            return False
    
    def assign_customer_service(self, user_id: int, username: str, assignment_method: str = 'smart') -> Optional[str]:
        """
        Assign a customer service account to a user.
        
        Args:
            user_id: User ID
            username: Username
            assignment_method: Assignment method (smart/round_robin/least_busy/weighted)
            
        Returns:
            Service account username or None
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Get available accounts based on method
            if assignment_method == 'smart':
                # Smart hybrid: available + online + not maxed out, then least busy, then by weight
                cursor.execute("""
                    SELECT * FROM customer_service_accounts 
                    WHERE is_active = 1 
                    AND status IN ('available', 'busy')
                    AND current_count < max_concurrent
                    ORDER BY current_count ASC, weight DESC, created_at ASC
                    LIMIT 1
                """)
                row = cursor.fetchone()
                
                # Fallback to round-robin if no available account
                if not row:
                    cursor.execute("""
                        SELECT * FROM customer_service_accounts 
                        WHERE is_active = 1
                        ORDER BY created_at ASC
                        LIMIT 1
                    """)
                    row = cursor.fetchone()
                    
            elif assignment_method == 'least_busy':
                cursor.execute("""
                    SELECT * FROM customer_service_accounts 
                    WHERE is_active = 1 
                    AND status IN ('available', 'busy')
                    AND current_count < max_concurrent
                    ORDER BY current_count ASC
                    LIMIT 1
                """)
                row = cursor.fetchone()
                
            elif assignment_method == 'weighted':
                cursor.execute("""
                    SELECT * FROM customer_service_accounts 
                    WHERE is_active = 1 
                    AND status IN ('available', 'busy')
                    AND current_count < max_concurrent
                    ORDER BY weight DESC, current_count ASC
                    LIMIT 1
                """)
                row = cursor.fetchone()
                
            else:  # round_robin (default)
                # Simple round-robin: get account with least recent assignment
                cursor.execute("""
                    SELECT csa.* FROM customer_service_accounts csa
                    LEFT JOIN (
                        SELECT service_account, MAX(assigned_at) as last_assigned
                        FROM customer_service_assignments
                        WHERE status = 'active'
                        GROUP BY service_account
                    ) last_assign ON csa.username = last_assign.service_account
                    WHERE csa.is_active = 1
                    ORDER BY last_assign.last_assigned ASC NULLS FIRST, csa.created_at ASC
                    LIMIT 1
                """)
                row = cursor.fetchone()
            
            if not row:
                logger.warning("No customer service account available for assignment")
                return None
            
            service_account = row['username']
            
            # Update current_count
            cursor.execute("""
                UPDATE customer_service_accounts 
                SET current_count = current_count + 1,
                    total_served = total_served + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
            """, (service_account,))
            
            # Record assignment
            cursor.execute("""
                INSERT INTO customer_service_assignments 
                (user_id, username, service_account, assignment_method, status)
                VALUES (?, ?, ?, ?, 'active')
            """, (user_id, username, service_account, assignment_method))
            
            conn.commit()
            logger.info(f"Assigned customer service {service_account} to user {user_id}")
            return service_account
            
        except Exception as e:
            logger.error(f"Error assigning customer service: {e}", exc_info=True)
            return None
    
    def get_customer_service_stats(self) -> dict:
        """
        Get customer service statistics.
        
        Returns:
            Dictionary with statistics
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Total accounts
        cursor.execute("SELECT COUNT(*) FROM customer_service_accounts")
        total_accounts = cursor.fetchone()[0]
        
        # Active accounts
        cursor.execute("SELECT COUNT(*) FROM customer_service_accounts WHERE is_active = 1")
        active_accounts = cursor.fetchone()[0]
        
        # Total served
        cursor.execute("SELECT SUM(total_served) FROM customer_service_accounts")
        total_served = cursor.fetchone()[0] or 0
        
        # Today's assignments
        cursor.execute("""
            SELECT COUNT(*) FROM customer_service_assignments 
            WHERE DATE(assigned_at) = DATE('now')
        """)
        today_served = cursor.fetchone()[0]
        
        # Accounts with stats
        cursor.execute("""
            SELECT id, username, display_name, status, weight, max_concurrent, 
                   current_count, total_served, is_active
            FROM customer_service_accounts
            ORDER BY total_served DESC
        """)
        
        accounts = []
        for row in cursor.fetchall():
            accounts.append({
                'id': row['id'],
                'username': row['username'],
                'display_name': row['display_name'] or row['username'],
                'status': row['status'],
                'weight': int(row['weight']),
                'max_concurrent': int(row['max_concurrent']),
                'current_count': int(row['current_count']),
                'total_served': int(row['total_served']),
                'is_active': bool(row['is_active'])
            })
        
        return {
            'total_accounts': total_accounts,
            'active_accounts': active_accounts,
            'total_served': total_served,
            'today_served': today_served,
            'accounts': accounts
        }


# Global database instance
db = Database()

