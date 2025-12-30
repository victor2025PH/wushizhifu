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
from services.settlement_service import (
    calculate_settlement, format_settlement_bill,
    calculate_batch_settlement, format_batch_settlement_bills
)
from services.math_service import is_number, is_simple_math, is_batch_amounts
from services.search_service import parse_amount_range, parse_date_range
from admin_checker import is_admin

logger = logging.getLogger(__name__)


# ========== Helper Functions ==========

async def send_group_message(update: Update, text: str, parse_mode: Optional[str] = None, reply_markup=None, inline_keyboard=None):
    """
    Send a message in a group with reply keyboard attached.
    This ensures the bottom keyboard is always shown in group messages.
    
    Args:
        update: Telegram Update object
        text: Message text
        parse_mode: Parse mode (HTML, Markdown, etc.)
        reply_markup: Optional inline keyboard (InlineKeyboardMarkup)
        inline_keyboard: Alias for reply_markup (for clarity)
    """
    chat = update.effective_chat
    user = update.effective_user
    
    # Determine if this is a group
    is_group = chat.type in ['group', 'supergroup']
    
    # Use inline_keyboard parameter if provided, otherwise use reply_markup
    inline_markup = inline_keyboard or reply_markup
    
    # Determine message target - handle both message and callback_query cases
    if update.message:
        message_target = update.message
    elif update.callback_query and update.callback_query.message:
        message_target = update.callback_query.message
    else:
        logger.error("No message target found in update for send_group_message")
        return
    
    # Get reply keyboard if in group (always show in groups)
    if is_group:
        from keyboards.reply_keyboard import get_main_reply_keyboard
        user_info = {
            'id': user.id,
            'first_name': user.first_name or '',
            'username': user.username,
            'language_code': user.language_code
        }
        reply_keyboard = get_main_reply_keyboard(user.id, is_group=True, user_info=user_info)
        
        # If we have an inline keyboard, we need to handle both
        # Telegram allows both inline and reply keyboards, but we'll prioritize inline
        # and ensure reply keyboard is always shown by sending it separately if needed
        if inline_markup:
            # Send message with inline keyboard first
            await message_target.reply_text(
                text,
                parse_mode=parse_mode,
                reply_markup=inline_markup
            )
            # Then send a minimal message with reply keyboard to ensure it's shown
            # Using visible emoji for better reliability than zero-width space
            try:
                await message_target.reply_text("💡", reply_markup=reply_keyboard)
            except Exception as e:
                logger.warning(f"Failed to send reply keyboard after message with inline keyboard: {e}")
        else:
            # No inline keyboard, just use reply keyboard
            await message_target.reply_text(
                text,
                parse_mode=parse_mode,
                reply_markup=reply_keyboard
            )
    else:
        # Not a group, just send normally
        await message_target.reply_text(
            text,
            parse_mode=parse_mode,
            reply_markup=inline_markup
        )

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
            message += f"• 加价: {group_setting['markup']:.4f} USDT\n"
            address_display = group_setting['usdt_address'] if group_setting['usdt_address'] else "未设置"
            if group_setting['usdt_address'] and len(group_setting['usdt_address']) > 20:
                address_display = f"{group_setting['usdt_address'][:10]}...{group_setting['usdt_address'][-10:]}"
            message += f"• USDT 地址: {address_display}\n\n"
        else:
            message += "<b>当前配置:</b> 使用全局默认设置\n\n"
        
        message += "<b>全局默认值:</b>\n"
        message += f"• 加价: {global_markup:.4f} USDT\n"
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
        
        await send_group_message(update, message, parse_mode="HTML")
        logger.info(f"Admin {update.effective_user.id} executed w0/SZ in group {group_id}")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w0: {e}", exc_info=True)
        await send_group_message(update, f"❌ 错误: {str(e)}")


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
                f"➕ 加价（{markup_source}）: {markup:.4f} USDT\n"
                f"💰 最终价格: {final_price:.4f} CNY\n"
            )
            if error_msg:
                message += f"\n⚠️ 注意: {error_msg}"
        
        await send_group_message(update, message, parse_mode="HTML")
        logger.info(f"User {update.effective_user.id} executed w1/HL")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w1: {e}", exc_info=True)
        await send_group_message(update, f"❌ 错误: {str(e)}")


async def handle_admin_w2(update: Update, context: ContextTypes.DEFAULT_TYPE, markup_value: float):
    """Handle w2/SJJ [number]: Set group markup (only in groups)"""
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        group_title = chat.title
        
        # Get old value for logging
        old_setting = db.get_group_setting(group_id)
        old_markup = old_setting['markup'] if old_setting else None
        
        if db.set_group_markup(group_id, markup_value, group_title, update.effective_user.id):
            # Log operation
            from services.audit_service import log_admin_operation, OperationType
            log_admin_operation(
                OperationType.SET_GROUP_MARKUP,
                update,
                target_type='group',
                target_id=str(group_id),
                description=f"设置群组加价: {markup_value:.4f} USDT",
                old_value=str(old_markup) if old_markup is not None else None,
                new_value=str(markup_value)
            )
            
            message = f"✅ 群组加价已设置为: {markup_value:.4f} USDT\n\n"
            message += f"群组: {group_title}\n"
            message += f"加价: {markup_value:+.4f} USDT"
        else:
            message = "❌ 设置失败"
        
        await send_group_message(update, message)
        logger.info(f"Admin {update.effective_user.id} set group {group_id} markup to {markup_value}")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w2: {e}", exc_info=True)
        await send_group_message(update, f"❌ 错误: {str(e)}")


async def handle_admin_w3(update: Update, context: ContextTypes.DEFAULT_TYPE, address: str):
    """Handle w3/SDZ [address]: Set group address (only in groups)"""
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        group_title = chat.title
        
        # Get old value for logging
        old_setting = db.get_group_setting(group_id)
        old_address = old_setting['usdt_address'] if old_setting else None
        
        if db.set_group_address(group_id, address, group_title, update.effective_user.id):
            # Log operation
            from services.audit_service import log_admin_operation, OperationType
            log_admin_operation(
                OperationType.SET_GROUP_ADDRESS,
                update,
                target_type='group',
                target_id=str(group_id),
                description=f"设置群组 USDT 地址",
                old_value=old_address,
                new_value=address[:20] + "..." if len(address) > 20 else address  # Truncate for privacy
            )
            
            address_display = address[:15] + "..." + address[-15:] if len(address) > 30 else address
            message = f"✅ 群组 USDT 地址已设置\n\n"
            message += f"群组: {group_title}\n"
            message += f"地址: <code>{address_display}</code>"
        else:
            message = "❌ 设置失败"
        
        await send_group_message(update, message, parse_mode="HTML")
        logger.info(f"Admin {update.effective_user.id} set group {group_id} address")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w3: {e}", exc_info=True)
        await send_group_message(update, f"❌ 错误: {str(e)}")


async def handle_admin_w4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w4/CKQJ: View global settings"""
    try:
        # Handle both message and callback query updates
        if update.message:
            message_target = update.message
        elif update.callback_query and update.callback_query.message:
            message_target = update.callback_query.message
        else:
            logger.error("handle_admin_w4: No message target found")
            return
        
        global_markup = db.get_admin_markup()
        global_address = db.get_usdt_address()
        
        message = f"🌐 <b>全局设置</b>\n\n"
        message += "────────────────────────\n"
        message += f"📈 全局默认加价: {global_markup:.4f} USDT\n"
        
        if global_address:
            address_display = global_address[:15] + "..." + global_address[-15:] if len(global_address) > 30 else global_address
            message += f"🔗 全局默认地址: <code>{address_display}</code>\n"
        else:
            message += "🔗 全局默认地址: 未设置\n"
        
        message += "────────────────────────\n"
        message += "ℹ️ 提示: 未配置独立设置的群组将使用此全局默认值"
        
        await send_group_message(update, message, parse_mode="HTML")
        logger.info(f"Admin {update.effective_user.id} executed w4/CKQJ")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w4: {e}", exc_info=True)
        await send_group_message(update, f"❌ 错误: {str(e)}")




async def handle_admin_w7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w7/CKQL: View all groups where bot is present"""
    try:
        # Use context.bot instead of message.bot to avoid attribute errors
        bot = context.bot
        
        # Handle both message and callback query updates
        query = update.callback_query if hasattr(update, 'callback_query') and update.callback_query else None
        if update.message:
            message_target = update.message
        elif query and query.message:
            message_target = query.message
        else:
            logger.error("handle_admin_w7: No message target found")
            return
        
        # Get all group IDs from database (from group_settings and transactions)
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get all unique group IDs from group_settings
        cursor.execute("SELECT DISTINCT group_id FROM group_settings WHERE is_active = 1")
        configured_group_ids = [row['group_id'] for row in cursor.fetchall()]
        
        # Get all unique group IDs from transactions
        cursor.execute("SELECT DISTINCT group_id FROM otc_transactions WHERE group_id IS NOT NULL")
        transaction_group_ids = [row['group_id'] for row in cursor.fetchall()]
        
        # Combine and get unique group IDs
        all_group_ids = list(set(configured_group_ids + transaction_group_ids))
        
        if not all_group_ids:
            error_msg = "📭 暂无群组记录\n\n机器人尚未加入任何群组或没有群组活动记录"
            if query:
                await query.edit_message_text(error_msg, parse_mode="HTML")
                await query.answer()
            else:
                await send_group_message(update, error_msg)
            # Don't close connection - Database class manages it as singleton
            return
        
        # Verify bot is still in each group and get group info
        valid_groups = []
        from keyboards.inline_keyboard import get_groups_list_keyboard_with_edit
        
        for group_id in all_group_ids[:50]:  # Limit to 50 groups for API calls
            try:
                # Verify bot is still in the group
                chat = await bot.get_chat(group_id)
                
                # Get group settings if exists
                cursor.execute("""
                    SELECT group_title, markup, usdt_address, created_at, updated_at
                    FROM group_settings
                    WHERE group_id = ? AND is_active = 1
                """, (group_id,))
                setting_row = cursor.fetchone()
                
                # Get first transaction date (as join date approximation)
                cursor.execute("""
                    SELECT MIN(created_at) as first_transaction
                    FROM otc_transactions
                    WHERE group_id = ?
                """, (group_id,))
                tx_row = cursor.fetchone()
                first_transaction = tx_row['first_transaction'] if tx_row and tx_row['first_transaction'] else None
                
                # Get transaction count
                cursor.execute("""
                    SELECT COUNT(*) as tx_count
                    FROM otc_transactions
                    WHERE group_id = ?
                """, (group_id,))
                tx_count_row = cursor.fetchone()
                tx_count = tx_count_row['tx_count'] if tx_count_row else 0
                
                # Determine join date (prefer group_settings.created_at, fallback to first transaction)
                join_date = None
                if setting_row and setting_row.get('created_at'):
                    join_date = setting_row['created_at']
                elif first_transaction:
                    join_date = first_transaction
                
                # Format join date
                join_date_str = "未知"
                if join_date:
                    try:
                        from datetime import datetime
                        if isinstance(join_date, str):
                            # Try parsing different formats
                            try:
                                dt = datetime.fromisoformat(join_date.replace('Z', '+00:00'))
                            except:
                                dt = datetime.strptime(join_date[:10], '%Y-%m-%d')
                        else:
                            dt = join_date
                        join_date_str = dt.strftime('%Y-%m-%d')
                    except:
                        join_date_str = str(join_date)[:10] if join_date else "未知"
                
                # Get markup (group-specific or global)
                markup = float(setting_row['markup']) if setting_row and setting_row.get('markup') is not None else None
                if markup is None:
                    markup = db.get_admin_markup()
                    is_configured = False
                else:
                    is_configured = True
                
                group_title = setting_row['group_title'] if setting_row and setting_row.get('group_title') else chat.title
                
                group_data = {
                    'group_id': group_id,
                    'group_title': group_title,
                    'markup': markup,
                    'is_configured': is_configured,
                    'join_date': join_date_str,
                    'tx_count': tx_count
                }
                
                # Update group_title in database if different
                if setting_row and setting_row.get('group_title') != chat.title:
                    cursor.execute("""
                        UPDATE group_settings 
                        SET group_title = ? 
                        WHERE group_id = ?
                    """, (chat.title, group_id))
                    conn.commit()
                    group_data['group_title'] = chat.title
                
                valid_groups.append(group_data)
                
            except Exception as e:
                # Bot is not in this group or cannot access it
                logger.debug(f"Bot not in group {group_id} or cannot access: {e}")
                continue
        
        # Don't close connection - Database class manages it as singleton
        
        if not valid_groups:
            error_msg = "📭 机器人当前不在任何群组中\n\n所有记录的群组中，机器人已经离开或无法访问"
            if query:
                await query.edit_message_text(error_msg, parse_mode="HTML")
                await query.answer()
            else:
                await send_group_message(update, error_msg)
            return
        
        # Sort by group_id for consistent ordering
        valid_groups.sort(key=lambda x: x['group_id'])
        
        message = f"📊 <b>所有群组列表</b>\n\n"
        message += f"共 {len(valid_groups)} 个群组（机器人当前在的群组）\n"
        message += "────────────────────────\n\n"
        
        configured_count = sum(1 for g in valid_groups if g.get('is_configured'))
        message += f"📈 <b>统计：</b>\n"
        message += f"• 已配置: {configured_count} 个\n"
        message += f"• 使用全局默认: {len(valid_groups) - configured_count} 个\n\n"
        message += "────────────────────────\n\n"
        
        # Display groups (limit to 20 for message length)
        display_groups = valid_groups[:20]
        for idx, group in enumerate(display_groups, 1):
            group_title = group.get('group_title') or f"群组 {group['group_id']}"
            is_configured = group.get('is_configured', False)
            group_id = group['group_id']
            markup = group.get('markup', 0.0)
            join_date = group.get('join_date', '未知')
            tx_count = group.get('tx_count', 0)
            
            # Status indicator
            status_icon = "⚙️" if is_configured else "🌐"
            
            message += f"{status_icon} <b>{idx}. {group_title}</b>\n"
            message += f"   ID: <code>{group_id}</code>\n"
            message += f"   加入日期: {join_date}\n"
            message += f"   上浮汇率: {markup:+.4f} USDT\n"
            if tx_count > 0:
                message += f"   交易记录: {tx_count} 笔\n"
            message += "\n"
        
        if len(valid_groups) > 20:
            message += f"\n... 还有 {len(valid_groups) - 20} 个群组未显示\n"
        
        # Create keyboard with group selection buttons for editing
        reply_markup = get_groups_list_keyboard_with_edit(display_groups)
        
        if query:
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
        else:
            await send_group_message(update, message, parse_mode="HTML", inline_keyboard=reply_markup)
        
        logger.info(f"Admin {update.effective_user.id} executed w7/CKQL, showing {len(valid_groups)} groups")
            
    except Exception as e:
        logger.error(f"Error in handle_admin_w7: {e}", exc_info=True)
        error_msg = f"❌ 错误: {str(e)}"
        if query:
            await query.answer(error_msg, show_alert=True)
        else:
            await send_group_message(update, error_msg)
            tx_count = group.get('tx_count', 0)
            last_active = group.get('last_active', '')
            if last_active:
                last_active = last_active[:16] if len(last_active) > 16 else last_active
                message += f"   交易: {tx_count} 笔 | 最后活跃: {last_active[-10:]}\n"
            else:
                message += f"   交易: {tx_count} 笔\n"
            
            message += "\n"
        
        if len(groups) > 20:
            message += f"\n... 还有 {len(groups) - 20} 个群组未显示"
        
        # Add inline keyboard for group management with edit buttons for each group
        from keyboards.inline_keyboard import get_groups_list_keyboard_with_edit
        reply_markup = get_groups_list_keyboard_with_edit(valid_groups)
        
        await send_group_message(update, message, parse_mode="HTML", inline_keyboard=reply_markup)
        logger.info(f"Admin {update.effective_user.id} executed w7/CKQL, showing {len(valid_groups)} groups")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w7: {e}", exc_info=True)
        await send_group_message(update, f"❌ 错误: {str(e)}")


async def handle_admin_w8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w8/CZSZ: Reset group settings"""
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        if db.reset_group_settings(group_id):
            # Log operation
            from services.audit_service import log_admin_operation, OperationType
            log_admin_operation(
                OperationType.RESET_GROUP_SETTINGS,
                update,
                target_type='group',
                target_id=str(group_id),
                description=f"重置群组设置，恢复全局默认值"
            )
            
            message = f"✅ 群组设置已重置\n\n"
            message += f"群组: {chat.title}\n"
            message += "已恢复使用全局默认设置"
        else:
            message = "❌ 重置失败（可能群组未配置独立设置）"
        
        await send_group_message(update, message)
        logger.info(f"Admin {update.effective_user.id} reset group {group_id} settings")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w8: {e}", exc_info=True)
        await send_group_message(update, f"❌ 错误: {str(e)}")


async def handle_admin_w9(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w9/SCSZ: Delete group settings"""
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        if db.delete_group_settings(group_id):
            # Log operation
            from services.audit_service import log_admin_operation, OperationType
            log_admin_operation(
                OperationType.DELETE_GROUP_SETTINGS,
                update,
                target_type='group',
                target_id=str(group_id),
                description=f"删除群组独立配置"
            )
            
            message = f"✅ 群组配置已删除\n\n"
            message += f"群组: {chat.title}\n"
            message += "已完全删除群组独立配置"
        else:
            message = "❌ 删除失败（可能群组未配置独立设置）"
        
        await send_group_message(update, message)
        logger.info(f"Admin {update.effective_user.id} deleted group {group_id} settings")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w9: {e}", exc_info=True)
        await send_group_message(update, f"❌ 错误: {str(e)}")


# ========== Settlement Handler ==========

async def handle_math_settlement(update: Update, context: ContextTypes.DEFAULT_TYPE, amount_text: str):
    """Handle math expression and calculate settlement with transaction recording"""
    try:
        chat = update.effective_chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        user = update.effective_user
        
        # Check if this is a batch settlement (multiple amounts)
        if is_batch_amounts(amount_text):
            # Handle batch settlement
            settlements, error_msg = calculate_batch_settlement(amount_text, group_id)
            
            if settlements is None:
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
            
            # Create transaction records for each settlement
            transaction_ids = []
            for settlement in settlements:
                transaction_id = db.create_transaction(
                    group_id=group_id,
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    cny_amount=settlement['cny_amount'],
                    usdt_amount=settlement['usdt_amount'],
                    exchange_rate=settlement['final_price'],
                    markup=settlement['markup'],
                    usdt_address=usdt_address or ''
                )
                if transaction_id:
                    transaction_ids.append(transaction_id)
            
            # Format and send batch settlement bill
            bill_message = format_batch_settlement_bills(settlements, usdt_address)
            
            await send_group_message(update, bill_message, parse_mode="HTML")
            
            logger.info(f"User {user.id} calculated batch settlement: {len(settlements)} bills, transaction_ids: {transaction_ids}")
            
            # Mark batch settlement feature as used
            db.set_user_preference(user.id, 'feature_used_batch_settlement', True)
            return
        
        # Single settlement (existing logic)
        settlement_data, error_msg = calculate_settlement(amount_text, group_id)
        
        if settlement_data is None:
            # Show error help if available
            if "格式错误" in error_msg or "金额" in error_msg:
                from handlers.help_handlers import show_error_help
                await show_error_help(update, 'invalid_amount', error_msg)
            elif "价格" in error_msg or "汇率" in error_msg:
                from handlers.help_handlers import show_error_help
                await show_error_help(update, 'no_price', error_msg)
            else:
                await send_group_message(update, f"❌ {error_msg}")
            return
        
        # Get USDT address (using address management or legacy)
        from services.settlement_service import get_settlement_address
        usdt_address = get_settlement_address(group_id=group_id, strategy='default')
        
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
        
        # Format and send settlement bill (with status 'pending')
        bill_message = format_settlement_bill(
            settlement_data, 
            usdt_address, 
            transaction_id,
            transaction_status='pending'
        )
        
        # Add inline keyboard for confirmation (pending status)
        from keyboards.inline_keyboard import get_settlement_bill_keyboard
        reply_markup = get_settlement_bill_keyboard(transaction_id, 'pending', False)
        
        # Use send_group_message to ensure reply keyboard is shown in groups
        await send_group_message(update, bill_message, parse_mode="HTML", inline_keyboard=reply_markup)
        
        logger.info(f"User {user.id} calculated settlement: {amount_text}, transaction_id: {transaction_id}")
        
    except Exception as e:
        logger.error(f"Error in handle_math_settlement: {e}", exc_info=True)
        await send_group_message(update, f"❌ 计算错误: {str(e)}")


# ========== Button Handlers ==========

async def handle_price_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle price button click - show Binance P2P merchant leaderboard"""
    from handlers.p2p_handlers import handle_p2p_price_command
    await handle_p2p_price_command(update, context, payment_method="alipay")


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
            await send_group_message(update, "📭 今日暂无交易记录")
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
        
        await send_group_message(update, message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in handle_today_bills_button: {e}", exc_info=True)
        await send_group_message(update, f"❌ 错误: {str(e)}")


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
    
    # Update user last active timestamp
    db.update_user_last_active(user_id)
    
    # Handle template input (after user selects template creation type)
    if 'awaiting_template_input' in context.user_data:
        from handlers.template_handlers import handle_template_input
        await handle_template_input(update, context, text)
        return
    
    # Handle address input (after admin clicks add address)
    if 'adding_address' in context.user_data:
        from handlers.address_handlers import handle_address_input
        await handle_address_input(update, context, text)
        return
    
    # Handle customer service username input (after admin clicks add customer service)
    if 'waiting_for' in context.user_data and context.user_data['waiting_for'] == 'customer_service_username':
        from services.customer_service_service import customer_service
        from keyboards.inline_keyboard import get_customer_service_list_keyboard
        del context.user_data['waiting_for']
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ 仅管理员可以添加客服账号")
            return
        
        username = text.strip().lstrip('@')
        if not username or len(username) < 3:
            await update.message.reply_text("❌ 用户名格式错误，请输入有效的Telegram用户名（至少3个字符）")
            return
        
        # Add customer service account
        success = customer_service.add_account(username=username, display_name=username)
        if success:
            await update.message.reply_text(f"✅ 客服账号已添加：@{username}")
            logger.info(f"Admin {user_id} added customer service account: {username}")
        else:
            await update.message.reply_text(f"❌ 添加失败，账号可能已存在：@{username}")
        return
    
    # Handle group markup input (after admin clicks edit group markup)
    for key in list(context.user_data.keys()):
        if key.startswith('awaiting_group_markup_'):
            group_id = int(key.split('_')[3])
            del context.user_data[key]
            try:
                markup_value = float(text.strip())
                if not is_admin(user_id):
                    await update.message.reply_text("❌ 仅管理员可以设置群组加价")
                    return
                
                # Get group title for audit
                bot = context.bot
                try:
                    chat = await bot.get_chat(group_id)
                    group_title = chat.title
                except:
                    group_title = f"群组 {group_id}"
                
                # Set group markup
                if db.set_group_markup(group_id, markup_value, group_title, user_id):
                    from services.audit_service import log_admin_operation, OperationType
                    log_admin_operation(
                        OperationType.SET_GROUP_MARKUP,
                        update,
                        target_type='group',
                        target_id=str(group_id),
                        description=f"设置群组加价: {markup_value:.4f} USDT"
                    )
                    await update.message.reply_text(f"✅ 群组上浮汇率已设置为: {markup_value:+.4f} USDT")
                    logger.info(f"Admin {user_id} set group {group_id} markup to {markup_value}")
                else:
                    await update.message.reply_text("❌ 设置失败，请重试")
            except ValueError:
                await update.message.reply_text("❌ 格式错误，请输入数字（例如：0.5 或 -0.1）")
            return
    
    # Handle group address input (after admin clicks edit group address)
    for key in list(context.user_data.keys()):
        if key.startswith('awaiting_group_address_'):
            group_id = int(key.split('_')[3])
            del context.user_data[key]
            
            # Check if user is group admin (for groups) or global admin (for any context)
            is_group_admin_user = False
            chat = update.effective_chat
            if chat.type in ['group', 'supergroup'] and chat.id == group_id:
                from utils.group_admin_checker import is_group_admin
                is_group_admin_user = await is_group_admin(context.bot, group_id, user_id)
            
            # Allow if user is group admin OR global admin
            if not is_group_admin_user and not is_admin(user_id):
                # Get chat info to show group owner info
                try:
                    chat_info = await context.bot.get_chat(group_id)
                    message = (
                        "❌ <b>权限不足</b>\n\n"
                        f"只有群组管理员才能编辑此群组的 USDT 地址。\n\n"
                        f"💡 <i>提示：请联系群主 @{chat_info.username if chat_info.username else '群主'} 提升您的权限，或联系全局管理员获取帮助。</i>"
                    )
                except:
                    message = (
                        "❌ <b>权限不足</b>\n\n"
                        "只有群组管理员才能编辑此群组的 USDT 地址。\n\n"
                        "💡 <i>提示：请联系群主提升您的权限，或联系全局管理员获取帮助。</i>"
                    )
                await update.message.reply_text(message, parse_mode="HTML")
                return
            
            address = text.strip()
            
            # Get group title for audit
            bot = context.bot
            try:
                chat = await bot.get_chat(group_id)
                group_title = chat.title
            except:
                group_title = f"群组 {group_id}"
            
            # Set group address
            if db.set_group_address(group_id, address, group_title, user_id):
                from services.audit_service import log_admin_operation, OperationType
                log_admin_operation(
                    OperationType.SET_GROUP_ADDRESS,
                    update,
                    target_type='group',
                    target_id=str(group_id),
                    description=f"设置群组地址"
                )
                addr_display = address[:15] + "..." + address[-15:] if len(address) > 30 else address
                await update.message.reply_text(f"✅ 群组地址已设置为: <code>{addr_display}</code>", parse_mode="HTML")
                logger.info(f"Admin {user_id} set group {group_id} address")
            else:
                await update.message.reply_text("❌ 设置失败，请重试")
            return
    
    # Handle filter input (after user clicks filter button)
    if 'awaiting_filter' in context.user_data:
        filter_type = context.user_data['awaiting_filter']
        group_id = context.user_data.get('filter_group_id')
        del context.user_data['awaiting_filter']
        del context.user_data['filter_group_id']
        
        if filter_type == 'amount':
            min_amount, max_amount = parse_amount_range(text)
            if min_amount is None and max_amount is None:
                await update.message.reply_text("❌ 金额格式错误，请重新输入")
                return
            
            # Apply filter and show results
            from handlers.search_handlers import apply_filters_and_show_results
            filters = {'min_amount': min_amount, 'max_amount': max_amount}
            await apply_filters_and_show_results(update, context, group_id, filters)
            return
        
        elif filter_type == 'date':
            start_date, end_date = parse_date_range(text)
            if not start_date and not end_date:
                await update.message.reply_text("❌ 日期格式错误，请重新输入")
                return
            
            # Apply filter and show results
            from handlers.search_handlers import apply_filters_and_show_results
            filters = {'start_date': start_date, 'end_date': end_date}
            await apply_filters_and_show_results(update, context, group_id, filters)
            return
        
        elif filter_type == 'user':
            try:
                user_id = int(text.strip())
            except ValueError:
                await update.message.reply_text("❌ 用户ID格式错误，请输入数字")
                return
            
            # Apply filter and show results
            from handlers.search_handlers import apply_filters_and_show_results
            filters = {'user_id': user_id}
            await apply_filters_and_show_results(update, context, group_id, filters)
            return
        
        elif filter_type == 'search':
            # Parse comprehensive search query
            from services.search_service import parse_search_query
            filters = parse_search_query(text)
            
            # Check if transaction ID was found
            if filters.get('transaction_id'):
                transaction = db.get_transaction_by_id(filters['transaction_id'])
                if transaction:
                    from handlers.bills_handlers import handle_transaction_detail
                    await handle_transaction_detail(
                        update, context,
                        filters['transaction_id'],
                        transaction['group_id'],
                        return_page=1
                    )
                    return
                else:
                    await update.message.reply_text("❌ 未找到该交易记录")
                    return
            
            # Apply filters and show results
            from handlers.search_handlers import apply_filters_and_show_results
            await apply_filters_and_show_results(update, context, group_id, filters)
            return
        
        return
    
    # Handle payment hash input (after user clicks "已支付")
    if 'awaiting_payment_hash' in context.user_data:
        transaction_id = context.user_data['awaiting_payment_hash']
        del context.user_data['awaiting_payment_hash']
        
        # Get transaction to verify ownership
        transaction = db.get_transaction_by_id(transaction_id)
        if not transaction:
            await update.message.reply_text("❌ 未找到该交易")
            return
        
        if transaction['user_id'] != user_id:
            await update.message.reply_text("❌ 您无权操作此交易")
            return
        
        # Validate payment hash (should be alphanumeric, typically 64 chars for TXID)
        payment_hash = text.strip()
        if len(payment_hash) > 200:  # Reasonable max length
            await update.message.reply_text("❌ 支付哈希过长，请输入有效的交易哈希")
            return
        
        # Mark transaction as paid with payment hash
        transaction = db.get_transaction_by_id(transaction_id)
        old_status = transaction['status'] if transaction else None
        
        if db.mark_transaction_paid(transaction_id, payment_hash):
            # Log operation
            from services.audit_service import log_transaction_operation, OperationType
            log_transaction_operation(
                OperationType.MARK_PAID,
                update,
                transaction_id,
                description=f"用户标记为已支付（支付哈希: {payment_hash[:20]}...）",
                old_status=old_status,
                new_status='paid'
            )
            
            # Get updated transaction
            transaction = db.get_transaction_by_id(transaction_id)
            
            # Refresh transaction message if it exists in a recent message
            # (Note: This is a simplified approach. In production, you might want to store message_id)
            from services.settlement_service import format_settlement_bill
            from keyboards.inline_keyboard import get_settlement_bill_keyboard
            
            settlement_data = {
                'cny_amount': transaction['cny_amount'],
                'base_price': transaction['exchange_rate'] - (transaction['markup'] or 0.0),
                'markup': transaction['markup'] or 0.0,
                'final_price': transaction['exchange_rate'],
                'usdt_amount': transaction['usdt_amount']
            }
            
            paid_at = transaction.get('paid_at')
            if paid_at:
                paid_at = paid_at[:16]
            
            bill_message = format_settlement_bill(
                settlement_data,
                usdt_address=transaction.get('usdt_address'),
                transaction_id=transaction['transaction_id'],
                transaction_status=transaction['status'],
                payment_hash=transaction.get('payment_hash'),
                paid_at=paid_at
            )
            
            reply_markup = get_settlement_bill_keyboard(
                transaction['transaction_id'],
                transaction['status'],
                is_admin_user
            )
            
            await update.message.reply_text(
                f"✅ <b>已标记为已支付</b>\n\n"
                f"交易编号: <code>{transaction_id}</code>\n"
                f"支付哈希: <code>{payment_hash[:20]}...</code>\n\n"
                f"管理员将进行确认。",
                parse_mode="HTML"
            )
            
            # Also send updated bill
            await update.message.reply_text(
                bill_message,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            
            logger.info(f"User {user_id} marked transaction {transaction_id} as paid with hash: {payment_hash[:20]}...")
        else:
            await update.message.reply_text("❌ 操作失败，请重试")
        
        return
    
    # Handle text commands that look like commands (for Chinese command support)
    # Telegram Bot API doesn't support Chinese commands, so we handle them as text messages
    if text.startswith("/"):
        # Extract command without the slash
        command = text[1:].split()[0] if text[1:].split() else text[1:]
        
        # Map Chinese commands to handlers
        command_map = {
            "结算": "settlement",
            "今日": "today",
            "历史": "history",
            "地址": "address",
            "客服": "support",
            "我的账单": "mybills",
        }
        
        if command in command_map:
            # Call the corresponding handler
            if command == "结算":
                from handlers.template_handlers import handle_template_menu
                await handle_template_menu(update, context)
            elif command == "今日":
                await handle_today_bills_button(update, context)
            elif command == "历史":
                from handlers.bills_handlers import handle_history_bills
                await handle_history_bills(update, context, page=1)
            elif command == "地址":
                # Show address (same logic as button handler)
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
                
                await send_group_message(update, message, parse_mode="HTML")
            elif command == "客服":
                contact_message = (
                    "📞 <b>联系人工客服</b>\n\n"
                    "如有任何问题，请联系管理员：\n"
                    "@wushizhifu_jianglai\n\n"
                    "或使用以下方式：\n"
                    "• 工作时间：7×24小时\n"
                    "• 响应时间：通常在5分钟内"
                )
                await send_group_message(update, contact_message, parse_mode="HTML")
            elif command == "我的账单":
                if chat.type == 'private':
                    from handlers.personal_handlers import handle_personal_bills
                    await handle_personal_bills(update, context, page=1)
                else:
                    await update.message.reply_text("❌ 此功能仅在私聊中可用")
            return
    
    # Handle reply keyboard buttons with help system
    # Show help first if needed, then execute function
    from services.button_help_service import (
        format_button_help_message, 
        should_show_help, 
        mark_help_shown
    )
    from keyboards.inline_keyboard import get_button_help_keyboard
    
    if text in ["💱 汇率", "💱 查看汇率", "📊 查看汇率"]:
        # Show help if needed
        if should_show_help(user_id, "💱 汇率"):
            help_message = format_button_help_message("💱 汇率")
            if help_message:
                help_keyboard = get_button_help_keyboard("💱 汇率")
                await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                mark_help_shown(user_id, "💱 汇率", shown=True)
        await handle_price_button(update, context)
        return
    
    if text == "📊 今日":
        # Show help if needed
        if should_show_help(user_id, "📊 今日"):
            help_message = format_button_help_message("📊 今日")
            if help_message:
                help_keyboard = get_button_help_keyboard("📊 今日")
                await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                mark_help_shown(user_id, "📊 今日", shown=True)
        await handle_today_bills_button(update, context)
        return
    
    if text == "📜 历史":
        # Show help if needed
        if should_show_help(user_id, "📜 历史"):
            help_message = format_button_help_message("📜 历史")
            if help_message:
                help_keyboard = get_button_help_keyboard("📜 历史")
                await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                mark_help_shown(user_id, "📜 历史", shown=True)
        # Show history bills (first page)
        from handlers.bills_handlers import handle_history_bills
        await handle_history_bills(update, context, page=1)
        return
    
    if text == "💰 结算":
        # Show help if needed
        if should_show_help(user_id, "💰 结算"):
            help_message = format_button_help_message("💰 结算")
            if help_message:
                help_keyboard = get_button_help_keyboard("💰 结算")
                await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                mark_help_shown(user_id, "💰 结算", shown=True)
        from handlers.template_handlers import handle_template_menu
        await handle_template_menu(update, context)
        return
    
    if text in ["⚙️ 设置", "⚙️ 管理"]:
        # Show help if needed
        button_text = "⚙️ 设置" if chat.type in ['group', 'supergroup'] else "⚙️ 管理"
        if should_show_help(user_id, button_text):
            help_message = format_button_help_message(button_text)
            if help_message:
                help_keyboard = get_button_help_keyboard(button_text)
                await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                mark_help_shown(user_id, button_text, shown=True)
        
        # Show group settings menu (admin only)
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        # 首先显示完整的指令教程
        from handlers.admin_commands_handlers import handle_admin_commands_help
        await handle_admin_commands_help(update, context)
        
        # 然后显示管理菜单
        if is_group := chat.type in ['group', 'supergroup']:
            from keyboards.inline_keyboard import get_group_settings_menu
            reply_markup = get_group_settings_menu()
            message = (
                "⚙️ <b>群组设置菜单</b>\n\n"
                "请选择要执行的操作：\n\n"
                "💡 <i>提示：上方已显示完整指令教程，也可以点击「⚡ 管理员指令教程」再次查看</i>"
            )
        else:
            from keyboards.inline_keyboard import get_global_management_menu
            reply_markup = get_global_management_menu()
            message = (
                "🌐 <b>全局管理菜单</b>\n\n"
                "请选择要执行的操作：\n\n"
                "💡 <i>提示：上方已显示完整指令教程，也可以点击「⚡ 管理员指令教程」再次查看</i>"
            )
        
        # Use send_group_message to ensure reply keyboard is shown in groups
        await send_group_message(update, message, parse_mode="HTML", inline_keyboard=reply_markup)
        return
    
    if text in ["📈 统计", "📊 数据"]:
        # Show help if needed
        button_text = "📈 统计" if chat.type in ['group', 'supergroup'] else "📊 数据"
        if should_show_help(user_id, button_text):
            help_message = format_button_help_message(button_text)
            if help_message:
                help_keyboard = get_button_help_keyboard(button_text)
                await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                mark_help_shown(user_id, button_text, shown=True)
        
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
        # Show help if needed
        if should_show_help(user_id, "🔗 地址"):
            help_message = format_button_help_message("🔗 地址")
            if help_message:
                help_keyboard = get_button_help_keyboard("🔗 地址")
                # For help message, keep inline keyboard but also add reply keyboard in groups
                if chat.type in ['group', 'supergroup']:
                    from keyboards.reply_keyboard import get_main_reply_keyboard
                    user = update.effective_user
                    user_info_dict = {
                        'id': user.id,
                        'first_name': user.first_name or '',
                        'username': user.username,
                        'language_code': user.language_code
                    }
                    reply_keyboard = get_main_reply_keyboard(user.id, is_group=True, user_info=user_info_dict)
                    # Combine inline and reply keyboards - use inline for help close button
                    await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                    # Also send a hidden message with reply keyboard to ensure it's shown
                    # Send reply keyboard - already using visible emoji, good!
                    await update.message.reply_text("💡", reply_markup=reply_keyboard)
                else:
                    await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                mark_help_shown(user_id, "🔗 地址", shown=True)
        
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
        
        await send_group_message(update, message, parse_mode="HTML")
        return
    
    if text in ["📞 联系客服", "📞 客服"]:
        # Show help if needed
        if should_show_help(user_id, "📞 客服"):
            help_message = format_button_help_message("📞 客服")
            if help_message:
                help_keyboard = get_button_help_keyboard("📞 客服")
                if chat.type in ['group', 'supergroup']:
                    from keyboards.reply_keyboard import get_main_reply_keyboard
                    user = update.effective_user
                    user_info_dict = {
                        'id': user.id,
                        'first_name': user.first_name or '',
                        'username': user.username,
                        'language_code': user.language_code
                    }
                    reply_keyboard = get_main_reply_keyboard(user.id, is_group=True, user_info=user_info_dict)
                    await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                    # Send reply keyboard - already using visible emoji, good!
                    await update.message.reply_text("💡", reply_markup=reply_keyboard)
                else:
                    await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                mark_help_shown(user_id, "📞 客服", shown=True)
        
        contact_message = (
            "📞 <b>联系人工客服</b>\n\n"
            "如有任何问题，请联系管理员：\n"
            "@wushizhifu_jianglai\n\n"
            "或使用以下方式：\n"
            "• 工作时间：7×24小时\n"
            "• 响应时间：通常在5分钟内"
        )
        await send_group_message(update, contact_message, parse_mode="HTML")
        return
    
    # Handle "📜 我的账单" button (both group and private)
    if text == "📜 我的账单":
        if chat.type == 'private':
            # Show help if needed
            if should_show_help(user_id, "📜 我的账单"):
                help_message = format_button_help_message("📜 我的账单")
                if help_message:
                    help_keyboard = get_button_help_keyboard("📜 我的账单")
                    await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                    mark_help_shown(user_id, "📜 我的账单", shown=True)
            from handlers.personal_handlers import handle_personal_bills
            await handle_personal_bills(update, context, page=1)
        else:
            # In groups, show a message that this feature is only available in private chat
            await send_group_message(update, 
                "❌ <b>「📜 我的账单」功能</b>\n\n"
                "此功能仅在私聊中可用。\n\n"
                "请与机器人私聊后使用此功能，或使用以下方式：\n"
                "• 在群组中查看「📊 今日」查看今日交易\n"
                "• 在群组中使用「📜 历史」查看历史账单\n\n"
                "💡 <i>点击机器人头像，选择「发送消息」进入私聊</i>",
                parse_mode="HTML"
            )
        return
    
    
    # Personal stats (private chat only)
    if chat.type == 'private':
        if text == "📊 我的统计":
            from handlers.personal_handlers import handle_personal_stats
            await handle_personal_stats(update, context)
            return
    
    # Handle admin commands (w0-w9 + pinyin)
    if is_admin_user:
        # w0 / SZ - View group settings
        if is_pinyin_command(text, "w0", "sz"):
            await handle_admin_w0(update, context)
            return
        
        # w1 / HL - View price
        if is_pinyin_command(text, "w1", "hl") or text == "w1" or text == "w01":
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
        
        # w7 / CKQL - View all groups
        if is_pinyin_command(text, "w7", "ckql"):
            await handle_admin_w7(update, context)
            return
        
        # w8 / CZSZ - Reset group settings
        if is_pinyin_command(text, "w8", "czsz") or text == "w8" or text == "w08":
            await handle_admin_w8(update, context)
            return
        
        # w9 / SCSZ - Delete group settings
        if is_pinyin_command(text, "w9", "scsz"):
            await handle_admin_w9(update, context)
            return
        
        # Legacy commands (backward compatibility - w01-w09 support)
        # w01 → w1
        if text == "w01":
            await handle_admin_w1(update, context)
            return
        
        # w02 → w2 (group only)
        w02_match = re.match(r'^w02\s+(-?\d+\.?\d*)$', text)
        if w02_match:
            try:
                markup_value = float(w02_match.group(1))
                chat = update.effective_chat
                if chat.type in ['group', 'supergroup']:
                    await handle_admin_w2(update, context, markup_value)
                else:
                    await update.message.reply_text("❌ w02 命令仅在群组中使用，请使用 w2 命令设置群组加价")
                return
            except ValueError:
                await update.message.reply_text("❌ w02 格式错误，应为: w02 [数字]")
                return
        
        # w03 → w2 (negative, group only)
        w03_match = re.match(r'^w03\s+(\d+\.?\d*)$', text)
        if w03_match:
            try:
                markdown_value = float(w03_match.group(1))
                markup_value = -markdown_value
                chat = update.effective_chat
                if chat.type in ['group', 'supergroup']:
                    await handle_admin_w2(update, context, markup_value)
                else:
                    await update.message.reply_text("❌ w03 命令仅在群组中使用，请使用 w2 命令设置群组加价")
                return
            except ValueError:
                await update.message.reply_text("❌ w03 格式错误，应为: w03 [数字]")
                return
        
        # w04 → w4
        if text == "w04":
            await handle_admin_w4(update, context)
            return
        
        # w08 → w8
        if text == "w08":
            await handle_admin_w8(update, context)
            return
    
    # Check if message is a number, math expression, or batch amounts (settlement calculation)
    if is_number(text) or is_simple_math(text) or is_batch_amounts(text):
        await handle_math_settlement(update, context, text)
        return
    
    # Otherwise, ignore the message


def get_message_handler():
    """Get message handler instance"""
    return MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
