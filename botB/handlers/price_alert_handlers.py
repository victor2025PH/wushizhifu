"""
Price alert handlers for Bot B
Handles price alert commands and UI
"""
import logging
from typing import Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import db
from services.price_service import get_price_with_markup

logger = logging.getLogger(__name__)


async def handle_price_alert_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle price alert menu"""
    try:
        if update.message:
            message_target = update.message
        elif update.callback_query and update.callback_query.message:
            message_target = update.callback_query.message
            query = update.callback_query
        else:
            logger.error("handle_price_alert_menu: No message target found")
            return
        
        user_id = update.effective_user.id
        
        message = (
            "🔔 <b>价格预警管理</b>\n\n"
            "请选择操作：\n\n"
            "💡 <i>提示：当价格达到设定条件时，Bot 会自动通知您</i>"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("➕ 创建预警", callback_data="alert_create"),
                InlineKeyboardButton("📋 我的预警", callback_data="alerts_list")
            ],
            [
                InlineKeyboardButton("📊 价格历史", callback_data="price_history_24"),
                InlineKeyboardButton("🔙 返回", callback_data="main_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await message_target.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        elif update.callback_query:
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_price_alert_menu: {e}", exc_info=True)
        try:
            if update.message:
                await update.message.reply_text("❌ 错误: " + str(e))
            elif update.callback_query:
                await update.callback_query.answer("❌ 错误: " + str(e), show_alert=True)
        except:
            pass


async def handle_create_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle alert creation menu"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        message = (
            "🔔 <b>创建价格预警</b>\n\n"
            "请选择预警类型：\n\n"
            "💡 <i>提示：当价格达到设定条件时，Bot 会自动通知您</i>"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📈 价格高于", callback_data="alert_type_above"),
                InlineKeyboardButton("📉 价格低于", callback_data="alert_type_below")
            ],
            [
                InlineKeyboardButton("🔙 返回", callback_data="alerts_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_create_alert: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误", show_alert=True)


async def handle_alert_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE, alert_type: str):
    """Handle alert type selection"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        alert_type_map = {
            'above': ('价格高于', '>'),
            'below': ('价格低于', '<')
        }
        
        type_name, operator = alert_type_map.get(alert_type, ('未知', '>'))
        
        # Store alert type in context
        context.user_data['creating_alert_type'] = alert_type
        context.user_data['creating_alert_operator'] = operator
        
        message = (
            f"🔔 <b>创建价格预警</b>\n\n"
            f"预警类型: {type_name}\n\n"
            f"请输入价格阈值（例如：7.50）：\n\n"
            f"💡 <i>当价格{type_name}此值时，您将收到通知</i>"
        )
        
        await query.edit_message_text(message, parse_mode="HTML")
        context.user_data['awaiting_alert_threshold'] = True
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_alert_type_selected: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误", show_alert=True)


async def handle_alert_threshold_input(update: Update, context: ContextTypes.DEFAULT_TYPE, threshold_text: str):
    """Handle alert threshold input"""
    try:
        user_id = update.effective_user.id
        
        try:
            threshold = float(threshold_text.strip())
            if threshold <= 0:
                await update.message.reply_text("❌ 价格阈值必须大于 0")
                return
        except ValueError:
            await update.message.reply_text("❌ 请输入有效的数字")
            return
        
        alert_type = context.user_data.get('creating_alert_type')
        operator = context.user_data.get('creating_alert_operator')
        
        if not alert_type or not operator:
            await update.message.reply_text("❌ 请重新选择预警类型")
            return
        
        # Create alert
        alert_type_name = 'price_above' if alert_type == 'above' else 'price_below'
        
        if db.create_price_alert(user_id, alert_type_name, threshold, operator):
            # Get current price for display
            current_price, _, _, _ = get_price_with_markup(group_id=None, save_history=False)
            
            message = (
                f"✅ <b>价格预警已创建</b>\n\n"
                f"预警类型: 价格{operator} {threshold:.4f} CNY\n"
                f"当前价格: {current_price:.4f} CNY\n\n"
                f"💡 当价格达到设定条件时，您将收到通知"
            )
            
            await update.message.reply_text(message, parse_mode="HTML")
            
            # Clean up context
            del context.user_data['creating_alert_type']
            del context.user_data['creating_alert_operator']
            del context.user_data['awaiting_alert_threshold']
            
            logger.info(f"User {user_id} created price alert: {alert_type_name} {operator} {threshold}")
        else:
            await update.message.reply_text("❌ 创建预警失败，请重试")
        
    except Exception as e:
        logger.error(f"Error in handle_alert_threshold_input: {e}", exc_info=True)
        await update.message.reply_text("❌ 错误: " + str(e))


async def handle_list_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle listing user's alerts"""
    try:
        query = update.callback_query if hasattr(update, 'callback_query') and update.callback_query else None
        user_id = (query.from_user if query else update.effective_user).id
        
        alerts = db.get_user_alerts(user_id, active_only=False)
        
        if not alerts:
            message = (
                "📋 <b>我的价格预警</b>\n\n"
                "您还没有创建任何价格预警。\n\n"
                "点击「➕ 创建预警」开始设置"
            )
        else:
            active_count = sum(1 for a in alerts if a['is_active'])
            message = (
                f"📋 <b>我的价格预警</b>\n\n"
                f"共 {len(alerts)} 个预警（{active_count} 个启用）\n"
                f"────────────────────────\n\n"
            )
            
            for idx, alert in enumerate(alerts, 1):
                status_icon = "✅" if alert['is_active'] else "❌"
                alert_type_name = "价格高于" if 'above' in alert['alert_type'] else "价格低于"
                operator = alert['comparison_operator']
                
                message += (
                    f"{idx}. {status_icon} <b>{alert_type_name}</b>\n"
                    f"   阈值: {operator} {alert['threshold_value']:.4f} CNY\n"
                    f"   通知次数: {alert['notification_count']}\n"
                )
                if alert['last_notified_at']:
                    message += f"   最后通知: {alert['last_notified_at']}\n"
                message += f"   <code>/alert_toggle_{alert['id']}</code>\n\n"
        
        keyboard = [
            [
                InlineKeyboardButton("➕ 创建预警", callback_data="alert_create"),
                InlineKeyboardButton("🔄 刷新", callback_data="alerts_list")
            ],
            [
                InlineKeyboardButton("📊 价格历史", callback_data="price_history_24"),
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
        logger.error(f"Error in handle_list_alerts: {e}", exc_info=True)
        await (query or update.message).reply_text("❌ 错误: " + str(e))


async def handle_price_history(update: Update, context: ContextTypes.DEFAULT_TYPE, hours: int = 24):
    """Handle price history query"""
    try:
        user_id = update.effective_user.id
        
        history = db.get_price_history(hours=hours, limit=100)
        stats = db.get_price_stats(hours=hours)
        
        if not history:
            await update.message.reply_text(f"📊 过去 {hours} 小时内暂无价格历史记录")
            return
        
        message = (
            f"📊 <b>价格历史</b>\n\n"
            f"时间范围: 过去 {hours} 小时\n"
            f"记录数: {stats.get('count', 0)}\n"
            f"────────────────────────\n\n"
        )
        
        if stats.get('count', 0) > 0:
            message += (
                f"📈 <b>统计信息</b>\n"
                f"最低: {stats['min_final']:.4f} CNY\n"
                f"最高: {stats['max_final']:.4f} CNY\n"
                f"平均: {stats['avg_final']:.4f} CNY\n\n"
            )
        
        message += "<b>最近记录（最多10条）：</b>\n\n"
        
        for idx, record in enumerate(history[:10], 1):
            time_str = record['created_at'][:16] if len(record['created_at']) > 16 else record['created_at']
            message += (
                f"{idx}. {time_str}\n"
                f"   最终价: {record['final_price']:.4f} CNY\n"
                f"   基础价: {record['base_price']:.4f} CNY\n\n"
            )
        
        keyboard = [
            [
                InlineKeyboardButton("📅 24小时", callback_data="price_history_24"),
                InlineKeyboardButton("📅 7天", callback_data="price_history_168")
            ],
            [
                InlineKeyboardButton("📅 30天", callback_data="price_history_720"),
                InlineKeyboardButton("🔔 预警管理", callback_data="alerts_list")
            ],
            [
                InlineKeyboardButton("🔙 返回", callback_data="main_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_price_history: {e}", exc_info=True)
        await update.message.reply_text("❌ 错误: " + str(e))

