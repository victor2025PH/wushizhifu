"""
Middleware for group operations
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from database.group_repository import GroupRepository
import logging

logger = logging.getLogger(__name__)


class GroupMiddleware(BaseMiddleware):
    """Middleware to handle group registration"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process event and register group if needed.
        
        Args:
            handler: Event handler
            event: Telegram event object
            data: Event data dictionary
            
        Returns:
            Handler result
        """
        # Register group if message is from group
        if isinstance(event, Message) and event.chat.type in ["group", "supergroup"]:
            try:
                group_id = event.chat.id
                group_title = event.chat.title
                
                # Register or update group
                GroupRepository.create_or_update_group(
                    group_id=group_id,
                    group_title=group_title
                )
            except Exception as e:
                logger.error(f"Error registering group: {e}")
        
        # Continue processing
        return await handler(event, data)

