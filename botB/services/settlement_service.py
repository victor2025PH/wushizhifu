"""
Settlement calculation service
Handles OTC settlement calculations with Binance P2P price (CoinGecko fallback) and admin markup
"""
import logging
from typing import Tuple, Optional
from services.price_service import get_price_with_markup
from services.math_service import parse_amount, is_number, is_simple_math

logger = logging.getLogger(__name__)


def calculate_settlement(amount_text: str) -> Tuple[Optional[dict], Optional[str]]:
    """
    Calculate settlement bill for given CNY amount.
    
    The input represents CNY (Chinese Yuan), and the function calculates
    how much USDT should be settled based on the current USDT/CNY rate + markup.
    
    Args:
        amount_text: CNY amount as text (number or math expression, e.g., "20000-200")
        
    Returns:
        Tuple of (settlement_data: dict or None, error_message: str or None)
        
    Settlement data structure:
        {
            'cny_amount': float,      # Input CNY amount (after calculation)
            'base_price': float,       # Base USDT/CNY price from Binance P2P
            'admin_markup': float,     # Admin markup added to price
            'final_price': float,      # Final USDT/CNY price (base + markup)
            'usdt_amount': float,      # Calculated USDT amount to settle
            'price_error': str or None
        }
        
    Calculation formula:
        usdt_amount = cny_amount / final_price
        where final_price = base_price + admin_markup
    """
    try:
        # Parse CNY amount (input is in CNY)
        cny_amount = parse_amount(amount_text)
        
        if cny_amount <= 0:
            return None, "金额必须大于 0"
        
        # Get price with markup (USDT/CNY rate)
        final_price, price_error, base_price = get_price_with_markup()
        
        if final_price is None:
            return None, f"无法获取价格: {price_error or '未知错误'}"
        
        if final_price <= 0:
            return None, "汇率无效，无法计算"
        
        # Import here to avoid circular import
        from database import db
        admin_markup = db.get_admin_markup()
        
        # Calculate USDT amount: CNY / (USDT/CNY rate)
        # Example: 19800 CNY / 7.25 (USDT/CNY) = 2731.03 USDT
        usdt_amount = cny_amount / final_price
        
        settlement_data = {
            'cny_amount': cny_amount,      # Input CNY amount
            'base_price': base_price,      # Base USDT/CNY price
            'admin_markup': admin_markup,  # Admin markup
            'final_price': final_price,    # Final USDT/CNY price (base + markup)
            'usdt_amount': usdt_amount,    # Calculated USDT amount
            'price_error': price_error
        }
        
        return settlement_data, None
        
    except ValueError as e:
        return None, f"金额格式错误: {str(e)}"
    except ZeroDivisionError:
        return None, "汇率不能为零"
    except Exception as e:
        logger.error(f"Error calculating settlement: {e}", exc_info=True)
        return None, f"计算错误: {str(e)}"


def format_settlement_bill(settlement_data: dict, usdt_address: str = None) -> str:
    """
    Format settlement bill as HTML message (receipt style).
    
    Shows: CNY amount (input) -> USDT amount (calculated based on rate).
    
    Args:
        settlement_data: Settlement data dictionary
        usdt_address: Optional USDT address to display
        
    Returns:
        Formatted HTML message
    """
    cny_amount = settlement_data['cny_amount']       # Input: CNY amount
    base_price = settlement_data['base_price']       # Base USDT/CNY price
    admin_markup = settlement_data['admin_markup']   # Admin markup
    final_price = settlement_data['final_price']     # Final USDT/CNY price
    usdt_amount = settlement_data['usdt_amount']     # Output: USDT amount
    price_error = settlement_data.get('price_error')
    
    # Build receipt-style HTML message
    message = "🧾 <b>交易结算单</b>\n"
    message += "────────────────────────\n\n"
    
    # Input: CNY amount
    message += f"💰 应收人民币: <b><code>{cny_amount:,.2f} CNY</code></b>\n\n"
    
    # Exchange rate breakdown
    if admin_markup != 0:
        markup_sign = "+" if admin_markup > 0 else ""
        rate_breakdown = f"{final_price:.4f} (Binance P2P: {base_price:.4f} {markup_sign}{admin_markup:.4f})"
    else:
        rate_breakdown = f"{final_price:.4f} (Binance P2P: {base_price:.4f})"
    
    message += f"📊 汇率 (USDT/CNY): {rate_breakdown}\n\n"
    
    # Output: USDT amount to settle
    message += f"💵 应结算 USDT: <b><code>{usdt_amount:,.2f} U</code></b>\n"
    
    message += "────────────────────────\n"
    
    # USDT address if provided
    if usdt_address:
        address_display = usdt_address
        if len(usdt_address) > 30:
            address_display = f"{usdt_address[:15]}...{usdt_address[-15:]}"
        message += f"🔗 收款地址: <code>{address_display}</code>\n"
    
    # Price error warning
    if price_error:
        message += f"\n⚠️ <i>{price_error}</i>"
    
    return message

