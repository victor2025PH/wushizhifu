"""
Audit log handlers for Bot B
Handles viewing and querying operation logs
"""
import logging
import datetime
from typing import Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from database import db
from admin_checker import is_admin

logger = logging.getLogger(__name__)


async def handle_view_logs(update: Update, context: ContextTypes.DEFAULT_TYPE,
                           operation_type: Optional[str] = None,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None,
                           page: int = 1):
    """
    Handle viewing operation logs.
    
    Args:
        update: Telegram update object
        context: Context object
        operation_type: Optional operation type filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        page: Page number
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            if update.callback_query:
                await update.callback_query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            else:
                await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        limit = 10
        offset = (page - 1) * limit
        
        # Get logs
        logs = db.get_operation_logs(
            operation_type=operation_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        total_count = db.count_operation_logs(
            operation_type=operation_type,
            start_date=start_date,
            end_date=end_date
        )
        
        if not logs:
            message = "📋 <b>操作日志</b>\n\n暂无操作记录。"
            if update.callback_query:
                await update.callback_query.edit_message_text(message, parse_mode="HTML")
            else:
                await update.message.reply_text(message, parse_mode="HTML")
            return
        
        total_pages = max(1, (total_count + limit - 1) // limit)
        
        message = f"📋 <b>操作日志</b>\n\n"
        message += "────────────────────────\n"
        message += f"共 {total_count} 条记录\n"
        message += f"当前页: {page}/{total_pages}\n\n"
        
        # Operation type names
        type_names = {
            'set_group_markup': '设置群组加价',
            'set_group_address': '设置群组地址',
            'reset_group_settings': '重置群组设置',
            'delete_group_settings': '删除群组配置',
            'set_global_markup': '设置全局加价',
            'set_global_address': '设置全局地址',
            'mark_paid': '标记已支付',
            'confirm_transaction': '确认交易',
            'cancel_transaction': '取消交易',
            'batch_confirm_transactions': '批量确认交易',
            'export_transactions': '导出交易',
            'export_stats': '导出统计'
        }
        
        for idx, log in enumerate(logs, 1):
            time_str = log['created_at'][:16] if len(log['created_at']) > 16 else log['created_at']
            op_name = type_names.get(log['operation_type'], log['operation_type'])
            user_name = log['first_name'] or log['username'] or f"用户{log['user_id']}"
            
            message += f"{idx}. <b>{op_name}</b>\n"
            message += f"   用户: {user_name}\n"
            message += f"   时间: {time_str}\n"
            if log['description']:
                message += f"   说明: {log['description']}\n"
            if log['target_type'] and log['target_id']:
                message += f"   目标: {log['target_type']} {log['target_id']}\n"
            message += "\n"
        
        # Keyboard
        keyboard = []
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"logs_page_{page - 1}"))
        nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="none"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"logs_page_{page + 1}"))
        keyboard.append(nav_buttons)
        
        keyboard.append([
            InlineKeyboardButton("🔍 筛选", callback_data="logs_filter"),
            InlineKeyboardButton("🔙 返回", callback_data="main_menu")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
                await update.callback_query.answer()
            except BadRequest as e:
                if "not modified" in str(e).lower():
                    await update.callback_query.answer("✅ 内容未更改")
                else:
                    raise
        else:
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
        logger.info(f"Admin {user_id} viewed operation logs (page {page})")
        
    except Exception as e:
        logger.error(f"Error in handle_view_logs: {e}", exc_info=True)
        try:
            if update.callback_query:
                await update.callback_query.answer(f"❌ 错误: {str(e)}", show_alert=True)
            else:
                await update.message.reply_text(f"❌ 错误: {str(e)}")
        except Exception as inner_e:
            logger.error(f"Error sending error message: {inner_e}", exc_info=True)


async def handle_logs_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    """Handle logs pagination"""
    await handle_view_logs(update, context, page=page)


async def handle_logs_filter_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show logs filter menu"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        message = (
            "🔍 <b>日志筛选</b>\n\n"
            "请选择筛选条件：\n\n"
            "💡 <i>提示：可组合多个筛选条件</i>"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📋 全部日志", callback_data="logs_view_all"),
                InlineKeyboardButton("📅 日期筛选", callback_data="logs_filter_date")
            ],
            [
                InlineKeyboardButton("🔙 返回", callback_data="logs_view_1")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_logs_filter_menu: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误", show_alert=True)

