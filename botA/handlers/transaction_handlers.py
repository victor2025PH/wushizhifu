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
from database.admin_repository import AdminRepository
from services.transaction_service import TransactionService
from utils.text_utils import escape_markdown_v2, format_amount_markdown, format_number_markdown

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
                "*📜 交易记录*\n\n"
                "暂无交易记录\n\n"
                "开始您的第一笔交易吧！"
            )
            is_admin = AdminRepository.is_admin(user_id)
            keyboard = get_main_keyboard(user_id=user_id, is_admin=is_admin)
        else:
            text = f"*📜 交易记录*\n\n*最近 {len(transactions)} 笔交易：*\n\n"
            
            for trans in transactions[:5]:  # Show first 5
                status_icon = "✅" if trans['status'] == 'paid' else "⏳" if trans['status'] == 'pending' else "❌"
                type_text = "收款" if trans['transaction_type'] == 'receive' else "付款"
                channel_text = "支付宝" if trans['payment_channel'] == 'alipay' else "微信"
                amount_str = format_amount_markdown(trans['amount'])
                order_id_escaped = escape_markdown_v2(trans['order_id'])
                created_at_escaped = escape_markdown_v2(str(trans['created_at']))
                
                text += (
                    f"{status_icon} {type_text} {amount_str} \\| "
                    f"{channel_text} \\| {created_at_escaped}\n"
                    f"  订单号：`{order_id_escaped}`\n\n"
                )
            
            if len(transactions) > 5:
                text += f"\n还有 {len(transactions) - 5} 笔交易..."
            
            text += "\n点击下方按钮筛选或查看全部记录"
            
            keyboard = get_transaction_filter_keyboard()
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_transactions: {e}", exc_info=True)
        await callback.answer("❌ 获取交易记录失败，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("filter_"))
async def callback_filter_transactions(callback: CallbackQuery):
    """Handle transaction filtering"""
    try:
        from datetime import datetime, timedelta
        from database.db import db
        
        filter_type = callback.data.split("_")[1]
        user_id = callback.from_user.id
        
        transaction_type = None
        channel = None
        date_filter = None
        
        # Date filters
        if filter_type == "today":
            date_filter = datetime.now().strftime("%Y-%m-%d")
        elif filter_type == "week":
            week_ago = datetime.now() - timedelta(days=7)
            date_filter = week_ago.strftime("%Y-%m-%d")
        elif filter_type == "month":
            month_ago = datetime.now() - timedelta(days=30)
            date_filter = month_ago.strftime("%Y-%m-%d")
        elif filter_type == "receive":
            transaction_type = "receive"
        elif filter_type == "pay":
            transaction_type = "pay"
        elif filter_type == "alipay":
            channel = "alipay"
        elif filter_type == "wechat":
            channel = "wechat"
        elif filter_type == "all":
            pass  # No filter
        
        # Build query with filters
        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [user_id]
        
        if date_filter:
            # SQLite date comparison
            query += " AND DATE(created_at) >= ?"
            params.append(date_filter)
        
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)
        
        if channel:
            query += " AND payment_channel = ?"
            params.append(channel)
        
        query += " ORDER BY created_at DESC LIMIT 20"
        
        cursor = db.execute(query, tuple(params))
        transactions = [dict(row) for row in cursor.fetchall()]
        
        if not transactions:
            text = "*📜 交易记录*\n\n暂无符合条件的交易记录"
        else:
            text = f"*📜 交易记录*\n\n*找到 {len(transactions)} 笔交易：*\n\n"
            
            for trans in transactions[:10]:
                status_icon = "✅" if trans['status'] == 'paid' else "⏳" if trans['status'] == 'pending' else "❌"
                type_text = "收款" if trans['transaction_type'] == 'receive' else "付款"
                channel_text = "支付宝" if trans['payment_channel'] == 'alipay' else "微信"
                
                created_at = trans['created_at'] if isinstance(trans['created_at'], str) else str(trans['created_at'])
                if len(created_at) > 10:
                    created_at = created_at[:16]
                
                amount_str = format_amount_markdown(trans['amount'])
                order_id_escaped = escape_markdown_v2(trans['order_id'])
                created_at_escaped = escape_markdown_v2(str(created_at))
                
                text += (
                    f"{status_icon} {type_text} {amount_str} \\| "
                    f"{channel_text} \\| {created_at_escaped}\n"
                    f"  订单号：`{order_id_escaped}`\n\n"
                )
            
            if len(transactions) > 10:
                text += f"\n还有 {len(transactions) - 10} 笔..."
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_transaction_list_keyboard(0, len(transactions) > 10)
        )
        
        filter_name_map = {
            "today": "今天",
            "week": "本周",
            "month": "本月",
            "receive": "收款",
            "pay": "付款",
            "alipay": "支付宝",
            "wechat": "微信",
            "all": "全部"
        }
        filter_name = filter_name_map.get(filter_type, filter_type)
        await callback.answer(f"已筛选：{filter_name}")
        
    except Exception as e:
        logger.error(f"Error in callback_filter_transactions: {e}", exc_info=True)
        await callback.answer("❌ 筛选失败，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("order_detail_"))
async def callback_order_detail(callback: CallbackQuery):
    """Handle order detail view"""
    try:
        order_id = callback.data.split("_", 2)[2]
        
        transaction = TransactionService.get_transaction(order_id)
        
        if not transaction:
            await callback.answer("❌ 订单不存在", show_alert=True)
            return
        
        if transaction['user_id'] != callback.from_user.id:
            await callback.answer("❌ 无权限查看此订单", show_alert=True)
            return
        
        status_map = {
            'pending': '⏳ 待支付',
            'paid': '✅ 支付成功',
            'failed': '❌ 支付失败',
            'refunded': '↩️ 已退款',
            'cancelled': '🚫 已取消'
        }
        
        type_map = {
            'receive': '收款',
            'pay': '付款',
            'refund': '退款'
        }
        
        channel_map = {
            'alipay': '支付宝',
            'wechat': '微信'
        }
        
        order_id_escaped = escape_markdown_v2(transaction['order_id'])
        amount_str = format_amount_markdown(transaction['amount'])
        fee_str = format_amount_markdown(transaction['fee'])
        actual_str = format_amount_markdown(transaction['actual_amount'])
        action_text = escape_markdown_v2('到账' if transaction['transaction_type'] == 'receive' else '支付')
        created_at_escaped = escape_markdown_v2(str(transaction['created_at']))
        
        text = (
            f"*📋 订单详情*\n\n"
            f"订单号：`{order_id_escaped}`\n"
            f"状态：{status_map.get(transaction['status'], transaction['status'])}\n"
            f"类型：{type_map.get(transaction['transaction_type'], transaction['transaction_type'])}\n"
            f"通道：{channel_map.get(transaction['payment_channel'], transaction['payment_channel'])}\n"
            f"金额：{amount_str}\n"
            f"手续费：{fee_str}\n"
            f"实际{action_text}：{actual_str}\n"
            f"创建时间：{created_at_escaped}\n"
        )
        
        if transaction.get('paid_at'):
            paid_at_escaped = escape_markdown_v2(str(transaction['paid_at']))
            text += f"支付时间：{paid_at_escaped}\n"
        
        if transaction.get('description'):
            desc_escaped = escape_markdown_v2(transaction['description'])
            text += f"\n备注：{desc_escaped}"
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_transaction_detail_keyboard(order_id)
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_order_detail: {e}", exc_info=True)
        await callback.answer("❌ 获取订单详情失败，请稍后再试", show_alert=True)

