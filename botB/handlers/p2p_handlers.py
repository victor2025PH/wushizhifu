"""
P2P Leaderboard handlers for Bot B
Handles P2P merchant leaderboard commands and callbacks
"""
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.p2p_leaderboard_service import get_p2p_leaderboard, format_p2p_leaderboard_html

logger = logging.getLogger(__name__)


def get_p2p_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for switching payment methods.
    
    Returns:
        InlineKeyboardMarkup with payment method buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("💳 银行卡", callback_data="p2p_bank"),
            InlineKeyboardButton("🔵 支付宝", callback_data="p2p_ali"),
            InlineKeyboardButton("🟢 微信", callback_data="p2p_wx")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def handle_p2p_price_command(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_method: str = "alipay"):
    """
    Handle /price command with P2P leaderboard.
    
    Args:
        update: Telegram update object
        context: Context object
        payment_method: Default payment method (bank, alipay, wechat)
    """
    try:
        # Send loading message
        loading_msg = await update.message.reply_text("⏳ 正在获取实时币价行情...")
        
        # Fetch leaderboard data
        leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=10)
        
        if not leaderboard_data:
            await loading_msg.edit_text("❌ 获取币价行情失败，请稍后重试。")
            return
        
        # Format message
        message = format_p2p_leaderboard_html(leaderboard_data)
        
        # Get keyboard
        reply_markup = get_p2p_keyboard()
        
        # Update message
        await loading_msg.edit_text(
            message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        logger.info(f"Sent P2P leaderboard ({payment_method}) to {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_p2p_price_command: {e}", exc_info=True)
        try:
            await loading_msg.edit_text(f"❌ 获取币价行情时出错: {str(e)}")
        except:
            await update.message.reply_text(f"❌ 获取币价行情时出错: {str(e)}")


async def handle_p2p_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
    """
    Handle P2P payment method switch callbacks.
    
    Args:
        update: Telegram update object
        context: Context object
        callback_data: Callback data (p2p_bank, p2p_ali, p2p_wx)
    """
    try:
        query = update.callback_query
        await query.answer("正在切换渠道...")
        
        # Map callback data to payment method
        payment_method_map = {
            "p2p_bank": "bank",
            "p2p_ali": "alipay",
            "p2p_wx": "wechat"
        }
        
        payment_method = payment_method_map.get(callback_data, "alipay")
        
        # Fetch new leaderboard data
        leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=10)
        
        if not leaderboard_data:
            await query.message.edit_text("❌ 获取币价行情失败，请稍后重试。")
            return
        
        # Format message
        message = format_p2p_leaderboard_html(leaderboard_data)
        
        # Get keyboard
        reply_markup = get_p2p_keyboard()
        
        # Update message
        await query.message.edit_text(
            message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        logger.info(f"Updated P2P leaderboard ({payment_method}) for {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_p2p_callback: {e}", exc_info=True)
        try:
            await query.answer("❌ 切换失败，请重试", show_alert=True)
        except:
            pass

