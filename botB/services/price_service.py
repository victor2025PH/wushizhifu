"""
Price service for fetching USDT/CNY exchange rate from OKX C2C API
Falls back to Binance P2P API, then CoinGecko API if OKX fails
Only uses Alipay payment method for price calculation
"""
import requests
import logging
import time
from typing import Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)

# In-memory cache for price data
_price_cache = {
    'price': None,
    'timestamp': 0,
    'cache_duration': 60  # Cache valid for 60 seconds
}

# OKX C2C API configuration (Primary source)
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

# Binance P2P API configuration (Fallback)
BINANCE_P2P_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
BINANCE_P2P_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
BINANCE_P2P_PAYLOAD = {
    "fiat": "CNY",
    "page": 1,
    "rows": 20,  # Get 20 results to calculate average price
    "tradeType": "BUY",  # BUY means merchants are selling USDT (Ask price)
    "asset": "USDT",
    "payTypes": ["ALIPAY"],  # Only use Alipay payment method
    "countries": [],
    "proMerchantAds": False,
    "shieldMerchantAds": False,
    "publisherType": None
}


def _is_cache_valid() -> bool:
    """
    Check if the cached price is still valid.
    
    Returns:
        True if cache exists and is within cache duration
    """
    if _price_cache['price'] is None:
        return False
    
    current_time = time.time()
    cache_age = current_time - _price_cache['timestamp']
    
    return cache_age < _price_cache['cache_duration']


def _update_cache(price: float):
    """
    Update the price cache with new price and timestamp.
    
    Args:
        price: The price to cache
    """
    _price_cache['price'] = price
    _price_cache['timestamp'] = time.time()


def _fetch_okx_price() -> Tuple[Optional[float], Optional[str]]:
    """
    Fetch USDT/CNY average price from OKX C2C API (Alipay only).
    Calculates average price from multiple merchants to get more accurate rate.
    
    Returns:
        Tuple of (average_price: float or None, error_message: str or None)
    """
    try:
        logger.info("Fetching USDT/CNY average price from OKX C2C API (Alipay only)...")
        
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
        #         ...
        #       },
        #       ...
        #     ]
        #   }
        # }
        
        if data.get('code') == 0:
            sell_data = data.get('data', {}).get('sell', [])
            if len(sell_data) > 0:
                prices = []
                for item in sell_data:
                    # Only use Alipay merchants
                    payment_methods = item.get('paymentMethods', [])
                    if 'aliPay' in payment_methods or 'aliPay' in [pm.lower() for pm in payment_methods]:
                        price_str = item.get('price')
                        if price_str:
                            try:
                                price = float(price_str)
                                prices.append(price)
                            except (ValueError, TypeError):
                                continue
                
                if prices:
                    # Calculate average price
                    average_price = sum(prices) / len(prices)
                    logger.info(f"OKX C2C Alipay average price calculated: {average_price} (from {len(prices)} merchants)")
                    return average_price, None
                else:
                    error_msg = "No valid Alipay prices found in OKX C2C API response"
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
        return None, "Request timeout"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OKX C2C API request failed: {e}")
        return None, f"Request failed: {str(e)}"
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error parsing OKX C2C response: {e}")
        return None, f"Failed to parse response: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error fetching OKX C2C price: {e}", exc_info=True)
        return None, f"Unexpected error: {str(e)}"


def _fetch_binance_p2p_price() -> Tuple[Optional[float], Optional[str]]:
    """
    Fetch USDT/CNY average price from Binance P2P API (Alipay only).
    Calculates average price from multiple merchants to get more accurate rate.
    
    Returns:
        Tuple of (average_price: float or None, error_message: str or None)
    """
    try:
        logger.info("Fetching USDT/CNY average price from Binance P2P API (Alipay only)...")
        
        # Make POST request to Binance P2P API
        response = requests.post(
            BINANCE_P2P_URL,
            json=BINANCE_P2P_PAYLOAD,
            headers=BINANCE_P2P_HEADERS,
            timeout=10  # 10 second timeout
        )
        
        # Check HTTP status
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Binance P2P API response structure:
        # {
        #   "code": "000000",
        #   "message": null,
        #   "messageDetail": null,
        #   "data": [
        #     {
        #       "adv": {
        #         "price": "7.2345",  // String price
        #         ...
        #       },
        #       ...
        #     }
        #   ],
        #   "total": 20,
        #   "success": true
        # }
        
        if data.get('success') and data.get('code') == '000000':
            if 'data' in data and len(data['data']) > 0:
                prices = []
                for item in data['data']:
                    price_str = item.get('adv', {}).get('price')
                    if price_str:
                        try:
                            price = float(price_str)
                            prices.append(price)
                        except (ValueError, TypeError):
                            continue
                
                if prices:
                    # Calculate average price
                    average_price = sum(prices) / len(prices)
                    logger.info(f"Binance P2P Alipay average price calculated: {average_price} (from {len(prices)} merchants)")
                    return average_price, None
                else:
                    error_msg = "No valid prices found in Binance P2P API response"
                    logger.warning(error_msg)
                    return None, error_msg
        
        # If data structure is unexpected
        error_msg = "Unexpected response structure from Binance P2P API"
        logger.warning(error_msg)
        return None, error_msg
        
    except requests.exceptions.Timeout:
        logger.error("Binance P2P API request timeout")
        return None, "Request timeout"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Binance P2P API request failed: {e}")
        return None, f"Request failed: {str(e)}"
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error parsing Binance P2P response: {e}")
        return None, f"Failed to parse response: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error fetching Binance P2P price: {e}", exc_info=True)
        return None, f"Unexpected error: {str(e)}"


def _fetch_coingecko_price() -> Tuple[Optional[float], Optional[str]]:
    """
    Fetch USDT/CNY price from CoinGecko API (fallback).
    
    Returns:
        Tuple of (price: float or None, error_message: str or None)
    """
    try:
        logger.info("Fetching USDT/CNY price from CoinGecko API (fallback)...")
        
        # CoinGecko API endpoint for USDT/CNY
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'tether',
            'vs_currencies': 'cny'
        }
        
        # Make request with timeout
        response = requests.get(
            url,
            params=params,
            timeout=10  # 10 second timeout
        )
        
        # Check HTTP status
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # CoinGecko API response structure:
        # {
        #   "tether": {
        #     "cny": 7.2345
        #   }
        # }
        
        if 'tether' in data and 'cny' in data['tether']:
            price = float(data['tether']['cny'])
            logger.info(f"CoinGecko price fetched successfully: {price}")
            return price, None
        
        # If data structure is unexpected
        error_msg = "Unexpected response structure from CoinGecko API"
        logger.warning(error_msg)
        return None, error_msg
        
    except requests.exceptions.Timeout:
        logger.error("CoinGecko API request timeout")
        return None, "Request timeout"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"CoinGecko API request failed: {e}")
        return None, f"Request failed: {str(e)}"
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error parsing CoinGecko response: {e}")
        return None, f"Failed to parse response: {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error fetching CoinGecko price: {e}", exc_info=True)
        return None, f"Unexpected error: {str(e)}"


def get_usdt_cny_price() -> Tuple[Optional[float], Optional[str]]:
    """
    Fetch USDT/CNY average price from OKX C2C API (Alipay payment method only).
    Falls back to Binance P2P API, then CoinGecko API if OKX fails.
    Uses in-memory cache (60 seconds) to prevent API rate limiting.
    This function is called only when requested (no background polling).
    
    Returns:
        Tuple of (average_price: float or None, error_message: str or None)
        - If successful: (average_price, None)
        - If failed: (fallback_price, "Using fallback price")
    """
    # Check cache first
    if _is_cache_valid():
        logger.info(f"Returning cached price: {_price_cache['price']}")
        return _price_cache['price'], None
    
    # Try OKX C2C first (primary source - Alipay average price)
    price, error_msg = _fetch_okx_price()
    
    if price is not None:
        # Update cache with successful average price
        _update_cache(price)
        return price, None
    
    # If OKX failed, try Binance P2P as fallback
    logger.warning(f"OKX C2C failed ({error_msg}), trying Binance P2P fallback...")
    price, binance_error = _fetch_binance_p2p_price()
    
    if price is not None:
        # Update cache with fallback price
        _update_cache(price)
        return price, f"Using Binance P2P fallback (OKX C2C failed: {error_msg})"
    
    # If Binance P2P also failed, try CoinGecko as last fallback
    logger.warning(f"Binance P2P also failed ({binance_error}), trying CoinGecko fallback...")
    price, coingecko_error = _fetch_coingecko_price()
    
    if price is not None:
        # Update cache with fallback price
        _update_cache(price)
        return price, f"Using CoinGecko fallback (OKX C2C failed: {error_msg}, Binance P2P failed: {binance_error})"
    
    # All APIs failed, use hardcoded fallback
    logger.error(f"All APIs failed. Using hardcoded fallback price: {Config.DEFAULT_FALLBACK_PRICE}")
    logger.error(f"OKX C2C error: {error_msg}")
    logger.error(f"Binance P2P error: {binance_error}")
    logger.error(f"CoinGecko error: {coingecko_error}")
    
    return Config.DEFAULT_FALLBACK_PRICE, f"All APIs failed (OKX C2C: {error_msg}, Binance P2P: {binance_error}, CoinGecko: {coingecko_error}), using fallback price"


def get_price_with_markup(group_id: Optional[int] = None, save_history: bool = True) -> Tuple[Optional[float], Optional[str], float, float]:
    """
    Get USDT/CNY price from OKX C2C (with Binance P2P and CoinGecko fallback) with markup applied (group-specific or global).
    
    Args:
        group_id: Optional Telegram group ID for group-specific markup
        save_history: Whether to save price to history (default: True)
        
    Returns:
        Tuple of (final_price: float or None, error_message: str or None, base_price: float, markup: float)
    """
    from database import db
    
    # Get base price from OKX C2C (with Binance P2P and CoinGecko fallback)
    base_price, error_msg = get_usdt_cny_price()
    
    if base_price is None:
        return None, error_msg or "Failed to fetch price", 0.0, 0.0
    
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
        # Determine source from error message
        if error_msg is None or 'okx' in (error_msg or '').lower():
            source = 'okx_c2c'
        elif 'binance' in (error_msg or '').lower():
            source = 'binance_p2p'
        else:
            source = 'coingecko'
        db.save_price_history(base_price, final_price, markup, source)
    
    logger.info(f"Price calculation: {base_price} (base) + {markup} (markup) = {final_price} (final)")
    
    return final_price, error_msg, base_price, markup

