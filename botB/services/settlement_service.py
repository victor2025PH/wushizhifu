"""
Settlement calculation service
Handles OTC settlement calculations with Binance P2P price (CoinGecko fallback) and admin markup
"""
import logging
from typing import Tuple, Optional
from services.price_service import get_price_with_markup
from services.math_service import parse_amount, is_number, is_simple_math, is_batch_amounts, parse_batch_amounts
from typing import List

logger = logging.getLogger(__name__)


def get_settlement_address(group_id: Optional[int] = None, strategy: str = 'default') -> Optional[str]:
    """
    Get USDT address for settlement using address management.
    
    Args:
        group_id: Optional group ID
        strategy: Address selection strategy ('default', 'round_robin', 'random')
        
    Returns:
        USDT address string or None
    """
    from database import db
    
    # Try to get from address management first
    address_obj = db.get_active_address(group_id=group_id, strategy=strategy)
    if address_obj:
        # Increment usage
        db.increment_address_usage(address_obj['id'])
        return address_obj['address']
    
    # Fallback to legacy single address (group or global)
    if group_id:
        group_setting = db.get_group_setting(group_id)
        if group_setting and group_setting.get('usdt_address'):
            return group_setting['usdt_address']
    
    return db.get_usdt_address()


def calculate_settlement(amount_text: str, group_id: Optional[int] = None) -> Tuple[Optional[dict], Optional[str]]:
    """
    Calculate settlement bill for given CNY amount.
    
    The input represents CNY (Chinese Yuan), and the function calculates
    how much USDT should be settled based on the current USDT/CNY rate + markup.
    
    Args:
        amount_text: CNY amount as text (number or math expression, e.g., "20000-200")
        group_id: Optional Telegram group ID for group-specific markup
        
    Returns:
        Tuple of (settlement_data: dict or None, error_message: str or None)
        
    Settlement data structure:
        {
            'cny_amount': float,      # Input CNY amount (after calculation)
            'base_price': float,       # Base USDT/CNY price from Binance P2P
            'markup': float,          # Markup applied (group-specific or global)
            'final_price': float,      # Final USDT/CNY price (base + markup)
            'usdt_amount': float,      # Calculated USDT amount to settle
            'price_error': str or None,
            'group_id': int or None    # Group ID if group-specific
        }
        
    Calculation formula:
        usdt_amount = cny_amount / final_price
        where final_price = base_price + markup
    """
    try:
        # Parse CNY amount (input is in CNY)
        cny_amount = parse_amount(amount_text)
        
        if cny_amount <= 0:
            return None, "金额必须大于 0"
        
        # Get price with markup (USDT/CNY rate) - supports group-specific markup
        final_price, price_error, base_price, markup = get_price_with_markup(group_id)
        
        if final_price is None:
            return None, f"无法获取价格: {price_error or '未知错误'}"
        
        if final_price <= 0:
            return None, "汇率无效，无法计算"
        
        # Calculate USDT amount: CNY / (USDT/CNY rate)
        # Example: 19800 CNY / 7.25 (USDT/CNY) = 2731.03 USDT
        usdt_amount = cny_amount / final_price
        
        settlement_data = {
            'cny_amount': cny_amount,      # Input CNY amount
            'base_price': base_price,      # Base USDT/CNY price
            'markup': markup,              # Markup applied (group or global)
            'final_price': final_price,    # Final USDT/CNY price (base + markup)
            'usdt_amount': usdt_amount,    # Calculated USDT amount
            'price_error': price_error,
            'group_id': group_id           # Group ID if applicable
        }
        
        return settlement_data, None
        
    except ValueError as e:
        return None, f"金额格式错误: {str(e)}"
    except ZeroDivisionError:
        return None, "汇率不能为零"
    except Exception as e:
        logger.error(f"Error calculating settlement: {e}", exc_info=True)
        return None, f"计算错误: {str(e)}"


def format_settlement_bill(settlement_data: dict, usdt_address: str = None, transaction_id: str = None, 
                          transaction_status: str = None, payment_hash: str = None, 
                          paid_at: str = None, confirmed_at: str = None) -> str:
    """
    Format settlement bill as HTML message (receipt style).
    
    Shows: CNY amount (input) -> USDT amount (calculated based on rate).
    
    Args:
        settlement_data: Settlement data dictionary
        usdt_address: Optional USDT address to display
        transaction_id: Optional transaction ID to display
        transaction_status: Optional transaction status (pending, paid, confirmed, cancelled)
        payment_hash: Optional payment hash (TXID)
        paid_at: Optional payment time
        confirmed_at: Optional confirmation time
        
    Returns:
        Formatted HTML message
    """
    cny_amount = settlement_data['cny_amount']       # Input: CNY amount
    base_price = settlement_data['base_price']       # Base USDT/CNY price
    markup = settlement_data.get('markup', settlement_data.get('admin_markup', 0.0))  # Support both keys
    final_price = settlement_data['final_price']     # Final USDT/CNY price
    usdt_amount = settlement_data['usdt_amount']     # Output: USDT amount
    price_error = settlement_data.get('price_error')
    
    # Status emoji mapping
    status_map = {
        'pending': '⏳ 待支付',
        'paid': '✅ 已支付（待确认）',
        'confirmed': '✅ 已确认',
        'cancelled': '❌ 已取消'
    }
    status_text = status_map.get(transaction_status, '⏳ 待支付') if transaction_status else '⏳ 待支付'
    
    # Build receipt-style HTML message
    message = "🧾 <b>交易结算单</b>\n"
    if transaction_id:
        message += f"<code>#{transaction_id}</code>\n"
    message += "────────────────────────\n\n"
    
    # Transaction status
    message += f"📊 状态: <b>{status_text}</b>\n\n"
    
    # Input: CNY amount
    message += f"💰 应收人民币: <b><code>{cny_amount:,.2f} CNY</code></b>\n\n"
    
    # Exchange rate breakdown
    if markup != 0:
        markup_sign = "+" if markup > 0 else ""
        rate_breakdown = f"{final_price:.4f} (Binance P2P: {base_price:.4f} {markup_sign}{markup:.4f})"
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
    
    # Payment information
    if payment_hash:
        hash_display = payment_hash
        if len(hash_display) > 30:
            hash_display = f"{hash_display[:15]}...{hash_display[-15:]}"
        message += f"🔐 支付哈希: <code>{hash_display}</code>\n"
    
    if paid_at:
        message += f"💰 支付时间: {paid_at}\n"
    
    if confirmed_at:
        message += f"✅ 确认时间: {confirmed_at}\n"
    
    # Price error warning
    if price_error:
        message += f"\n⚠️ <i>{price_error}</i>"
    
    return message


def calculate_batch_settlement(amounts_text: str, group_id: Optional[int] = None) -> Tuple[Optional[List[dict]], Optional[str]]:
    """
    Calculate batch settlement bills for multiple CNY amounts.
    
    Args:
        amounts_text: Multiple amounts separated by comma or newline (e.g., "1000,2000,3000")
        group_id: Optional Telegram group ID for group-specific markup
        
    Returns:
        Tuple of (settlements_list: list of dict or None, error_message: str or None)
        
    Each settlement dict has the same structure as calculate_settlement
    """
    try:
        # Parse multiple amounts
        amounts = parse_batch_amounts(amounts_text)
        
        if not amounts:
            return None, "未找到有效的金额"
        
        if len(amounts) > 20:  # Limit to 20 amounts per batch
            return None, "批量结算最多支持 20 笔金额"
        
        # Get price once for all calculations (same rate for batch)
        final_price, price_error, base_price, markup = get_price_with_markup(group_id)
        
        if final_price is None:
            return None, f"无法获取价格: {price_error or '未知错误'}"
        
        if final_price <= 0:
            return None, "汇率无效，无法计算"
        
        # Calculate settlement for each amount
        settlements = []
        for cny_amount in amounts:
            usdt_amount = cny_amount / final_price
            
            settlement_data = {
                'cny_amount': cny_amount,
                'base_price': base_price,
                'markup': markup,
                'final_price': final_price,
                'usdt_amount': usdt_amount,
                'price_error': price_error,
                'group_id': group_id
            }
            settlements.append(settlement_data)
        
        return settlements, None
        
    except ValueError as e:
        return None, f"金额格式错误: {str(e)}"
    except Exception as e:
        logger.error(f"Error calculating batch settlement: {e}", exc_info=True)
        return None, f"计算错误: {str(e)}"


def format_batch_settlement_bills(settlements: List[dict], usdt_address: str = None) -> str:
    """
    Format batch settlement bills as HTML message.
    
    Args:
        settlements: List of settlement data dictionaries
        usdt_address: Optional USDT address to display
        
    Returns:
        Formatted HTML message
    """
    if not settlements:
        return "❌ 无结算数据"
    
    final_price = settlements[0]['final_price']
    base_price = settlements[0]['base_price']
    markup = settlements[0]['markup']
    price_error = settlements[0].get('price_error')
    
    # Calculate totals
    total_cny = sum(s['cny_amount'] for s in settlements)
    total_usdt = sum(s['usdt_amount'] for s in settlements)
    
    # Build message
    message = f"🧾 <b>批量结算单</b>\n"
    message += f"共 {len(settlements)} 笔交易\n"
    message += "────────────────────────\n\n"
    
    # Rate info
    if markup != 0:
        markup_sign = "+" if markup > 0 else ""
        rate_breakdown = f"{final_price:.4f} (Binance P2P: {base_price:.4f} {markup_sign}{markup:.4f})"
    else:
        rate_breakdown = f"{final_price:.4f} (Binance P2P: {base_price:.4f})"
    
    message += f"📊 汇率 (USDT/CNY): {rate_breakdown}\n\n"
    
    # Individual bills
    message += "<b>📋 明细:</b>\n"
    for idx, settlement in enumerate(settlements, 1):
        message += f"{idx}. {settlement['cny_amount']:,.2f} CNY → {settlement['usdt_amount']:,.2f} USDT\n"
    
    message += "\n────────────────────────\n"
    message += f"<b>💰 合计人民币: {total_cny:,.2f} CNY</b>\n"
    message += f"<b>💵 合计 USDT: {total_usdt:,.2f} U</b>\n"
    message += "────────────────────────\n"
    
    # USDT address
    if usdt_address:
        address_display = usdt_address
        if len(usdt_address) > 30:
            address_display = f"{usdt_address[:15]}...{usdt_address[-15:]}"
        message += f"🔗 收款地址: <code>{address_display}</code>\n"
    
    # Price error warning
    if price_error:
        message += f"\n⚠️ <i>{price_error}</i>"
    
    return message

