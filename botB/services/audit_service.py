"""
Audit service for Bot B
Handles operation logging for audit trail
"""
import logging
from typing import Optional
from telegram import Update

logger = logging.getLogger(__name__)


def log_admin_operation(operation_type: str, update: Update, target_type: str = None,
                       target_id: str = None, description: str = None,
                       old_value: str = None, new_value: str = None):
    """
    Log an admin operation.
    
    Args:
        operation_type: Type of operation (e.g., 'set_markup', 'set_address')
        update: Telegram update object
        target_type: Type of target (e.g., 'group', 'global')
        target_id: ID of target (e.g., group_id)
        description: Operation description
        old_value: Old value (for updates)
        new_value: New value (for updates)
    """
    try:
        from database import db
        
        user = update.effective_user
        
        # Get IP address if available (Telegram Bot API doesn't provide this directly)
        # For now, we'll use None
        ip_address = None
        
        db.log_operation(
            operation_type=operation_type,
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            target_type=target_type,
            target_id=str(target_id) if target_id else None,
            description=description,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            ip_address=ip_address
        )
        
        logger.info(f"Logged operation: {operation_type} by user {user.id} ({user.username or user.first_name})")
        
    except Exception as e:
        logger.error(f"Error logging admin operation: {e}", exc_info=True)


def log_transaction_operation(operation_type: str, update: Update, transaction_id: str,
                             description: str = None, old_status: str = None,
                             new_status: str = None):
    """
    Log a transaction operation.
    
    Args:
        operation_type: Type of operation (e.g., 'mark_paid', 'confirm_transaction', 'cancel_transaction')
        update: Telegram update object
        transaction_id: Transaction ID
        description: Operation description
        old_status: Old transaction status
        new_status: New transaction status
    """
    try:
        from database import db
        
        user = update.effective_user
        
        db.log_operation(
            operation_type=operation_type,
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            target_type='transaction',
            target_id=transaction_id,
            description=description,
            old_value=old_status,
            new_value=new_status,
            ip_address=None
        )
        
        logger.info(f"Logged transaction operation: {operation_type} for transaction {transaction_id} by user {user.id}")
        
    except Exception as e:
        logger.error(f"Error logging transaction operation: {e}", exc_info=True)


# Operation type constants
class OperationType:
    # Admin operations
    SET_GROUP_MARKUP = 'set_group_markup'
    SET_GROUP_ADDRESS = 'set_group_address'
    RESET_GROUP_SETTINGS = 'reset_group_settings'
    DELETE_GROUP_SETTINGS = 'delete_group_settings'
    SET_GLOBAL_MARKUP = 'set_global_markup'
    SET_GLOBAL_ADDRESS = 'set_global_address'
    
    # Transaction operations
    MARK_PAID = 'mark_paid'
    CONFIRM_TRANSACTION = 'confirm_transaction'
    CANCEL_TRANSACTION = 'cancel_transaction'
    BATCH_CONFIRM = 'batch_confirm_transactions'
    
    # Export operations
    EXPORT_TRANSACTIONS = 'export_transactions'
    EXPORT_STATS = 'export_stats'

