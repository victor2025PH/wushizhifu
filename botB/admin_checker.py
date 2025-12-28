"""
Admin checker for Bot B
Checks admin status from both Bot A's database and Config.INITIAL_ADMINS
"""
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """
    Check if user is admin.
    First checks Bot A's database, then falls back to Config.INITIAL_ADMINS.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is admin
    """
    # First, check Bot A's database (shared admins)
    try:
        # Import Bot A's database module
        # Add parent directory to path to access database module
        root_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(root_dir))
        
        try:
            from database.admin_repository import AdminRepository
            if AdminRepository.is_admin(user_id):
                logger.debug(f"User {user_id} is admin (from Bot A database)")
                return True
        except ImportError as e:
            logger.debug(f"Could not import Bot A's admin repository: {e}")
        except Exception as e:
            logger.warning(f"Error checking Bot A database for admin {user_id}: {e}")
    except Exception as e:
        logger.debug(f"Error accessing Bot A database: {e}")
    finally:
        # Clean up path
        if str(root_dir) in sys.path:
            sys.path.remove(str(root_dir))
    
    # Fallback to Config.INITIAL_ADMINS
    from config import Config
    if user_id in Config.INITIAL_ADMINS:
        logger.debug(f"User {user_id} is admin (from Config.INITIAL_ADMINS)")
        return True
    
    return False

