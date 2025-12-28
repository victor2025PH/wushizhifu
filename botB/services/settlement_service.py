"""
Settlement calculation service
Handles OTC settlement calculations with OKX price and admin markup
"""
import logging
from typing import Tuple, Optional
from services.price_service import get_price_with_markup
from services.math_service import parse_amount, is_number, is_simple_math

logger = logging.getLogger(__name__)


def calculate_settlement(amount_text: str) -> Tuple[Optional[dict], Optional[str]]:
    """
    Calculate settlement bill for given amount.
    
    Args:
        amount_text: Amount as text (number or math expression)
        
    Returns:
        Tuple of (settlement_data: dict or None, error_message: str or None)
        
    Settlement data structure:
        {
            'amount': float,
            'base_price': float,
            'admin_markup': float,
            'final_price': float,
            'total_cny': float,
            'price_error': str or None
        }
    """
    try:
        # Parse amount
        amount = parse_amount(amount_text)
        
        if amount <= 0:
            return None, "金额必须大于 0"
        
        # Get price with markup
        final_price, price_error, base_price = get_price_with_markup()
        
        if final_price is None:
            return None, f"无法获取价格: {price_error or '未知错误'}"
        
        # Import here to avoid circular import
        from database import db
        admin_markup = db.get_admin_markup()
        
        # Calculate total
        total_cny = final_price * amount
        
        settlement_data = {
            'amount': amount,
            'base_price': base_price,
            'admin_markup': admin_markup,
            'final_price': final_price,
            'total_cny': total_cny,
            'price_error': price_error
        }
        
        return settlement_data, None
        
    except ValueError as e:
        return None, f"金额格式错误: {str(e)}"
    except Exception as e:
        logger.error(f"Error calculating settlement: {e}", exc_info=True)
        return None, f"计算错误: {str(e)}"


def format_settlement_bill(settlement_data: dict, usdt_address: str = None) -> str:
    """
    Format settlement bill as HTML message (receipt style).
    
    Args:
        settlement_data: Settlement data dictionary
        usdt_address: Optional USDT address to display
        
    Returns:
        Formatted HTML message
    """
    amount = settlement_data['amount']
    base_price = settlement_data['base_price']
    admin_markup = settlement_data['admin_markup']
    final_price = settlement_data['final_price']
    total_cny = settlement_data['total_cny']
    price_error = settlement_data.get('price_error')
    
    # Build receipt-style HTML message
    message = "🧾 <b>交易结算单</b>\n"
    message += "────────────────────────\n\n"
    
    # Amount
    message += f"💰 数量: <code>{amount:,.2f} U</code>\n"
    
    # Exchange rate breakdown
    if admin_markup != 0:
        markup_sign = "+" if admin_markup > 0 else ""
        rate_breakdown = f"{final_price:.4f} (OKX: {base_price:.4f} {markup_sign}{admin_markup:.4f})"
    else:
        rate_breakdown = f"{final_price:.4f} (OKX: {base_price:.4f})"
    
    message += f"📊 汇率: {rate_breakdown}\n"
    
    # Total amount
    message += f"🇨🇳 应付: <b>{total_cny:,.2f} CNY</b>\n"
    
    message += "────────────────────────\n"
    
    # USDT address if provided
    if usdt_address:
        message += f"🔗 地址: <code>{usdt_address}</code>\n"
    
    # Price error warning
    if price_error:
        message += f"\n⚠️ <i>{price_error}</i>"
    
    return message

