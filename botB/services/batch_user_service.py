"""
Batch user operation service for handling bulk user operations
"""
import logging
from typing import List, Dict, Tuple
from database import db

logger = logging.getLogger(__name__)


class BatchUserService:
    """Service for batch user operations"""
    
    @staticmethod
    def batch_set_vip(user_ids: List[int], vip_level: int) -> Dict[str, any]:
        """
        Batch set VIP level for multiple users.
        
        Args:
            user_ids: List of user IDs
            vip_level: VIP level to set (0-10)
            
        Returns:
            Dict with success_count, failed_count, and details
        """
        if vip_level < 0 or vip_level > 10:
            raise ValueError("VIP level must be between 0 and 10")
        
        if len(user_ids) > 50:
            raise ValueError("Batch operation supports up to 50 users at a time")
        
        success_count = 0
        failed_count = 0
        failed_users = []
        
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            for user_id in user_ids:
                try:
                    cursor.execute("""
                        UPDATE users 
                        SET vip_level = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """, (vip_level, user_id))
                    
                    if cursor.rowcount > 0:
                        success_count += 1
                    else:
                        failed_count += 1
                        failed_users.append(user_id)
                except Exception as e:
                    logger.error(f"Error setting VIP for user {user_id}: {e}")
                    failed_count += 1
                    failed_users.append(user_id)
            
            conn.commit()
            
            return {
                'success_count': success_count,
                'failed_count': failed_count,
                'failed_users': failed_users,
                'vip_level': vip_level
            }
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in batch_set_vip: {e}", exc_info=True)
            raise
        finally:
            cursor.close()
    
    @staticmethod
    def batch_disable_users(user_ids: List[int], disable: bool = True) -> Dict[str, any]:
        """
        Batch disable or enable multiple users.
        
        Args:
            user_ids: List of user IDs
            disable: True to disable, False to enable
            
        Returns:
            Dict with success_count, failed_count, and details
        """
        if len(user_ids) > 50:
            raise ValueError("Batch operation supports up to 50 users at a time")
        
        status = 'disabled' if disable else 'active'
        success_count = 0
        failed_count = 0
        failed_users = []
        
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            for user_id in user_ids:
                try:
                    cursor.execute("""
                        UPDATE users 
                        SET status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """, (status, user_id))
                    
                    if cursor.rowcount > 0:
                        success_count += 1
                    else:
                        failed_count += 1
                        failed_users.append(user_id)
                except Exception as e:
                    logger.error(f"Error {'disabling' if disable else 'enabling'} user {user_id}: {e}")
                    failed_count += 1
                    failed_users.append(user_id)
            
            conn.commit()
            
            return {
                'success_count': success_count,
                'failed_count': failed_count,
                'failed_users': failed_users,
                'action': 'disable' if disable else 'enable'
            }
        except Exception as e:
            conn.rollback()
            logger.error(f"Error in batch_disable_users: {e}", exc_info=True)
            raise
        finally:
            cursor.close()
    
    @staticmethod
    def batch_export_users(user_ids: List[int]) -> Tuple[List[Dict], int]:
        """
        Batch export user data for specified user IDs.
        
        Args:
            user_ids: List of user IDs to export
            
        Returns:
            Tuple of (user_data_list, total_count)
        """
        if len(user_ids) > 100:
            raise ValueError("Batch export supports up to 100 users at a time")
        
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            # Create placeholders for IN clause
            placeholders = ','.join('?' * len(user_ids))
            
            cursor.execute(f"""
                SELECT user_id, username, first_name, vip_level, status, 
                       total_transactions, total_amount, created_at
                FROM users
                WHERE user_id IN ({placeholders})
                ORDER BY created_at DESC
            """, user_ids)
            
            users = cursor.fetchall()
            return (users, len(users))
        except Exception as e:
            logger.error(f"Error in batch_export_users: {e}", exc_info=True)
            raise
        finally:
            cursor.close()
    
    @staticmethod
    def validate_user_ids(user_ids_str: str) -> List[int]:
        """
        Validate and parse user IDs string.
        
        Args:
            user_ids_str: Comma-separated user IDs string
            
        Returns:
            List of valid user IDs
            
        Raises:
            ValueError: If format is invalid
        """
        if not user_ids_str or not user_ids_str.strip():
            raise ValueError("User IDs cannot be empty")
        
        # Split by comma and strip whitespace
        ids_str_list = [id_str.strip() for id_str in user_ids_str.split(',')]
        
        # Validate and convert to integers
        user_ids = []
        invalid_ids = []
        
        for id_str in ids_str_list:
            try:
                user_id = int(id_str)
                if user_id > 0:  # User IDs should be positive
                    user_ids.append(user_id)
                else:
                    invalid_ids.append(id_str)
            except ValueError:
                invalid_ids.append(id_str)
        
        if invalid_ids:
            raise ValueError(f"Invalid user IDs: {', '.join(invalid_ids)}")
        
        if not user_ids:
            raise ValueError("No valid user IDs found")
        
        return user_ids
