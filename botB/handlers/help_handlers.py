"""
Context-aware help handlers for Bot B
Provides contextual help and guidance
"""
import logging
from typing import Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.help_service import get_contextual_help, get_button_help, get_error_help

logger = logging.getLogger(__name__)


async def show_contextual_help(update: Update, context_key: str):
    """
    Show contextual help for a specific context.
    
    Args:
        update: Telegram update object
        context_key: Context identifier
    """
    try:
        help_data = get_contextual_help(context_key)
        
        if not help_data:
            return
        
        message = f"{help_data['title']}\n\n{help_data['content']}"
        
        keyboard = [
            [
                InlineKeyboardButton("❌ 关闭", callback_data="help_close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        elif update.message:
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error showing contextual help: {e}", exc_info=True)


async def show_button_help(update: Update, button_text: str):
    """
    Show help for a button.
    
    Args:
        update: Telegram update object
        button_text: Button text
    """
    try:
        help_text = get_button_help(button_text)
        
        if not help_text:
            return
        
        message = f"💡 <b>功能说明</b>\n\n{help_text}"
        
        if update.callback_query:
            await update.callback_query.answer(help_text, show_alert=False)
        elif update.message:
            await update.message.reply_text(message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error showing button help: {e}", exc_info=True)


async def show_error_help(update: Update, error_type: str, error_message: str = None):
    """
    Show error help with suggestions.
    
    Args:
        update: Telegram update object
        error_type: Error type identifier
        error_message: Optional error message
    """
    try:
        help_data = get_error_help(error_type)
        
        message = help_data['title'] if help_data else "❌ 错误"
        
        if error_message:
            message += f"\n\n错误信息：{error_message}"
        
        if help_data:
            message += f"\n\n{help_data['content']}"
        
        keyboard = [
            [
                InlineKeyboardButton("❌ 关闭", callback_data="help_close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        elif update.message:
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error showing error help: {e}", exc_info=True)


async def handle_help_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help close button"""
    try:
        query = update.callback_query
        await query.message.delete()
        await query.answer()
    except Exception as e:
        logger.error(f"Error closing help: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误", show_alert=True)


async def handle_contextual_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, help_context: str):
    """
    Handle contextual help command.
    
    Args:
        update: Telegram update object
        context: Context object
        help_context: Help context identifier
    """
    await show_contextual_help(update, help_context)

