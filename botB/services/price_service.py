"""
Price service for fetching USDT/CNY exchange rate from OKX API
"""
import requests
import logging
from typing import Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)


def get_okx_price() -> Tuple[Optional[float], Optional[str]]:
    """
    Fetch USDT/CNY price from OKX Public API.
    This function is called only when requested (no background polling).
    
    Returns:
        Tuple of (price: float or None, error_message: str or None)
        - If successful: (price, None)
        - If failed: (None, error_message) or (fallback_price, "Using fallback price")
    """
    try:
        # OKX API endpoint for USDT/CNY ticker
        # Note: OKX may use different instrument IDs, common formats:
        # - USDT-CNY (if available)
        # - USDT/CNY
        # We'll try USDT-CNY first, with fallback logic
        url = Config.OKX_API_URL
        params = {
            'instId': 'USDT-CNY'  # OKX instrument ID for USDT/CNY spot trading
        }
        
        logger.info("Fetching USDT/CNY price from OKX API...")
        
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
        
        # OKX API response structure:
        # {
        #   "code": "0",
        #   "data": [
        #     {
        #       "instId": "USDT-CNY",
        #       "last": "7.2345",  # Last traded price
        #       ...
        #     }
        #   ]
        # }
        
        if data.get('code') == '0' and data.get('data'):
            ticker_data = data['data'][0]
            price_str = ticker_data.get('last')
            
            if price_str:
                try:
                    price = float(price_str)
                    logger.info(f"OKX price fetched successfully: {price}")
                    return price, None
                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing price from OKX response: {e}")
                    # Return fallback price
                    return Config.DEFAULT_FALLBACK_PRICE, "Failed to parse price, using fallback"
        
        # If code is not '0' or data is empty
        error_msg = data.get('msg', 'Unknown error from OKX API')
        logger.warning(f"OKX API returned error: {error_msg}")
        return Config.DEFAULT_FALLBACK_PRICE, f"OKX API error: {error_msg}, using fallback price"
        
    except requests.exceptions.Timeout:
        logger.error("OKX API request timeout")
        return Config.DEFAULT_FALLBACK_PRICE, "Request timeout, using fallback price"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OKX API request failed: {e}")
        return Config.DEFAULT_FALLBACK_PRICE, f"Request failed: {str(e)}, using fallback price"
        
    except Exception as e:
        logger.error(f"Unexpected error fetching OKX price: {e}", exc_info=True)
        return Config.DEFAULT_FALLBACK_PRICE, f"Unexpected error: {str(e)}, using fallback price"


def get_price_with_markup() -> Tuple[Optional[float], Optional[str], float]:
    """
    Get OKX price with admin markup applied.
    
    Returns:
        Tuple of (final_price: float or None, error_message: str or None, base_price: float)
    """
    from database import db
    
    # Get base price from OKX
    base_price, error_msg = get_okx_price()
    
    if base_price is None:
        return None, error_msg or "Failed to fetch price", 0.0
    
    # Get admin markup
    markup = db.get_admin_markup()
    
    # Calculate final price
    final_price = base_price + markup
    
    logger.info(f"Price calculation: {base_price} (base) + {markup} (markup) = {final_price} (final)")
    
    return final_price, error_msg, base_price

