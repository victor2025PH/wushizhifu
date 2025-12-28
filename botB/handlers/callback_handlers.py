"""
Callback handlers for Bot B
Handles inline keyboard button callbacks
"""
import logging
import re
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from database import db
from admin_checker import is_admin
from keyboards.inline_keyboard import (
    get_group_settings_menu, get_global_management_menu,
    get_bills_history_keyboard, get_confirmation_keyboard,
    get_settlement_bill_keyboard
)
from handlers.bills_handlers import handle_transaction_detail
from handlers.stats_handlers import handle_group_stats, handle_global_stats

logger = logging.getLogger(__name__)


# ========== Settlement Bill Confirmation ==========

async def handle_confirm_bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation button click on settlement bill"""
    query = update.callback_query
    
    try:
        # Extract transaction_id from callback_data (format: confirm_bill_{transaction_id})
        callback_data = query.data
        transaction_id = None
        if callback_data.startswith("confirm_bill_"):
            parts = callback_data.split("_", 2)
            if len(parts) > 2:
                transaction_id = parts[2]
        
        # Update transaction status to 'confirmed' if transaction_id exists
        if transaction_id:
            db.update_transaction_status(transaction_id, 'confirmed')
        
        # Get current message text
        current_text = query.message.text
        
        # Check if already confirmed
        if "(已确认)" in current_text or "✅ 已核对" in current_text:
            await query.answer("✅ 账单已确认")
            return
        
        # Append confirmation text
        new_text = current_text + "\n\n✅ <b>(已确认)</b>"
        
        # Edit the message
        await query.edit_message_text(
            text=new_text,
            parse_mode="HTML"
        )
        
        # Acknowledge the callback
        await query.answer("✅ 已确认")
        
        logger.info(f"User {query.from_user.id} confirmed settlement bill, transaction_id: {transaction_id}")
        
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
        if callback_data == "global_settings_view":
            from handlers.message_handlers import handle_admin_w4
            await handle_admin_w4(update, context)
            await query.answer()
            return
        
        elif callback_data == "global_settings_markup":
            await query.message.reply_text("请输入全局默认加价值（例如：0.5）")
            await query.answer("💡 请在聊天中输入加价值")
            return
        
        elif callback_data == "global_settings_address":
            await query.message.reply_text("请输入全局默认 USDT 收款地址")
            await query.answer("💡 请在聊天中输入地址")
            return
        
        elif callback_data == "global_groups_list":
            from handlers.message_handlers import handle_admin_w7
            await handle_admin_w7(update, context)
            await query.answer()
            return
        
        elif callback_data == "global_stats":
            await handle_global_stats(update, context)
            await query.answer()
            return
        
    except Exception as e:
        logger.error(f"Error in handle_global_management_menu: {e}", exc_info=True)
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
    
    # Settlement bill confirmation
    if callback_data.startswith("confirm_bill"):
        await handle_confirm_bill(update, context)
        return
    
    # Group settings menu
    if callback_data.startswith("group_settings"):
        await handle_group_settings_menu(update, context)
        return
    
    # Global management menu
    if callback_data.startswith("global_settings") or callback_data == "global_groups_list" or callback_data == "global_stats":
        await handle_global_management_menu(update, context)
        return
    
    # Bills pagination
    if callback_data.startswith("bills_page"):
        await handle_bills_pagination(update, context)
        return
    
    # Confirmation dialogs
    if callback_data.startswith("confirm_") or callback_data.startswith("cancel_"):
        await handle_confirmation(update, context)
        return
    
    # Main menu
    if callback_data == "main_menu":
        await query.answer("💡 使用底部按钮或 /start 查看主菜单")
        return


def get_callback_handler():
    """Get callback handler instance"""
    return CallbackQueryHandler(callback_handler)
