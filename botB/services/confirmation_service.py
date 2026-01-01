"""
Confirmation service for handling user confirmations before critical operations
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ConfirmationService:
    """Service for managing operation confirmations"""
    
    # Store pending confirmations: {user_id: {operation: data, expires_at: timestamp}}
    _pending_confirmations: Dict[int, Dict] = {}
    _confirmation_ttl = 300  # 5 minutes TTL
    
    @staticmethod
    def create_confirmation(user_id: int, operation: str, operation_data: dict) -> str:
        """
        Create a confirmation token for an operation.
        
        Args:
            user_id: User ID requesting the operation
            operation: Operation type (e.g., 'delete_admin', 'disable_user')
            operation_data: Data related to the operation
            
        Returns:
            Confirmation token (can be used in confirmation commands)
        """
        # Clean expired confirmations
        ConfirmationService._clean_expired()
        
        # Generate token (simple hash based on user_id, operation, and timestamp)
        token = f"{user_id}_{operation}_{datetime.now().timestamp()}"
        
        # Store confirmation
        ConfirmationService._pending_confirmations[user_id] = {
            'token': token,
            'operation': operation,
            'data': operation_data,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=ConfirmationService._confirmation_ttl)
        }
        
        return token
    
    @staticmethod
    def get_confirmation(user_id: int) -> Optional[Dict]:
        """
        Get pending confirmation for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Confirmation data or None
        """
        ConfirmationService._clean_expired()
        
        if user_id not in ConfirmationService._pending_confirmations:
            return None
        
        confirmation = ConfirmationService._pending_confirmations[user_id]
        
        # Check if expired
        if datetime.now() > confirmation['expires_at']:
            del ConfirmationService._pending_confirmations[user_id]
            return None
        
        return confirmation
    
    @staticmethod
    def confirm_operation(user_id: int) -> Optional[Dict]:
        """
        Confirm and consume a pending operation.
        
        Args:
            user_id: User ID
            
        Returns:
            Confirmation data if found and valid, None otherwise
        """
        confirmation = ConfirmationService.get_confirmation(user_id)
        
        if confirmation:
            # Remove after confirmation
            del ConfirmationService._pending_confirmations[user_id]
            return confirmation
        
        return None
    
    @staticmethod
    def cancel_confirmation(user_id: int) -> bool:
        """
        Cancel a pending confirmation.
        
        Args:
            user_id: User ID
            
        Returns:
            True if cancellation was successful
        """
        if user_id in ConfirmationService._pending_confirmations:
            del ConfirmationService._pending_confirmations[user_id]
            return True
        return False
    
    @staticmethod
    def _clean_expired():
        """Remove expired confirmations"""
        now = datetime.now()
        expired_users = [
            user_id for user_id, conf in ConfirmationService._pending_confirmations.items()
            if now > conf['expires_at']
        ]
        for user_id in expired_users:
            del ConfirmationService._pending_confirmations[user_id]
