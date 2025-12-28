"""
Binance P2P Merchant Leaderboard Service
Fetches real-time P2P merchant data from Binance and formats it for display
"""
import requests
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Binance P2P API configuration
BINANCE_P2P_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
BINANCE_P2P_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Payment method mapping
PAYMENT_METHOD_MAP = {
    "bank": ["BANK"],
    "alipay": ["ALIPAY"],
    "wechat": ["WECHAT"],
    "银行卡": ["BANK"],
    "支付宝": ["ALIPAY"],
    "微信": ["WECHAT"]
}

PAYMENT_METHOD_LABELS = {
    "bank": "银行卡",
    "alipay": "支付宝",
    "wechat": "微信",
    "银行卡": "银行卡",
    "支付宝": "支付宝",
    "微信": "微信"
}

# Rank emojis
RANK_EMOJIS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def get_p2p_leaderboard(payment_method: str = "alipay", rows: int = 10) -> Optional[Dict]:
    """
    Fetch P2P merchant leaderboard from Binance API.
    
    Args:
        payment_method: Payment method code ("bank", "alipay", "wechat")
        rows: Number of merchants to fetch (default: 10)
        
    Returns:
        Dictionary with merchant data or None if error
    """
    try:
        # Map payment method to API codes
        pay_types = PAYMENT_METHOD_MAP.get(payment_method.lower(), ["ALIPAY"])
        
        # Prepare payload
        payload = {
            "fiat": "CNY",
            "asset": "USDT",
            "tradeType": "BUY",  # Showing sellers
            "rows": rows,
            "payTypes": pay_types,
            "page": 1,
            "countries": [],
            "proMerchantAds": False,
            "shieldMerchantAds": False,
            "publisherType": None
        }
        
        logger.info(f"Fetching P2P leaderboard for payment method: {payment_method}")
        
        # Make POST request
        response = requests.post(
            BINANCE_P2P_URL,
            json=payload,
            headers=BINANCE_P2P_HEADERS,
            timeout=10
        )
        
        # Check HTTP status
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Binance P2P API response structure:
        # {
        #   "code": "000000",
        #   "message": null,
        #   "data": [
        #     {
        #       "adv": {
        #         "price": "7.2345",
        #         "minSingleTransAmount": "1000",
        #         "maxSingleTransAmount": "50000",
        #         "tradeMethods": [...],
        #         ...
        #       },
        #       "advertiser": {
        #         "nickName": "Merchant Name",
        #         "monthFinishRate": 0.98,
        #         "monthFinishCount": 1234,
        #         ...
        #       }
        #     },
        #     ...
        #   ],
        #   "total": 10,
        #   "success": true
        # }
        
        if data.get('success') and data.get('code') == '000000':
            merchants = []
            
            for idx, item in enumerate(data.get('data', [])[:rows], 1):
                adv = item.get('adv', {})
                advertiser = item.get('advertiser', {})
                
                # Extract merchant information
                price = float(adv.get('price', 0))
                min_amount = float(adv.get('minSingleTransAmount', 0))
                max_amount = float(adv.get('maxSingleTransAmount', 0))
                merchant_name = advertiser.get('nickName', 'Unknown')
                month_finish_count = advertiser.get('monthFinishCount', 0) or 0
                month_finish_rate = advertiser.get('monthFinishRate', 0) or 0
                
                # Calculate credibility score (total orders approximation)
                # monthFinishCount is typically monthly, we'll use it as a proxy
                total_orders = month_finish_count * 12  # Rough estimate
                
                merchants.append({
                    'rank': idx,
                    'price': price,
                    'min_amount': min_amount,
                    'max_amount': max_amount,
                    'merchant_name': merchant_name,
                    'trade_count': month_finish_count,
                    'finish_rate': month_finish_rate,
                    'total_orders_estimate': total_orders,
                    'credibility_icon': '🌟' if total_orders > 1000 else '⭐' if total_orders > 500 else ''
                })
            
            payment_label = PAYMENT_METHOD_LABELS.get(payment_method.lower(), "支付宝")
            
            return {
                'merchants': merchants,
                'payment_method': payment_method,
                'payment_label': payment_label,
                'total': len(merchants),
                'timestamp': datetime.now()
            }
        
        logger.warning(f"Unexpected response structure from Binance P2P API: {data}")
        return None
        
    except requests.exceptions.Timeout:
        logger.error("Binance P2P API request timeout")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Binance P2P API request failed: {e}")
        return None
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error parsing Binance P2P response: {e}", exc_info=True)
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error fetching P2P leaderboard: {e}", exc_info=True)
        return None


def format_p2p_leaderboard_html(leaderboard_data: Dict) -> str:
    """
    Format P2P leaderboard data as high-end HTML message.
    
    Args:
        leaderboard_data: Dictionary from get_p2p_leaderboard()
        
    Returns:
        Formatted HTML message string
    """
    if not leaderboard_data or not leaderboard_data.get('merchants'):
        return "❌ 无法获取商户数据，请稍后重试。"
    
    merchants = leaderboard_data['merchants']
    payment_label = leaderboard_data['payment_label']
    timestamp = leaderboard_data['timestamp']
    
    # Format timestamp
    time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    # Build header
    message = f"🟢 <b>实时币价行情 (Live Market)</b>\n"
    message += f"📅 更新于: {time_str}\n"
    message += f"💳 渠道: <b>{payment_label}</b>\n"
    message += f"{'─' * 35}\n\n"
    
    # Build body (loop through merchants)
    for merchant in merchants:
        rank = merchant['rank']
        price = merchant['price']
        merchant_name = merchant['merchant_name']
        min_amount = merchant['min_amount']
        max_amount = merchant['max_amount']
        trade_count = merchant['trade_count']
        credibility_icon = merchant['credibility_icon']
        
        # Get rank emoji
        rank_emoji = RANK_EMOJIS[rank - 1] if rank <= len(RANK_EMOJIS) else f"{rank}."
        
        # Format price with fixed width (using code tag)
        price_str = f"<code>{price:.4f}</code>"
        
        # Format amount range
        if max_amount >= 1000000:
            max_str = f"{max_amount/1000000:.1f}M"
        elif max_amount >= 1000:
            max_str = f"{max_amount/1000:.0f}K"
        else:
            max_str = f"{max_amount:.0f}"
        
        if min_amount >= 1000:
            min_str = f"{min_amount/1000:.0f}K"
        else:
            min_str = f"{min_amount:.0f}"
        
        # Build row
        message += f"{price_str} | <b>{merchant_name}</b> {credibility_icon} {rank_emoji}\n"
        message += f"└ <i>限额: {min_str}-{max_str} CNY | 成单: {trade_count:,}</i>\n\n"
    
    # Build footer
    message += f"{'─' * 35}\n"
    message += "💡 输入 /buy 获取交易详情"
    
    return message

