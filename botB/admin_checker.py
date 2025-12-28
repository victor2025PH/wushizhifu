"""
Admin checker for Bot B
Checks admin status from both Bot A's database and Config.INITIAL_ADMINS

This allows Bot B to recognize admins added via Bot A's /addadmin command
without requiring a restart. Bot B will check Bot A's database first,
then fall back to Config.INITIAL_ADMINS.
"""
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Cache for sys.path modification to avoid repeated operations
_root_dir = None


def is_admin(user_id: int) -> bool:
    """
    Check if user is admin.
    First checks Bot A's database, then falls back to Config.INITIAL_ADMINS.
    
    This allows Bot A's /addadmin command to automatically grant admin access in Bot B.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is admin
    """
    global _root_dir
    
    # First, check Bot A's database (shared admins)
    # This allows Bot A's /addadmin command to automatically grant admin access in Bot B
    try:
        # Import Bot A's database module
        # Add parent directory to path to access database module
        if _root_dir is None:
            _root_dir = Path(__file__).parent.parent
        
        # Add to path if not already there
        root_str = str(_root_dir)
        path_added = False
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
            path_added = True
        
        try:
            from database.admin_repository import AdminRepository
            if AdminRepository.is_admin(user_id):
                logger.info(f"User {user_id} is admin (from Bot A database)")
                return True
        except ImportError as e:
            logger.debug(f"Could not import Bot A's admin repository: {e}")
        except Exception as e:
            logger.warning(f"Error checking Bot A database for admin {user_id}: {e}")
        finally:
            # Clean up path only if we added it
            if path_added and root_str in sys.path:
                sys.path.remove(root_str)
    except Exception as e:
        logger.debug(f"Error accessing Bot A database: {e}")
    
    # Fallback to Config.INITIAL_ADMINS
    from config import Config
    if user_id in Config.INITIAL_ADMINS:
        logger.debug(f"User {user_id} is admin (from Config.INITIAL_ADMINS)")
        return True
    
    return False

