"""
Bills handlers for Bot B
Handles bill queries and history
"""
import logging
import datetime
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from telegram import Document
from database import db
from admin_checker import is_admin
from keyboards.inline_keyboard import get_bills_history_keyboard, get_transaction_detail_keyboard
from services.export_service import (
    export_transactions_to_csv,
    export_transactions_to_excel,
    generate_export_filename
)
from services.search_service import (
    parse_search_query,
    parse_amount_range,
    parse_date_range,
    parse_status_filter
)

logger = logging.getLogger(__name__)


async def handle_history_bills(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              page: int = 1, start_date: str = None, end_date: str = None,
                              status: str = None, min_amount: float = None, max_amount: float = None,
                              user_id: int = None, edit_message: bool = False):
    """
    Handle history bills query with pagination and advanced filtering.
    
    Args:
        update: Telegram update object
        context: Context object
        page: Page number (1-based)
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        status: Optional status filter
        min_amount: Optional minimum CNY amount
        max_amount: Optional maximum CNY amount
        user_id: Optional user ID filter
        edit_message: Whether to edit existing message
    """
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await (update.callback_query or update.message).reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        limit = 10  # 10 transactions per page
        offset = (page - 1) * limit
        
        # Get transactions with filters
        transactions = db.get_transactions_by_group(
            group_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            min_amount=min_amount,
            max_amount=max_amount,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        total_count = db.count_transactions_by_group(
            group_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            min_amount=min_amount,
            max_amount=max_amount,
            user_id=user_id
        )
        
        if not transactions:
            no_data_msg = "📭 暂无符合条件的交易记录"
            if edit_message and update.callback_query:
                await update.callback_query.edit_message_text(no_data_msg)
            else:
                await (update.callback_query or update.message).reply_text(no_data_msg)
            return
        
        total_pages = max(1, (total_count + limit - 1) // limit)
        if page > total_pages:
            page = total_pages
            offset = (page - 1) * limit
            transactions = db.get_transactions_by_group(
                group_id,
                start_date=start_date,
                end_date=end_date,
                status=status,
                min_amount=min_amount,
                max_amount=max_amount,
                user_id=user_id,
                limit=limit,
                offset=offset
            )
        
        # Build message
        message = f"📜 <b>历史账单</b>\n\n"
        message += "────────────────────────\n"
        message += f"群组: {chat.title or '未知群组'}\n"
        
        # Show active filters
        filters_info = []
        if start_date and end_date:
            filters_info.append(f"日期: {start_date} 至 {end_date}")
        if status:
            status_names = {
                'pending': '待支付',
                'paid': '已支付',
                'confirmed': '已确认',
                'cancelled': '已取消'
            }
            filters_info.append(f"状态: {status_names.get(status, status)}")
        if min_amount is not None or max_amount is not None:
            if min_amount == max_amount:
                filters_info.append(f"金额: {min_amount:,.2f} CNY")
            else:
                min_str = f"{min_amount:,.2f}" if min_amount else "0"
                max_str = f"{max_amount:,.2f}" if max_amount else "∞"
                filters_info.append(f"金额: {min_str} - {max_str} CNY")
        if user_id:
            filters_info.append(f"用户ID: {user_id}")
        
        if filters_info:
            message += "筛选条件: " + " | ".join(filters_info) + "\n"
        else:
            message += "筛选条件: 全部\n"
        
        message += f"\n📋 账单列表（第 {page} 页，共 {total_pages} 页，共 {total_count} 笔）:\n\n"
        
        for idx, tx in enumerate(transactions, 1):
            date_str = tx['created_at'][:16] if len(tx['created_at']) > 16 else tx['created_at']
            user_name = tx['first_name'] or tx['username'] or f"用户{tx['user_id']}"
            status_icon = {
                'pending': '⏳',
                'paid': '✅',
                'confirmed': '✅',
                'cancelled': '❌'
            }.get(tx['status'], '⏳')
            message += f"{idx}. {date_str} {status_icon}\n"
            message += f"   {tx['cny_amount']:,.2f} CNY → {tx['usdt_amount']:,.2f} USDT"
            if user_name:
                message += f" - {user_name}"
            message += f"\n   <code>{tx['transaction_id']}</code>\n\n"
        
        # Add keyboard
        reply_markup = get_bills_history_keyboard(group_id, page, start_date, end_date)
        
        if edit_message and update.callback_query:
            await update.callback_query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await update.callback_query.answer()
        else:
            await (update.callback_query or update.message).reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_history_bills: {e}", exc_info=True)
        await (update.callback_query or update.message).reply_text(f"❌ 错误: {str(e)}")


async def handle_export_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    group_id: Optional[int] = None,
                                    export_format: str = 'csv',
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None,
                                    status_filter: Optional[str] = None):
    """
    Handle export transactions to CSV or Excel.
    
    Args:
        update: Telegram update object
        context: Context object
        group_id: Optional group ID to filter by
        export_format: Export format ('csv' or 'excel')
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        status_filter: Optional status filter (pending, paid, confirmed, cancelled)
    """
    try:
        user_id = update.effective_user.id
        
        # Check admin permission
        if not is_admin(user_id):
            await (update.callback_query or update.message).reply_text("❌ 此功能仅限管理员使用")
            return
        
        # Show processing message
        if update.callback_query:
            await update.callback_query.answer("📥 正在生成导出文件...", show_alert=False)
            await update.callback_query.message.reply_text("⏳ 正在准备导出文件，请稍候...")
        else:
            processing_msg = await update.message.reply_text("⏳ 正在准备导出文件，请稍候...")
        
        # Get all transactions matching filters
        if status_filter:
            transactions = db.get_transactions_by_status(status_filter, group_id=group_id, limit=10000)
        elif group_id:
            transactions = db.get_transactions_by_group(group_id, limit=10000)
        else:
            # Get all transactions (may be slow for large datasets)
            transactions = []
            # We need a method to get all transactions, for now we'll get by status and combine
            all_statuses = ['pending', 'paid', 'confirmed', 'cancelled']
            for status in all_statuses:
                txs = db.get_transactions_by_status(status, group_id=group_id, limit=10000)
                transactions.extend(txs)
        
        # Filter by date range if provided
        if start_date and end_date:
            transactions = [
                tx for tx in transactions
                if start_date <= tx['created_at'][:10] <= end_date
            ]
        
        if not transactions:
            error_msg = "❌ 没有找到符合条件的交易记录"
            if update.callback_query:
                await update.callback_query.message.reply_text(error_msg)
            else:
                if 'processing_msg' in locals():
                    await processing_msg.edit_text(error_msg)
                else:
                    await update.message.reply_text(error_msg)
            return
        
        # Export to requested format
        try:
            if export_format == 'excel':
                file_data = export_transactions_to_excel(transactions)
                filename = generate_export_filename('transactions', 'excel')
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:  # csv
                file_data = export_transactions_to_csv(transactions)
                filename = generate_export_filename('transactions', 'csv')
                mime_type = 'text/csv'
            
            # Send file
            file_data.seek(0)
            if update.callback_query:
                await update.callback_query.message.reply_document(
                    document=file_data,
                    filename=filename,
                    caption=(
                        f"📥 <b>导出完成</b>\n\n"
                        f"共导出 {len(transactions)} 笔交易记录\n"
                        f"格式: {export_format.upper()}\n"
                        f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ),
                    parse_mode="HTML"
                )
            else:
                if 'processing_msg' in locals():
                    await processing_msg.delete()
                await update.message.reply_document(
                    document=file_data,
                    filename=filename,
                    caption=(
                        f"📥 <b>导出完成</b>\n\n"
                        f"共导出 {len(transactions)} 笔交易记录\n"
                        f"格式: {export_format.upper()}\n"
                        f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ),
                    parse_mode="HTML"
                )
            
            logger.info(f"Admin {user_id} exported {len(transactions)} transactions ({export_format})")
            
        except Exception as e:
            logger.error(f"Error during export: {e}", exc_info=True)
            error_msg = f"❌ 导出失败: {str(e)}"
            if update.callback_query:
                await update.callback_query.message.reply_text(error_msg)
            else:
                if 'processing_msg' in locals():
                    await processing_msg.edit_text(error_msg)
                else:
                    await update.message.reply_text(error_msg)
        
    except Exception as e:
        logger.error(f"Error in handle_export_transactions: {e}", exc_info=True)
        await (update.callback_query or update.message).reply_text(f"❌ 错误: {str(e)}")


async def handle_transaction_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   transaction_id: str, group_id: int, return_page: int = 1):
    """
    Handle transaction detail view.
    
    Args:
        update: Telegram update object
        context: Context object
        transaction_id: Transaction ID
        group_id: Telegram group ID
        return_page: Page number to return to
    """
    try:
        transaction = db.get_transaction_by_id(transaction_id)
        
        if not transaction:
            await update.callback_query.answer("❌ 交易记录不存在", show_alert=True)
            return
        
        message = f"📄 <b>账单详情</b>\n\n"
        message += "────────────────────────\n"
        message += f"交易编号: <code>{transaction['transaction_id']}</code>\n"
        message += f"时间: {transaction['created_at']}\n"
        message += f"用户: {transaction['first_name'] or transaction['username'] or '未知'}\n"
        message += f"用户ID: <code>{transaction['user_id']}</code>\n\n"
        message += f"💰 金额: {transaction['cny_amount']:,.2f} CNY\n"
        message += f"📊 汇率: {transaction['exchange_rate']:.4f} USDT/CNY\n"
        message += f"💵 应结算: {transaction['usdt_amount']:,.2f} USDT\n"
        
        if transaction['usdt_address']:
            addr = transaction['usdt_address']
            addr_display = addr[:15] + "..." + addr[-15:] if len(addr) > 30 else addr
            message += f"🔗 收款地址: <code>{addr_display}</code>\n"
        
        message += f"📝 状态: {transaction['status']}\n"
        
        if transaction['payment_hash']:
            message += f"🔐 支付哈希: <code>{transaction['payment_hash'][:20]}...</code>\n"
        
        if transaction['confirmed_at']:
            message += f"✅ 确认时间: {transaction['confirmed_at']}\n"
        
        reply_markup = get_transaction_detail_keyboard(transaction_id, group_id, return_page)
        
        await update.callback_query.edit_message_text(
            text=message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        await update.callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_transaction_detail: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误: " + str(e), show_alert=True)

