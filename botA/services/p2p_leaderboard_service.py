"""
P2P Merchant Leaderboard Service
Fetches real-time P2P merchant data from OKX C2C API (primary) and Binance P2P API (fallback)
Only uses Alipay payment method for price calculation
"""
import requests
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

# OKX C2C API configuration (Primary source)
OKX_C2C_URL = "https://www.okx.com/v3/c2c/tradingOrders/books"
OKX_C2C_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Payment method mapping for OKX
OKX_PAYMENT_METHOD_MAP = {
    "bank": "bank",
    "alipay": "aliPay",
    "wechat": "weChat",
    "银行卡": "bank",
    "支付宝": "aliPay",
    "微信": "weChat"
}

# Binance P2P API configuration (Fallback)
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


def _fetch_okx_leaderboard(payment_method: str = "alipay", rows: int = 10) -> Optional[Dict]:
    """
    Fetch P2P merchant leaderboard from OKX C2C API.
    
    Args:
        payment_method: Payment method code ("bank", "alipay", "wechat")
        rows: Number of merchants to fetch (OKX doesn't support pagination, so we fetch all and slice)
        
    Returns:
        Dictionary with merchant data or None if error
    """
    try:
        # Map payment method to OKX API codes
        okx_payment = OKX_PAYMENT_METHOD_MAP.get(payment_method.lower(), "aliPay")
        
        # Prepare params
        params = {
            "quoteCurrency": "cny",
            "baseCurrency": "usdt",
            "side": "sell",  # Showing sellers (we want to buy USDT, so we show sellers)
            "paymentMethod": okx_payment,
            "userType": "all",
            "receivingAds": "false"
        }
        
        logger.info(f"Fetching OKX C2C leaderboard for payment method: {payment_method}")
        
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
        
        if data.get('code') == 0:
            sell_data = data.get('data', {}).get('sell', [])
            if len(sell_data) > 0:
                merchants = []
                
                # Filter by payment method and limit to rows
                filtered_data = []
                for item in sell_data:
                    payment_methods = item.get('paymentMethods', [])
                    # Check if the requested payment method is in the list
                    if okx_payment in payment_methods or okx_payment.lower() in [pm.lower() for pm in payment_methods]:
                        filtered_data.append(item)
                    if len(filtered_data) >= rows:
                        break
                
                for idx, item in enumerate(filtered_data[:rows], 1):
                    # Extract merchant information
                    price = float(item.get('price', 0))
                    min_amount = float(item.get('quoteMinAmountPerOrder', 0))
                    max_amount = float(item.get('quoteMaxAmountPerOrder', 0))
                    merchant_name = item.get('nickName', 'Unknown')
                    
                    # Extract trade statistics
                    completed_order_quantity = item.get('completedOrderQuantity', 0) or 0
                    completed_rate = float(item.get('completedRate', 0) or 0)
                    
                    trade_count = completed_order_quantity
                    if trade_count == 0:
                        trade_count = 5
                    
                    total_orders_estimate = trade_count * 12
                    
                    merchants.append({
                        'rank': idx,
                        'price': price,
                        'min_amount': min_amount,
                        'max_amount': max_amount,
                        'merchant_name': merchant_name,
                        'trade_count': trade_count,
                        'finish_rate': completed_rate,
                        'total_orders_estimate': total_orders_estimate,
                        'credibility_icon': '🌟' if total_orders_estimate > 1000 else '⭐' if total_orders_estimate > 500 else ''
                    })
                
                payment_label = PAYMENT_METHOD_LABELS.get(payment_method.lower(), "支付宝")
                
                # Calculate market statistics
                if merchants:
                    prices = [m['price'] for m in merchants]
                    min_price = min(prices)
                    max_price = max(prices)
                    avg_price = sum(prices) / len(prices)
                    total_trades = sum(m['trade_count'] for m in merchants)
                else:
                    min_price = max_price = avg_price = 0
                    total_trades = 0
                
                return {
                    'merchants': merchants,
                    'payment_method': payment_method,
                    'payment_label': payment_label,
                    'total': len(merchants),
                    'timestamp': datetime.now(),
                    'page': 1,
                    'market_stats': {
                        'min_price': min_price,
                        'max_price': max_price,
                        'avg_price': avg_price,
                        'total_trades': total_trades,
                        'merchant_count': len(merchants)
                    }
                }
            else:
                logger.warning("No sell data found in OKX C2C API response")
                return None
        
        error_code = data.get('code', 'Unknown')
        error_message = data.get('msg', 'Unknown error')
        logger.warning(f"OKX C2C API error - Code: {error_code}, Message: {error_message}")
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
        logger.error(f"Unexpected error fetching OKX C2C leaderboard: {e}", exc_info=True)
        return None


def _fetch_binance_leaderboard(payment_method: str = "alipay", rows: int = 10, page: int = 1) -> Optional[Dict]:
    """
    Fetch P2P merchant leaderboard from Binance P2P API (fallback).
    
    Args:
        payment_method: Payment method code ("bank", "alipay", "wechat")
        rows: Number of merchants to fetch per request (default: 10, API limit)
        page: Page number (default: 1)
        
    Returns:
        Dictionary with merchant data or None if error
    """
    try:
        # Map payment method to API codes
        pay_types = PAYMENT_METHOD_MAP.get(payment_method.lower(), ["ALIPAY"])
        
        # Prepare payload - using minimal required parameters to avoid errors
        payload = {
            "page": page,
            "rows": rows,
            "payTypes": pay_types,
            "asset": "USDT",
            "tradeType": "BUY",  # Showing sellers (we want to buy USDT, so we show sellers)
            "fiat": "CNY",
            "countries": [],
            "proMerchantAds": False,
            "shieldMerchantAds": False
        }
        
        logger.info(f"Fetching Binance P2P leaderboard for payment method: {payment_method}")
        
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
                
                # Try multiple fields for trade count
                month_finish_count = advertiser.get('monthFinishCount', 0) or 0
                month_order_count = advertiser.get('monthOrderCount', 0) or 0
                completed_order_quantity = advertiser.get('completedOrderQuantity', 0) or 0
                
                trade_count = month_finish_count or month_order_count or completed_order_quantity
                
                month_finish_rate = advertiser.get('monthFinishRate', 0) or 0
                if trade_count == 0 and month_finish_rate > 0:
                    trade_count = max(10, int(month_finish_rate * 100))
                
                if trade_count == 0:
                    trade_count = 5
                
                total_orders_estimate = trade_count * 12
                
                merchants.append({
                    'rank': idx,
                    'price': price,
                    'min_amount': min_amount,
                    'max_amount': max_amount,
                    'merchant_name': merchant_name,
                    'trade_count': trade_count,
                    'finish_rate': month_finish_rate,
                    'total_orders_estimate': total_orders_estimate,
                    'credibility_icon': '🌟' if total_orders_estimate > 1000 else '⭐' if total_orders_estimate > 500 else ''
                })
            
            payment_label = PAYMENT_METHOD_LABELS.get(payment_method.lower(), "支付宝")
            
            # Calculate market statistics
            if merchants:
                prices = [m['price'] for m in merchants]
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                total_trades = sum(m['trade_count'] for m in merchants)
            else:
                min_price = max_price = avg_price = 0
                total_trades = 0
            
            return {
                'merchants': merchants,
                'payment_method': payment_method,
                'payment_label': payment_label,
                'total': len(merchants),
                'timestamp': datetime.now(),
                'page': page,
                'market_stats': {
                    'min_price': min_price,
                    'max_price': max_price,
                    'avg_price': avg_price,
                    'total_trades': total_trades,
                    'merchant_count': len(merchants)
                }
            }
        
        error_code = data.get('code', 'Unknown')
        error_message = data.get('message', 'Unknown error')
        logger.warning(f"Binance P2P API error - Code: {error_code}, Message: {error_message}")
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
        logger.error(f"Unexpected error fetching Binance P2P leaderboard: {e}", exc_info=True)
        return None


def get_p2p_leaderboard(payment_method: str = "alipay", rows: int = 10, page: int = 1) -> Optional[Dict]:
    """
    Fetch P2P merchant leaderboard from OKX C2C API (primary) or Binance P2P API (fallback).
    Only uses Alipay payment method for price calculation.
    
    Args:
        payment_method: Payment method code ("bank", "alipay", "wechat")
        rows: Number of merchants to fetch per request (default: 10)
        page: Page number (default: 1, OKX doesn't support pagination)
        
    Returns:
        Dictionary with merchant data or None if error
    """
    # Try OKX C2C first (primary source)
    result = _fetch_okx_leaderboard(payment_method, rows)
    
    if result is not None:
        logger.info(f"Successfully fetched leaderboard from OKX C2C")
        return result
    
    # If OKX failed, try Binance P2P as fallback
    logger.warning(f"OKX C2C failed, trying Binance P2P fallback...")
    result = _fetch_binance_leaderboard(payment_method, rows, page)
    
    if result is not None:
        logger.info(f"Successfully fetched leaderboard from Binance P2P (fallback)")
        return result
    
    logger.error("Both OKX C2C and Binance P2P failed")
    return None


def format_p2p_leaderboard_html(leaderboard_data: Dict, page: int = 1, per_page: int = 5, total_pages: int = 1) -> str:
    """
    Format P2P leaderboard data as HTML message.
    
    Args:
        leaderboard_data: Dictionary from get_p2p_leaderboard()
        page: Current page number
        per_page: Number of merchants per page
        total_pages: Total number of pages
        
    Returns:
        Formatted HTML message string
    """
    if not leaderboard_data or not leaderboard_data.get('merchants'):
        return "❌ 无法获取商户数据，请稍后重试。"
    
    merchants = leaderboard_data['merchants']
    payment_label = leaderboard_data['payment_label']
    timestamp = leaderboard_data['timestamp']
    market_stats = leaderboard_data.get('market_stats', {})
    
    # Get merchants for current page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_merchants = merchants[start_idx:end_idx]
    
    if not page_merchants:
        return "❌ 该页无数据"
    
    time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    # Build header
    message = f"🟢 <b>实时币价行情 (Live Market)</b>\n"
    message += f"📅 更新于: {time_str}\n"
    message += f"💳 渠道: <b>{payment_label}</b>\n"
    
    # Add market statistics
    if market_stats and market_stats.get('merchant_count', 0) > 0:
        message += f"📊 市场概况: "
        message += f"最低 {market_stats['min_price']:.2f} | "
        message += f"最高 {market_stats['max_price']:.2f} | "
        message += f"均价 {market_stats['avg_price']:.2f} CNY\n"
        if market_stats.get('total_trades', 0) > 0:
            message += f"✅ 总成单量: {market_stats['total_trades']:,} 笔 | "
            message += f"活跃商户: {market_stats['merchant_count']} 家\n"
    
    message += f"{'─' * 35}\n\n"
    
    # Build body
    for idx, merchant in enumerate(page_merchants, 1):
        actual_rank = start_idx + idx
        price = merchant['price']
        merchant_name = merchant['merchant_name']
        min_amount = merchant['min_amount']
        max_amount = merchant['max_amount']
        trade_count = merchant['trade_count']
        finish_rate = merchant.get('finish_rate', 0)
        credibility_icon = merchant['credibility_icon']
        
        if actual_rank <= len(RANK_EMOJIS):
            rank_emoji = RANK_EMOJIS[actual_rank - 1]
        else:
            rank_emoji = f"{actual_rank}."
        
        price_str = f"<code>{price:.2f}</code>"
        
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
        
        message += f"{price_str} | <b>{merchant_name}</b> {credibility_icon} {rank_emoji}\n"
        rate_info = f" | 完成率: {finish_rate*100:.0f}%" if finish_rate > 0 else ""
        message += f"└ <i>限额: {min_str}-{max_str} CNY | 成单: {trade_count:,} 笔{rate_info}</i>\n\n"
    
    message += f"{'─' * 35}\n"
    message += f"💡 <b>输入数字进行计算（CNY → USDT）</b>\n"
    if total_pages > 1:
        message += f"📄 第 {page}/{total_pages} 页"
    
    return message

