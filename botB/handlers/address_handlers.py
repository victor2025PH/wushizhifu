"""
Address management handlers for Bot B
Handles multiple USDT address management
"""
import logging
from typing import Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import db
from admin_checker import is_admin

logger = logging.getLogger(__name__)


async def handle_address_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle address list display"""
    try:
        query = update.callback_query if hasattr(update, 'callback_query') and update.callback_query else None
        user = (query.from_user if query else update.effective_user)
        user_id = user.id
        
        if not is_admin(user_id):
            await (query or update.message).reply_text("❌ 此功能仅限管理员使用")
            return
        
        chat = update.effective_chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        
        addresses = db.get_usdt_addresses(group_id=group_id, active_only=False)
        
        if not addresses:
            scope = "群组" if group_id else "全局"
            message = (
                f"📍 <b>{scope}地址管理</b>\n\n"
                f"暂无配置的地址。\n\n"
                f"点击「➕ 添加地址」开始添加"
            )
        else:
            scope = "群组" if group_id else "全局"
            active_count = sum(1 for a in addresses if a['is_active'])
            message = (
                f"📍 <b>{scope}地址管理</b>\n\n"
                f"共 {len(addresses)} 个地址（{active_count} 个启用）\n"
                f"────────────────────────\n\n"
            )
            
            for idx, addr in enumerate(addresses, 1):
                status_icon = "✅" if addr['is_active'] else "❌"
                default_icon = "⭐" if addr['is_default'] else ""
                addr_display = addr['address'][:15] + "..." + addr['address'][-15:] if len(addr['address']) > 30 else addr['address']
                
                message += (
                    f"{idx}. {status_icon} {default_icon} <b>{addr['label'] or '未命名'}</b>\n"
                    f"   <code>{addr_display}</code>\n"
                    f"   使用次数: {addr['usage_count']}\n"
                )
                if addr['last_used_at']:
                    message += f"   最后使用: {addr['last_used_at'][:16]}\n"
                message += "\n"
        
        keyboard = [
            [
                InlineKeyboardButton("➕ 添加地址", callback_data="address_add"),
                InlineKeyboardButton("🔄 刷新", callback_data="address_list")
            ],
            [
                InlineKeyboardButton("🔙 返回", callback_data="main_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
        else:
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_address_list: {e}", exc_info=True)
        await (query or update.message).reply_text("❌ 错误: " + str(e))


async def handle_address_add_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle address add prompt"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        chat = query.message.chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        
        scope = "群组" if group_id else "全局"
        
        message = (
            f"➕ <b>添加{scope}地址</b>\n\n"
            f"请输入 USDT 地址：\n\n"
            f"💡 <i>提示：地址格式应为有效的 USDT 钱包地址</i>"
        )
        
        await query.edit_message_text(message, parse_mode="HTML")
        
        context.user_data['adding_address'] = True
        context.user_data['address_group_id'] = group_id
        
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_address_add_prompt: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误", show_alert=True)


async def handle_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE, address_text: str):
    """Handle address input"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if 'adding_address' not in context.user_data:
            return
        
        group_id = context.user_data.get('address_group_id')
        address = address_text.strip()
        
        # Basic validation (USDT addresses are typically 34-42 characters)
        if len(address) < 26 or len(address) > 60:
            await update.message.reply_text("❌ 地址格式无效，USDT 地址应为 26-60 个字符")
            return
        
        # Check if address already exists
        existing = db.get_usdt_addresses(group_id=group_id, active_only=False)
        if any(a['address'] == address for a in existing):
            await update.message.reply_text("❌ 该地址已存在")
            return
        
        # Add address
        scope = "群组" if group_id else "全局"
        if db.add_usdt_address(group_id=group_id, address=address, label=f"{scope}地址", created_by=user_id):
            message = (
                f"✅ <b>地址已添加</b>\n\n"
                f"范围: {scope}\n"
                f"地址: <code>{address[:20]}...</code>\n\n"
                f"💡 提示：您可以在地址列表中设置默认地址"
            )
            await update.message.reply_text(message, parse_mode="HTML")
            
            # Clean up context
            del context.user_data['adding_address']
            del context.user_data['address_group_id']
            
            logger.info(f"Admin {user_id} added address (group_id: {group_id})")
        else:
            await update.message.reply_text("❌ 添加地址失败，请重试")
        
    except Exception as e:
        logger.error(f"Error in handle_address_input: {e}", exc_info=True)
        await update.message.reply_text("❌ 错误: " + str(e))

