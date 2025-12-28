"""
Message handlers for Bot B
Handles admin shortcuts, w0-w9 commands, pinyin commands, and math/settlement processing
"""
import re
import logging
from typing import Optional
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from config import Config
from database import db
from services.price_service import get_price_with_markup
from services.settlement_service import calculate_settlement, format_settlement_bill
from services.math_service import is_number, is_simple_math
from admin_checker import is_admin

logger = logging.getLogger(__name__)


# ========== Helper Functions ==========

def normalize_command(text: str) -> str:
    """Normalize command (case-insensitive)"""
    return text.strip().lower()


def is_pinyin_command(text: str, command: str, pinyin: str) -> bool:
    """Check if text matches w command or pinyin command (case-insensitive)"""
    text_lower = normalize_command(text)
    return text_lower == command.lower() or text_lower == pinyin.lower()


# ========== Admin Command Handlers (w0-w9) ==========

async def handle_admin_w0(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w0/SZ: View current group settings"""
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        group_setting = db.get_group_setting(group_id)
        
        # Get global settings
        global_markup = db.get_admin_markup()
        global_address = db.get_usdt_address()
        
        message = f"📋 <b>当前群组设置</b>\n\n"
        message += "────────────────────────\n"
        message += f"群组: {chat.title or '未知群组'}\n"
        message += f"群组 ID: <code>{group_id}</code>\n\n"
        
        if group_setting:
            message += "<b>当前配置（群组独立）:</b>\n"
            message += f"• 加价: {group_setting['markup']:.4f} CNY\n"
            address_display = group_setting['usdt_address'] if group_setting['usdt_address'] else "未设置"
            if group_setting['usdt_address'] and len(group_setting['usdt_address']) > 20:
                address_display = f"{group_setting['usdt_address'][:10]}...{group_setting['usdt_address'][-10:]}"
            message += f"• USDT 地址: {address_display}\n\n"
        else:
            message += "<b>当前配置:</b> 使用全局默认设置\n\n"
        
        message += "<b>全局默认值:</b>\n"
        message += f"• 加价: {global_markup:.4f} CNY\n"
        global_addr_display = global_address if global_address else "未设置"
        if global_address and len(global_address) > 20:
            global_addr_display = f"{global_address[:10]}...{global_address[-10:]}"
        message += f"• USDT 地址: {global_addr_display}\n"
        message += "────────────────────────\n"
        
        if group_setting:
            message += f"✅ 状态: 使用群组独立设置\n"
            message += f"最后更新: {group_setting.get('updated_at', '未知')}"
        else:
            message += "ℹ️ 状态: 使用全局默认设置"
        
        await update.message.reply_text(message, parse_mode="HTML")
        logger.info(f"Admin {update.effective_user.id} executed w0/SZ in group {group_id}")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w0: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w1/HL: Get current price with markup"""
    try:
        chat = update.effective_chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        
        final_price, error_msg, base_price, markup = get_price_with_markup(group_id)
        
        if final_price is None:
            message = f"❌ 获取价格失败\n\n{error_msg or '未知错误'}"
        else:
            markup_source = "群组" if group_id and db.get_group_setting(group_id) else "全局"
            message = (
                f"💱 <b>USDT/CNY 价格信息</b>\n\n"
                f"📊 Binance P2P 基础价格: {base_price:.4f} CNY\n"
                f"➕ 加价（{markup_source}）: {markup:.4f} CNY\n"
                f"💰 最终价格: {final_price:.4f} CNY\n"
            )
            if error_msg:
                message += f"\n⚠️ 注意: {error_msg}"
        
        await update.message.reply_text(message, parse_mode="HTML")
        logger.info(f"User {update.effective_user.id} executed w1/HL")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w1: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w2(update: Update, context: ContextTypes.DEFAULT_TYPE, markup_value: float):
    """Handle w2/SJJ [number]: Set group markup (only in groups)"""
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        group_title = chat.title
        
        if db.set_group_markup(group_id, markup_value, group_title, update.effective_user.id):
            message = f"✅ 群组加价已设置为: {markup_value:.4f} CNY\n\n"
            message += f"群组: {group_title}\n"
            message += f"加价: {markup_value:+.4f} CNY"
        else:
            message = "❌ 设置失败"
        
        await update.message.reply_text(message)
        logger.info(f"Admin {update.effective_user.id} set group {group_id} markup to {markup_value}")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w2: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w3(update: Update, context: ContextTypes.DEFAULT_TYPE, address: str):
    """Handle w3/SDZ [address]: Set group address (only in groups)"""
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        group_title = chat.title
        
        if db.set_group_address(group_id, address, group_title, update.effective_user.id):
            address_display = address[:15] + "..." + address[-15:] if len(address) > 30 else address
            message = f"✅ 群组 USDT 地址已设置\n\n"
            message += f"群组: {group_title}\n"
            message += f"地址: <code>{address_display}</code>"
        else:
            message = "❌ 设置失败"
        
        await update.message.reply_text(message, parse_mode="HTML")
        logger.info(f"Admin {update.effective_user.id} set group {group_id} address")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w3: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w4/CKQJ: View global settings"""
    try:
        global_markup = db.get_admin_markup()
        global_address = db.get_usdt_address()
        
        message = f"🌐 <b>全局设置</b>\n\n"
        message += "────────────────────────\n"
        message += f"📈 全局默认加价: {global_markup:.4f} CNY\n"
        
        if global_address:
            address_display = global_address[:15] + "..." + global_address[-15:] if len(global_address) > 30 else global_address
            message += f"🔗 全局默认地址: <code>{address_display}</code>\n"
        else:
            message += "🔗 全局默认地址: 未设置\n"
        
        message += "────────────────────────\n"
        message += "ℹ️ 提示: 未配置独立设置的群组将使用此全局默认值"
        
        await update.message.reply_text(message, parse_mode="HTML")
        logger.info(f"Admin {update.effective_user.id} executed w4/CKQJ")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w4: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w5(update: Update, context: ContextTypes.DEFAULT_TYPE, markup_value: float):
    """Handle w5/SQJJ [number]: Set global markup"""
    try:
        if db.set_admin_markup(markup_value):
            message = f"✅ 全局默认加价已设置为: {markup_value:.4f} CNY\n\n"
            message += "ℹ️ 此设置将应用于所有未配置独立加价的群组"
        else:
            message = "❌ 设置失败"
        
        await update.message.reply_text(message)
        logger.info(f"Admin {update.effective_user.id} set global markup to {markup_value}")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w5: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w6(update: Update, context: ContextTypes.DEFAULT_TYPE, address: str):
    """Handle w6/SQJDZ [address]: Set global address"""
    try:
        if db.set_usdt_address(address):
            address_display = address[:15] + "..." + address[-15:] if len(address) > 30 else address
            message = f"✅ 全局默认 USDT 地址已设置\n\n"
            message += f"地址: <code>{address_display}</code>\n\n"
            message += "ℹ️ 此设置将应用于所有未配置独立地址的群组"
        else:
            message = "❌ 设置失败"
        
        await update.message.reply_text(message, parse_mode="HTML")
        logger.info(f"Admin {update.effective_user.id} set global address")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w6: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w7/CKQL: View all configured groups"""
    try:
        groups = db.get_all_groups()
        
        if not groups:
            await update.message.reply_text("📭 暂无已配置的群组\n\n所有群组都在使用全局默认设置")
            return
        
        message = f"📊 <b>所有已配置群组</b>\n\n"
        message += f"共 {len(groups)} 个群组\n"
        message += "────────────────────────\n\n"
        
        for idx, group in enumerate(groups[:20], 1):  # Limit to 20 groups
            message += f"<b>{idx}. {group['group_title'] or '未知群组'}</b>\n"
            message += f"   ID: <code>{group['group_id']}</code>\n"
            message += f"   加价: {group['markup']:+.4f} CNY\n"
            if group['usdt_address']:
                addr = group['usdt_address']
                addr_display = addr[:10] + "..." + addr[-10:] if len(addr) > 20 else addr
                message += f"   地址: <code>{addr_display}</code>\n"
            else:
                message += f"   地址: 未设置（使用全局）\n"
            message += "\n"
        
        if len(groups) > 20:
            message += f"\n... 还有 {len(groups) - 20} 个群组未显示"
        
        await update.message.reply_text(message, parse_mode="HTML")
        logger.info(f"Admin {update.effective_user.id} executed w7/CKQL")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w7: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w8/CZSZ: Reset group settings"""
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        if db.reset_group_settings(group_id):
            message = f"✅ 群组设置已重置\n\n"
            message += f"群组: {chat.title}\n"
            message += "已恢复使用全局默认设置"
        else:
            message = "❌ 重置失败（可能群组未配置独立设置）"
        
        await update.message.reply_text(message)
        logger.info(f"Admin {update.effective_user.id} reset group {group_id} settings")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w8: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w9(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w9/SCSZ: Delete group settings"""
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        if db.delete_group_settings(group_id):
            message = f"✅ 群组配置已删除\n\n"
            message += f"群组: {chat.title}\n"
            message += "已完全删除群组独立配置"
        else:
            message = "❌ 删除失败（可能群组未配置独立设置）"
        
        await update.message.reply_text(message)
        logger.info(f"Admin {update.effective_user.id} deleted group {group_id} settings")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w9: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


# ========== Settlement Handler ==========

async def handle_math_settlement(update: Update, context: ContextTypes.DEFAULT_TYPE, amount_text: str):
    """Handle math expression and calculate settlement with transaction recording"""
    try:
        chat = update.effective_chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        user = update.effective_user
        
        # Calculate settlement with group-specific markup
        settlement_data, error_msg = calculate_settlement(amount_text, group_id)
        
        if settlement_data is None:
            await update.message.reply_text(f"❌ {error_msg}")
            return
        
        # Get USDT address (group-specific or global)
        usdt_address = None
        if group_id:
            group_setting = db.get_group_setting(group_id)
            if group_setting and group_setting.get('usdt_address'):
                usdt_address = group_setting['usdt_address']
        
        if not usdt_address:
            usdt_address = db.get_usdt_address()
        
        # Create transaction record
        transaction_id = db.create_transaction(
            group_id=group_id,
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            cny_amount=settlement_data['cny_amount'],
            usdt_amount=settlement_data['usdt_amount'],
            exchange_rate=settlement_data['final_price'],
            markup=settlement_data['markup'],
            usdt_address=usdt_address or ''
        )
        
        # Format and send settlement bill
        bill_message = format_settlement_bill(settlement_data, usdt_address, transaction_id)
        
        # Add inline keyboard for confirmation
        from keyboards.inline_keyboard import get_settlement_bill_keyboard
        reply_markup = get_settlement_bill_keyboard(transaction_id)
        
        await update.message.reply_text(
            bill_message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        logger.info(f"User {user.id} calculated settlement: {amount_text}, transaction_id: {transaction_id}")
        
    except Exception as e:
        logger.error(f"Error in handle_math_settlement: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 计算错误: {str(e)}")


# ========== Button Handlers ==========

async def handle_price_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle price button click"""
    await handle_admin_w1(update, context)


async def handle_today_bills_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle today bills button click (only in groups)"""
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        transactions = db.get_today_transactions_by_group(group_id)
        stats = db.get_transaction_stats_by_group(group_id)
        
        if not transactions:
            await update.message.reply_text("📭 今日暂无交易记录")
            return
        
        message = f"📊 <b>今日账单统计</b>\n\n"
        message += "────────────────────────\n"
        message += f"群组: {chat.title or '未知群组'}\n"
        import datetime
        message += f"日期: {datetime.date.today().strftime('%Y-%m-%d')}\n\n"
        message += "<b>📈 交易统计:</b>\n"
        message += f"• 交易次数: {stats['count']} 笔\n"
        message += f"• 总金额: {stats['total_cny']:,.2f} CNY\n"
        message += f"• 应结算: {stats['total_usdt']:,.2f} USDT\n"
        message += f"• 平均金额: {stats['avg_cny']:,.2f} CNY\n\n"
        
        message += "<b>📋 最近 5 笔交易:</b>\n"
        for idx, tx in enumerate(transactions[:5], 1):
            time_str = tx['created_at'][:16] if len(tx['created_at']) > 16 else tx['created_at']
            message += f"{idx}. {tx['cny_amount']:,.2f} CNY → {tx['usdt_amount']:,.2f} USDT [{time_str[-5:]}]"
            if tx['first_name']:
                message += f" - {tx['first_name']}"
            message += "\n"
        
        await update.message.reply_text(message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in handle_today_bills_button: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


# ========== Main Message Handler ==========

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main message handler - processes all text messages
    Handles w0-w9 commands, pinyin commands, reply keyboard buttons, and math/settlement calculations
    """
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    user_id = update.effective_user.id
    is_admin_user = is_admin(user_id)
    chat = update.effective_chat
    
    # Handle reply keyboard buttons (optimized text)
    if text in ["💱 汇率", "💱 查看汇率", "📊 查看汇率"]:
        await handle_price_button(update, context)
        return
    
    if text == "📊 今日":
        await handle_today_bills_button(update, context)
        return
    
    if text == "📜 历史":
        # Show history bills (first page)
        from handlers.bills_handlers import handle_history_bills
        await handle_history_bills(update, context, page=1)
        return
    
    if text in ["⚙️ 设置", "⚙️ 管理"]:
        # Show group settings menu (admin only)
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if is_group := chat.type in ['group', 'supergroup']:
            from keyboards.inline_keyboard import get_group_settings_menu
            reply_markup = get_group_settings_menu()
            message = (
                "⚙️ <b>群组设置菜单</b>\n\n"
                "请选择要执行的操作："
            )
        else:
            from keyboards.inline_keyboard import get_global_management_menu
            reply_markup = get_global_management_menu()
            message = (
                "🌐 <b>全局管理菜单</b>\n\n"
                "请选择要执行的操作："
            )
        
        await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        return
    
    if text in ["📈 统计", "📊 数据"]:
        # Show statistics (admin only)
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type in ['group', 'supergroup']:
            from handlers.stats_handlers import handle_group_stats
            await handle_group_stats(update, context)
        else:
            from handlers.stats_handlers import handle_global_stats
            await handle_global_stats(update, context)
        return
    
    if text in ["🔗 收款地址", "🔗 地址"]:
        # Show address (group-specific or global)
        chat = update.effective_chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        usdt_address = None
        
        if group_id:
            group_setting = db.get_group_setting(group_id)
            if group_setting and group_setting.get('usdt_address'):
                usdt_address = group_setting['usdt_address']
        
        if not usdt_address:
            usdt_address = db.get_usdt_address()
        
        if usdt_address:
            address_display = usdt_address[:15] + "..." + usdt_address[-15:] if len(usdt_address) > 30 else usdt_address
            message = f"🔗 USDT 收款地址:\n\n<code>{address_display}</code>"
        else:
            message = "⚠️ USDT 收款地址未设置"
        
        await update.message.reply_text(message, parse_mode="HTML")
        return
    
    if text in ["📞 联系客服", "📞 客服"]:
        contact_message = (
            "📞 <b>联系人工客服</b>\n\n"
            "如有任何问题，请联系管理员：\n"
            "@wushizhifu_jianglai\n\n"
            "或使用以下方式：\n"
            "• 工作时间：7×24小时\n"
            "• 响应时间：通常在5分钟内"
        )
        await update.message.reply_text(contact_message, parse_mode="HTML")
        return
    
    # Handle admin commands (w0-w9 + pinyin)
    if is_admin_user:
        # w0 / SZ - View group settings
        if is_pinyin_command(text, "w0", "sz"):
            await handle_admin_w0(update, context)
            return
        
        # w1 / HL - View price
        if is_pinyin_command(text, "w1", "hl") or text == "w01":
            await handle_admin_w1(update, context)
            return
        
        # w2 / SJJ [number] - Set group markup
        w2_match = re.match(r'^(w2|sjj)\s+(-?\d+\.?\d*)$', text, re.IGNORECASE)
        if w2_match:
            try:
                markup_value = float(w2_match.group(2))
                await handle_admin_w2(update, context, markup_value)
                return
            except ValueError:
                await update.message.reply_text("❌ 格式错误，应为: w2 [数字] 或 SJJ [数字]")
                return
        
        # w3 / SDZ [address] - Set group address
        w3_match = re.match(r'^(w3|sdz)\s+(.+)$', text, re.IGNORECASE)
        if w3_match:
            address = w3_match.group(2).strip()
            await handle_admin_w3(update, context, address)
            return
        
        # w4 / CKQJ - View global settings
        if is_pinyin_command(text, "w4", "ckqj"):
            await handle_admin_w4(update, context)
            return
        
        # w5 / SQJJ [number] - Set global markup
        w5_match = re.match(r'^(w5|sqjj)\s+(-?\d+\.?\d*)$', text, re.IGNORECASE)
        if w5_match:
            try:
                markup_value = float(w5_match.group(2))
                await handle_admin_w5(update, context, markup_value)
                return
            except ValueError:
                await update.message.reply_text("❌ 格式错误，应为: w5 [数字] 或 SQJJ [数字]")
                return
        
        # w6 / SQJDZ [address] - Set global address
        w6_match = re.match(r'^(w6|sqjdz)\s+(.+)$', text, re.IGNORECASE)
        if w6_match:
            address = w6_match.group(2).strip()
            await handle_admin_w6(update, context, address)
            return
        
        # w7 / CKQL - View all groups
        if is_pinyin_command(text, "w7", "ckql"):
            await handle_admin_w7(update, context)
            return
        
        # w8 / CZSZ - Reset group settings
        if is_pinyin_command(text, "w8", "czsz") or text == "w08":
            await handle_admin_w8(update, context)
            return
        
        # w9 / SCSZ - Delete group settings
        if is_pinyin_command(text, "w9", "scsz"):
            await handle_admin_w9(update, context)
            return
        
        # Legacy commands (backward compatibility)
        if text == "w01":
            await handle_admin_w1(update, context)
            return
        
        w02_match = re.match(r'^w02\s+(-?\d+\.?\d*)$', text)
        if w02_match:
            try:
                markup_value = float(w02_match.group(1))
                # w02 in group = w2 (group), w02 in private = w5 (global)
                chat = update.effective_chat
                if chat.type in ['group', 'supergroup']:
                    await handle_admin_w2(update, context, markup_value)
                else:
                    await handle_admin_w5(update, context, markup_value)
                return
            except ValueError:
                await update.message.reply_text("❌ w02 格式错误，应为: w02 [数字]")
                return
        
        w03_match = re.match(r'^w03\s+(\d+\.?\d*)$', text)
        if w03_match:
            try:
                markdown_value = float(w03_match.group(1))
                markup_value = -markdown_value
                chat = update.effective_chat
                if chat.type in ['group', 'supergroup']:
                    await handle_admin_w2(update, context, markup_value)
                else:
                    await handle_admin_w5(update, context, markup_value)
                return
            except ValueError:
                await update.message.reply_text("❌ w03 格式错误，应为: w03 [数字]")
                return
        
        if text == "w04":
            await handle_admin_w4(update, context)
            return
    
    # Check if message is a number or math expression (settlement calculation)
    if is_number(text) or is_simple_math(text):
        await handle_math_settlement(update, context, text)
        return
    
    # Otherwise, ignore the message


def get_message_handler():
    """Get message handler instance"""
    return MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
