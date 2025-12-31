"""
Calculator-related handlers
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from keyboards.calculator_kb import (
    get_calculator_type_keyboard, get_calculator_channel_keyboard,
    get_calculator_result_keyboard
)
from keyboards.main_kb import get_main_keyboard
from services.calculator_service import CalculatorService
from database.user_repository import UserRepository
from utils.text_utils import escape_markdown_v2, format_amount_markdown, format_percentage_markdown, format_number_markdown

router = Router()
logger = logging.getLogger(__name__)

# Store calculator state
_calc_states = {}


@router.callback_query(F.data == "calculator")
async def callback_calculator(callback: CallbackQuery):
    """Handle calculator menu"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        text = (
            "*🧮 伍拾支付计算器*\n\n"
            "请选择计算类型："
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_calculator_type_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_calculator: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "calc_fee")
async def callback_calc_fee(callback: CallbackQuery):
    """Handle fee calculator"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        _calc_states[callback.from_user.id] = {"type": "fee"}
        
        text = (
            "*💰 费率计算器*\n\n"
            "请选择支付通道："
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_calculator_channel_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_calc_fee: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("calc_channel_"))
async def callback_calc_channel(callback: CallbackQuery):
    """Handle calculator channel selection"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        channel = callback.data.split("_")[-1]
        user_id = callback.from_user.id
        
        if user_id not in _calc_states:
            _calc_states[user_id] = {}
        
        _calc_states[user_id]["channel"] = channel
        
        channel_text = "支付寶" if channel == "alipay" else "微信"
        
        text = (
            f"*💰 费率计算器*\n\n"
            f"通道：{channel_text}\n\n"
            "请输入交易金额：\n"
            "格式：數字（如：1000\\.50）\n"
            "最小金额：¥1\n"
            "最大金额：¥500,000"
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=None
        )
        
        await callback.answer(f"请输入金额")
        
    except Exception as e:
        logger.error(f"Error in callback_calc_channel: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)




@router.callback_query(F.data == "calc_exchange")
async def callback_calc_exchange(callback: CallbackQuery):
    """Handle exchange rate calculator - show P2P merchant leaderboard"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        user_id = callback.from_user.id
        _calc_states[user_id] = {"type": "exchange", "awaiting_amount": True}
        
        # Show P2P leaderboard with default payment method (alipay)
        # Use shared P2P service from root services directory
        import sys
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(root_dir))
        from services.p2p_leaderboard_service import get_p2p_leaderboard, format_p2p_leaderboard_html, PAYMENT_METHOD_LABELS
        
        # Send loading message
        loading_msg = await callback.message.edit_text("⏳ 正在获取实时币价行情...")
        
        # Get P2P leaderboard - fetch multiple pages for better coverage
        payment_method = "alipay"
        all_merchants = []
        for api_page in range(1, 3):  # Fetch up to 2 API pages (20 merchants)
            leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=10, page=api_page)
            if leaderboard_data and leaderboard_data.get('merchants'):
                all_merchants.extend(leaderboard_data['merchants'])
            else:
                break
        
        if not all_merchants:
            await loading_msg.edit_text("❌ 获取币价行情失败，请稍后重试。")
            await callback.answer("获取失败", show_alert=True)
            return
        
        # Calculate total pages
        per_page = 5
        total_pages = (len(all_merchants) + per_page - 1) // per_page
        
        # Recreate leaderboard_data structure
        from datetime import datetime
        from services.p2p_leaderboard_service import PAYMENT_METHOD_LABELS
        
        payment_label = PAYMENT_METHOD_LABELS.get(payment_method.lower(), "支付宝")
        
        # Calculate market stats
        if all_merchants:
            prices = [m['price'] for m in all_merchants]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            total_trades = sum(m['trade_count'] for m in all_merchants)
        else:
            min_price = max_price = avg_price = 0
            total_trades = 0
        
        leaderboard_data = {
            'merchants': all_merchants,
            'payment_method': payment_method,
            'payment_label': payment_label,
            'total': len(all_merchants),
            'timestamp': datetime.now(),
            'market_stats': {
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': avg_price,
                'total_trades': total_trades,
                'merchant_count': len(all_merchants)
            }
        }
        
        # Format message
        message = format_p2p_leaderboard_html(leaderboard_data, page=1, per_page=per_page, total_pages=total_pages)
        
        # Get keyboard with payment method selection and pagination
        from keyboards.calculator_kb import get_p2p_exchange_keyboard
        keyboard = get_p2p_exchange_keyboard(payment_method, page=1, total_pages=total_pages)
        
        # Update message
        await loading_msg.edit_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        # Store current leaderboard data in state for calculation
        _calc_states[user_id]["leaderboard_data"] = leaderboard_data
        _calc_states[user_id]["payment_method"] = payment_method
        _calc_states[user_id]["page"] = 1
        
        await callback.answer("已显示实时币价行情")
        
    except Exception as e:
        logger.error(f"Error in callback_calc_exchange: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("p2p_exchange_"))
async def callback_p2p_exchange(callback: CallbackQuery):
    """Handle P2P exchange rate leaderboard pagination and payment method switch"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    try:
        query = callback.data
        await callback.answer("⏳ 正在加载...")
        
        # Parse callback data: p2p_exchange_{payment_method}_{page}
        parts = query.split('_')
        if len(parts) >= 4:
            payment_method_code = parts[2]  # bank, ali, wx
            page = int(parts[3]) if parts[3].isdigit() else 1
        else:
            payment_method_code = "ali"
            page = 1
        
        # Map payment method code
        payment_method_map = {
            "bank": "bank",
            "ali": "alipay",
            "wx": "wechat"
        }
        payment_method = payment_method_map.get(payment_method_code, "alipay")
        
        user_id = callback.from_user.id
        
        # Get P2P leaderboard - use shared service
        import sys
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(root_dir))
        from services.p2p_leaderboard_service import get_p2p_leaderboard, format_p2p_leaderboard_html, PAYMENT_METHOD_LABELS
        
        # Send loading
        await callback.answer("⏳ 正在获取最新汇率...")
        
        # Get leaderboard (fetch multiple pages if needed)
        per_page = 5
        all_merchants = []
        for api_page in range(1, 3):  # Fetch up to 2 API pages (20 merchants)
            leaderboard_data = get_p2p_leaderboard(payment_method=payment_method, rows=10, page=api_page)
            if leaderboard_data and leaderboard_data.get('merchants'):
                all_merchants.extend(leaderboard_data['merchants'])
            else:
                break
        
        if not all_merchants:
            await callback.message.edit_text("❌ 获取币价行情失败，请稍后重试。")
            return
        
        # Calculate total pages
        total_pages = (len(all_merchants) + per_page - 1) // per_page
        current_page = min(page, total_pages) if total_pages > 0 else 1
        
        # Recreate leaderboard_data structure
        from datetime import datetime
        
        payment_label = PAYMENT_METHOD_LABELS.get(payment_method.lower(), "支付宝")
        
        # Calculate market stats
        if all_merchants:
            prices = [m['price'] for m in all_merchants]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            total_trades = sum(m['trade_count'] for m in all_merchants)
        else:
            min_price = max_price = avg_price = 0
            total_trades = 0
        
        leaderboard_data = {
            'merchants': all_merchants,
            'payment_method': payment_method,
            'payment_label': payment_label,
            'total': len(all_merchants),
            'timestamp': datetime.now(),
            'market_stats': {
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': avg_price,
                'total_trades': total_trades,
                'merchant_count': len(all_merchants)
            }
        }
        
        # Format message
        message = format_p2p_leaderboard_html(leaderboard_data, page=current_page, per_page=per_page, total_pages=total_pages)
        
        # Get keyboard
        from keyboards.calculator_kb import get_p2p_exchange_keyboard
        keyboard = get_p2p_exchange_keyboard(payment_method, current_page, total_pages)
        
        # Update message
        await callback.message.edit_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        # Update state
        if user_id not in _calc_states:
            _calc_states[user_id] = {}
        _calc_states[user_id]["type"] = "exchange"
        _calc_states[user_id]["awaiting_amount"] = True
        _calc_states[user_id]["leaderboard_data"] = leaderboard_data
        _calc_states[user_id]["payment_method"] = payment_method
        _calc_states[user_id]["page"] = current_page
        
        await callback.answer("✅ 已更新")
        
    except Exception as e:
        logger.error(f"Error in callback_p2p_exchange: {e}", exc_info=True)
        await callback.answer("❌ 操作失败，请重试", show_alert=True)


@router.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def handle_calculator_amount(message: Message):
    """Handle amount input for calculator (both fee and exchange)"""
    # Skip if message is from a group (Bot A should be silent in groups)
    if message.chat.type in ['group', 'supergroup']:
        return
    
    try:
        user_id = message.from_user.id
        
        # Check if user is in calculator mode
        if user_id not in _calc_states:
            return  # Not in calculator mode
        
        state = _calc_states[user_id]
        calc_type = state.get("type")
        
        # For exchange calculator, check if awaiting amount
        if calc_type == "exchange" and not state.get("awaiting_amount", False):
            return  # Not in exchange calculation mode
        
        try:
            amount = float(message.text)
            
            # Fee calculator
            if calc_type == "fee":
                if amount < 1 or amount > 500000:
                    await message.answer("❌ 金额超出範圍（¥1 - ¥500,000）")
                    return
                
                channel = state.get("channel", "alipay")
                
                # Get user VIP level
                user = UserRepository.get_user(user_id)
                vip_level = user.get('vip_level', 0) if user else 0
                
                # Calculate
                calc_result = CalculatorService.calculate_fee(amount, channel, vip_level)
                
                channel_text = "支付宝" if channel == "alipay" else "微信"
                amount_str = format_amount_markdown(amount)
                rate_str = format_percentage_markdown(calc_result['rate_percentage'])
                fee_str = format_amount_markdown(calc_result['fee'])
                actual_str = format_amount_markdown(calc_result['actual_amount'])
                vip_level_str = format_number_markdown(vip_level)
                
                text = (
                    f"*📊 计算结果*\n\n"
                    f"交易金额：{amount_str}\n"
                    f"支付通道：{channel_text}\n"
                    f"VIP 等级：{vip_level_str}\n"
                    f"费率：{rate_str}\n\n"
                    f"手续费：{fee_str}\n"
                    f"实际到账：{actual_str}"
                )
                
                await message.answer(
                    text=text,
                    parse_mode="MarkdownV2",
                    reply_markup=get_calculator_result_keyboard()
                )
                
                # Clear state
                _calc_states.pop(user_id, None)
            
            # Exchange calculator - use P2P rate from leaderboard
            elif calc_type == "exchange":
                # Get leaderboard data and calculate using average price
                leaderboard_data = state.get("leaderboard_data")
                
                if leaderboard_data and leaderboard_data.get('merchants'):
                    # Use average price from market stats
                    market_stats = leaderboard_data.get('market_stats', {})
                    exchange_rate = market_stats.get('avg_price', 7.25)
                    payment_label = leaderboard_data.get('payment_label', '支付宝')
                    
                    # Calculate: input is CNY, calculate USDT
                    usdt_amount = amount / exchange_rate
                    
                    amount_str = format_amount_markdown(amount) + " CNY"
                    rate_str = escape_markdown_v2(f"1 USDT = {exchange_rate:.2f} CNY")
                    converted_str = format_number_markdown(usdt_amount, 4) + " USDT"
                    
                    text = (
                        f"*💱 汇率转换结果*\n\n"
                        f"输入金额：{amount_str}\n"
                        f"支付渠道：{payment_label}\n"
                        f"参考汇率：{rate_str}\n"
                        f"（基于币安 P2P 市场均价）\n\n"
                        f"*应结算：{converted_str}*"
                    )
                else:
                    # Fallback to default rate if no leaderboard data
                    exchange_rate = 7.25
                    usdt_amount = amount / exchange_rate
                    
                    amount_str = format_amount_markdown(amount) + " CNY"
                    rate_str = escape_markdown_v2(f"1 USDT = {exchange_rate:.2f} CNY")
                    converted_str = format_number_markdown(usdt_amount, 4) + " USDT"
                    
                    text = (
                        f"*💱 汇率转换结果*\n\n"
                        f"输入金额：{amount_str}\n"
                        f"汇率：{rate_str}\n\n"
                        f"*应结算：{converted_str}*"
                    )
                
                await message.answer(
                    text=text,
                    parse_mode="MarkdownV2",
                    reply_markup=get_calculator_result_keyboard()
                )
                
                # Clear state
                _calc_states.pop(user_id, None)
                
        except ValueError:
            await message.answer("❌ 请输入有效的數字")
            
    except Exception as e:
        logger.error(f"Error in handle_calculator_amount: {e}", exc_info=True)
        await message.answer("❌ 计算錯誤，请稍後再試")

