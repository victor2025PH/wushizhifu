"""
Admin repository for database operations
"""
from typing import List, Optional
from database.db import db
import logging

logger = logging.getLogger(__name__)


class AdminRepository:
    """Repository for admin database operations"""
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """
        Check if user is admin.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is admin
        """
        cursor = db.execute(
            "SELECT COUNT(*) FROM admins WHERE user_id = ? AND status = 'active'",
            (user_id,)
        )
        return cursor.fetchone()[0] > 0
    
    @staticmethod
    def add_admin(user_id: int, role: str = "admin", 
                  added_by: Optional[int] = None) -> bool:
        """
        Add admin.
        
        Args:
            user_id: Telegram user ID
            role: Admin role
            added_by: User ID who added this admin
            
        Returns:
            True if successful
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO admins (user_id, role, added_by)
                VALUES (?, ?, ?)
            """, (user_id, role, added_by))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error adding admin: {e}")
            conn.rollback()
            return False
    
    @staticmethod
    def remove_admin(user_id: int) -> bool:
        """Remove admin"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE admins SET status = 'inactive' WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error removing admin: {e}")
            conn.rollback()
            return False
    
    @staticmethod
    def get_all_admins() -> List[dict]:
        """Get all active admins"""
        cursor = db.execute(
            "SELECT * FROM admins WHERE status = 'active'"
        )
        admins = cursor.fetchall()
        return [dict(a) for a in admins]
    
    @staticmethod
    def get_admin(user_id: int) -> Optional[dict]:
        """Get admin by user ID"""
        cursor = db.execute(
            "SELECT * FROM admins WHERE user_id = ? AND status = 'active'",
            (user_id,)
        )
        admin = cursor.fetchone()
        return dict(admin) if admin else None

