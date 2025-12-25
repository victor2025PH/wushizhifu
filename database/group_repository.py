"""
Group repository for database operations
"""
from typing import List, Optional
from datetime import datetime
from database.db import db
import logging

logger = logging.getLogger(__name__)


class GroupRepository:
    """Repository for group database operations"""
    
    @staticmethod
    def create_or_update_group(group_id: int, group_title: Optional[str] = None,
                               verification_enabled: bool = False,
                               verification_type: str = "none") -> dict:
        """Create or update group"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE groups 
                    SET group_title = ?, verification_enabled = ?,
                        verification_type = ?, updated_at = ?
                    WHERE group_id = ?
                """, (group_title, int(verification_enabled), verification_type, now, group_id))
            else:
                cursor.execute("""
                    INSERT INTO groups 
                    (group_id, group_title, verification_enabled, verification_type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (group_id, group_title, int(verification_enabled), verification_type, now, now))
            
            conn.commit()
            
            cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
            group = cursor.fetchone()
            return dict(group) if group else {}
            
        except Exception as e:
            logger.error(f"Error creating/updating group: {e}")
            conn.rollback()
            raise
    
    @staticmethod
    def get_group(group_id: int) -> Optional[dict]:
        """Get group by ID"""
        cursor = db.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
        group = cursor.fetchone()
        return dict(group) if group else None
    
    @staticmethod
    def add_member(group_id: int, user_id: int, status: str = "pending") -> dict:
        """Add group member (pending verification)"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                INSERT OR REPLACE INTO group_members 
                (group_id, user_id, status, joined_at)
                VALUES (?, ?, ?, ?)
            """, (group_id, user_id, status, now))
            
            conn.commit()
            
            cursor.execute("""
                SELECT * FROM group_members 
                WHERE group_id = ? AND user_id = ?
            """, (group_id, user_id))
            member = cursor.fetchone()
            return dict(member) if member else {}
            
        except Exception as e:
            logger.error(f"Error adding group member: {e}")
            conn.rollback()
            raise
    
    @staticmethod
    def verify_member(group_id: int, user_id: int) -> bool:
        """Verify group member"""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cursor = db.execute("""
            UPDATE group_members 
            SET status = 'verified', verified_at = ?
            WHERE group_id = ? AND user_id = ?
        """, (now, group_id, user_id))
        db.commit()
        return cursor.rowcount > 0
    
    @staticmethod
    def get_pending_members(group_id: int) -> List[dict]:
        """Get pending members for verification"""
        cursor = db.execute("""
            SELECT * FROM group_members 
            WHERE group_id = ? AND status = 'pending'
            ORDER BY joined_at ASC
        """, (group_id,))
        members = cursor.fetchall()
        return [dict(m) for m in members]
    
    @staticmethod
    def is_member_verified(group_id: int, user_id: int) -> bool:
        """Check if member is verified"""
        cursor = db.execute("""
            SELECT COUNT(*) FROM group_members 
            WHERE group_id = ? AND user_id = ? AND status = 'verified'
        """, (group_id, user_id))
        return cursor.fetchone()[0] > 0
    
    @staticmethod
    def set_verification_enabled(group_id: int, enabled: bool):
        """Enable/disable verification for group"""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        db.execute("""
            UPDATE groups 
            SET verification_enabled = ?, updated_at = ?
            WHERE group_id = ?
        """, (int(enabled), now, group_id))
        db.commit()

