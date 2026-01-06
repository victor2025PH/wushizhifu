"""
Price service for fetching USDT/CNY exchange rate from OKX C2C API
Only uses Alipay payment method
Fetches merchant information (name and rate) on demand (no caching)
"""
import requests
import logging
from typing import Optional, Tuple, List, Dict
from config import Config

logger = logging.getLogger(__name__)

# OKX C2C API configuration
OKX_C2C_URL = "https://www.okx.com/v3/c2c/tradingOrders/books"
OKX_C2C_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
OKX_C2C_PARAMS = {
    "quoteCurrency": "cny",
    "baseCurrency": "usdt",
    "side": "sell",  # sell means merchants are selling USDT
    "paymentMethod": "aliPay",  # Only use Alipay payment method
    "userType": "all",
    "receivingAds": "false"
}


def _fetch_okx_merchants() -> Tuple[Optional[List[Dict]], Optional[str]]:
    """
    Fetch USDT/CNY merchant data from OKX C2C API (Alipay only).
    Returns merchant information including name and rate.
    
    Returns:
        Tuple of (merchants: List[Dict] or None, error_message: str or None)
        Each merchant dict contains: {'name': str, 'rate': float}
    """
    try:
        logger.info("Fetching USDT/CNY merchant data from OKX C2C API (Alipay only)...")
        
        # Make GET request to OKX C2C API
        response = requests.get(
            OKX_C2C_URL,
            params=OKX_C2C_PARAMS,
            headers=OKX_C2C_HEADERS,
            timeout=10  # 10 second timeout
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
        #         ...
        #       },
        #       ...
        #     ]
        #   }
        # }
        
        if data.get('code') == 0:
            sell_data = data.get('data', {}).get('sell', [])
            if len(sell_data) > 0:
                merchants = []
                for item in sell_data:
                    # Only use Alipay merchants
                    payment_methods = item.get('paymentMethods', [])
                    if 'aliPay' in payment_methods or 'aliPay' in [pm.lower() for pm in payment_methods]:
                        price_str = item.get('price')
                        if price_str:
                            try:
                                price = float(price_str)
                                # Get merchant name (nickName or uniqueName)
                                merchant_name = item.get('nickName') or item.get('uniqueName') or '未知商家'
                                merchants.append({
                                    'name': merchant_name,
                                    'rate': price
                                })
                            except (ValueError, TypeError):
                                continue
                
                if merchants:
                    logger.info(f"OKX C2C Alipay merchants fetched: {len(merchants)} merchants")
                    return merchants, None
                else:
                    error_msg = "No valid Alipay merchants found in OKX C2C API response"
                    logger.warning(error_msg)
                    return None, error_msg
            else:
                error_msg = "No sell data found in OKX C2C API response"
                logger.warning(error_msg)
                return None, error_msg
        
        # If data structure is unexpected
        error_msg = f"Unexpected response structure from OKX C2C API (code: {data.get('code')})"
        logger.warning(error_msg)
        return None, error_msg
        
    except requests.exceptions.Timeout:
        logger.error("OKX C2C API request timeout")
        return None, "请求超时"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OKX C2C API request failed: {e}")
        return None, f"请求失败: {str(e)}"
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error parsing OKX C2C response: {e}")
        return None, f"解析响应失败: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error fetching OKX C2C merchants: {e}", exc_info=True)
        return None, f"未知错误: {str(e)}"


def get_okx_merchants() -> Tuple[Optional[List[Dict]], Optional[str]]:
    """
    Fetch USDT/CNY merchant data from OKX C2C API (Alipay only).
    This function is called on demand (when user clicks exchange rate button).
    No caching - always fetches fresh data.
    
    Returns:
        Tuple of (merchants: List[Dict] or None, error_message: str or None)
        Each merchant dict contains: {'name': str, 'rate': float}
        Merchants are sorted by rate (ascending - lowest price first)
    """
    merchants, error_msg = _fetch_okx_merchants()
    
    if merchants:
        # Sort merchants by rate (ascending - lowest price first)
        merchants.sort(key=lambda x: x['rate'])
        return merchants, None
    
    return None, error_msg or "获取商家数据失败"


def get_usdt_cny_price() -> Tuple[Optional[float], Optional[str]]:
    """
    Get average USDT/CNY price from OKX C2C API (Alipay only).
    Calculates average from all Alipay merchants.
    This function is called on demand (no caching).
    
    Returns:
        Tuple of (average_price: float or None, error_message: str or None)
    """
    merchants, error_msg = get_okx_merchants()
    
    if merchants and len(merchants) > 0:
        # Calculate average price
        total_rate = sum(m['rate'] for m in merchants)
        average_price = total_rate / len(merchants)
        logger.info(f"OKX C2C Alipay average price: {average_price} (from {len(merchants)} merchants)")
        return average_price, None
    
    return None, error_msg or "获取价格失败"


def get_price_with_markup(group_id: Optional[int] = None, save_history: bool = True) -> Tuple[Optional[float], Optional[str], float, float]:
    """
    Get USDT/CNY price from OKX C2C (Alipay only) with markup applied (group-specific or global).
    This function is called on demand (no caching).
    
    Args:
        group_id: Optional Telegram group ID for group-specific markup
        save_history: Whether to save price to history (default: True)
        
    Returns:
        Tuple of (final_price: float or None, error_message: str or None, base_price: float, markup: float)
    """
    from database import db
    
    # Get base price from OKX C2C (Alipay only)
    base_price, error_msg = get_usdt_cny_price()
    
    if base_price is None:
        return None, error_msg or "获取价格失败", 0.0, 0.0
    
    # Check for group-specific markup first
    markup = 0.0
    if group_id:
        group_setting = db.get_group_setting(group_id)
        if group_setting:
            markup = group_setting.get('markup', 0.0)
            logger.info(f"Using group {group_id} markup: {markup}")
    
    # Fallback to global markup if no group-specific markup
    if markup == 0.0 or not group_id:
        markup = db.get_admin_markup()
        logger.info(f"Using global markup: {markup}")
    
    # Calculate final price
    final_price = base_price + markup
    
    # Save price history if requested
    if save_history:
        db.save_price_history(base_price, final_price, markup, 'okx_c2c')
    
    logger.info(f"Price calculation: {base_price} (base) + {markup} (markup) = {final_price} (final) from OKX")
    
    return final_price, error_msg, base_price, markup
