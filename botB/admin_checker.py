"""
Admin checker for Bot B
Checks admin status from multiple sources:
1. Bot A's database (shared admins) - if available
2. Bot B's own database (admins table) - primary source for dynamically added admins
3. Config.INITIAL_ADMINS - fallback for initial admins

This allows:
- Bot A's /addadmin command to automatically grant admin access in Bot B
- Bot B's UI to add admins that are immediately recognized
- Initial admins from config to work without database
"""
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Cache for sys.path modification to avoid repeated operations
_root_dir = None

# Cache for Bot B database instance to avoid repeated initialization
_bot_b_db = None


def _get_bot_b_database():
    """Get or create Bot B database instance"""
    global _bot_b_db
    if _bot_b_db is None:
        try:
            from database import db
            _bot_b_db = db
        except Exception as e:
            logger.debug(f"Could not initialize Bot B database: {e}")
            return None
    return _bot_b_db


def is_admin(user_id: int) -> bool:
    """
    Check if user is admin.
    Checks in this order:
    1. Bot A's database (shared admins) - if available
    2. Bot B's own database (admins table) - for dynamically added admins
    3. Config.INITIAL_ADMINS - fallback for initial admins
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is admin
    """
    global _root_dir
    
    # Step 1: Check Bot A's database (shared admins)
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
            is_admin_from_db = AdminRepository.is_admin(user_id)
            if is_admin_from_db:
                logger.info(f"✅ User {user_id} is admin (from Bot A database)")
                return True
            else:
                logger.debug(f"User {user_id} is not admin in Bot A database")
        except ImportError as e:
            logger.debug(f"Could not import Bot A's admin repository: {e}")
        except Exception as e:
            logger.warning(f"Error checking Bot A database for admin {user_id}: {e}", exc_info=True)
        finally:
            # Clean up path only if we added it
            if path_added and root_str in sys.path:
                sys.path.remove(root_str)
    except Exception as e:
        logger.debug(f"Error accessing Bot A database: {e}", exc_info=True)
    
    # Step 2: Check Bot B's own database (admins table)
    # This is the primary source for admins added via Bot B's UI
    try:
        db = _get_bot_b_database()
        if db:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM admins WHERE user_id = ? AND status = 'active'",
                (user_id,)
            )
            count = cursor.fetchone()[0]
            cursor.close()
            
            if count > 0:
                logger.info(f"✅ User {user_id} is admin (from Bot B database)")
                return True
            else:
                logger.debug(f"User {user_id} is not admin in Bot B database")
        else:
            logger.debug("Bot B database not available for admin check")
    except Exception as e:
        logger.warning(f"Error checking Bot B database for admin {user_id}: {e}", exc_info=True)
    
    # Step 3: Fallback to Config.INITIAL_ADMINS
    from config import Config
    current_admins = Config.INITIAL_ADMINS
    if user_id in current_admins:
        logger.info(f"✅ User {user_id} is admin (from Config.INITIAL_ADMINS)")
        return True
    else:
        logger.debug(
            f"User {user_id} is not in Config.INITIAL_ADMINS. "
            f"Current admins: {current_admins}."
        )
    
    logger.warning(f"❌ User {user_id} is not recognized as admin")
    return False

