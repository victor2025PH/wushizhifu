"""
Group Admin Checker for Bot B
Checks if a user is an administrator in a Telegram group
"""
import logging
from telegram import Bot, ChatMemberAdministrator, ChatMemberOwner
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


async def is_group_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    """
    Check if a user is an administrator or owner in a group.
    
    Args:
        bot: Telegram Bot instance
        chat_id: Telegram chat/group ID
        user_id: Telegram user ID to check
        
    Returns:
        True if user is admin or owner, False otherwise
    """
    try:
        chat_member = await bot.get_chat_member(chat_id, user_id)
        
        # Check if user is owner or administrator
        if isinstance(chat_member, (ChatMemberOwner, ChatMemberAdministrator)):
            return True
        
        return False
        
    except TelegramError as e:
        logger.warning(f"Error checking group admin status for user {user_id} in chat {chat_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking group admin status: {e}", exc_info=True)
        return False

