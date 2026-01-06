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


def _get_all_merchants_with_pagination(payment_method: str, required_page: int, per_page: int = 5) -> tuple:
    """
    Get all merchants with pagination - always fetch real-time data from OKX (no cache).
    
    Args:
        payment_method: Payment method code (always uses Alipay)
        required_page: The page number the user wants to see
        per_page: Number of merchants per page
        
    Returns:
        Tuple of (merchants_for_page: List, total_pages: int)
    """
    # Always fetch fresh data from OKX - no cache
    # OKX API doesn't support pagination, so we fetch all and slice
    logger.info(f"Fetching real-time OKX C2C data for payment method: {payment_method} (page {required_page})")
    
    # Fetch all merchants (OKX returns all available merchants)
    leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=100, page=1)
    
    if not leaderboard_data or not leaderboard_data.get('merchants'):
        logger.warning("No merchants data from OKX C2C API")
        return [], 1
    
    # Get all available merchants (from market_stats)
    total_merchants = leaderboard_data.get('total', len(leaderboard_data.get('merchants', [])))
    
    # Fetch more pages if needed to get enough merchants for the required page
    all_merchants = []
    max_pages_to_fetch = (required_page * per_page + 9) // 10  # Calculate how many API calls we need
    
    for api_page in range(1, max_pages_to_fetch + 1):
        page_data = get_p2p_leaderboard(payment_method=payment_method, rows=10, page=api_page)
        if page_data and page_data.get('merchants'):
            all_merchants.extend(page_data['merchants'])
            # If we got less merchants than requested, we've reached the end
            if len(page_data['merchants']) < 10:
                break
        else:
            break
    
    # Calculate total pages based on all fetched merchants
    total_pages = (len(all_merchants) + per_page - 1) // per_page if all_merchants else 1
    
    # Get merchants for the required page
    start_idx = (required_page - 1) * per_page
    end_idx = start_idx + per_page
    page_merchants = all_merchants[start_idx:end_idx]
    
    return page_merchants, total_pages




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
        page: Display page number (default: 1)
    """
    try:
        per_page = 5  # Show 5 merchants per page
        
        # Send loading message
        loading_msg = await update.message.reply_text("⏳ 正在获取实时币价行情...")
        
        # Get all merchants with pagination (always fetch real-time data, no cache)
        all_merchants, total_pages = _get_all_merchants_with_pagination(payment_method, page, per_page)
        
        if not all_merchants:
            await loading_msg.edit_text("❌ 获取币价行情失败，请稍后重试。")
            return
        
        # Validate page number
        current_page = min(page, total_pages) if total_pages > 0 else 1
        
        # Create leaderboard_data structure for formatting
        from datetime import datetime
        from services.p2p_leaderboard_service import PAYMENT_METHOD_LABELS
        
        payment_label = PAYMENT_METHOD_LABELS.get(payment_method.lower(), "支付宝")
        
        # Fetch all merchants to calculate market stats (for display)
        # We need to fetch all merchants to get accurate market statistics
        all_merchants_for_stats = []
        for api_page in range(1, 6):  # Fetch first 5 pages (50 merchants) for stats
            stats_data = get_p2p_leaderboard(payment_method=payment_method, rows=10, page=api_page)
            if stats_data and stats_data.get('merchants'):
                all_merchants_for_stats.extend(stats_data['merchants'])
                if len(stats_data['merchants']) < 10:
                    break
            else:
                break
        
        # Calculate market stats from all fetched merchants
        if all_merchants_for_stats:
            prices = [m['price'] for m in all_merchants_for_stats]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            total_trades = sum(m['trade_count'] for m in all_merchants_for_stats)
        else:
            # Fallback to current page merchants
            if all_merchants:
                prices = [m['price'] for m in all_merchants]
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                total_trades = sum(m['trade_count'] for m in all_merchants)
            else:
                min_price = max_price = avg_price = 0
                total_trades = 0
        
        leaderboard_data = {
            'merchants': all_merchants,  # Merchants for current page
            'payment_method': payment_method,
            'payment_label': payment_label,
            'total': len(all_merchants_for_stats) if all_merchants_for_stats else len(all_merchants),
            'timestamp': datetime.now(),  # Always use current time for real-time display
            'market_stats': {
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': avg_price,
                'total_trades': total_trades,
                'merchant_count': len(all_merchants_for_stats) if all_merchants_for_stats else len(all_merchants)
            }
        }
        
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
        
        # Also send reply keyboard if in group (after edit, keyboard may not show)
        chat = update.effective_chat
        if chat.type in ['group', 'supergroup']:
            from utils.message_utils import send_with_reply_keyboard
            try:
                await send_with_reply_keyboard(update, "💡")  # Visible emoji to show keyboard reliably
            except Exception as e:
                logger.warning(f"Failed to send reply keyboard after P2P leaderboard: {e}")
        
        logger.info(f"Sent P2P leaderboard ({payment_method}, page {current_page}/{total_pages}, {len(all_merchants)} total merchants) to {update.effective_user.id}")
        
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
        
        per_page = 5  # Show 5 merchants per page
        
        # Get all merchants with pagination (always fetch real-time data, no cache)
        all_merchants, total_pages = _get_all_merchants_with_pagination(payment_method, page, per_page)
        
        if not all_merchants:
            await query.message.edit_text("❌ 获取币价行情失败，请稍后重试。")
            return
        
        # Validate page number
        current_page = min(page, total_pages) if total_pages > 0 else 1
        
        # Create leaderboard_data structure for formatting
        from datetime import datetime
        from services.p2p_leaderboard_service import PAYMENT_METHOD_LABELS
        
        payment_label = PAYMENT_METHOD_LABELS.get(payment_method.lower(), "支付宝")
        
        # Fetch all merchants to calculate market stats (for display)
        # We need to fetch all merchants to get accurate market statistics
        all_merchants_for_stats = []
        for api_page in range(1, 6):  # Fetch first 5 pages (50 merchants) for stats
            stats_data = get_p2p_leaderboard(payment_method=payment_method, rows=10, page=api_page)
            if stats_data and stats_data.get('merchants'):
                all_merchants_for_stats.extend(stats_data['merchants'])
                if len(stats_data['merchants']) < 10:
                    break
            else:
                break
        
        # Calculate market stats from all fetched merchants
        if all_merchants_for_stats:
            prices = [m['price'] for m in all_merchants_for_stats]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            total_trades = sum(m['trade_count'] for m in all_merchants_for_stats)
        else:
            # Fallback to current page merchants
            if all_merchants:
                prices = [m['price'] for m in all_merchants]
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                total_trades = sum(m['trade_count'] for m in all_merchants)
            else:
                min_price = max_price = avg_price = 0
                total_trades = 0
        
        leaderboard_data = {
            'merchants': all_merchants,  # Merchants for current page
            'payment_method': payment_method,
            'payment_label': payment_label,
            'total': len(all_merchants_for_stats) if all_merchants_for_stats else len(all_merchants),
            'timestamp': datetime.now(),  # Always use current time for real-time display
            'market_stats': {
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': avg_price,
                'total_trades': total_trades,
                'merchant_count': len(all_merchants_for_stats) if all_merchants_for_stats else len(all_merchants)
            }
        }
        
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
        
        # Also send reply keyboard if in group (after edit, keyboard may not show)
        chat = update.effective_chat
        if chat.type in ['group', 'supergroup']:
            from utils.message_utils import send_with_reply_keyboard
            try:
                await send_with_reply_keyboard(update, "💡")  # Visible emoji to show keyboard reliably
            except Exception as e:
                logger.warning(f"Failed to send reply keyboard after P2P callback: {e}")
        
        logger.info(f"Updated P2P leaderboard ({payment_method}, page {current_page}/{total_pages}, {len(all_merchants)} total merchants) for {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_p2p_callback: {e}", exc_info=True)
        try:
            await query.answer("❌ 操作失败，请重试", show_alert=True)
        except:
            pass

