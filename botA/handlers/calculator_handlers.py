"""
Calculator-related handlers
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from keyboards.calculator_kb import (
    get_calculator_type_keyboard, get_calculator_channel_keyboard,
    get_calculator_result_keyboard, get_exchange_direction_keyboard
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
    """Handle exchange rate calculator"""
    try:
        user_id = callback.from_user.id
        _calc_states[user_id] = {"type": "exchange"}
        
        # Get current exchange rate (default 7.42)
        exchange_rate = 7.42  # Can be fetched from database or API
        
        rate_str = escape_markdown_v2(f"1 USDT = {exchange_rate} CNY")
        text = (
            "*💱 汇率转换器*\n\n"
            f"当前汇率：{rate_str}\n"
            "（实时更新）\n\n"
            "请选择转换方向："
        )
        
        keyboard = get_exchange_direction_keyboard()
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer("请选择转换方向")
        
    except Exception as e:
        logger.error(f"Error in callback_calc_exchange: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("exchange_"))
async def callback_exchange_direction(callback: CallbackQuery):
    """Handle exchange direction selection"""
    try:
        direction = callback.data.replace("exchange_", "")
        user_id = callback.from_user.id
        
        if user_id not in _calc_states:
            _calc_states[user_id] = {}
        
        _calc_states[user_id]["exchange_direction"] = direction
        
        exchange_rate = 7.42  # Default rate
        rate_str = escape_markdown_v2(f"1 USDT = {exchange_rate} CNY")
        
        if direction == "usdt_cny":
            text = (
                f"*💱 汇率转换：USDT → CNY*\n\n"
                f"当前汇率：{rate_str}\n\n"
                "请输入 USDT 金额：\n"
                "格式：数字（如：100\\.5）"
            )
        else:  # cny_usdt
            cny_rate = 1/exchange_rate
            cny_rate_str = format_number_markdown(cny_rate, 4)
            text = (
                f"*💱 汇率转换：CNY → USDT*\n\n"
                f"当前汇率：{rate_str}\n"
                f"即：1 CNY = {cny_rate_str} USDT\n\n"
                "请输入 CNY 金额：\n"
                "格式：数字（如：1000\\.50）"
            )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=None
        )
        
        await callback.answer("请输入金额")
        
    except Exception as e:
        logger.error(f"Error in callback_exchange_direction: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def handle_calculator_amount(message: Message):
    """Handle amount input for calculator (both fee and exchange)"""
    try:
        user_id = message.from_user.id
        
        # Check if user is in calculator mode
        if user_id not in _calc_states:
            return  # Not in calculator mode
        
        state = _calc_states[user_id]
        calc_type = state.get("type")
        
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
            
            # Exchange calculator
            elif calc_type == "exchange":
                exchange_rate = 7.42  # Default rate
                direction = state.get("exchange_direction", "usdt_cny")
                
                if direction == "usdt_cny":
                    result = CalculatorService.convert_currency(amount, "USDT", "CNY", exchange_rate)
                    amount_str = format_number_markdown(amount, 2) + " USDT"
                    rate_str = escape_markdown_v2(f"1 USDT = {exchange_rate} CNY")
                    converted_str = format_amount_markdown(result['converted_amount']) + " CNY"
                    
                    text = (
                        f"*💱 转换结果*\n\n"
                        f"输入金额：{amount_str}\n"
                        f"汇率：{rate_str}\n\n"
                        f"转换金额：{converted_str}"
                    )
                else:  # cny_usdt
                    result = CalculatorService.convert_currency(amount, "CNY", "USDT", exchange_rate)
                    amount_str = format_amount_markdown(amount) + " CNY"
                    rate_str = escape_markdown_v2(f"1 USDT = {exchange_rate} CNY")
                    converted_str = format_number_markdown(result['converted_amount'], 4) + " USDT"
                    
                    text = (
                        f"*💱 转换结果*\n\n"
                        f"输入金额：{amount_str}\n"
                        f"汇率：{rate_str}\n\n"
                        f"转换金额：{converted_str}"
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

