"""
User service for managing user data and operations
"""
from typing import Optional
from datetime import datetime
from aiogram.types import User
from database.user_repository import UserRepository


class UserService:
    """Service for user-related operations"""
    
    @classmethod
    def register_user(cls, user: User) -> dict:
        """
        Register or update user information.
        
        Args:
            user: Telegram User object
            
        Returns:
            User data dictionary
        """
        return UserRepository.create_or_update_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=getattr(user, "language_code", None),
            is_premium=getattr(user, "is_premium", False)
        )
    
    @classmethod
    def get_user(cls, user_id: int) -> Optional[dict]:
        """
        Get user data by user ID.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User data dictionary or None if not found
        """
        return UserRepository.get_user(user_id)
    
    @classmethod
    def update_last_seen(cls, user_id: int):
        """
        Update user's last seen timestamp.
        
        Args:
            user_id: Telegram user ID
        """
        # Last seen is updated automatically in register_user
        pass
    
    @classmethod
    def increment_message_count(cls, user_id: int):
        """
        Increment user's message count.
        
        Args:
            user_id: Telegram user ID
        """
        # Message count is not tracked separately in database
        pass
    
    @classmethod
    def get_total_users(cls) -> int:
        """
        Get total number of registered users.
        
        Returns:
            Total user count
        """
        from database.db import db
        cursor = db.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]
    
    @classmethod
    def is_new_user(cls, user_id: int) -> bool:
        """
        Check if user is new (first interaction).
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is new, False otherwise
        """
        user_data = cls.get_user(user_id)
        if not user_data:
            return True
        # Check if user has any transactions
        from database.transaction_repository import TransactionRepository
        count = TransactionRepository.get_transaction_count(user_id)
        return count == 0

