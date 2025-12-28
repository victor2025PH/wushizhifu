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
        
        # Referral codes table (推荐码)
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
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_referral_codes_code 
            ON referral_codes(referral_code)
        """)
        
        # Referrals table (推荐关系)
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
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_referrals_referrer 
            ON referrals(referrer_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_referrals_referred 
            ON referrals(referred_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_referrals_status 
            ON referrals(status)
        """)
        
        # Referral rewards table (奖励记录)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referral_rewards (
                reward_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT NOT NULL,
                reward_type VARCHAR(20) NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                referral_id INTEGER,
                description TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                paid_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (referral_id) REFERENCES referrals(referral_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_referral_rewards_user 
            ON referral_rewards(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_referral_rewards_status 
            ON referral_rewards(status)
        """)
        
        # Lottery entries table (抽奖记录)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lottery_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT NOT NULL,
                prize_level INTEGER NOT NULL,
                prize_amount DECIMAL(15,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                claimed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_lottery_entries_user 
            ON lottery_entries(user_id)
        """)
        
        # Monthly rankings table (月度排行榜)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_rankings (
                ranking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT NOT NULL,
                month VARCHAR(7) NOT NULL,
                invite_count INTEGER DEFAULT 0,
                rank INTEGER,
                reward_amount DECIMAL(15,2) DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                paid_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, month)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_monthly_rankings_month 
            ON monthly_rankings(month)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_monthly_rankings_user_month 
            ON monthly_rankings(user_id, month)
        """)
        
        # Verification questions table (审核问题库)
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
        
        # Verification records table (审核记录)
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
        
        # Verification configs table (审核配置)
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
        
        # Initialize default questions (全局默认问题)
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

