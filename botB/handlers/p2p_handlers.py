"""
P2P Leaderboard handlers for Bot B
Handles P2P merchant leaderboard commands and callbacks
"""
import logging
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.p2p_leaderboard_service import get_p2p_leaderboard, format_p2p_leaderboard_html

logger = logging.getLogger(__name__)

# No caching - always fetch real-time data when requested
# Removed cache to ensure real-time data on every click


def _get_merchants_list(payment_method: str = "alipay") -> list:
    """
    Get 10 merchants - always fetch real-time data from OKX (no cache, no pagination).
    
    Args:
        payment_method: Payment method code (always uses Alipay)
        
    Returns:
        List of 10 merchants
    """
    # Always fetch fresh data from OKX - no cache
    # Fetch exactly 10 merchants (no pagination)
    logger.info(f"Fetching real-time OKX C2C data for payment method: {payment_method} (10 merchants)")
    
    # Fetch 10 merchants from OKX
    leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=10, page=1)
    
    if not leaderboard_data or not leaderboard_data.get('merchants'):
        logger.warning("No merchants data from OKX C2C API")
        return []
    
    # Return first 10 merchants
    merchants = leaderboard_data.get('merchants', [])[:10]
    return merchants




def get_p2p_leaderboard_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for P2P leaderboard (no buttons - display only).
    
    Returns:
        Empty InlineKeyboardMarkup (no buttons)
    """
    # No buttons - just display the data
    return InlineKeyboardMarkup([])


async def handle_p2p_price_command(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_method: str = "alipay", page: int = 1):
    """
    Handle /price command with P2P leaderboard - shows 10 merchants (Alipay only, no pagination).
    
    Args:
        update: Telegram update object
        context: Context object
        payment_method: Payment method (always uses Alipay)
        page: Not used (kept for compatibility)
    """
    try:
        # Send loading message
        loading_msg = await update.message.reply_text("⏳ 正在获取实时币价行情...")
        
        # Get 10 merchants (real-time, no cache, no pagination)
        merchants = _get_merchants_list(payment_method)
        
        if not merchants:
            await loading_msg.edit_text("❌ 获取币价行情失败，请稍后重试。")
            return
        
        # Create leaderboard_data structure for formatting
        from datetime import datetime
        from services.p2p_leaderboard_service import PAYMENT_METHOD_LABELS
        
        payment_label = PAYMENT_METHOD_LABELS.get(payment_method.lower(), "支付宝")
        
        # Calculate market stats from the 10 merchants
        if merchants:
            prices = [m['price'] for m in merchants]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            total_trades = sum(m['trade_count'] for m in merchants)
        else:
            min_price = max_price = avg_price = 0
            total_trades = 0
        
        leaderboard_data = {
            'merchants': merchants,  # 10 merchants
            'payment_method': payment_method,
            'payment_label': payment_label,
            'total': len(merchants),
            'timestamp': datetime.now(),  # Always use current time for real-time display
            'market_stats': {
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': avg_price,
                'total_trades': total_trades,
                'merchant_count': len(merchants)
            }
        }
        
        # Format message (no pagination)
        message = format_p2p_leaderboard_html(leaderboard_data, page=1, per_page=10, total_pages=1)
        
        # Get keyboard (no buttons)
        reply_markup = get_p2p_leaderboard_keyboard()
        
        # Update message
        await loading_msg.edit_text(
            message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        # Also send reply keyboard if in group (after edit, keyboard may not show)
        chat = update.effective_chat
        if chat.type in ['group', 'supergroup']:
            from utils.message_utils import send_with_reply_keyboard
            try:
                await send_with_reply_keyboard(update, "💡")  # Visible emoji to show keyboard reliably
            except Exception as e:
                logger.warning(f"Failed to send reply keyboard after P2P leaderboard: {e}")
        
        logger.info(f"Sent P2P leaderboard ({payment_method}, {len(merchants)} merchants) to {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_p2p_price_command: {e}", exc_info=True)
        from utils.message_utils import send_with_reply_keyboard
        try:
            await loading_msg.edit_text(f"❌ 获取币价行情时出错: {str(e)}")
            # Also send reply keyboard if in group
            chat = update.effective_chat
            if chat.type in ['group', 'supergroup']:
                await send_with_reply_keyboard(update, "​")
        except:
            await send_with_reply_keyboard(update, f"❌ 获取币价行情时出错: {str(e)}")


async def handle_p2p_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
    """
    Handle P2P callbacks - refresh data (no pagination, no payment method switching).
    
    Args:
        update: Telegram update object
        context: Context object
        callback_data: Callback data (ignored, always uses Alipay)
    """
    try:
        query = update.callback_query
        await query.answer("⏳ 正在刷新...")
        
        # Always use Alipay, no pagination
        payment_method = "alipay"
        
        # Get 10 merchants (real-time, no cache)
        merchants = _get_merchants_list(payment_method)
        
        if not merchants:
            await query.message.edit_text("❌ 获取币价行情失败，请稍后重试。")
            return
        
        # Create leaderboard_data structure for formatting
        from datetime import datetime
        from services.p2p_leaderboard_service import PAYMENT_METHOD_LABELS
        
        payment_label = PAYMENT_METHOD_LABELS.get(payment_method.lower(), "支付宝")
        
        # Calculate market stats from the 10 merchants
        if merchants:
            prices = [m['price'] for m in merchants]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            total_trades = sum(m['trade_count'] for m in merchants)
        else:
            min_price = max_price = avg_price = 0
            total_trades = 0
        
        leaderboard_data = {
            'merchants': merchants,  # 10 merchants
            'payment_method': payment_method,
            'payment_label': payment_label,
            'total': len(merchants),
            'timestamp': datetime.now(),  # Always use current time for real-time display
            'market_stats': {
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': avg_price,
                'total_trades': total_trades,
                'merchant_count': len(merchants)
            }
        }
        
        # Format message (no pagination)
        message = format_p2p_leaderboard_html(leaderboard_data, page=1, per_page=10, total_pages=1)
        
        # Get keyboard (no buttons)
        reply_markup = get_p2p_leaderboard_keyboard()
        
        # Update message
        await query.message.edit_text(
            message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        # Also send reply keyboard if in group (after edit, keyboard may not show)
        chat = update.effective_chat
        if chat.type in ['group', 'supergroup']:
            from utils.message_utils import send_with_reply_keyboard
            try:
                await send_with_reply_keyboard(update, "💡")  # Visible emoji to show keyboard reliably
            except Exception as e:
                logger.warning(f"Failed to send reply keyboard after P2P callback: {e}")
        
        logger.info(f"Updated P2P leaderboard ({payment_method}, {len(merchants)} merchants) for {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_p2p_callback: {e}", exc_info=True)
        try:
            await query.answer("❌ 操作失败，请重试", show_alert=True)
        except:
            pass

