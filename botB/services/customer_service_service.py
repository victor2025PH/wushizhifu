"""
Customer Service Management Service
Handles customer service account management and assignment logic
"""
import logging
from typing import Optional, List, Dict
from database import db

logger = logging.getLogger(__name__)


class CustomerServiceService:
    """Service for managing customer service accounts and assignments"""
    
    @staticmethod
    def get_all_accounts(active_only: bool = True) -> List[Dict]:
        """Get all customer service accounts"""
        return db.get_customer_service_accounts(active_only=active_only)
    
    @staticmethod
    def get_account(account_id: int = None, username: str = None) -> Optional[Dict]:
        """Get customer service account by ID or username"""
        return db.get_customer_service_account(account_id=account_id, username=username)
    
    @staticmethod
    def add_account(username: str, display_name: str = None, 
                    weight: int = 5, max_concurrent: int = 50) -> bool:
        """Add a new customer service account"""
        if not username or len(username.strip()) == 0:
            return False
        
        # Remove @ if present
        username = username.strip().lstrip('@')
        
        return db.add_customer_service_account(
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
        return db.update_customer_service_account(
            account_id=account_id,
            display_name=display_name,
            weight=weight,
            max_concurrent=max_concurrent,
            status=status
        )
    
    @staticmethod
    def toggle_account(account_id: int) -> bool:
        """Toggle customer service account active status"""
        return db.toggle_customer_service_account(account_id=account_id)
    
    @staticmethod
    def delete_account(account_id: int) -> bool:
        """Delete customer service account"""
        return db.delete_customer_service_account(account_id=account_id)
    
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
        return db.assign_customer_service(
            user_id=user_id,
            username=username,
            assignment_method=method
        )
    
    @staticmethod
    def get_stats() -> Dict:
        """Get customer service statistics"""
        return db.get_customer_service_stats()
    
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


# Global service instance
customer_service = CustomerServiceService()

