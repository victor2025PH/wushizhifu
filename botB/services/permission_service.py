"""
Permission service for managing admin permissions
"""
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import AdminRepository from database package
# Handle case where database is in parent directory
AdminRepository = None
try:
    from database.admin_repository import AdminRepository
except ImportError:
    # Try adding parent directory to path
    try:
        parent_dir = Path(__file__).parent.parent.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
        from database.admin_repository import AdminRepository
    except ImportError:
        logger.warning("Could not import AdminRepository from database.admin_repository. Admin management features may be limited.")
        # Create a fallback class
        class AdminRepository:
            @staticmethod
            def is_admin(user_id: int) -> bool:
                return False
            
            @staticmethod
            def get_admin(user_id: int):
                return None
            
            @staticmethod
            def add_admin(user_id: int, role: str = "admin", added_by: int = None):
                pass


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
        
        Initial admins from Config.INITIAL_ADMINS are considered super admins.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is super admin or in INITIAL_ADMINS
        """
        # Check if user is in INITIAL_ADMINS (these are super admins)
        try:
            from config import Config
            if user_id in Config.INITIAL_ADMINS:
                return True
        except Exception as e:
            logger.debug(f"Could not check INITIAL_ADMINS: {e}")
        
        # Check database for super_admin role
        if AdminRepository:
            try:
                admin_info = AdminRepository.get_admin(user_id)
                if admin_info:
                    return admin_info.get('role') == PermissionService.SUPER_ADMIN
            except Exception as e:
                logger.debug(f"Could not check admin role from database: {e}")
        
        return False
    
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
        """
        Check if user can manage admins (super admin or initial admin)
        
        Initial admins from Config.INITIAL_ADMINS should be able to manage admins
        even if they haven't been explicitly set as super_admin in the database.
        """
        # Check if user is in INITIAL_ADMINS (these should have full permissions)
        try:
            from config import Config
            if user_id in Config.INITIAL_ADMINS:
                return True
        except Exception as e:
            logger.debug(f"Could not check INITIAL_ADMINS: {e}")
        
        # Check if user has admin_manage permission (super admin)
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
