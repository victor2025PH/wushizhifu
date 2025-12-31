"""
Customer Service Management Service (Shared)
Handles customer service account management and assignment logic
"""
import logging
import sys
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import database from botB (since it has the customer service tables)
# If that fails, try to import from a shared location
try:
    # Try botB database first (most likely to work)
    sys.path.insert(0, str(Path(__file__).parent.parent / "botB"))
    from database import db as botb_db
    _db = botb_db
    logger.info("Using botB database for customer service")
except ImportError:
    try:
        # Fallback: try to import from root database module
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from database.db import Database
        _db = Database()
        logger.info("Using root database for customer service")
    except ImportError:
        logger.error("Could not import database module for customer service")
        _db = None


class CustomerServiceService:
    """Service for managing customer service accounts and assignments"""
    
    @staticmethod
    def get_all_accounts(active_only: bool = True) -> List[Dict]:
        """Get all customer service accounts"""
        if not _db:
            logger.error("Database not available for customer service")
            return []
        return _db.get_customer_service_accounts(active_only=active_only)
    
    @staticmethod
    def get_account(account_id: int = None, username: str = None) -> Optional[Dict]:
        """Get customer service account by ID or username"""
        if not _db:
            return None
        return _db.get_customer_service_account(account_id=account_id, username=username)
    
    @staticmethod
    def add_account(username: str, display_name: str = None, 
                    weight: int = 5, max_concurrent: int = 50) -> bool:
        """Add a new customer service account"""
        if not _db:
            return False
        if not username or len(username.strip()) == 0:
            return False
        
        # Remove @ if present
        username = username.strip().lstrip('@')
        
        return _db.add_customer_service_account(
            username=username,
            display_name=display_name,
            weight=weight,
            max_concurrent=max_concurrent
        )
    
    @staticmethod
    def update_account(account_id: int, display_name: str = None,
                       weight: int = None, max_concurrent: int = None,
                       status: str = None) -> bool:
        """Update customer service account"""
        if not _db:
            return False
        return _db.update_customer_service_account(
            account_id=account_id,
            display_name=display_name,
            weight=weight,
            max_concurrent=max_concurrent,
            status=status
        )
    
    @staticmethod
    def toggle_account(account_id: int) -> bool:
        """Toggle customer service account active status"""
        if not _db:
            return False
        return _db.toggle_customer_service_account(account_id=account_id)
    
    @staticmethod
    def delete_account(account_id: int) -> bool:
        """Delete customer service account"""
        if not _db:
            return False
        return _db.delete_customer_service_account(account_id=account_id)
    
    @staticmethod
    def assign_service(user_id: int, username: str, method: str = 'smart') -> Optional[str]:
        """
        Assign a customer service account to a user.
        
        Args:
            user_id: User ID
            username: Username
            method: Assignment method (smart/round_robin/least_busy/weighted)
            
        Returns:
            Service account username or None
        """
        if not _db:
            logger.error("Database not available for customer service assignment")
            return None
        return _db.assign_customer_service(
            user_id=user_id,
            username=username,
            assignment_method=method
        )
    
    @staticmethod
    def get_stats() -> Dict:
        """Get customer service statistics"""
        if not _db:
            return {}
        return _db.get_customer_service_stats()
    
    @staticmethod
    def get_assignment_method_display_name(method: str) -> str:
        """Get display name for assignment method"""
        method_names = {
            'smart': '智能混合分配',
            'round_robin': '简单轮询',
            'least_busy': '最少任务优先',
            'weighted': '权重分配'
        }
        return method_names.get(method, method)
    
    @staticmethod
    def get_status_display(status: str) -> str:
        """Get display emoji and text for status"""
        status_map = {
            'available': '🟢 在线',
            'busy': '🟡 忙碌',
            'offline': '🔴 离线',
            'disabled': '⚫ 禁用'
        }
        return status_map.get(status, status)
    
    @staticmethod
    def get_assignment_strategy() -> str:
        """Get current assignment strategy from settings"""
        if not _db:
            return 'smart'
        try:
            all_settings = _db.get_all_settings()
            return all_settings.get('customer_service_strategy', 'smart')
        except Exception as e:
            logger.error(f"Error getting assignment strategy: {e}")
            return 'smart'


# Global service instance
customer_service = CustomerServiceService()
