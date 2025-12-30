"""
Customer Service Management Handlers
Handles customer service account management callbacks
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from admin_checker import is_admin
from services.customer_service_service import customer_service
from keyboards.inline_keyboard import (
    get_customer_service_management_menu,
    get_customer_service_list_keyboard,
    get_customer_service_edit_keyboard,
    get_customer_service_strategy_keyboard
)
from database import db

logger = logging.getLogger(__name__)


async def handle_customer_service_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle customer service management menu"""
    query = update.callback_query
    callback_data = query.data
    
    if not is_admin(query.from_user.id):
        await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
        return
    
    try:
        if callback_data == "customer_service_management":
            message = (
                "👥 <b>客服管理</b>\n\n"
                "请选择要执行的操作：\n\n"
                "• <b>客服账号列表</b>：查看和管理所有客服账号\n"
                "• <b>添加客服账号</b>：添加新的客服账号\n"
                "• <b>分配策略设置</b>：配置客服分配方式\n"
                "• <b>客服统计报表</b>：查看客服工作统计"
            )
            reply_markup = get_customer_service_management_menu()
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
            return
        
        elif callback_data == "customer_service_list" or callback_data.startswith("customer_service_list_page_"):
            await handle_customer_service_list(update, context)
            return
        
        elif callback_data.startswith("customer_service_edit_"):
            await handle_customer_service_edit(update, context)
            return
        
        elif callback_data.startswith("customer_service_toggle_"):
            await handle_customer_service_toggle(update, context)
            return
        
        elif callback_data.startswith("customer_service_delete_"):
            await handle_customer_service_delete(update, context)
            return
        
        elif callback_data == "customer_service_add":
            await handle_customer_service_add(update, context)
            return
        
        elif callback_data == "customer_service_strategy" or callback_data.startswith("customer_service_strategy_set_"):
            await handle_customer_service_strategy(update, context)
            return
        
        elif callback_data == "customer_service_stats":
            await handle_customer_service_stats(update, context)
            return
        
    except Exception as e:
        logger.error(f"Error in handle_customer_service_management: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_customer_service_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle customer service account list"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        # Parse page number if present
        page = 0
        if callback_data.startswith("customer_service_list_page_"):
            page = int(callback_data.split("_")[-1])
        
        # Get all accounts
        accounts = customer_service.get_all_accounts(active_only=False)
        
        if not accounts:
            message = "📋 <b>客服账号列表</b>\n\n暂无客服账号。\n\n请点击「➕ 添加客服账号」添加第一个客服账号。"
            reply_markup = get_customer_service_list_keyboard([], page=0)
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
            return
        
        # Format message
        start_idx = page * 10
        end_idx = min(start_idx + 10, len(accounts))
        page_accounts = accounts[start_idx:end_idx]
        
        message = f"📋 <b>客服账号列表</b>\n\n"
        message += f"共 {len(accounts)} 个账号（显示第 {start_idx + 1}-{end_idx} 个）\n\n"
        
        for idx, account in enumerate(page_accounts, start=start_idx + 1):
            status_emoji = "🟢" if account['status'] == 'available' else \
                          "🟡" if account['status'] == 'busy' else \
                          "🔴" if account['status'] == 'offline' else "⚫"
            active_icon = "✅" if account['is_active'] else "❌"
            message += (
                f"{idx}. {active_icon} <b>{account['display_name']}</b>\n"
                f"   状态：{status_emoji} {account['status']}\n"
                f"   权重：{account['weight']} | 当前接待：{account['current_count']}/{account['max_concurrent']}\n"
                f"   累计接待：{account['total_served']} 次\n\n"
            )
        
        reply_markup = get_customer_service_list_keyboard(accounts, page=page)
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_customer_service_list: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_customer_service_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle customer service account edit view"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        # Parse account_id
        account_id = int(callback_data.split("_")[-1])
        
        # Get account info
        account = customer_service.get_account(account_id=account_id)
        if not account:
            await query.answer("❌ 客服账号不存在", show_alert=True)
            return
        
        # Format message
        status_display = customer_service.get_status_display(account['status'])
        active_text = "启用" if account['is_active'] else "禁用"
        
        message = f"⚙️ <b>编辑客服账号</b>\n\n"
        message += f"<b>用户名：</b>@{account['username']}\n"
        message += f"<b>显示名称：</b>{account['display_name']}\n"
        message += f"<b>状态：</b>{status_display}\n"
        message += f"<b>账号状态：</b>{active_text}\n"
        message += f"<b>权重：</b>{account['weight']} (1-10)\n"
        message += f"<b>最大同时接待：</b>{account['max_concurrent']}\n"
        message += f"<b>当前接待：</b>{account['current_count']}\n"
        message += f"<b>累计接待：</b>{account['total_served']} 次\n"
        
        reply_markup = get_customer_service_edit_keyboard(account_id)
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_customer_service_edit: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_customer_service_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle toggle customer service account active status"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        # Parse account_id
        account_id = int(callback_data.split("_")[-1])
        
        # Toggle account
        success = customer_service.toggle_account(account_id)
        if not success:
            await query.answer("❌ 操作失败", show_alert=True)
            return
        
        # Get updated account info
        account = customer_service.get_account(account_id=account_id)
        if not account:
            await query.answer("❌ 客服账号不存在", show_alert=True)
            return
        
        # Update message
        active_text = "已启用" if account['is_active'] else "已禁用"
        await query.answer(f"✅ 客服账号{active_text}", show_alert=False)
        
        # Refresh edit view
        await handle_customer_service_edit(update, context)
        
    except Exception as e:
        logger.error(f"Error in handle_customer_service_toggle: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_customer_service_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delete customer service account"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        # Parse account_id
        account_id = int(callback_data.split("_")[-1])
        
        # Get account info for confirmation
        account = customer_service.get_account(account_id=account_id)
        if not account:
            await query.answer("❌ 客服账号不存在", show_alert=True)
            return
        
        # Delete account
        success = customer_service.delete_account(account_id)
        if not success:
            await query.answer("❌ 删除失败", show_alert=True)
            return
        
        await query.answer("✅ 客服账号已删除", show_alert=False)
        
        # Return to list
        await handle_customer_service_list(update, context)
        
    except Exception as e:
        logger.error(f"Error in handle_customer_service_delete: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_customer_service_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add customer service account (prompt for input)"""
    query = update.callback_query
    
    try:
        message = (
            "➕ <b>添加客服账号</b>\n\n"
            "请输入客服账号用户名（不含@）：\n\n"
            "💡 <i>提示：输入格式如 wushizhifu_support2</i>"
        )
        
        # Set user data to indicate we're waiting for input
        context.user_data['waiting_for'] = 'customer_service_username'
        
        await query.edit_message_text(message, parse_mode="HTML")
        await query.answer("请在对话框中输入客服账号用户名")
        
    except Exception as e:
        logger.error(f"Error in handle_customer_service_add: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_customer_service_strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle customer service assignment strategy settings"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        # Get current strategy from settings (default: smart)
        all_settings = db.get_all_settings()
        current_method = all_settings.get('customer_service_strategy', 'smart')
        
        # Handle strategy change
        if callback_data.startswith("customer_service_strategy_set_"):
            method = callback_data.split("_")[-1]
            
            # Save to settings
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES ('customer_service_strategy', ?, CURRENT_TIMESTAMP)
            """, (method,))
            conn.commit()
            
            current_method = method
            method_display = customer_service.get_assignment_method_display_name(method)
            await query.answer(f"✅ 分配策略已设置为：{method_display}", show_alert=False)
        
        # Format message
        method_display = customer_service.get_assignment_method_display_name(current_method)
        message = f"⚙️ <b>分配策略设置</b>\n\n"
        message += f"当前策略：<b>{method_display}</b>\n\n"
        message += "可选策略：\n"
        message += "• <b>智能混合分配</b>：综合考虑在线状态、工作量、权重（推荐）\n"
        message += "• <b>简单轮询</b>：按顺序依次分配\n"
        message += "• <b>最少任务优先</b>：分配给当前接待最少的客服\n"
        message += "• <b>权重分配</b>：按权重比例分配\n"
        
        reply_markup = get_customer_service_strategy_keyboard(current_method=current_method)
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_customer_service_strategy: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_customer_service_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle customer service statistics"""
    query = update.callback_query
    
    try:
        stats = customer_service.get_stats()
        
        message = f"📊 <b>客服统计报表</b>\n\n"
        message += f"📈 <b>总体统计</b>\n"
        message += f"• 总账号数：{stats['total_accounts']}\n"
        message += f"• 启用账号：{stats['active_accounts']}\n"
        message += f"• 累计接待：{stats['total_served']} 次\n"
        message += f"• 今日接待：{stats['today_served']} 次\n\n"
        
        if stats['accounts']:
            message += f"📋 <b>账号详情</b>\n\n"
            for idx, account in enumerate(stats['accounts'], 1):
                status_display = customer_service.get_status_display(account['status'])
                active_icon = "✅" if account['is_active'] else "❌"
                message += (
                    f"{idx}. {active_icon} <b>{account['display_name']}</b>\n"
                    f"   状态：{status_display}\n"
                    f"   权重：{account['weight']} | 当前：{account['current_count']}/{account['max_concurrent']}\n"
                    f"   累计：{account['total_served']} 次\n\n"
                )
        else:
            message += "暂无客服账号"
        
        from keyboards.inline_keyboard import get_customer_service_management_menu
        reply_markup = get_customer_service_management_menu()
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_customer_service_stats: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)

