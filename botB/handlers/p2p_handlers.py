"""
P2P Leaderboard handlers for Bot B
Handles P2P merchant leaderboard commands and callbacks
"""
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.p2p_leaderboard_service import get_p2p_leaderboard, format_p2p_leaderboard_html

logger = logging.getLogger(__name__)




def get_p2p_leaderboard_keyboard(payment_method: str, current_page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for P2P leaderboard with pagination.
    
    Args:
        payment_method: Current payment method
        current_page: Current page number
        total_pages: Total number of pages
        
    Returns:
        InlineKeyboardMarkup with payment method and pagination buttons
    """
    keyboard = []
    
    # Payment method buttons
    keyboard.append([
        InlineKeyboardButton("💳 银行卡", callback_data=f"p2p_bank_1"),
        InlineKeyboardButton("🔵 支付宝", callback_data=f"p2p_ali_1"),
        InlineKeyboardButton("🟢 微信", callback_data=f"p2p_wx_1")
    ])
    
    # Pagination buttons (only show if more than one page)
    if total_pages > 1:
        pagination_row = []
        if current_page > 1:
            pagination_row.append(InlineKeyboardButton("◀️ 上一页", callback_data=f"p2p_{payment_method}_{current_page - 1}"))
        if current_page < total_pages:
            pagination_row.append(InlineKeyboardButton("下一页 ▶️", callback_data=f"p2p_{payment_method}_{current_page + 1}"))
        if pagination_row:
            keyboard.append(pagination_row)
    
    return InlineKeyboardMarkup(keyboard)


async def handle_p2p_price_command(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_method: str = "alipay", page: int = 1):
    """
    Handle /price command with P2P leaderboard.
    
    Args:
        update: Telegram update object
        context: Context object
        payment_method: Default payment method (bank, alipay, wechat)
        page: Page number (default: 1)
    """
    try:
        per_page = 8  # Show 8 merchants per page
        
        # Send loading message
        loading_msg = await update.message.reply_text("⏳ 正在获取实时币价行情...")
        
        # Fetch leaderboard data (fetch more for pagination)
        leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=40, page=1)
        
        if not leaderboard_data:
            await loading_msg.edit_text("❌ 获取币价行情失败，请稍后重试。")
            return
        
        # Calculate pagination
        total_merchants = len(leaderboard_data['merchants'])
        total_pages = (total_merchants + per_page - 1) // per_page
        current_page = min(page, total_pages) if total_pages > 0 else 1
        
        # Format message with pagination
        message = format_p2p_leaderboard_html(leaderboard_data, page=current_page, per_page=per_page, total_pages=total_pages)
        
        # Get keyboard with pagination
        reply_markup = get_p2p_leaderboard_keyboard(payment_method, current_page, total_pages)
        
        # Update message
        await loading_msg.edit_text(
            message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        logger.info(f"Sent P2P leaderboard ({payment_method}, page {current_page}/{total_pages}) to {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_p2p_price_command: {e}", exc_info=True)
        try:
            await loading_msg.edit_text(f"❌ 获取币价行情时出错: {str(e)}")
        except:
            await update.message.reply_text(f"❌ 获取币价行情时出错: {str(e)}")


async def handle_p2p_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
    """
    Handle P2P payment method switch and pagination callbacks.
    
    Args:
        update: Telegram update object
        context: Context object
        callback_data: Callback data (p2p_bank_1, p2p_ali_2, p2p_wx_1, etc.)
    """
    try:
        query = update.callback_query
        await query.answer("⏳ 正在加载...")
        
        # Parse callback data: p2p_{payment_method}_{page}
        parts = callback_data.split('_')
        if len(parts) >= 3:
            payment_method_code = parts[1]  # bank, ali, wx
            page = int(parts[2]) if parts[2].isdigit() else 1
        else:
            # Fallback for old format
            payment_method_map = {
                "p2p_bank": "bank",
                "p2p_ali": "alipay",
                "p2p_wx": "wechat"
            }
            payment_method_code = payment_method_map.get(callback_data, "alipay")
            page = 1
        
        # Map payment method code
        payment_method_map = {
            "bank": "bank",
            "ali": "alipay",
            "wx": "wechat"
        }
        payment_method = payment_method_map.get(payment_method_code, "alipay")
        
        per_page = 8
        
        # Fetch leaderboard data
        leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=40, page=1)
        
        if not leaderboard_data:
            await query.message.edit_text("❌ 获取币价行情失败，请稍后重试。")
            return
        
        # Calculate pagination
        total_merchants = len(leaderboard_data['merchants'])
        total_pages = (total_merchants + per_page - 1) // per_page
        current_page = min(page, total_pages) if total_pages > 0 else 1
        
        # Format message with pagination
        message = format_p2p_leaderboard_html(leaderboard_data, page=current_page, per_page=per_page, total_pages=total_pages)
        
        # Get keyboard with pagination
        reply_markup = get_p2p_leaderboard_keyboard(payment_method, current_page, total_pages)
        
        # Update message
        await query.message.edit_text(
            message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        logger.info(f"Updated P2P leaderboard ({payment_method}, page {current_page}/{total_pages}) for {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_p2p_callback: {e}", exc_info=True)
        try:
            await query.answer("❌ 操作失败，请重试", show_alert=True)
        except:
            pass

