"""
Price service for fetching USDT/CNY exchange rate from CoinGecko API
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


def get_usdt_cny_price() -> Tuple[Optional[float], Optional[str]]:
    """
    Fetch USDT/CNY price from CoinGecko API.
    Uses in-memory cache (60 seconds) to prevent API rate limiting.
    This function is called only when requested (no background polling).
    
    Returns:
        Tuple of (price: float or None, error_message: str or None)
        - If successful: (price, None)
        - If failed: (fallback_price, "Using fallback price")
    """
    # Check cache first
    if _is_cache_valid():
        logger.info(f"Returning cached price: {_price_cache['price']}")
        return _price_cache['price'], None
    
    try:
        # CoinGecko API endpoint for USDT/CNY
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'tether',
            'vs_currencies': 'cny'
        }
        
        logger.info("Fetching USDT/CNY price from CoinGecko API...")
        
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
            
            # Update cache
            _update_cache(price)
            
            return price, None
        
        # If data structure is unexpected
        error_msg = "Unexpected response structure from CoinGecko API"
        logger.warning(error_msg)
        return Config.DEFAULT_FALLBACK_PRICE, f"{error_msg}, using fallback price"
        
    except requests.exceptions.Timeout:
        logger.error("CoinGecko API request timeout")
        return Config.DEFAULT_FALLBACK_PRICE, "Request timeout, using fallback price"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"CoinGecko API request failed: {e}")
        return Config.DEFAULT_FALLBACK_PRICE, f"Request failed: {str(e)}, using fallback price"
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error parsing CoinGecko response: {e}")
        return Config.DEFAULT_FALLBACK_PRICE, f"Failed to parse response: {str(e)}, using fallback price"
        
    except Exception as e:
        logger.error(f"Unexpected error fetching CoinGecko price: {e}", exc_info=True)
        return Config.DEFAULT_FALLBACK_PRICE, f"Unexpected error: {str(e)}, using fallback price"


def get_price_with_markup() -> Tuple[Optional[float], Optional[str], float]:
    """
    Get USDT/CNY price from CoinGecko with admin markup applied.
    
    Returns:
        Tuple of (final_price: float or None, error_message: str or None, base_price: float)
    """
    from database import db
    
    # Get base price from CoinGecko
    base_price, error_msg = get_usdt_cny_price()
    
    if base_price is None:
        return None, error_msg or "Failed to fetch price", 0.0
    
    # Get admin markup
    markup = db.get_admin_markup()
    
    # Calculate final price
    final_price = base_price + markup
    
    logger.info(f"Price calculation: {base_price} (base) + {markup} (markup) = {final_price} (final)")
    
    return final_price, error_msg, base_price

