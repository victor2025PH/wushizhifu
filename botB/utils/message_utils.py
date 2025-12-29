"""
Message utilities for Bot B
Provides helper functions to ensure reply keyboard is always shown in groups
"""
import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def send_with_reply_keyboard(update: Update, text: str, 
                                   parse_mode: Optional[str] = None, 
                                   inline_keyboard=None,
                                   edit_message: bool = False):
    """
    Send a message ensuring reply keyboard is shown in group chats.
    
    This function should be used by all handlers to ensure consistency
    and prevent keyboard conflicts with other bots.
    
    Args:
        update: Telegram Update object
        text: Message text
        parse_mode: Parse mode (HTML, Markdown, etc.)
        inline_keyboard: Optional inline keyboard (InlineKeyboardMarkup)
        edit_message: If True and update has callback_query, edit the message instead of sending new one
    
    Returns:
        The sent or edited message object
    """
    chat = update.effective_chat
    user = update.effective_user
    
    # Determine if this is a group
    is_group = chat.type in ['group', 'supergroup']
    
    # Get reply keyboard if in group
    reply_keyboard = None
    if is_group:
        from keyboards.reply_keyboard import get_main_reply_keyboard
        user_info = {
            'id': user.id,
            'first_name': user.first_name or '',
            'username': user.username,
            'language_code': user.language_code
        }
        reply_keyboard = get_main_reply_keyboard(user.id, is_group=True, user_info=user_info)
    
    # Determine message target
    if update.callback_query and edit_message:
        # Edit existing message (for callback queries)
        message = await update.callback_query.edit_message_text(
            text,
            parse_mode=parse_mode,
            reply_markup=inline_keyboard
        )
        # If in group and we have reply keyboard, also send a message to ensure keyboard is shown
        # Note: Telegram removes reply keyboard after edit_message_text in groups
        if is_group and reply_keyboard:
            try:
                # Send a visible message with reply keyboard to ensure it's shown
                # Using a small visible text instead of zero-width space for better reliability
                await update.callback_query.message.reply_text(
                    "💡",  # Small emoji to show keyboard reliably
                    reply_markup=reply_keyboard
                )
            except Exception as e:
                logger.warning(f"Failed to send reply keyboard after edit: {e}")
        return message
    elif update.callback_query:
        # Send new message from callback query context
        message_target = update.callback_query.message
    elif update.message:
        message_target = update.message
    else:
        logger.error("No message target found in update")
        return None
    
    # Send message
    if is_group and reply_keyboard:
        # In groups, always include reply keyboard
        if inline_keyboard:
            # Send message with inline keyboard first
            message = await message_target.reply_text(
                text,
                parse_mode=parse_mode,
                reply_markup=inline_keyboard
            )
            # Then send minimal message with reply keyboard to ensure it's shown
            # Note: Using visible emoji for better reliability than zero-width space
            try:
                await message_target.reply_text("💡", reply_markup=reply_keyboard)
            except Exception as e:
                logger.warning(f"Failed to send reply keyboard: {e}")
            return message
        else:
            # Just use reply keyboard
            return await message_target.reply_text(
                text,
                parse_mode=parse_mode,
                reply_markup=reply_keyboard
            )
    else:
        # Not a group, just send normally
        return await message_target.reply_text(
            text,
            parse_mode=parse_mode,
            reply_markup=inline_keyboard
        )

