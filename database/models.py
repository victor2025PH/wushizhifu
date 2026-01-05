"""
Database models and table creation
"""
import sqlite3
from datetime import datetime
from typing import Optional
from database.db import db
import logging

logger = logging.getLogger(__name__)


def init_database():
    """Initialize database tables"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Users table
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
        
        # Create indexes for users
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username 
            ON users(username)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_created_at 
            ON users(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_status 
            ON users(status)
        """)
        
        # Transactions table
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
        
        # Create indexes for transactions
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
            ON transactions(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_order_id 
            ON transactions(order_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_status 
            ON transactions(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_created_at 
            ON transactions(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_payment_channel 
            ON transactions(payment_channel)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_status 
            ON transactions(user_id, status)
        """)
        
        # Rate configs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_configs (
                config_id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel VARCHAR(20) NOT NULL,
                vip_level INTEGER DEFAULT 0,
                rate_percentage DECIMAL(5,4) NOT NULL,
                min_amount DECIMAL(15,2) DEFAULT 1,
                max_amount DECIMAL(15,2) DEFAULT 500000,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rate_configs_channel_vip 
            ON rate_configs(channel, vip_level)
        """)
        
        # Admins table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT UNIQUE NOT NULL,
                role VARCHAR(20) DEFAULT 'admin',
                permissions TEXT,
                added_by BIGINT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admins_user_id 
            ON admins(user_id)
        """)
        
        # Groups table
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
        
        # Group members (pending verification)
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
        
        # Sensitive words table
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
        
        # Video configs table (视频配置表)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_type VARCHAR(20) NOT NULL UNIQUE,
                channel_id BIGINT NOT NULL,
                message_id INTEGER NOT NULL,
                file_id TEXT NOT NULL,
                file_unique_id VARCHAR(255),
                file_size INTEGER,
                duration INTEGER,
                thumbnail_file_id TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by BIGINT,
                UNIQUE(video_type)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_video_configs_type 
            ON video_configs(video_type)
        """)
        
        # Initialize default rate configs
        cursor.execute("SELECT COUNT(*) FROM rate_configs")
        if cursor.fetchone()[0] == 0:
            default_rates = [
                ('alipay', 0, 0.0060, 1, 500000, 1),
                ('alipay', 1, 0.0055, 1, 500000, 1),
                ('alipay', 2, 0.0050, 1, 500000, 1),
                ('alipay', 3, 0.0045, 1, 500000, 1),
                ('wechat', 0, 0.0060, 1, 500000, 1),
                ('wechat', 1, 0.0055, 1, 500000, 1),
                ('wechat', 2, 0.0050, 1, 500000, 1),
                ('wechat', 3, 0.0045, 1, 500000, 1),
            ]
            cursor.executemany("""
                INSERT INTO rate_configs 
                (channel, vip_level, rate_percentage, min_amount, max_amount, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, default_rates)
        
        # Initialize initial admins
        from config import Config
        for admin_id in Config.INITIAL_ADMINS:
            cursor.execute("""
                INSERT OR IGNORE INTO admins (user_id, role, status)
                VALUES (?, 'admin', 'active')
            """, (admin_id,))
            logger.info(f"Initialized admin: {admin_id}")
        
        # ========== BotB Tables (OTC Group Management) ==========
        
        # Settings table for admin_markup and usdt_address
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
        
        # Group settings table for group-level markup and address
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
        
        # User settings table for user preferences and onboarding
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
        
        # Price history table for price tracking
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
        
        # Price alerts table for user price alerts
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
        
        # Settlement templates table for quick settlement templates
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
        
        # USDT addresses table for multiple address management
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
        
        # Operation logs table for audit trail
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
        
        # OTC Transactions table (BotB's transaction format - renamed to avoid conflict with BotA's transactions)
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
        
        # Add columns if they don't exist (migration for existing databases)
        cursor.execute("PRAGMA table_info(otc_transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'paid_at' not in columns:
            cursor.execute("ALTER TABLE otc_transactions ADD COLUMN paid_at TIMESTAMP")
        if 'cancelled_at' not in columns:
            cursor.execute("ALTER TABLE otc_transactions ADD COLUMN cancelled_at TIMESTAMP")
        if 'cancelled_by' not in columns:
            cursor.execute("ALTER TABLE otc_transactions ADD COLUMN cancelled_by BIGINT")
        if 'price_source' not in columns:
            cursor.execute("ALTER TABLE otc_transactions ADD COLUMN price_source TEXT")
        
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
        
        # Customer service accounts table for managing customer service accounts
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
        
        # Customer service assignments table for tracking assignments
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
        
        conn.commit()
        logger.info("Database tables initialized successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
        raise
    
    finally:
        cursor.close()


def get_timestamp() -> str:
    """Get current timestamp string"""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

