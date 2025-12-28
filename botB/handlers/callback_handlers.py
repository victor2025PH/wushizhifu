"""
Callback handlers for Bot B
Handles inline keyboard button callbacks
"""
import logging
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

logger = logging.getLogger(__name__)


async def handle_confirm_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation button click on settlement bill"""
    query = update.callback_query
    
    # Acknowledge the callback
    await query.answer("✅ 已确认")
    
    try:
        # Get current message text
        current_text = query.message.text
        
        # Check if already confirmed
        if "(已确认)" in current_text:
            return
        
        # Append confirmation text
        new_text = current_text + "\n\n✅ <b>(已确认)</b>"
        
        # Edit the message
        await query.edit_message_text(
            text=new_text,
            parse_mode="HTML"
        )
        
        logger.info(f"User {query.from_user.id} confirmed settlement bill")
        
    except Exception as e:
        logger.error(f"Error in handle_confirm_bill: {e}", exc_info=True)
        await query.answer("❌ 操作失败，请重试", show_alert=True)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main callback handler - routes callback queries to appropriate handlers
    """
    query = update.callback_query
    
    if not query or not query.data:
        return
    
    # Handle bill confirmation
    if query.data.startswith("confirm_bill"):
        await handle_confirm_bill(update, context)
        return


def get_callback_handler():
    """Get callback handler instance"""
    return CallbackQueryHandler(callback_handler)

