"""
OKX C2C Merchant Leaderboard Service
Fetches real-time P2P merchant data from OKX C2C API (Alipay only)
"""
import requests
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

# OKX C2C API configuration
OKX_C2C_URL = "https://www.okx.com/v3/c2c/tradingOrders/books"
OKX_C2C_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Payment method mapping (only Alipay is supported)
PAYMENT_METHOD_MAP = {
    "alipay": "aliPay",
    "支付宝": "aliPay",
    "bank": "aliPay",  # Fallback to Alipay
    "银行卡": "aliPay",  # Fallback to Alipay
    "wechat": "aliPay",  # Fallback to Alipay
    "微信": "aliPay"  # Fallback to Alipay
}

PAYMENT_METHOD_LABELS = {
    "alipay": "支付宝",
    "支付宝": "支付宝",
    "bank": "支付宝",  # Always show Alipay
    "银行卡": "支付宝",  # Always show Alipay
    "wechat": "支付宝",  # Always show Alipay
    "微信": "支付宝"  # Always show Alipay
}

# Rank emojis
RANK_EMOJIS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def get_p2p_leaderboard(payment_method: str = "alipay", rows: int = 10, page: int = 1) -> Optional[Dict]:
    """
    Fetch P2P merchant leaderboard from OKX C2C API (Alipay only).
    
    Args:
        payment_method: Payment method code (always uses Alipay)
        rows: Number of merchants to fetch per request (default: 10)
        page: Page number (default: 1) - Note: OKX doesn't support pagination, so we slice the results
    
    Returns:
        Dictionary with merchant data or None if error
    """
    try:
        # Always use Alipay payment method
        okx_payment_method = PAYMENT_METHOD_MAP.get(payment_method.lower(), "aliPay")
        
        # OKX C2C API parameters
        params = {
            "quoteCurrency": "cny",
            "baseCurrency": "usdt",
            "side": "sell",  # sell means merchants are selling USDT
            "paymentMethod": okx_payment_method,  # Only Alipay
            "userType": "all",
            "receivingAds": "false"
        }
        
        logger.info(f"Fetching OKX C2C leaderboard for payment method: {payment_method} (using Alipay)")
        
        # Make GET request
        response = requests.get(
            OKX_C2C_URL,
            params=params,
            headers=OKX_C2C_HEADERS,
            timeout=10
        )
        
        # Check HTTP status
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # OKX C2C API response structure:
        # {
        #   "code": 0,
        #   "data": {
        #     "sell": [
        #       {
        #         "price": "6.88",  // String price
        #         "paymentMethods": ["aliPay"],
        #         "nickName": "商家名称",
        #         "minQuote": "1000",  // Min amount in CNY
        #         "maxQuote": "50000",  // Max amount in CNY
        #         "finishRate": 0.98,  // Completion rate
        #         "finishCount": 1234,  // Completed orders
        #         ...
        #       },
        #       ...
        #     ]
        #   }
        # }
        
        if data.get('code') == 0:
            sell_data = data.get('data', {}).get('sell', [])
            if not sell_data:
                logger.warning("No sell data found in OKX C2C API response")
                return None
            
            merchants = []
            
            # Filter only Alipay merchants and process
            for idx, item in enumerate(sell_data, 1):
                # Only use Alipay merchants
                payment_methods = item.get('paymentMethods', [])
                if 'aliPay' not in payment_methods and 'aliPay' not in [pm.lower() for pm in payment_methods]:
                    continue
                
                # Extract merchant information
                price_str = item.get('price', '0')
                try:
                    price = float(price_str)
                except (ValueError, TypeError):
                    continue
                
                merchant_name = item.get('nickName') or item.get('uniqueName') or '未知商家'
                min_amount = float(item.get('minQuote', 0))
                max_amount = float(item.get('maxQuote', 0))
                
                # Get trade count and finish rate
                finish_count = item.get('finishCount', 0) or 0
                finish_rate = item.get('finishRate', 0) or 0
                
                # If finish_count is 0, use a minimum value
                if finish_count == 0:
                    finish_count = 5  # Minimum display value
                
                merchants.append({
                    'rank': idx,
                    'price': price,
                    'min_amount': min_amount,
                    'max_amount': max_amount,
                    'merchant_name': merchant_name,
                    'trade_count': finish_count,
                    'finish_rate': finish_rate,
                    'total_orders_estimate': finish_count * 12,  # Rough annual estimate
                    'credibility_icon': '🌟' if finish_count > 1000 else '⭐' if finish_count > 500 else ''
                })
            
            # Return first 10 merchants (no pagination)
            merchants = merchants[:10]
            
            if not merchants:
                logger.warning("No merchants found")
                return None
            
            payment_label = PAYMENT_METHOD_LABELS.get(payment_method.lower(), "支付宝")
            
            # Calculate market statistics
            if merchants:
                prices = [m['price'] for m in merchants]
                min_price = min(prices)
                max_price = max(prices)
                # Get third-tier price (3rd merchant, index 2)
                if len(merchants) >= 3:
                    third_tier_price = merchants[2]['price']
                else:
                    # Fallback: use last merchant's price if less than 3 merchants
                    third_tier_price = merchants[-1]['price']
                total_trades = sum(m['trade_count'] for m in merchants)
            else:
                min_price = max_price = third_tier_price = 0
                total_trades = 0
            
            return {
                'merchants': merchants,  # First 10 merchants
                'payment_method': payment_method,
                'payment_label': payment_label,
                'total': len(merchants),  # 10 merchants
                'timestamp': datetime.now(),
                'page': 1,  # Always page 1 (no pagination)
                'market_stats': {
                    'min_price': min_price,
                    'max_price': max_price,
                    'third_tier_price': third_tier_price,  # Changed from avg_price to third_tier_price
                    'total_trades': total_trades,
                    'merchant_count': len(merchants)
                }
            }
        
        # Log error details
        error_code = data.get('code', 'Unknown')
        logger.warning(f"OKX C2C API error - Code: {error_code}")
        logger.debug(f"Full API response: {data}")
        return None
        
    except requests.exceptions.Timeout:
        logger.error("OKX C2C API request timeout")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OKX C2C API request failed: {e}")
        return None
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error parsing OKX C2C response: {e}", exc_info=True)
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error fetching P2P leaderboard: {e}", exc_info=True)
        return None


def format_p2p_leaderboard_html(leaderboard_data: Dict, page: int = 1, per_page: int = 10, total_pages: int = 1) -> str:
    """
    Format P2P leaderboard data as HTML message (10 merchants, no pagination, no limit/order count).
    
    Args:
        leaderboard_data: Dictionary from get_p2p_leaderboard()
        page: Not used (kept for compatibility)
        per_page: Not used (kept for compatibility)
        total_pages: Not used (kept for compatibility)
        
    Returns:
        Formatted HTML message string
    """
    if not leaderboard_data or not leaderboard_data.get('merchants'):
        return "❌ 无法获取商户数据，请稍后重试。"
    
    merchants = leaderboard_data['merchants']
    payment_label = leaderboard_data['payment_label']
    timestamp = leaderboard_data['timestamp']
    market_stats = leaderboard_data.get('market_stats', {})
    
    # Format timestamp (always use current time for real-time display)
    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Build header with market statistics
    message = f"🟢 <b>实时币价行情 (Live Market)</b>\n"
    message += f"📅 更新于: {time_str}\n"
    message += f"💳 渠道: <b>{payment_label}</b>\n"
    
    # Add market statistics
    if market_stats and market_stats.get('merchant_count', 0) > 0:
        message += f"📊 市场概况: "
        message += f"最低 {market_stats['min_price']:.2f} | "
        message += f"最高 {market_stats['max_price']:.2f} | "
        # Use third_tier_price instead of avg_price
        third_tier_price = market_stats.get('third_tier_price', market_stats.get('avg_price', 0))
        message += f"采用价格 {third_tier_price:.2f} CNY\n"
        if market_stats.get('total_trades', 0) > 0:
            message += f"✅ 总成单量: {market_stats['total_trades']:,} 笔 | "
            message += f"活跃商户: {market_stats['merchant_count']} 家\n"
    
    message += f"{'─' * 35}\n\n"
    
    # Build body (show all 10 merchants, no pagination)
    for idx, merchant in enumerate(merchants, 1):
        price = merchant['price']
        merchant_name = merchant['merchant_name']
        credibility_icon = merchant['credibility_icon']
        
        # Get rank emoji (only for top 10)
        if idx <= len(RANK_EMOJIS):
            rank_emoji = RANK_EMOJIS[idx - 1]
        else:
            rank_emoji = f"{idx}."
        
        # Format price with 2 decimal places
        price_str = f"<code>{price:.2f}</code>"
        
        # Build row (only show price and merchant name, no limit or order count)
        message += f"{price_str} | <b>{merchant_name}</b> {credibility_icon} {rank_emoji}\n\n"
    
    # Build footer (no pagination info, no buttons)
    message += f"{'─' * 35}\n"
    
    return message
