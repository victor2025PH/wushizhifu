"""
Callback handlers for Bot B
Handles inline keyboard button callbacks
"""
import logging
import re
from typing import Optional
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from database import db
from admin_checker import is_admin
from keyboards.inline_keyboard import (
    get_group_settings_menu, get_global_management_menu,
    get_bills_history_keyboard, get_confirmation_keyboard,
    get_settlement_bill_keyboard, get_payment_hash_input_keyboard,
    get_paid_transactions_keyboard,
    get_customer_service_management_menu, get_customer_service_list_keyboard,
    get_customer_service_edit_keyboard, get_customer_service_strategy_keyboard
)
from handlers.bills_handlers import handle_transaction_detail
from handlers.stats_handlers import handle_group_stats, handle_global_stats

logger = logging.getLogger(__name__)


# ========== Transaction Lifecycle Management ==========

async def handle_mark_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'mark as paid' button click on settlement bill"""
    query = update.callback_query
    
    try:
        # Extract transaction_id from callback_data
        callback_data = query.data
        transaction_id = None
        if callback_data.startswith("mark_paid_"):
            parts = callback_data.split("_", 2)
            if len(parts) > 2:
                transaction_id = parts[2]
        
        if not transaction_id:
            await query.answer("❌ 交易编号无效", show_alert=True)
            return
        
        # Get transaction details
        transaction = db.get_transaction_by_id(transaction_id)
        if not transaction:
            await query.answer("❌ 未找到该交易", show_alert=True)
            return
        
        # Check if user owns this transaction
        if transaction['user_id'] != query.from_user.id:
            await query.answer("❌ 您无权操作此交易", show_alert=True)
            return
        
        # Check if already paid or confirmed
        if transaction['status'] in ['paid', 'confirmed']:
            await query.answer(f"✅ 交易状态：{transaction['status']}", show_alert=True)
            return
        
        # Ask for payment hash (optional)
        context.user_data['awaiting_payment_hash'] = transaction_id
        await query.message.reply_text(
            "💰 <b>标记已支付</b>\n\n"
            "请输入支付哈希（TXID）：\n"
            "• 可直接输入哈希值\n"
            "• 或点击「跳过」不填写\n\n"
            "<i>提示：填写支付哈希有助于对账和审计</i>",
            parse_mode="HTML",
            reply_markup=get_payment_hash_input_keyboard(transaction_id)
        )
        await query.answer("💡 请输入支付哈希（可选）")
        
    except Exception as e:
        logger.error(f"Error in handle_mark_paid: {e}", exc_info=True)
        await query.answer("❌ 操作失败，请重试", show_alert=True)


async def handle_skip_payment_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle skip payment hash button"""
    query = update.callback_query
    
    try:
        callback_data = query.data
        transaction_id = None
        if callback_data.startswith("skip_payment_hash_"):
            parts = callback_data.split("_", 3)
            if len(parts) > 3:
                transaction_id = parts[3]
        
        if not transaction_id:
            await query.answer("❌ 交易编号无效", show_alert=True)
            return
        
        # Mark as paid without payment hash
        transaction = db.get_transaction_by_id(transaction_id)
        old_status = transaction['status'] if transaction else None
        
        if db.mark_transaction_paid(transaction_id):
            # Log operation
            from services.audit_service import log_transaction_operation, OperationType
            log_transaction_operation(
                OperationType.MARK_PAID,
                update,
                transaction_id,
                description=f"用户标记为已支付（未提供支付哈希）",
                old_status=old_status,
                new_status='paid'
            )
            
            # Refresh transaction and update message
            transaction = db.get_transaction_by_id(transaction_id)
            await refresh_transaction_message(query, transaction)
            await query.answer("✅ 已标记为已支付")
            logger.info(f"User {query.from_user.id} marked transaction {transaction_id} as paid (no hash)")
        else:
            await query.answer("❌ 操作失败，请重试", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error in handle_skip_payment_hash: {e}", exc_info=True)
        await query.answer("❌ 操作失败，请重试", show_alert=True)


async def handle_cancel_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel transaction button click"""
    query = update.callback_query
    
    try:
        callback_data = query.data
        transaction_id = None
        if callback_data.startswith("cancel_tx_"):
            parts = callback_data.split("_", 2)
            if len(parts) > 2:
                transaction_id = parts[2]
        
        if not transaction_id:
            await query.answer("❌ 交易编号无效", show_alert=True)
            return
        
        # Get transaction details
        transaction = db.get_transaction_by_id(transaction_id)
        if not transaction:
            await query.answer("❌ 未找到该交易", show_alert=True)
            return
        
        # Check permissions: user can cancel own pending transactions, admin can cancel any pending
        is_admin_user = is_admin(query.from_user.id)
        if transaction['user_id'] != query.from_user.id and not is_admin_user:
            await query.answer("❌ 您无权取消此交易", show_alert=True)
            return
        
        # Check if can be cancelled
        if transaction['status'] not in ['pending', 'paid']:
            await query.answer(f"❌ 交易状态为 {transaction['status']}，无法取消", show_alert=True)
            return
        
        # Cancel transaction
        old_status = transaction['status']
        
        if db.cancel_transaction(transaction_id, query.from_user.id):
            # Log operation
            from services.audit_service import log_transaction_operation, OperationType
            is_admin_user = is_admin(query.from_user.id)
            desc = "管理员取消交易" if is_admin_user else "用户取消交易"
            log_transaction_operation(
                OperationType.CANCEL_TRANSACTION,
                update,
                transaction_id,
                description=desc,
                old_status=old_status,
                new_status='cancelled'
            )
            
            # Refresh transaction and update message
            transaction = db.get_transaction_by_id(transaction_id)
            await refresh_transaction_message(query, transaction)
            await query.answer("❌ 交易已取消")
            logger.info(f"User {query.from_user.id} cancelled transaction {transaction_id}")
        else:
            await query.answer("❌ 操作失败，请重试", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error in handle_cancel_transaction: {e}", exc_info=True)
        await query.answer("❌ 操作失败，请重试", show_alert=True)


async def handle_confirm_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirm transaction button click (admin only)"""
    query = update.callback_query
    
    try:
        # Check admin permission
        if not is_admin(query.from_user.id):
            await query.answer("❌ 仅管理员可以确认交易", show_alert=True)
            return
        
        callback_data = query.data
        transaction_id = None
        if callback_data.startswith("confirm_tx_"):
            parts = callback_data.split("_", 2)
            if len(parts) > 2:
                transaction_id = parts[2]
        
        if not transaction_id:
            await query.answer("❌ 交易编号无效", show_alert=True)
            return
        
        # Get transaction details
        transaction = db.get_transaction_by_id(transaction_id)
        if not transaction:
            await query.answer("❌ 未找到该交易", show_alert=True)
            return
        
        # Check if can be confirmed (must be paid)
        if transaction['status'] != 'paid':
            await query.answer(f"❌ 交易状态为 {transaction['status']}，无法确认", show_alert=True)
            return
        
        # Confirm transaction
        if db.confirm_transaction(transaction_id):
            # Log operation
            from services.audit_service import log_transaction_operation, OperationType
            log_transaction_operation(
                OperationType.CONFIRM_TRANSACTION,
                update,
                transaction_id,
                description=f"管理员确认交易",
                old_status=transaction['status'],
                new_status='confirmed'
            )
            
            # Refresh transaction and update message
            transaction = db.get_transaction_by_id(transaction_id)
            await refresh_transaction_message(query, transaction)
            await query.answer("✅ 交易已确认")
            logger.info(f"Admin {query.from_user.id} confirmed transaction {transaction_id}")
        else:
            await query.answer("❌ 操作失败，请重试", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error in handle_confirm_transaction: {e}", exc_info=True)
        await query.answer("❌ 操作失败，请重试", show_alert=True)


async def handle_batch_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: Optional[int] = None):
    """Handle batch confirm paid transactions"""
    query = update.callback_query
    
    try:
        if not is_admin(query.from_user.id):
            await query.answer("❌ 仅管理员可以批量确认", show_alert=True)
            return
        
        # Get all paid transactions
        paid_txs = db.get_paid_transactions(group_id=group_id, limit=100)
        
        if not paid_txs:
            await query.answer("✅ 没有待确认的交易", show_alert=True)
            return
        
        # Confirm all transactions
        confirmed_count = 0
        from services.audit_service import log_transaction_operation, log_admin_operation, OperationType
        
        for tx in paid_txs:
            if db.confirm_transaction(tx['transaction_id']):
                log_transaction_operation(
                    OperationType.CONFIRM_TRANSACTION,
                    update,
                    tx['transaction_id'],
                    description=f"批量确认交易",
                    old_status='paid',
                    new_status='confirmed'
                )
                confirmed_count += 1
        
        if confirmed_count > 0:
            # Log batch operation
            log_admin_operation(
                OperationType.BATCH_CONFIRM,
                update,
                target_type='group' if group_id else 'global',
                target_id=str(group_id) if group_id else None,
                description=f"批量确认 {confirmed_count} 笔交易"
            )
            
            await query.answer(f"✅ 已批量确认 {confirmed_count} 笔交易", show_alert=True)
            # Refresh the paid transactions list
            from handlers.stats_handlers import handle_paid_transactions
            await handle_paid_transactions(update, context, group_id)
            logger.info(f"Admin {query.from_user.id} batch confirmed {confirmed_count} transactions (group_id: {group_id})")
        else:
            await query.answer("❌ 批量确认失败", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error in handle_batch_confirm: {e}", exc_info=True)
        await query.answer("❌ 操作失败，请重试", show_alert=True)


async def refresh_transaction_message(query, transaction):
    """Refresh transaction bill message with updated status"""
    from services.settlement_service import format_settlement_bill
    from keyboards.inline_keyboard import get_settlement_bill_keyboard
    
    # Rebuild settlement data from transaction
    settlement_data = {
        'cny_amount': transaction['cny_amount'],
        'base_price': transaction['exchange_rate'] - (transaction['markup'] or 0.0),
        'markup': transaction['markup'] or 0.0,
        'final_price': transaction['exchange_rate'],
        'usdt_amount': transaction['usdt_amount']
    }
    
    # Format time strings
    paid_at = transaction.get('paid_at')
    if paid_at:
        paid_at = paid_at[:16]  # YYYY-MM-DD HH:MM
    confirmed_at = transaction.get('confirmed_at')
    if confirmed_at:
        confirmed_at = confirmed_at[:16]
    
    # Format bill message
    bill_message = format_settlement_bill(
        settlement_data,
        usdt_address=transaction.get('usdt_address'),
        transaction_id=transaction['transaction_id'],
        transaction_status=transaction['status'],
        payment_hash=transaction.get('payment_hash'),
        paid_at=paid_at,
        confirmed_at=confirmed_at
    )
    
    # Get keyboard based on status
    is_admin_user = is_admin(query.from_user.id)
    reply_markup = get_settlement_bill_keyboard(
        transaction['transaction_id'],
        transaction['status'],
        is_admin_user
    )
    
    # Update message
    await query.edit_message_text(
        text=bill_message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def handle_confirm_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle old confirmation button (backward compatibility) - redirects to confirm transaction"""
    # This is for backward compatibility with old bills
    # New bills use handle_confirm_transaction
    query = update.callback_query
    
    try:
        callback_data = query.data
        transaction_id = None
        if callback_data.startswith("confirm_bill_"):
            parts = callback_data.split("_", 2)
            if len(parts) > 2:
                transaction_id = parts[2]
        
        if transaction_id:
            # Check if transaction is already paid, then confirm it
            transaction = db.get_transaction_by_id(transaction_id)
            if transaction:
                if transaction['status'] == 'paid':
                    await handle_confirm_transaction(update, context)
                    return
                elif transaction['status'] == 'pending':
                    # Old behavior: just mark as confirmed (without payment)
                    # For backward compatibility, we'll mark as paid first
                    db.mark_transaction_paid(transaction_id)
                    db.confirm_transaction(transaction_id)
                    transaction = db.get_transaction_by_id(transaction_id)
                    await refresh_transaction_message(query, transaction)
                    await query.answer("✅ 已确认")
                    return
        
        await query.answer("✅ 已确认")
        
    except Exception as e:
        logger.error(f"Error in handle_confirm_bill: {e}", exc_info=True)
        await query.answer("❌ 操作失败，请重试", show_alert=True)


# ========== Group Settings Menu ==========

async def handle_group_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group settings menu callbacks"""
    query = update.callback_query
    
    if not is_admin(query.from_user.id):
        await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
        return
    
    chat = query.message.chat
    if chat.type not in ['group', 'supergroup']:
        await query.answer("❌ 此功能仅在群组中可用", show_alert=True)
        return
    
    callback_data = query.data
    group_id = chat.id
    
    try:
        if callback_data == "group_settings_view":
            # Show group settings (same as w0)
            from handlers.message_handlers import handle_admin_w0
            await handle_admin_w0(update, context)
            await query.answer()
            return
        
        elif callback_data == "group_settings_markup":
            await query.message.reply_text("请输入加价值（例如：0.5）")
            await query.answer("💡 请在聊天中输入加价值")
            return
        
        elif callback_data == "group_settings_address":
            await query.message.reply_text("请输入 USDT 收款地址")
            await query.answer("💡 请在聊天中输入地址")
            return
        
        elif callback_data == "group_settings_reset":
            # Show confirmation
            message = (
                f"⚠️ <b>确认重置群组设置</b>\n\n"
                f"群组: {chat.title or '未知群组'}\n\n"
                f"重置后将恢复使用全局默认设置。\n\n"
                f"确定要重置吗？"
            )
            reply_markup = get_confirmation_keyboard("reset_group_settings", str(group_id))
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
            return
        
        elif callback_data == "group_settings_delete":
            # Show confirmation
            message = (
                f"⚠️ <b>确认删除群组配置</b>\n\n"
                f"群组: {chat.title or '未知群组'}\n\n"
                f"删除后将完全清除群组独立配置。\n\n"
                f"确定要删除吗？"
            )
            reply_markup = get_confirmation_keyboard("delete_group_settings", str(group_id))
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
            return
        
        elif callback_data == "group_stats":
            # Show group stats
            await handle_group_stats(update, context)
            await query.answer()
            return
        
        elif callback_data == "pending_transactions":
            # Show pending transactions
            from handlers.stats_handlers import handle_pending_transactions
            await handle_pending_transactions(update, context, group_id)
            await query.answer()
            return
        
        elif callback_data == "paid_transactions":
            # Show paid transactions (waiting for confirmation)
            from handlers.stats_handlers import handle_paid_transactions
            await handle_paid_transactions(update, context, group_id)
            await query.answer()
            return
        
    except Exception as e:
        logger.error(f"Error in handle_group_settings_menu: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


# ========== Global Management Menu ==========

async def handle_global_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle global management menu callbacks"""
    query = update.callback_query
    
    if not is_admin(query.from_user.id):
        await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
        return
    
    callback_data = query.data
    
    try:
        # Show help for each button if needed
        from services.button_help_service import (
            format_button_help_message, 
            should_show_help, 
            mark_help_shown
        )
        from keyboards.inline_keyboard import get_button_help_keyboard
        
        if callback_data == "global_groups_list":
            # Answer callback first to prevent timeout
            await query.answer()
            
            # Show help if needed
            if should_show_help(query.from_user.id, "所有群组列表"):
                help_message = format_button_help_message("所有群组列表")
                if help_message:
                    help_keyboard = get_button_help_keyboard("所有群组列表")
                    await query.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                    mark_help_shown(query.from_user.id, "所有群组列表", shown=True)
            
            # Call handle_admin_w7 to show groups list
            # handle_admin_w7 will edit the original message (global management menu) to show groups list
            from handlers.message_handlers import handle_admin_w7
            try:
                await handle_admin_w7(update, context)
            except Exception as e:
                logger.error(f"Error calling handle_admin_w7 from callback: {e}", exc_info=True)
                await query.message.reply_text(f"❌ 错误: {str(e)}", parse_mode="HTML")
            return
        
        elif callback_data == "global_stats":
            # Show help if needed
            if should_show_help(query.from_user.id, "全局统计"):
                help_message = format_button_help_message("全局统计")
                if help_message:
                    help_keyboard = get_button_help_keyboard("全局统计")
                    await query.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                    mark_help_shown(query.from_user.id, "全局统计", shown=True)
            
            await handle_global_stats(update, context)
            await query.answer()
            return
        
        elif callback_data == "customer_service_management":
            from handlers.customer_service_handlers import handle_customer_service_management
            await handle_customer_service_management(update, context)
            await query.answer()
            return
        
    except Exception as e:
        logger.error(f"Error in handle_global_management_menu: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


# ========== Group Edit Handlers ==========

async def handle_group_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group edit callbacks (select group, edit markup, edit address)"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        # Handle group selection
        if callback_data.startswith("group_select_"):
            group_id = int(callback_data.split("_")[2])
            from keyboards.inline_keyboard import get_group_edit_keyboard
            from database import db
            
            # Get group info
            groups = db.get_all_groups()
            group = next((g for g in groups if g['group_id'] == group_id), None)
            
            if not group:
                await query.answer("❌ 群组不存在", show_alert=True)
                return
            
            group_title = group.get('group_title', f"群组 {group_id}")
            current_markup = group.get('markup', 0.0)
            current_address = group.get('usdt_address', '')
            
            message = f"⚙️ <b>编辑群组设置</b>\n\n"
            message += f"群组: <b>{group_title}</b>\n"
            message += f"ID: <code>{group_id}</code>\n\n"
            message += f"当前上浮汇率: <code>{current_markup:+.4f} USDT</code>\n"
            
            if current_address:
                addr_display = current_address[:15] + "..." + current_address[-15:] if len(current_address) > 30 else current_address
                message += f"当前地址: <code>{addr_display}</code>\n"
            else:
                global_address = db.get_usdt_address()
                if global_address:
                    addr_display = global_address[:15] + "..." + global_address[-15:] if len(global_address) > 30 else global_address
                    message += f"当前地址: <code>{addr_display}</code> (全局)\n"
                else:
                    message += f"当前地址: 未设置\n"
            
            reply_markup = get_group_edit_keyboard(group_id)
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
            return
        
        # Handle edit markup
        elif callback_data.startswith("group_edit_markup_"):
            group_id = int(callback_data.split("_")[3])
            context.user_data[f'awaiting_group_markup_{group_id}'] = True
            await query.message.reply_text(f"请输入群组的上浮汇率值（例如：0.5 或 -0.1）")
            await query.answer("💡 请在聊天中输入上浮汇率值")
            return
        
        # Handle edit address
        elif callback_data.startswith("group_edit_address_"):
            group_id = int(callback_data.split("_")[3])
            
            # Check if user is group admin
            from utils.group_admin_checker import is_group_admin
            user_id = query.from_user.id
            
            # Check if user is group admin (check in the target group) or global admin
            is_group_admin_user = await is_group_admin(context.bot, group_id, user_id)
            
            # Allow if user is group admin OR global admin
            if not is_group_admin_user and not is_admin(user_id):
                # Get chat info to show group owner info
                try:
                    chat_info = await context.bot.get_chat(group_id)
                    message = (
                        "❌ <b>权限不足</b>\n\n"
                        f"只有群组管理员才能编辑此群组的 USDT 地址。\n\n"
                        f"💡 <i>提示：请联系群主提升您的权限，或联系全局管理员获取帮助。</i>"
                    )
                except:
                    message = (
                        "❌ <b>权限不足</b>\n\n"
                        "只有群组管理员才能编辑此群组的 USDT 地址。\n\n"
                        "💡 <i>提示：请联系群主提升您的权限，或联系全局管理员获取帮助。</i>"
                    )
                
                await query.answer("❌ 权限不足", show_alert=True)
                await query.message.reply_text(message, parse_mode="HTML")
                return
            
            context.user_data[f'awaiting_group_address_{group_id}'] = True
            await query.message.reply_text(f"请输入群组的 USDT 收款地址")
            await query.answer("💡 请在聊天中输入地址")
            return
            
    except Exception as e:
        logger.error(f"Error in handle_group_edit: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


# ========== Bills History Pagination ==========

async def handle_bills_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bills history pagination"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        # Parse callback data: bills_page_{group_id}_{page}
        match = re.match(r'bills_page_(-?\d+)_(\d+)', callback_data)
        if not match:
            await query.answer("❌ 无效的页码", show_alert=True)
            return
        
        group_id = int(match.group(1))
        page = int(match.group(2))
        
        # Verify group ID matches current chat
        if query.message.chat.id != group_id:
            await query.answer("❌ 群组不匹配", show_alert=True)
            return
        
        # Get transactions for this page
        from handlers.bills_handlers import handle_history_bills
        
        # We need to update the message instead of sending new one
        from database import db
        limit = 10
        offset = (page - 1) * limit
        
        transactions = db.get_transactions_by_group(group_id, limit=limit, offset=offset)
        total_count = db.count_transactions_by_group(group_id)
        total_pages = (total_count + limit - 1) // limit
        
        if not transactions and page > 1:
            # Go back to last page if current page is empty
            page = total_pages
            offset = (page - 1) * limit
            transactions = db.get_transactions_by_group(group_id, limit=limit, offset=offset)
        
        if not transactions:
            await query.answer("📭 暂无数据", show_alert=True)
            return
        
        # Build message
        message = f"📜 <b>历史账单</b>\n\n"
        message += "────────────────────────\n"
        message += f"群组: {query.message.chat.title or '未知群组'}\n"
        message += f"日期范围: 全部\n"
        message += f"\n📋 账单列表（第 {page} 页，共 {total_pages} 页）:\n\n"
        
        for idx, tx in enumerate(transactions, 1):
            date_str = tx['created_at'][:16] if len(tx['created_at']) > 16 else tx['created_at']
            user_name = tx['first_name'] or tx['username'] or f"用户{tx['user_id']}"
            message += f"{idx}. {date_str}\n"
            message += f"   {tx['cny_amount']:,.2f} CNY → {tx['usdt_amount']:,.2f} USDT"
            if user_name:
                message += f" - {user_name}"
            message += "\n\n"
        
        reply_markup = get_bills_history_keyboard(group_id, page)
        
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_bills_pagination: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


# ========== Confirmation Handlers ==========

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation callbacks"""
    query = update.callback_query
    
    if not is_admin(query.from_user.id):
        await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
        return
    
    callback_data = query.data
    
    try:
        # Parse: confirm_{action}_{data}
        if callback_data.startswith("confirm_"):
            parts = callback_data.split("_", 2)
            if len(parts) < 3:
                await query.answer("❌ 无效的确认操作", show_alert=True)
                return
            
            action = parts[1]
            data = parts[2] if len(parts) > 2 else ""
            
            chat = query.message.chat
            
            if action == "reset_group_settings":
                group_id = int(data)
                if db.reset_group_settings(group_id):
                    message = f"✅ 群组设置已重置\n\n群组: {chat.title or '未知群组'}\n已恢复使用全局默认设置"
                    await query.edit_message_text(message, parse_mode="HTML")
                    await query.answer("✅ 重置成功")
                else:
                    await query.answer("❌ 重置失败", show_alert=True)
                return
            
            elif action == "delete_group_settings":
                group_id = int(data)
                if db.delete_group_settings(group_id):
                    message = f"✅ 群组配置已删除\n\n群组: {chat.title or '未知群组'}\n已完全删除群组独立配置"
                    await query.edit_message_text(message, parse_mode="HTML")
                    await query.answer("✅ 删除成功")
                else:
                    await query.answer("❌ 删除失败", show_alert=True)
                return
        
        # Parse: cancel_{action}
        elif callback_data.startswith("cancel_"):
            parts = callback_data.split("_", 1)
            action = parts[1] if len(parts) > 1 else ""
            
            await query.edit_message_text("❌ 操作已取消")
            await query.answer("已取消")
            return
        
    except Exception as e:
        logger.error(f"Error in handle_confirmation: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


# ========== Main Callback Handler ==========

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main callback handler - routes callback queries to appropriate handlers
    """
    query = update.callback_query
    
    if not query or not query.data:
        return
    
    callback_data = query.data
    
    # Transaction lifecycle management
    if callback_data.startswith("mark_paid"):
        await handle_mark_paid(update, context)
        return
    
    if callback_data.startswith("skip_payment_hash"):
        await handle_skip_payment_hash(update, context)
        return
    
    if callback_data.startswith("cancel_tx"):
        await handle_cancel_transaction(update, context)
        return
    
    if callback_data.startswith("confirm_tx"):
        await handle_confirm_transaction(update, context)
        return
    
    # Settlement bill confirmation (backward compatibility)
    if callback_data.startswith("confirm_bill"):
        await handle_confirm_bill(update, context)
        return
    
    # Group settings menu
    if callback_data.startswith("group_settings"):
        await handle_group_settings_menu(update, context)
        return
    
    # Admin commands help
    if callback_data == "admin_commands_help":
        from handlers.admin_commands_handlers import handle_admin_commands_help
        await handle_admin_commands_help(update, context)
        return
    
    # Group settings menu (when returning from help)
    if callback_data == "group_settings_menu":
        chat = query.message.chat
        from keyboards.inline_keyboard import get_group_settings_menu
        reply_markup = get_group_settings_menu()
        message = (
            "⚙️ <b>群组设置菜单</b>\n\n"
            "请选择要执行的操作："
        )
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        return
    
    # Global management menu (when returning from help)
    if callback_data == "global_management_menu":
        from keyboards.inline_keyboard import get_global_management_menu
        reply_markup = get_global_management_menu()
        message = (
            "🌐 <b>全局管理菜单</b>\n\n"
            "请选择要执行的操作："
        )
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        return
    
    # Group edit handlers
    if callback_data.startswith("group_select_") or callback_data.startswith("group_edit_markup_") or callback_data.startswith("group_edit_address_"):
        await handle_group_edit(update, context)
        return
    
    # Global management menu
    if callback_data.startswith("global_settings") or callback_data == "global_groups_list" or callback_data == "global_stats":
        await handle_global_management_menu(update, context)
        return
    
    # Customer service management
    if callback_data.startswith("customer_service"):
        from handlers.customer_service_handlers import handle_customer_service_management
        await handle_customer_service_management(update, context)
        return
    
    # Bills pagination
    if callback_data.startswith("bills_page"):
        await handle_bills_pagination(update, context)
        return
    
    # Confirmation dialogs (exclude cancel_tx which is handled above)
    if callback_data.startswith("confirm_") or (callback_data.startswith("cancel_") and not callback_data.startswith("cancel_tx")):
        await handle_confirmation(update, context)
        return
    
    # Pending/Paid transactions
    if callback_data == "pending_transactions":
        from handlers.stats_handlers import handle_pending_transactions
        chat = query.message.chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        await handle_pending_transactions(update, context, group_id)
        return
    
    if callback_data == "paid_transactions":
        from handlers.stats_handlers import handle_paid_transactions
        chat = query.message.chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        await handle_paid_transactions(update, context, group_id)
        return
    
    # Refresh buttons
    if callback_data.startswith("refresh_pending") or callback_data.startswith("refresh_paid"):
        # Parse group_id and page from callback_data
        parts = callback_data.split("_")
        if len(parts) >= 3:
            group_id = int(parts[2]) if parts[2].isdigit() else None
            if "pending" in callback_data:
                from handlers.stats_handlers import handle_pending_transactions
                await handle_pending_transactions(update, context, group_id)
            else:
                from handlers.stats_handlers import handle_paid_transactions
                await handle_paid_transactions(update, context, group_id)
        return
    
    # Batch confirm
    if callback_data.startswith("batch_confirm"):
        parts = callback_data.split("_")
        group_id = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
        await handle_batch_confirm(update, context, group_id)
        return
    
    # Export transactions
    if callback_data.startswith("export_csv") or callback_data.startswith("export_excel"):
        parts = callback_data.split("_")
        export_format = parts[1]  # 'csv' or 'excel'
        group_id = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
        from handlers.bills_handlers import handle_export_transactions
        await handle_export_transactions(update, context, group_id, export_format)
        return
    
    # Export statistics
    if callback_data == "export_stats":
        chat = query.message.chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        from handlers.stats_handlers import handle_export_stats
        await handle_export_stats(update, context, group_id)
        return
    
    # Search and filter handlers
    if callback_data.startswith("filter_menu"):
        group_id = int(callback_data.split("_")[2]) if len(callback_data.split("_")) > 2 else None
        from handlers.search_handlers import handle_search_filter_menu
        await handle_search_filter_menu(update, context)
        return
    
    if callback_data.startswith("filter_amount"):
        group_id = int(callback_data.split("_")[2])
        from handlers.search_handlers import handle_amount_filter
        await handle_amount_filter(update, context, group_id)
        return
    
    if callback_data.startswith("filter_date"):
        group_id = int(callback_data.split("_")[2])
        from handlers.search_handlers import handle_date_filter
        await handle_date_filter(update, context, group_id)
        return
    
    if callback_data.startswith("filter_status"):
        group_id = int(callback_data.split("_")[2])
        from handlers.search_handlers import handle_status_filter
        await handle_status_filter(update, context, group_id)
        return
    
    if callback_data.startswith("status_filter"):
        parts = callback_data.split("_")
        group_id = int(parts[2])
        status = parts[3]
        from handlers.search_handlers import apply_filters_and_show_results
        filters = {'status': status}
        await apply_filters_and_show_results(update, context, group_id, filters)
        return
    
    if callback_data.startswith("filter_user"):
        group_id = int(callback_data.split("_")[2])
        from handlers.search_handlers import handle_user_filter
        await handle_user_filter(update, context, group_id)
        return
    
    if callback_data.startswith("filter_search"):
        group_id = int(callback_data.split("_")[2])
        from handlers.search_handlers import handle_comprehensive_search
        await handle_comprehensive_search(update, context, group_id)
        return
    
    if callback_data.startswith("filter_clear"):
        group_id = int(callback_data.split("_")[2])
        from handlers.bills_handlers import handle_history_bills
        await handle_history_bills(update, context, page=1, edit_message=True)
        return
    
    # Onboarding handlers
    if callback_data.startswith("onboarding_step"):
        step = int(callback_data.split("_")[2])
        from services.onboarding_service import show_onboarding_step
        await show_onboarding_step(update, context, step)
        return
    
    if callback_data == "onboarding_complete":
        from services.onboarding_service import complete_onboarding
        await complete_onboarding(update, context)
        return
    
    if callback_data == "onboarding_skip":
        from services.onboarding_service import complete_onboarding
        await complete_onboarding(update, context)
        return
    
    # Audit log handlers
    if callback_data == "view_logs" or callback_data.startswith("logs_view"):
        page = 1
        if callback_data.startswith("logs_view_"):
            if callback_data.endswith("_all"):
                page = 1
            else:
                try:
                    page = int(callback_data.split("_")[2])
                except:
                    page = 1
        from handlers.audit_handlers import handle_view_logs
        await handle_view_logs(update, context, page=page)
        return
    
    if callback_data.startswith("logs_page"):
        page = int(callback_data.split("_")[2])
        from handlers.audit_handlers import handle_logs_pagination
        await handle_logs_pagination(update, context, page)
        return
    
    if callback_data == "logs_filter":
        from handlers.audit_handlers import handle_logs_filter_menu
        await handle_logs_filter_menu(update, context)
        return
    
    # Template handlers
    if callback_data == "template_menu":
        from handlers.template_handlers import handle_template_menu
        await handle_template_menu(update, context)
        return
    
    if callback_data.startswith("template_list_"):
        template_type = callback_data.split("_")[2]  # 'amount' or 'formula'
        from handlers.template_handlers import handle_template_list
        await handle_template_list(update, context, template_type)
        return
    
    if callback_data.startswith("template_use_"):
        template_id = int(callback_data.split("_")[2])
        from handlers.template_handlers import handle_template_use
        await handle_template_use(update, context, template_id)
        return
    
    if callback_data == "template_create":
        from handlers.template_handlers import handle_template_create_menu
        await handle_template_create_menu(update, context)
        return
    
    if callback_data.startswith("template_create_"):
        template_type = callback_data.split("_")[2]  # 'amount' or 'formula'
        from handlers.template_handlers import handle_template_create_type
        await handle_template_create_type(update, context, template_type)
        return
    
    # Address management handlers
    if callback_data == "address_list" or callback_data == "address_manage":
        from handlers.address_handlers import handle_address_list
        await handle_address_list(update, context)
        return
    
    if callback_data == "address_add":
        from handlers.address_handlers import handle_address_add_prompt
        await handle_address_add_prompt(update, context)
        return
    
    # Help handlers
    if callback_data.startswith("help_"):
        if callback_data == "help_close":
            from handlers.help_handlers import handle_help_close
            await handle_help_close(update, context)
            return
        elif callback_data.startswith("help_"):
            help_context = callback_data[5:]  # Remove "help_" prefix
            from handlers.help_handlers import show_contextual_help
            await show_contextual_help(update, help_context)
            return
    
    # P2P leaderboard handlers
    # P2P Leaderboard callbacks (supports pagination: p2p_bank_1, p2p_ali_2, etc.)
    if callback_data.startswith("p2p_"):
        from handlers.p2p_handlers import handle_p2p_callback
        await handle_p2p_callback(update, context, callback_data)
        return
    
    # Main menu
    if callback_data == "main_menu":
        await query.answer("💡 使用底部按钮或 /start 查看主菜单")
        return
    
    # Button help close
    if callback_data.startswith("close_help_"):
        button_text = callback_data.replace("close_help_", "", 1)
        from services.button_help_service import mark_help_shown
        mark_help_shown(query.from_user.id, button_text, shown=False)
        await query.answer("✅ 已关闭帮助提示，可在 /start 中重新打开", show_alert=False)
        try:
            await query.message.delete()
        except:
            pass
        return
    
    # Reset all help
    if callback_data == "reset_all_help":
        from services.button_help_service import reset_all_help
        reset_all_help(query.from_user.id)
        await query.answer("✅ 已重置所有按钮帮助，下次点击按钮时会重新显示", show_alert=True)
        try:
            await query.message.edit_text(
                "✅ <b>按钮帮助已重置</b>\n\n"
                "所有按钮的帮助提示已重新启用。\n"
                "下次点击按钮时会显示功能介绍和使用教程。",
                parse_mode="HTML"
            )
        except:
            pass
        return
    
    # None action (placeholder buttons)
    if callback_data == "none":
        await query.answer()
        return


def get_callback_handler():
    """Get callback handler instance"""
    return CallbackQueryHandler(callback_handler)
