"""
Middleware for tracking user activity
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from services.user_service import UserService
from database.user_repository import UserRepository


class UserTrackingMiddleware(BaseMiddleware):
    """Middleware to track user activity and update user data"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process event and track user information.
        
        Args:
            handler: Event handler
            event: Telegram event object
            data: Event data dictionary
            
        Returns:
            Handler result
        """
        # Extract user from event
        user = None
        
        if hasattr(event, "from_user") and event.from_user:
            user = event.from_user
        elif hasattr(event, "message") and event.message and event.message.from_user:
            user = event.message.from_user
        elif hasattr(event, "callback_query") and event.callback_query and event.callback_query.from_user:
            user = event.callback_query.from_user
        
        # Register or update user data in database
        if user:
            UserService.register_user(user)
        
        # Continue processing
        return await handler(event, data)

