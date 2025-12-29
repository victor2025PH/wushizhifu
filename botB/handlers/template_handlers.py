"""
Template handlers for Bot B
Handles template selection and management
"""
import logging
from typing import Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import db
from services.template_service import get_all_templates, format_template_display_name, get_template_by_id
from handlers.message_handlers import handle_math_settlement

logger = logging.getLogger(__name__)


async def handle_template_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle template selection menu"""
    try:
        query = update.callback_query if hasattr(update, 'callback_query') and update.callback_query else None
        user = (query.from_user if query else update.effective_user)
        user_id = user.id
        
        templates = get_all_templates(user_id=user_id)
        
        message = "💰 <b>快速结算模板</b>\n\n"
        message += "请选择模板类型：\n\n"
        message += f"💡 常用金额模板：{len(templates['amount'])} 个\n"
        message += f"📝 常用算式模板：{len(templates['formula'])} 个\n"
        
        keyboard = [
            [
                InlineKeyboardButton("💰 金额模板", callback_data="template_list_amount"),
                InlineKeyboardButton("📝 算式模板", callback_data="template_list_formula")
            ],
            [
                InlineKeyboardButton("➕ 添加模板", callback_data="template_create"),
                InlineKeyboardButton("📋 我的模板", callback_data="template_list_user")
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
        logger.error(f"Error in handle_template_menu: {e}", exc_info=True)
        await (query or update.message).reply_text("❌ 错误: " + str(e))


async def handle_template_list(update: Update, context: ContextTypes.DEFAULT_TYPE, template_type: str):
    """Handle template list display - shows max 10 templates"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        # Get templates with limit of 10 per type
        templates = get_all_templates(user_id=user_id, limit=10)
        template_list = templates.get(template_type, [])
        
        if not template_list:
            type_name = "金额" if template_type == 'amount' else "算式"
            await query.answer(f"暂无{type_name}模板", show_alert=True)
            return
        
        # Limit to 10 templates maximum
        template_list = template_list[:10]
        
        # Build keyboard with templates
        keyboard = []
        
        # Group templates in rows of 2
        for i in range(0, len(template_list), 2):
            row = []
            for j in range(2):
                if i + j < len(template_list):
                    template = template_list[i + j]
                    display_name = format_template_display_name(template)
                    # Truncate if too long
                    if len(display_name) > 12:
                        display_name = display_name[:10] + "..."
                    row.append(
                        InlineKeyboardButton(
                            display_name,
                            callback_data=f"template_use_{template['id']}"
                        )
                    )
            keyboard.append(row)
        
        keyboard.append([
            InlineKeyboardButton("🔙 返回", callback_data="template_menu")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        type_name = "金额" if template_type == 'amount' else "算式"
        message = f"💰 <b>{type_name}模板</b>\n\n"
        message += f"共 {len(template_list)} 个模板\n"
        message += "请选择要使用的模板："
        
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_template_list: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误", show_alert=True)


async def handle_template_use(update: Update, context: ContextTypes.DEFAULT_TYPE, template_id: int):
    """Handle template usage - apply template for settlement"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        template = get_template_by_id(template_id)
        
        if not template:
            await query.answer("❌ 模板不存在", show_alert=True)
            return
        
        # Increment usage count
        db.increment_template_usage(template_id)
        
        # Use the template value for settlement
        template_value = template['template_value']
        
        # Delete the template menu message
        try:
            await query.message.delete()
        except:
            pass
        
        # Create a message update from template value
        # We'll simulate a message by directly calling the settlement handler
        # But first, let's inform the user
        await query.answer(f"✅ 正在应用模板: {template_value}")
        
        # Create a simple text message update simulation
        # Actually, we can just send a message with the template value
        # and let the normal message handler process it
        from telegram import Message, Chat, User
        
        # Send the template value as if user typed it
        # This will trigger the normal settlement flow
        await query.message.chat.send_message(template_value)
        
        logger.info(f"User {user_id} used template {template_id}: {template_value}")
        
    except Exception as e:
        logger.error(f"Error in handle_template_use: {e}", exc_info=True)
        await update.callback_query.answer("❌ 应用模板失败", show_alert=True)


async def handle_template_create_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle template creation menu"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        message = (
            "➕ <b>创建模板</b>\n\n"
            "请选择模板类型：\n\n"
            "💡 <i>提示：</i>\n"
            "• 金额模板：直接输入数字（如：10000）\n"
            "• 算式模板：输入算式（如：20000-200）"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("💰 金额模板", callback_data="template_create_amount"),
                InlineKeyboardButton("📝 算式模板", callback_data="template_create_formula")
            ],
            [
                InlineKeyboardButton("🔙 返回", callback_data="template_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_template_create_menu: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误", show_alert=True)


async def handle_template_create_type(update: Update, context: ContextTypes.DEFAULT_TYPE, template_type: str):
    """Handle template type selection for creation"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        type_name = "金额" if template_type == 'amount' else "算式"
        
        message = (
            f"➕ <b>创建{type_name}模板</b>\n\n"
            f"请输入模板名称和值：\n\n"
        )
        
        if template_type == 'amount':
            message += (
                "<b>示例：</b>\n"
                "名称: 常用金额\n"
                "值: 10000\n\n"
                "或直接输入金额数字（将自动创建）"
            )
        else:
            message += (
                "<b>示例：</b>\n"
                "名称: 常用算式\n"
                "值: 20000-200\n\n"
                "或直接输入算式（将自动创建）"
            )
        
        await query.edit_message_text(message, parse_mode="HTML")
        
        context.user_data['creating_template_type'] = template_type
        context.user_data['awaiting_template_input'] = True
        
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_template_create_type: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误", show_alert=True)


async def handle_template_input(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str):
    """Handle template input"""
    try:
        user_id = update.effective_user.id
        
        template_type = context.user_data.get('creating_template_type')
        if not template_type:
            await update.message.reply_text("❌ 请重新选择模板类型")
            return
        
        # Parse input
        # Format 1: "名称: 值" or "名称 值"
        # Format 2: Just the value (auto-generate name)
        
        template_name = None
        template_value = None
        
        if ':' in input_text:
            parts = input_text.split(':', 1)
            template_name = parts[0].strip()
            template_value = parts[1].strip()
        elif ' ' in input_text:
            parts = input_text.split(' ', 1)
            template_name = parts[0].strip()
            template_value = parts[1].strip()
        else:
            # Just value, auto-generate name
            template_value = input_text.strip()
            if template_type == 'amount':
                try:
                    amount = float(template_value)
                    if amount >= 10000:
                        template_name = f"{amount/10000:.1f}万"
                    else:
                        template_name = f"{amount:,.0f}"
                except:
                    template_name = template_value
            else:
                template_name = template_value
        
        # Validate template value
        if template_type == 'amount':
            try:
                float(template_value)
            except ValueError:
                await update.message.reply_text("❌ 金额模板必须是有效数字")
                return
        
        # Create template
        if db.create_template(user_id, template_name, template_value, template_type):
            message = (
                f"✅ <b>模板已创建</b>\n\n"
                f"名称: {template_name}\n"
                f"值: {template_value}\n\n"
                f"💡 您可以在快速结算中使用此模板"
            )
            await update.message.reply_text(message, parse_mode="HTML")
            
            # Clean up context
            del context.user_data['creating_template_type']
            del context.user_data['awaiting_template_input']
            
            logger.info(f"User {user_id} created template: {template_name} = {template_value}")
        else:
            await update.message.reply_text("❌ 创建模板失败，请重试")
        
    except Exception as e:
        logger.error(f"Error in handle_template_input: {e}", exc_info=True)
        await update.message.reply_text("❌ 错误: " + str(e))

