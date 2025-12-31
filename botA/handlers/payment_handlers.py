"""
Payment-related handlers
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from keyboards.payment_kb import (
    get_payment_type_keyboard, get_amount_quick_keyboard,
    get_confirm_order_keyboard, get_order_detail_keyboard
)
from keyboards.main_kb import get_main_keyboard
from services.transaction_service import TransactionService
from services.calculator_service import CalculatorService
from utils.text_utils import escape_markdown_v2, format_amount_markdown, format_percentage_markdown
from database.user_repository import UserRepository

router = Router()
logger = logging.getLogger(__name__)

# Store payment state (in production, use Redis or database)
_payment_states = {}


@router.callback_query(F.data == "pay_ali")
async def callback_pay_ali(callback: CallbackQuery):
    """Handle Alipay payment channel selection"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        await callback.answer("正在启动支付宝通道...", show_alert=False)
        
        text = (
            "*💳 支付宝通道*\n\n"
            "请选择支付类型："
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_payment_type_keyboard()
        )
        
        _payment_states[callback.from_user.id] = {"channel": "alipay"}
        
        logger.info(f"User {callback.from_user.id} selected Alipay payment channel")
        
    except Exception as e:
        logger.error(f"Error in callback_pay_ali: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "pay_wechat")
async def callback_pay_wechat(callback: CallbackQuery):
    """Handle WeChat payment channel selection"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        await callback.answer("正在啟動微信支付通道...", show_alert=False)
        
        text = (
            "*🍀 微信支付通道*\n\n"
            "请选择支付类型："
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_payment_type_keyboard()
        )
        
        _payment_states[callback.from_user.id] = {"channel": "wechat"}
        
        logger.info(f"User {callback.from_user.id} selected WeChat payment channel")
        
    except Exception as e:
        logger.error(f"Error in callback_pay_wechat: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data.in_(["payment_receive", "payment_pay"]))
async def callback_payment_type(callback: CallbackQuery):
    """Handle payment type selection"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        transaction_type = "receive" if callback.data == "payment_receive" else "pay"
        user_id = callback.from_user.id
        
        if user_id not in _payment_states:
            await callback.answer("❌ 请重新选择支付通道", show_alert=True)
            return
        
        _payment_states[user_id]["type"] = transaction_type
        
        type_text = "收款" if transaction_type == "receive" else "付款"
        channel = _payment_states[user_id].get("channel", "支付宝")
        
        text = (
            f"*{type_text}* \\(通道: {channel}\\)\n\n"
            "请输入金额：\n"
            "格式：数字（如：100\\.50）\n"
            "最小金额：¥1\n"
            "最大金额：¥500,000\n\n"
            "或选择快捷金额："
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_amount_quick_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_payment_type: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("amount_"))
async def callback_amount_quick(callback: CallbackQuery):
    """Handle quick amount selection"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        amount_str = callback.data.split("_")[1]
        amount = float(amount_str)
        
        user_id = callback.from_user.id
        if user_id not in _payment_states:
            await callback.answer("❌ 请重新选择支付通道", show_alert=True)
            return
        
        await process_amount(callback, amount)
        
    except Exception as e:
        logger.error(f"Error in callback_amount_quick: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


async def process_amount(callback: CallbackQuery, amount: float):
    """Process amount input and show order details"""
    user_id = callback.from_user.id
    state = _payment_states.get(user_id, {})
    
    channel = state.get("channel", "alipay")
    transaction_type = state.get("type", "receive")
    
    # Get user VIP level
    user = UserRepository.get_user(user_id)
    vip_level = user.get('vip_level', 0) if user else 0
    
    # Calculate fee
    calc_result = CalculatorService.calculate_fee(amount, channel, vip_level)
    
    # Store calculation result
    _payment_states[user_id]["amount"] = amount
    _payment_states[user_id]["calc_result"] = calc_result
    
    type_text = "收款" if transaction_type == "receive" else "付款"
    channel_text = "支付宝" if channel == "alipay" else "微信"
    amount_str = format_amount_markdown(amount)
    rate_str = format_percentage_markdown(calc_result['rate_percentage'])
    fee_str = format_amount_markdown(calc_result['fee'])
    actual_str = format_amount_markdown(calc_result['actual_amount'])
    action_text = escape_markdown_v2('到账' if transaction_type == 'receive' else '支付')
    
    text = (
        f"*📊 订单详情*\n\n"
        f"类型：{type_text}\n"
        f"通道：{channel_text}\n"
        f"交易金额：{amount_str}\n"
        f"费率：{rate_str}\n"
        f"手续费：{fee_str}\n"
        f"实际{action_text}：{actual_str}\n\n"
        "请确认是否创建订单："
    )
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=get_confirm_order_keyboard("preview")
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_order_"))
async def callback_confirm_order(callback: CallbackQuery):
    """Handle order confirmation"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        user_id = callback.from_user.id
        state = _payment_states.get(user_id, {})
        
        if not state.get("amount") or not state.get("calc_result"):
            await callback.answer("❌ 订单信息不完整，请重新操作", show_alert=True)
            return
        
        channel = state.get("channel", "alipay")
        transaction_type = state.get("type", "receive")
        amount = state["amount"]
        calc_result = state["calc_result"]
        
        # Create transaction
        transaction = TransactionService.create_transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            payment_channel=channel,
            amount=amount,
            description=f"{'收款' if transaction_type == 'receive' else '付款'}订单"
        )
        
        order_id = transaction["order_id"]
        
        # Clear state
        _payment_states.pop(user_id, None)
        
        type_text = "收款" if transaction_type == "receive" else "付款"
        channel_text = "支付宝" if channel == "alipay" else "微信"
        amount_str = format_amount_markdown(amount)
        fee_str = format_amount_markdown(calc_result['fee'])
        actual_str = format_amount_markdown(calc_result['actual_amount'])
        action_text = escape_markdown_v2('到账' if transaction_type == 'receive' else '支付')
        order_id_escaped = escape_markdown_v2(order_id)
        
        text = (
            f"*✅ 订单已创建*\n\n"
            f"订单号：`{order_id_escaped}`\n"
            f"类型：{type_text}\n"
            f"通道：{channel_text}\n"
            f"金额：{amount_str}\n"
            f"手续费：{fee_str}\n"
            f"实际{action_text}：{actual_str}\n"
            f"状态：待支付\n\n"
            "⚠️ 支付功能开发中，此为演示订单"
        )
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_order_detail_keyboard(order_id)
        )
        
        await callback.answer("订单创建成功")
        
        logger.info(f"User {user_id} created order {order_id}")
        
    except Exception as e:
        logger.error(f"Error in callback_confirm_order: {e}", exc_info=True)
        await callback.answer("❌ 创建订单失敗，请稍後再試", show_alert=True)

