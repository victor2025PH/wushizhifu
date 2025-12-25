"""
Transaction record handlers
"""
import logging
from typing import Optional
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.transaction_kb import (
    get_transaction_filter_keyboard, get_transaction_list_keyboard,
    get_transaction_detail_keyboard
)
from keyboards.main_kb import get_main_keyboard
from services.transaction_service import TransactionService
from utils.text_utils import escape_markdown_v2

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "transactions")
async def callback_transactions(callback: CallbackQuery):
    """Handle transaction records menu"""
    try:
        user_id = callback.from_user.id
        
        # Get recent transactions
        transactions = TransactionService.get_user_transactions(user_id, limit=10)
        
        if not transactions:
            text = (
                "*📜 交易記錄*\n\n"
                "暫無交易記錄\n\n"
                "開始您的第一筆交易吧！"
            )
            keyboard = get_main_keyboard()
        else:
            text = f"*📜 交易記錄*\n\n*最近 {len(transactions)} 筆交易：*\n\n"
            
            for trans in transactions[:5]:  # Show first 5
                status_icon = "✅" if trans['status'] == 'paid' else "⏳" if trans['status'] == 'pending' else "❌"
                type_text = "收款" if trans['transaction_type'] == 'receive' else "付款"
                channel_text = "支付寶" if trans['payment_channel'] == 'alipay' else "微信"
                
                created_at = trans['created_at']
                text += (
                    f"{status_icon} {type_text} ¥{trans['amount']:,.2f} \\| "
                    f"{channel_text} \\| {created_at}\n"
                    f"  訂單號：`{trans['order_id']}`\n\n"
                )
            
            if len(transactions) > 5:
                text += f"\n還有 {len(transactions) - 5} 筆交易..."
            
            text += "\n[查看全部記錄] [篩選查詢]"
            
            keyboard = get_transaction_filter_keyboard()
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_transactions: {e}", exc_info=True)
        await callback.answer("❌ 獲取交易記錄失敗，請稍後再試", show_alert=True)


@router.callback_query(F.data.startswith("filter_"))
async def callback_filter_transactions(callback: CallbackQuery):
    """Handle transaction filtering"""
    try:
        filter_type = callback.data.split("_")[1]
        user_id = callback.from_user.id
        
        transaction_type = None
        channel = None
        
        if filter_type == "receive":
            transaction_type = "receive"
        elif filter_type == "pay":
            transaction_type = "pay"
        elif filter_type == "alipay":
            channel = "alipay"
        elif filter_type == "wechat":
            channel = "wechat"
        elif filter_type == "all":
            pass  # No filter
        # TODO: Implement date filters (today, week, month)
        
        transactions = TransactionService.get_user_transactions(
            user_id, limit=20, transaction_type=transaction_type
        )
        
        if channel:
            transactions = [t for t in transactions if t['payment_channel'] == channel]
        
        if not transactions:
            text = "*📜 交易記錄*\n\n暫無符合條件的交易記錄"
        else:
            text = f"*📜 交易記錄*\n\n*找到 {len(transactions)} 筆交易：*\n\n"
            
            for trans in transactions[:10]:
                status_icon = "✅" if trans['status'] == 'paid' else "⏳" if trans['status'] == 'pending' else "❌"
                type_text = "收款" if trans['transaction_type'] == 'receive' else "付款"
                channel_text = "支付寶" if trans['payment_channel'] == 'alipay' else "微信"
                
                text += (
                    f"{status_icon} {type_text} ¥{trans['amount']:,.2f} \\| "
                    f"{channel_text} \\| {trans['created_at']}\n"
                    f"  `{trans['order_id']}`\n\n"
                )
            
            if len(transactions) > 10:
                text += f"\n還有 {len(transactions) - 10} 筆..."
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_transaction_list_keyboard(0, len(transactions) > 10)
        )
        
        await callback.answer(f"已篩選：{filter_type}")
        
    except Exception as e:
        logger.error(f"Error in callback_filter_transactions: {e}", exc_info=True)
        await callback.answer("❌ 篩選失敗，請稍後再試", show_alert=True)


@router.callback_query(F.data.startswith("order_detail_"))
async def callback_order_detail(callback: CallbackQuery):
    """Handle order detail view"""
    try:
        order_id = callback.data.split("_", 2)[2]
        
        transaction = TransactionService.get_transaction(order_id)
        
        if not transaction:
            await callback.answer("❌ 訂單不存在", show_alert=True)
            return
        
        if transaction['user_id'] != callback.from_user.id:
            await callback.answer("❌ 無權限查看此訂單", show_alert=True)
            return
        
        status_map = {
            'pending': '⏳ 待支付',
            'paid': '✅ 支付成功',
            'failed': '❌ 支付失敗',
            'refunded': '↩️ 已退款',
            'cancelled': '🚫 已取消'
        }
        
        type_map = {
            'receive': '收款',
            'pay': '付款',
            'refund': '退款'
        }
        
        channel_map = {
            'alipay': '支付寶',
            'wechat': '微信'
        }
        
        text = (
            f"*📋 訂單詳情*\n\n"
            f"訂單號：`{transaction['order_id']}`\n"
            f"狀態：{status_map.get(transaction['status'], transaction['status'])}\n"
            f"類型：{type_map.get(transaction['transaction_type'], transaction['transaction_type'])}\n"
            f"通道：{channel_map.get(transaction['payment_channel'], transaction['payment_channel'])}\n"
            f"金額：¥{transaction['amount']:,.2f}\n"
            f"手續費：¥{transaction['fee']:,.2f}\n"
            f"實際{'到賬' if transaction['transaction_type'] == 'receive' else '支付'}：¥{transaction['actual_amount']:,.2f}\n"
            f"創建時間：{transaction['created_at']}\n"
        )
        
        if transaction.get('paid_at'):
            text += f"支付時間：{transaction['paid_at']}\n"
        
        if transaction.get('description'):
            text += f"\n備註：{transaction['description']}"
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_transaction_detail_keyboard(order_id)
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_order_detail: {e}", exc_info=True)
        await callback.answer("❌ 獲取訂單詳情失敗，請稍後再試", show_alert=True)

