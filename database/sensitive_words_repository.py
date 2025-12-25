"""
Sensitive words repository for database operations
"""
from typing import List, Optional
from database.db import db
import logging

logger = logging.getLogger(__name__)


class SensitiveWordsRepository:
    """Repository for sensitive words database operations"""
    
    @staticmethod
    def add_word(group_id: Optional[int], word: str, action: str = "warn",
                 added_by: Optional[int] = None) -> bool:
        """
        Add sensitive word.
        
        Args:
            group_id: Group ID (None for global)
            word: Sensitive word
            action: Action to take (warn, delete, ban)
            added_by: User ID who added this word
            
        Returns:
            True if successful
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO sensitive_words 
                (group_id, word, action, added_by)
                VALUES (?, ?, ?, ?)
            """, (group_id, word.lower(), action, added_by))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error adding sensitive word: {e}")
            conn.rollback()
            return False
    
    @staticmethod
    def remove_word(word_id: int) -> bool:
        """Remove sensitive word by ID"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE sensitive_words SET is_active = 0 WHERE word_id = ?",
                (word_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error removing sensitive word: {e}")
            conn.rollback()
            return False
    
    @staticmethod
    def get_words(group_id: Optional[int] = None) -> List[dict]:
        """
        Get sensitive words.
        
        Args:
            group_id: Group ID (None for global words)
            
        Returns:
            List of sensitive words
        """
        if group_id:
            cursor = db.execute("""
                SELECT * FROM sensitive_words 
                WHERE (group_id = ? OR group_id IS NULL) AND is_active = 1
                ORDER BY group_id DESC, word_id ASC
            """, (group_id,))
        else:
            cursor = db.execute("""
                SELECT * FROM sensitive_words 
                WHERE group_id IS NULL AND is_active = 1
                ORDER BY word_id ASC
            """)
        
        words = cursor.fetchall()
        return [dict(w) for w in words]
    
    @staticmethod
    def check_message(message_text: str, group_id: Optional[int] = None) -> Optional[dict]:
        """
        Check if message contains sensitive words.
        
        Args:
            message_text: Message text to check
            group_id: Group ID (for group-specific words)
            
        Returns:
            First matching sensitive word dict or None
        """
        words = SensitiveWordsRepository.get_words(group_id)
        message_lower = message_text.lower()
        
        for word_data in words:
            if word_data['word'].lower() in message_lower:
                return word_data
        
        return None

