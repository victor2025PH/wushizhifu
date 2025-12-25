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
from utils.text_utils import escape_markdown_v2

router = Router()
logger = logging.getLogger(__name__)

# Store calculator state
_calc_states = {}


@router.callback_query(F.data == "calculator")
async def callback_calculator(callback: CallbackQuery):
    """Handle calculator menu"""
    try:
        text = (
            "*🧮 伍拾支付計算器*\n\n"
            "請選擇計算類型："
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_calculator_type_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_calculator: {e}", exc_info=True)
        await callback.answer("❌ 系統錯誤，請稍後再試", show_alert=True)


@router.callback_query(F.data == "calc_fee")
async def callback_calc_fee(callback: CallbackQuery):
    """Handle fee calculator"""
    try:
        _calc_states[callback.from_user.id] = {"type": "fee"}
        
        text = (
            "*💰 費率計算器*\n\n"
            "請選擇支付通道："
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_calculator_channel_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_calc_fee: {e}", exc_info=True)
        await callback.answer("❌ 系統錯誤，請稍後再試", show_alert=True)


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
            f"*💰 費率計算器*\n\n"
            f"通道：{channel_text}\n\n"
            "請輸入交易金額：\n"
            "格式：數字（如：1000\\.50）\n"
            "最小金額：¥1\n"
            "最大金額：¥500,000"
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=None
        )
        
        await callback.answer(f"請輸入金額")
        
    except Exception as e:
        logger.error(f"Error in callback_calc_channel: {e}", exc_info=True)
        await callback.answer("❌ 系統錯誤，請稍後再試", show_alert=True)


@router.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def handle_calculator_amount(message: Message):
    """Handle amount input for calculator"""
    try:
        user_id = message.from_user.id
        
        if user_id not in _calc_states or _calc_states[user_id].get("type") != "fee":
            return  # Not in calculator mode
        
        try:
            amount = float(message.text)
            
            if amount < 1 or amount > 500000:
                await message.answer("❌ 金額超出範圍（¥1 - ¥500,000）")
                return
            
            state = _calc_states[user_id]
            channel = state.get("channel", "alipay")
            
            # Get user VIP level
            user = UserRepository.get_user(user_id)
            vip_level = user.get('vip_level', 0) if user else 0
            
            # Calculate
            calc_result = CalculatorService.calculate_fee(amount, channel, vip_level)
            
            channel_text = "支付寶" if channel == "alipay" else "微信"
            
            text = (
                f"*📊 計算結果*\n\n"
                f"交易金額：¥{amount:,.2f}\n"
                f"支付通道：{channel_text}\n"
                f"VIP 等級：{vip_level}\n"
                f"費率：{calc_result['rate_percentage']:.2f}%\n\n"
                f"手續費：¥{calc_result['fee']:,.2f}\n"
                f"實際到賬：¥{calc_result['actual_amount']:,.2f}"
            )
            
            await message.answer(
                text=text,
                parse_mode="MarkdownV2",
                reply_markup=get_calculator_result_keyboard()
            )
            
            # Clear state
            _calc_states.pop(user_id, None)
            
        except ValueError:
            await message.answer("❌ 請輸入有效的數字")
            
    except Exception as e:
        logger.error(f"Error in handle_calculator_amount: {e}", exc_info=True)
        await message.answer("❌ 計算錯誤，請稍後再試")


@router.callback_query(F.data == "calc_exchange")
async def callback_calc_exchange(callback: CallbackQuery):
    """Handle exchange rate calculator"""
    try:
        _calc_states[callback.from_user.id] = {"type": "exchange"}
        
        text = (
            "*💱 匯率轉換器*\n\n"
            "從：USDT → 到：CNY\n\n"
            "當前匯率：1 USDT = 7\\.42 CNY\n"
            "（實時更新）\n\n"
            "請輸入 USDT 金額："
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=None
        )
        
        await callback.answer("請輸入 USDT 金額")
        
    except Exception as e:
        logger.error(f"Error in callback_calc_exchange: {e}", exc_info=True)
        await callback.answer("❌ 系統錯誤，請稍後再試", show_alert=True)

