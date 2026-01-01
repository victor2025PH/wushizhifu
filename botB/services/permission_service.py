"""
Permission service for managing admin permissions
"""
import logging
from database.admin_repository import AdminRepository

logger = logging.getLogger(__name__)


class PermissionService:
    """Service for checking admin permissions"""
    
    # Permission constants
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    
    # Permission flags
    PERM_USER_MANAGE = "user_manage"  # 用户管理
    PERM_ADMIN_MANAGE = "admin_manage"  # 管理员管理
    PERM_WORD_MANAGE = "word_manage"  # 敏感词管理
    PERM_GROUP_MANAGE = "group_manage"  # 群组管理
    PERM_STATS_VIEW = "stats_view"  # 统计查看
    PERM_EXPORT = "export"  # 数据导出
    PERM_LOG_VIEW = "log_view"  # 日志查看
    
    # Default permissions for regular admin
    DEFAULT_ADMIN_PERMISSIONS = [
        PERM_USER_MANAGE,
        PERM_WORD_MANAGE,
        PERM_GROUP_MANAGE,
        PERM_STATS_VIEW,
        PERM_EXPORT,
        PERM_LOG_VIEW,
    ]
    
    # Super admin has all permissions
    SUPER_ADMIN_PERMISSIONS = [
        PERM_USER_MANAGE,
        PERM_ADMIN_MANAGE,
        PERM_WORD_MANAGE,
        PERM_GROUP_MANAGE,
        PERM_STATS_VIEW,
        PERM_EXPORT,
        PERM_LOG_VIEW,
    ]
    
    @staticmethod
    def is_super_admin(user_id: int) -> bool:
        """
        Check if user is super admin.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is super admin
        """
        admin_info = AdminRepository.get_admin(user_id)
        if not admin_info:
            return False
        return admin_info.get('role') == PermissionService.SUPER_ADMIN
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """
        Check if user is admin (super admin or regular admin).
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is admin
        """
        return AdminRepository.is_admin(user_id)
    
    @staticmethod
    def get_permissions(user_id: int) -> list:
        """
        Get user permissions.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of permission strings
        """
        if not PermissionService.is_admin(user_id):
            return []
        
        admin_info = AdminRepository.get_admin(user_id)
        if not admin_info:
            return []
        
        role = admin_info.get('role', PermissionService.ADMIN)
        
        # Super admin has all permissions
        if role == PermissionService.SUPER_ADMIN:
            return PermissionService.SUPER_ADMIN_PERMISSIONS.copy()
        
        # Regular admin has default permissions
        # Check if custom permissions are stored
        permissions_str = admin_info.get('permissions')
        if permissions_str:
            try:
                import json
                return json.loads(permissions_str)
            except:
                pass
        
        return PermissionService.DEFAULT_ADMIN_PERMISSIONS.copy()
    
    @staticmethod
    def has_permission(user_id: int, permission: str) -> bool:
        """
        Check if user has specific permission.
        
        Args:
            user_id: Telegram user ID
            permission: Permission string to check
            
        Returns:
            True if user has permission
        """
        permissions = PermissionService.get_permissions(user_id)
        return permission in permissions
    
    @staticmethod
    def can_manage_admins(user_id: int) -> bool:
        """Check if user can manage admins (only super admin)"""
        return PermissionService.has_permission(user_id, PermissionService.PERM_ADMIN_MANAGE)
    
    @staticmethod
    def can_manage_users(user_id: int) -> bool:
        """Check if user can manage users"""
        return PermissionService.has_permission(user_id, PermissionService.PERM_USER_MANAGE)
    
    @staticmethod
    def can_manage_words(user_id: int) -> bool:
        """Check if user can manage sensitive words"""
        return PermissionService.has_permission(user_id, PermissionService.PERM_WORD_MANAGE)
    
    @staticmethod
    def can_manage_groups(user_id: int) -> bool:
        """Check if user can manage groups"""
        return PermissionService.has_permission(user_id, PermissionService.PERM_GROUP_MANAGE)
    
    @staticmethod
    def can_view_stats(user_id: int) -> bool:
        """Check if user can view statistics"""
        return PermissionService.has_permission(user_id, PermissionService.PERM_STATS_VIEW)
    
    @staticmethod
    def can_export(user_id: int) -> bool:
        """Check if user can export data"""
        return PermissionService.has_permission(user_id, PermissionService.PERM_EXPORT)
    
    @staticmethod
    def can_view_logs(user_id: int) -> bool:
        """Check if user can view operation logs"""
        return PermissionService.has_permission(user_id, PermissionService.PERM_LOG_VIEW)
