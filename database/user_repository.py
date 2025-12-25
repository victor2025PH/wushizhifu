"""
User repository for database operations
"""
from typing import Optional
from datetime import datetime
from database.db import db
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user database operations"""
    
    @staticmethod
    def create_or_update_user(user_id: int, username: Optional[str], 
                              first_name: Optional[str], last_name: Optional[str],
                              language_code: Optional[str] = None,
                              is_premium: bool = False) -> dict:
        """
        Create or update user in database.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: First name
            last_name: Last name
            language_code: Language code
            is_premium: Is premium user
            
        Returns:
            User data dictionary
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            existing = cursor.fetchone()
            
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            
            if existing:
                # Update existing user
                cursor.execute("""
                    UPDATE users 
                    SET username = ?, first_name = ?, last_name = ?,
                        language_code = ?, is_premium = ?,
                        last_active_at = ?, updated_at = ?
                    WHERE user_id = ?
                """, (username, first_name, last_name, language_code, 
                      int(is_premium), now, now, user_id))
            else:
                # Create new user
                cursor.execute("""
                    INSERT INTO users 
                    (user_id, username, first_name, last_name, language_code, 
                     is_premium, created_at, updated_at, last_active_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, username, first_name, last_name, language_code,
                      int(is_premium), now, now, now))
            
            conn.commit()
            
            # Fetch updated user
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            return dict(user) if user else {}
            
        except Exception as e:
            logger.error(f"Error creating/updating user {user_id}: {e}")
            conn.rollback()
            raise
    
    @staticmethod
    def get_user(user_id: int) -> Optional[dict]:
        """
        Get user by ID.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User data dictionary or None
        """
        cursor = db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None
    
    @staticmethod
    def update_vip_level(user_id: int, vip_level: int):
        """Update user VIP level"""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        db.execute("""
            UPDATE users 
            SET vip_level = ?, updated_at = ?
            WHERE user_id = ?
        """, (vip_level, now, user_id))
        db.commit()
    
    @staticmethod
    def update_statistics(user_id: int, amount: float):
        """Update user transaction statistics"""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        db.execute("""
            UPDATE users 
            SET total_transactions = total_transactions + 1,
                total_amount = total_amount + ?,
                updated_at = ?
            WHERE user_id = ?
        """, (amount, now, user_id))
        db.commit()

