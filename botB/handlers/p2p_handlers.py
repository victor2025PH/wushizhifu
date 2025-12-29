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

# Cache for P2P merchant data to avoid excessive API calls
# Structure: {payment_method: {page_num: [merchants], 'last_update': timestamp}}
_p2p_cache: Dict[str, Dict] = {}

# Cache expiration time (seconds) - refresh cache after 5 minutes
CACHE_EXPIRY = 300

def _get_cached_merchants(payment_method: str) -> Optional[List]:
    """
    Get all cached merchants for a payment method.
    
    Args:
        payment_method: Payment method code
        
    Returns:
        List of all cached merchants or None if cache expired/empty
    """
    import time
    
    if payment_method not in _p2p_cache:
        return None
    
    cache_entry = _p2p_cache[payment_method]
    
    # Check if cache expired
    last_update = cache_entry.get('last_update', 0)
    if time.time() - last_update > CACHE_EXPIRY:
        # Cache expired, clear it
        _p2p_cache.pop(payment_method, None)
        return None
    
    # Collect all cached merchants from all pages
    all_merchants = []
    for key in sorted(cache_entry.keys()):
        if key != 'last_update' and isinstance(key, int):
            merchants = cache_entry.get(key, [])
            all_merchants.extend(merchants)
    
    return all_merchants if all_merchants else None


def _cache_merchants(payment_method: str, page: int, merchants: List):
    """
    Cache merchants for a payment method and page.
    
    Args:
        payment_method: Payment method code
        page: Page number
        merchants: List of merchant dictionaries
    """
    import time
    
    if payment_method not in _p2p_cache:
        _p2p_cache[payment_method] = {}
    
    _p2p_cache[payment_method][page] = merchants
    _p2p_cache[payment_method]['last_update'] = time.time()


def _get_all_merchants_with_pagination(payment_method: str, required_page: int, per_page: int = 5) -> tuple:
    """
    Get all merchants with smart pagination - fetch new data only when needed.
    
    Args:
        payment_method: Payment method code
        required_page: The page number the user wants to see
        per_page: Number of merchants per page
        
    Returns:
        Tuple of (all_merchants_list, total_pages)
    """
    # Get cached merchants first
    cached_merchants = _get_cached_merchants(payment_method)
    
    # Calculate which API page we need based on required display page
    # Each API call gets 10 merchants, each display page shows 5
    # So: display page 1-2 need API page 1, display page 3-4 need API page 2, etc.
    api_pages_needed = (required_page * per_page + 9) // 10  # Ceiling division
    
    # Check if we have enough cached data
    if cached_merchants:
        total_cached = len(cached_merchants)
        required_count = required_page * per_page
        
        # If we have enough cached data, use it
        if total_cached >= required_count:
            # Calculate total pages based on cached data
            total_pages = (total_cached + per_page - 1) // per_page
            return cached_merchants, total_pages
        
        # If we need more data, fetch the missing pages
        cached_api_pages = len(_p2p_cache.get(payment_method, {}).keys()) - 1  # Exclude 'last_update'
        
        # Fetch missing pages
        for api_page in range(cached_api_pages + 1, api_pages_needed + 1):
            logger.info(f"Fetching API page {api_page} for payment method {payment_method}")
            leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=10, page=api_page)
            
            if leaderboard_data and leaderboard_data.get('merchants'):
                new_merchants = leaderboard_data['merchants']
                _cache_merchants(payment_method, api_page, new_merchants)
                cached_merchants.extend(new_merchants)
            else:
                # No more data available
                break
        
        # Recalculate total pages
        total_pages = (len(cached_merchants) + per_page - 1) // per_page
        return cached_merchants, total_pages
    
    # No cache, fetch initial pages
    all_merchants = []
    for api_page in range(1, api_pages_needed + 1):
        logger.info(f"Fetching API page {api_page} for payment method {payment_method}")
        leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=10, page=api_page)
        
        if leaderboard_data and leaderboard_data.get('merchants'):
            merchants = leaderboard_data['merchants']
            _cache_merchants(payment_method, api_page, merchants)
            all_merchants.extend(merchants)
            
            # If we got less than 10 merchants, we've reached the end
            if len(merchants) < 10:
                break
        else:
            break
    
    total_pages = (len(all_merchants) + per_page - 1) // per_page if all_merchants else 1
    return all_merchants, total_pages




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
        
        # Get all merchants with smart pagination (fetch only when needed)
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
        
        # Calculate market stats from all merchants
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
            'merchants': all_merchants,
            'payment_method': payment_method,
            'payment_label': payment_label,
            'total': len(all_merchants),
            'timestamp': datetime.now(),
            'market_stats': {
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': avg_price,
                'total_trades': total_trades,
                'merchant_count': len(all_merchants)
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
        
        logger.info(f"Sent P2P leaderboard ({payment_method}, page {current_page}/{total_pages}, {len(all_merchants)} total merchants) to {update.effective_user.id}")
        
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
        
        per_page = 5  # Show 5 merchants per page
        
        # Get all merchants with smart pagination (fetch only when needed)
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
        
        # Calculate market stats from all merchants
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
            'merchants': all_merchants,
            'payment_method': payment_method,
            'payment_label': payment_label,
            'total': len(all_merchants),
            'timestamp': datetime.now(),
            'market_stats': {
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': avg_price,
                'total_trades': total_trades,
                'merchant_count': len(all_merchants)
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
        
        logger.info(f"Updated P2P leaderboard ({payment_method}, page {current_page}/{total_pages}, {len(all_merchants)} total merchants) for {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_p2p_callback: {e}", exc_info=True)
        try:
            await query.answer("❌ 操作失败，请重试", show_alert=True)
        except:
            pass

