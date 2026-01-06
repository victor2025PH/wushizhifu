"""
Message handlers for Bot B
Handles admin shortcuts, w0-w9 commands, pinyin commands, and math/settlement processing
"""
import re
import logging
import asyncio
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes
from config import Config
from database import db
from services.price_service import get_price_with_markup, get_okx_merchants
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
            # Using zero-width space for invisible placeholder
            try:
                await message_target.reply_text("\u200B", reply_markup=reply_keyboard)
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
        
        # 使用新的地址管理系统获取群组地址
        from services.settlement_service import get_settlement_address
        group_address = get_settlement_address(group_id=group_id, strategy='default')
        
        if group_setting:
            message += "<b>当前配置（群组独立）:</b>\n"
            message += f"• 加价: {group_setting['markup']:.4f} USDT\n"
            # 使用新地址管理系统获取的地址
            if group_address:
                address_display = group_address
                if len(group_address) > 20:
                    address_display = f"{group_address[:10]}...{group_address[-10:]}"
                message += f"• USDT 地址: {address_display}\n\n"
            else:
                message += "• USDT 地址: 未设置\n\n"
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
    """Handle w1/HL: Get current price with markup - shows OKX merchants (Alipay only)"""
    try:
        chat = update.effective_chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        
        # Fetch merchants data from OKX (real-time, no cache)
        merchants, error_msg = get_okx_merchants()
        
        if merchants is None or len(merchants) == 0:
            message = f"❌ 获取汇率失败\n\n{error_msg or '未知错误'}"
            await send_group_message(update, message, parse_mode="HTML")
            return
        
        # Get price with markup
        final_price, price_error, base_price, markup = get_price_with_markup(group_id)
        
        if final_price is None:
            message = f"❌ 计算价格失败\n\n{price_error or '未知错误'}"
            await send_group_message(update, message, parse_mode="HTML")
            return
        
        markup_source = "群组" if group_id and db.get_group_setting(group_id) else "全局"
        
        # Build message with merchant information
        message = (
            f"💱 <b>USDT/CNY 实时汇率（欧易 OKX - 支付宝）</b>\n\n"
            f"📊 <b>商家汇率：</b>\n"
        )
        
        # Show top 10 merchants (sorted by rate, lowest first)
        for idx, merchant in enumerate(merchants[:10], 1):
            message += f"{idx}. <b>{merchant['name']}</b>: {merchant['rate']:.4f} CNY\n"
        
        if len(merchants) > 10:
            message += f"\n... 共 {len(merchants)} 个商家\n"
        
        # Add average price and final price
        message += (
            f"\n📈 平均价格: {base_price:.4f} CNY\n"
            f"➕ 加价（{markup_source}）: {markup:.4f} USDT\n"
            f"💰 最终价格: {final_price:.4f} CNY\n"
        )
        
        await send_group_message(update, message, parse_mode="HTML")
        logger.info(f"User {update.effective_user.id} executed w1/HL - fetched {len(merchants)} merchants")
        
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
        # 改進：優先從 group_settings 獲取所有群組，包括非活躍的（用於顯示）
        conn = db.connect()
        cursor = conn.cursor()
        
        # 獲取所有群組（優先獲取活躍的，非活躍的用於顯示但會標記）
        # 只獲取活躍的群組，避免顯示已不存在的群組
        cursor.execute("SELECT DISTINCT group_id FROM group_settings WHERE is_active = 1")
        configured_group_ids = [row['group_id'] for row in cursor.fetchall()]
        
        # 如果沒有活躍群組，也檢查非活躍的（可能是臨時網絡問題）
        if not configured_group_ids:
            cursor.execute("SELECT DISTINCT group_id FROM group_settings")
            configured_group_ids = [row['group_id'] for row in cursor.fetchall()]
        
        # 獲取有交易記錄的群組（補充可能遺漏的群組）
        cursor.execute("SELECT DISTINCT group_id FROM otc_transactions WHERE group_id IS NOT NULL")
        transaction_group_ids = [row['group_id'] for row in cursor.fetchall()]
        
        # 合併並去重
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
        # 策略：只要機器人在群組中（能成功 get_chat），就顯示這個群組
        valid_groups = []
        inactive_groups = []  # 記錄無法訪問的群組
        from keyboards.inline_keyboard import get_groups_list_keyboard_with_edit
        
        for group_id in all_group_ids[:50]:  # Limit to 50 groups for API calls
            try:
                # 驗證機器人是否在群組中：只要 get_chat 成功，就認為機器人在群組中
                # 使用較長的超時時間，避免網絡問題導致誤判
                try:
                    chat = await asyncio.wait_for(
                        bot.get_chat(group_id),
                        timeout=10.0  # 增加到10秒超時，給網絡更多時間
                    )
                except asyncio.TimeoutError:
                    # 超時：可能是網絡問題，不標記為非活躍，跳過本次驗證
                    logger.warning(f"⚠️ 群組 {group_id} 驗證超時（可能是網絡問題），跳過本次驗證")
                    continue
                except Exception as timeout_err:
                    # 其他超時相關錯誤，也跳過
                    logger.warning(f"⚠️ 群組 {group_id} 驗證時發生錯誤: {timeout_err}，跳過本次驗證")
                    continue
                
                # Get group settings if exists (包括非活躍的)
                cursor.execute("""
                    SELECT group_title, markup, usdt_address, is_active, created_at, updated_at
                    FROM group_settings
                    WHERE group_id = ?
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
                if setting_row and setting_row['created_at']:
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
                # 修復：sqlite3.Row 不支持 .get()，使用字典式訪問
                markup = None
                if setting_row and setting_row['markup'] is not None:
                    markup = float(setting_row['markup'])
                
                if markup is None:
                    markup = db.get_admin_markup()
                    is_configured = False
                else:
                    is_configured = True
                
                # 優先使用驗證時獲取的實際標題，如果沒有則使用資料庫中的標題
                actual_chat_title = chat.title if chat.title else None
                db_title = setting_row['group_title'] if setting_row and setting_row['group_title'] else None
                
                # 如果驗證獲取的標題與資料庫不同，更新資料庫
                if actual_chat_title and db_title and actual_chat_title != db_title:
                    logger.info(f"🔄 群組 {group_id} 標題不一致，更新: '{db_title}' -> '{actual_chat_title}'")
                    cursor.execute("""
                        UPDATE group_settings 
                        SET group_title = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE group_id = ?
                    """, (actual_chat_title, group_id))
                    conn.commit()
                    group_title = actual_chat_title
                else:
                    # 使用實際獲取的標題或資料庫標題
                    group_title = actual_chat_title if actual_chat_title else (db_title if db_title else f"群組 {group_id}")
                
                is_active = setting_row['is_active'] if setting_row else True
                
                group_data = {
                    'group_id': group_id,
                    'group_title': group_title,
                    'markup': markup,
                    'is_configured': is_configured,
                    'is_active': bool(is_active),
                    'join_date': join_date_str,
                    'tx_count': tx_count
                }
                
                # Update group_title and status in database if different
                if setting_row:
                    needs_update = False
                    updates = []
                    params = []
                    
                    # 修復：sqlite3.Row 不支持 .get()，使用字典式訪問
                    # 檢查標題是否需要更新（使用實際獲取的標題）
                    actual_chat_title = chat.title if chat.title else None
                    db_title = setting_row['group_title'] if setting_row['group_title'] else None
                    
                    if actual_chat_title and db_title and actual_chat_title != db_title:
                        updates.append("group_title = ?")
                        params.append(actual_chat_title)
                        needs_update = True
                        logger.info(f"🔄 群組 {group_id} 標題不一致，將更新: '{db_title}' -> '{actual_chat_title}'")
                    
                    if not bool(setting_row['is_active']):
                        updates.append("is_active = 1")
                        needs_update = True
                    
                    if needs_update:
                        updates.append("updated_at = CURRENT_TIMESTAMP")
                        params.append(group_id)
                        cursor.execute(f"""
                            UPDATE group_settings 
                            SET {', '.join(updates)}
                            WHERE group_id = ?
                        """, tuple(params))
                        conn.commit()
                        group_data['group_title'] = chat.title
                        group_data['is_active'] = True
                else:
                    # 群組不在 group_settings 中，創建記錄
                    db.ensure_group_exists(group_id, chat.title)
                    group_data['is_active'] = True
                
                valid_groups.append(group_data)
                
            except Exception as e:
                # Bot is not in this group or cannot access it
                error_msg = str(e).lower()
                logger.debug(f"群組 {group_id} 驗證失敗: {e}")
                
                # 只處理明確的錯誤：群組不存在或機器人被移除
                # 其他錯誤（如網絡問題）不標記為非活躍，跳過本次驗證
                is_chat_not_found = (
                    'chat not found' in error_msg or 
                    'not found' in error_msg or
                    'chat_id is empty' in error_msg
                )
                is_unauthorized = (
                    'unauthorized' in error_msg or 
                    'forbidden' in error_msg or
                    'bot was kicked' in error_msg or
                    'bot is not a member' in error_msg
                )
                
                # 只有明確的錯誤才標記為非活躍
                if is_chat_not_found or is_unauthorized:
                    logger.info(f"🗑️ 群組 {group_id} 不存在或機器人已被移除，標記為非活躍")
                    cursor.execute("""
                        UPDATE group_settings 
                        SET is_active = 0,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE group_id = ?
                    """, (group_id,))
                    conn.commit()
                    # 記錄到 inactive_groups 但不顯示
                    cursor.execute("""
                        SELECT group_title FROM group_settings WHERE group_id = ?
                    """, (group_id,))
                    inactive_row = cursor.fetchone()
                    if inactive_row:
                        inactive_groups.append({
                            'group_id': group_id,
                            'group_title': inactive_row['group_title'] or f"群組 {group_id}",
                            'is_active': False
                        })
                else:
                    # 其他錯誤（可能是網絡問題），不標記為非活躍，跳過本次驗證
                    logger.warning(f"⚠️ 群組 {group_id} 驗證失敗（可能是網絡問題）: {e}，跳過本次驗證")
                
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
        inactive_groups.sort(key=lambda x: x['group_id'])
        
        message = f"📊 <b>所有群组列表</b>\n\n"
        message += f"✅ 活跃群组: {len(valid_groups)} 个\n"
        if inactive_groups:
            message += f"⚠️ 无法访问: {len(inactive_groups)} 个\n"
        message += "────────────────────────\n\n"
        
        configured_count = sum(1 for g in valid_groups if g.get('is_configured'))
        message += f"📈 <b>统计：</b>\n"
        message += f"• 已配置: {configured_count} 个\n"
        message += f"• 使用全局默认: {len(valid_groups) - configured_count} 个\n\n"
        message += "────────────────────────\n\n"
        
        # Display active groups (limit to 20 for message length)
        if valid_groups:
            message += "<b>✅ 活跃群组：</b>\n\n"
            display_groups = valid_groups[:20]
            
            # 檢查標題重複，如果重複則添加區分標識
            title_count = {}
            for group in display_groups:
                title = group.get('group_title') or f"群组 {group['group_id']}"
                if title in title_count:
                    title_count[title] += 1
                else:
                    title_count[title] = 1
            
            for idx, group in enumerate(display_groups, 1):
                base_title = group.get('group_title') or f"群组 {group['group_id']}"
                is_configured = group.get('is_configured', False)
                group_id = group['group_id']
                markup = group.get('markup', 0.0)
                join_date = group.get('join_date', '未知')
                tx_count = group.get('tx_count', 0)
                has_warning = group.get('warning', False)
                
                # 获取USDT地址
                usdt_address = group.get('usdt_address', '')
                if not usdt_address:
                    usdt_address = db.get_usdt_address()
                
                # 如果標題重複，添加群組 ID 後綴作為區分
                if title_count.get(base_title, 0) > 1:
                    group_title = f"{base_title} (ID: {abs(group_id)})"
                else:
                    group_title = base_title
                
                # Status indicator
                status_icon = "⚙️" if is_configured else "🌐"
                if has_warning:
                    status_icon = "⚠️"  # 標記為可能有網絡問題
                
                message += f"{status_icon} <b>{idx}. {group_title}</b>\n"
                message += f"   ID: <code>{group_id}</code>\n"
                message += f"   加入日期: {join_date}\n"
                message += f"   上浮汇率: {markup:+.4f} USDT\n"
                if usdt_address:
                    address_display = usdt_address[:15] + "..." + usdt_address[-15:] if len(usdt_address) > 30 else usdt_address
                    message += f"   USDT地址: <code>{address_display}</code>\n"
                else:
                    message += f"   USDT地址: 未设置\n"
                if tx_count > 0:
                    message += f"   交易记录: {tx_count} 笔\n"
                if has_warning:
                    message += f"   ⚠️ 驗證時遇到網絡問題，顯示的是資料庫中的資訊\n"
                message += "\n"
            
            if len(valid_groups) > 20:
                message += f"\n... 还有 {len(valid_groups) - 20} 个活跃群组未显示\n"
        
        # Display inactive groups (limit to 5)
        if inactive_groups:
            message += "\n────────────────────────\n\n"
            message += "<b>⚠️ 无法访问的群组：</b>\n\n"
            display_inactive = inactive_groups[:5]
            for idx, group in enumerate(display_inactive, 1):
                message += f"❌ {idx}. {group['group_title']}\n"
                message += f"   ID: <code>{group['group_id']}</code>\n\n"
            
            if len(inactive_groups) > 5:
                message += f"... 还有 {len(inactive_groups) - 5} 个无法访问的群组\n"
        
        # Use main menu keyboard for navigation (old management panel removed)
        from keyboards.reply_keyboard import get_main_reply_keyboard
        user = update.effective_user
        user_info = {
            'id': user.id,
            'first_name': user.first_name or '',
            'username': user.username,
            'language_code': user.language_code
        }
        reply_keyboard = get_main_reply_keyboard(user.id, is_group=False, user_info=user_info)
        
        # For groups list, we'll still use inline keyboard for selecting groups to edit
        # But add reply keyboard for navigation
        if query:
            # If called from callback, edit the message
            inline_keyboard = get_groups_list_keyboard_with_edit(display_groups)
            try:
                await query.edit_message_text(message, parse_mode="HTML", reply_markup=inline_keyboard)
                await query.answer()
            except Exception as edit_error:
                # 如果消息內容完全相同，Telegram 會拋出 BadRequest 錯誤
                # 這種情況下只需要回答回調查詢即可
                error_msg = str(edit_error).lower()
                if 'message is not modified' in error_msg:
                    # 消息未修改，這是正常的，只需要回答回調查詢
                    await query.answer()
                    logger.debug(f"消息未修改（內容相同），已忽略: {edit_error}")
                else:
                    # 其他錯誤，記錄並回答
                    logger.warning(f"編輯消息失敗: {edit_error}")
                    await query.answer("⚠️ 更新消息時發生錯誤", show_alert=False)
            
            # Don't send additional navigation message - inline keyboard already has back button
        else:
            # If called from message, send new message with inline keyboard only
            # Reply keyboard is not needed as inline keyboard has back button
            inline_keyboard = get_groups_list_keyboard_with_edit(display_groups)
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=inline_keyboard)
        
        logger.info(f"Admin {update.effective_user.id} executed w7/CKQL, showing {len(valid_groups)} groups")
            
    except Exception as e:
        logger.error(f"Error in handle_admin_w7: {e}", exc_info=True)
        error_msg = f"❌ 错误: {str(e)}"
        if query:
            try:
                await query.answer(error_msg, show_alert=True)
            except Exception:
                # 如果回答失敗，嘗試發送新消息
                try:
                    await query.message.reply_text(error_msg)
                except Exception:
                    pass
        else:
            await send_group_message(update, error_msg)


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
            
            # Get USDT address using new address management system
            from services.settlement_service import get_settlement_address
            usdt_address = None
            if group_id:
                usdt_address = get_settlement_address(group_id=group_id, strategy='default')
            
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
                    usdt_address=usdt_address or '',
                    price_source=settlement.get('price_source')
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
            usdt_address=usdt_address or '',
            price_source=settlement_data.get('price_source')
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
    """Handle price button click - show P2P merchant leaderboard (OKX/Binance)"""
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
    
    # Import is_admin at function level to avoid UnboundLocalError
    # This ensures the function is always available even if there are scope issues
    from admin_checker import is_admin as check_is_admin
    
    text = update.message.text.strip()
    user = update.effective_user
    user_id = user.id
    chat = update.effective_chat
    
    # Log user information for debugging
    logger.debug(
        f"Message from user {user_id} "
        f"(username: {user.username}, name: {user.first_name}, "
        f"chat_id: {chat.id}, chat_type: {chat.type})"
    )
    
    is_admin_user = check_is_admin(user_id)
    
    # Auto-track groups: ensure group exists in database when bot receives group messages
    # This allows "所有群组列表" to detect all groups bot is in, not just those with transactions/settings
    if chat.type in ['group', 'supergroup']:
        db.ensure_group_exists(chat.id, chat.title)
    
    # Update user last active timestamp
    db.update_user_last_active(user_id)
    
    # Handle template input (after user selects template creation type)
    if 'awaiting_template_input' in context.user_data:
        from handlers.template_handlers import handle_template_input
        await handle_template_input(update, context, text)
        return
    
    # Check if awaiting admin ID input (must check BEFORE number check and other handlers)
    # BUT skip if text is a known button/command (like "⚙️ 管理")
    known_buttons = ["⚙️ 管理", "⚙️ 设置", "🔙 返回主菜单", "➕ 添加管理员", "🗑️ 删除管理员", "📋 管理员列表"]
    if 'awaiting_admin_id' in context.user_data and text not in known_buttons:
        await handle_admin_id_input(update, context, text)
        return
    
    # Handle address input (after admin clicks add address)
    if 'adding_address' in context.user_data:
        from handlers.address_handlers import handle_address_input
        await handle_address_input(update, context, text)
        return
    
    # Handle address editing inputs
    if 'editing_address_label' in context.user_data:
        from handlers.address_handlers import handle_address_label_input
        await handle_address_label_input(update, context, text)
        return
    
    if 'editing_address' in context.user_data:
        from handlers.address_handlers import handle_address_addr_input
        await handle_address_addr_input(update, context, text)
        return
    
    # Handle customer service username input (after admin clicks add customer service)
    if 'waiting_for' in context.user_data and context.user_data['waiting_for'] == 'customer_service_username':
        from services.customer_service_service import customer_service
        from keyboards.inline_keyboard import get_customer_service_list_keyboard
        del context.user_data['waiting_for']
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ 仅管理员可以添加客服账号")
            return
        
        # Support batch adding: split by newline, comma, or space
        # Support formats:
        # 1. Newline-separated: @username1\n@username2\n@username3
        # 2. Comma-separated: @username1, @username2, @username3
        # 3. Space-separated: @username1 @username2 @username3
        # 4. Mixed: @username1, @username2\n@username3
        usernames_raw = text.strip()
        usernames_list = []
        
        # First, split by newline (most common format for bulk input)
        lines = usernames_raw.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Then split by comma
            comma_parts = line.split(',')
            for comma_part in comma_parts:
                comma_part = comma_part.strip()
                if not comma_part:
                    continue
                
                # Finally split by space (in case user uses space-separated format)
                space_parts = comma_part.split()
                for space_part in space_parts:
                    space_part = space_part.strip()
                    if not space_part:
                        continue
                    
                    # Remove @ symbol if present
                    username = space_part.lstrip('@').strip()
                    
                    # Validate username (Telegram usernames are 5-32 characters, but we allow 3+ for flexibility)
                    if username and len(username) >= 3 and len(username) <= 32:
                        # Basic validation: should only contain letters, numbers, and underscores
                        if re.match(r'^[a-zA-Z0-9_]+$', username):
                            usernames_list.append(username)
                        else:
                            logger.warning(f"Invalid username format: {username}")
                    elif username:
                        logger.warning(f"Username length invalid: {username} (length: {len(username)})")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_usernames = []
        for username in usernames_list:
            if username.lower() not in seen:
                seen.add(username.lower())
                unique_usernames.append(username)
        usernames_list = unique_usernames
        
        if not usernames_list:
            await update.message.reply_text(
                "❌ 未找到有效的用户名。\n\n"
                "💡 <b>支持的格式：</b>\n"
                "• 换行分隔：每行一个用户名（推荐）\n"
                "• 逗号分隔：用逗号分隔\n"
                "• 空格分隔：用空格分隔\n"
                "• 用户名可以带或不带 @ 符号\n\n"
                "示例：\n"
                "<code>@username1\n@username2\n@username3</code>",
                parse_mode="HTML"
            )
            return
        
        # Add all accounts
        success_count = 0
        failed_count = 0
        failed_usernames = []
        
        for username in usernames_list:
            success = customer_service.add_account(username=username, display_name=username)
            if success:
                success_count += 1
                logger.info(f"Admin {user_id} added customer service account: {username}")
            else:
                failed_count += 1
                failed_usernames.append(username)
        
        # Format response message
        if success_count > 0 and failed_count == 0:
            if success_count == 1:
                await update.message.reply_text(f"✅ 客服账号已添加：@{usernames_list[0]}")
            else:
                message = f"✅ 成功添加 {success_count} 个客服账号：\n\n"
                for username in usernames_list:
                    message += f"• @{username}\n"
                await update.message.reply_text(message)
        elif success_count > 0 and failed_count > 0:
            message = f"⚠️ 部分添加成功\n\n"
            message += f"✅ 成功：{success_count} 个\n"
            message += f"❌ 失败：{failed_count} 个（可能已存在）\n\n"
            if failed_usernames:
                message += "失败的账号：\n"
                for username in failed_usernames:
                    message += f"• @{username}\n"
            await update.message.reply_text(message)
        else:
            message = f"❌ 所有账号添加失败（可能已存在）：\n\n"
            for username in usernames_list:
                message += f"• @{username}\n"
            await update.message.reply_text(message)
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
                'usdt_amount': transaction['usdt_amount'],
                'price_source': transaction.get('price_source')  # May be None for old transactions
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
                # Show address using new address management system
                chat = update.effective_chat
                group_id = chat.id if chat.type in ['group', 'supergroup'] else None
                usdt_address = None
                
                if group_id:
                    from services.settlement_service import get_settlement_address
                    usdt_address = get_settlement_address(group_id=group_id, strategy='default')
                
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
        # Clear any pending context states when clicking management button
        if 'awaiting_admin_id' in context.user_data:
            del context.user_data['awaiting_admin_id']
        
        # Show help if needed
        button_text = "⚙️ 设置" if chat.type in ['group', 'supergroup'] else "⚙️ 管理"
        if should_show_help(user_id, button_text):
            help_message = format_button_help_message(button_text)
            if help_message:
                help_keyboard = get_button_help_keyboard(button_text)
                await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                mark_help_shown(user_id, button_text, shown=True)

        # Check admin permission - re-check to ensure consistency
        # The button is only shown to admins, so if user can see it, they should be admin
        # But we double-check here for security
        # Use the imported function from function scope to avoid UnboundLocalError
        from admin_checker import is_admin as check_is_admin
        current_admin_status = check_is_admin(user_id)
        logger.info(f"Settings button clicked by user {user_id}. Initial check: {is_admin_user}, Re-check: {current_admin_status}")
        
        if not current_admin_status:
            logger.warning(f"User {user_id} clicked settings button but is not admin. Initial check was: {is_admin_user}")
            # Show current admin list for diagnosis
            from config import Config
            current_admins = Config.INITIAL_ADMINS
            admin_list = ", ".join([str(uid) for uid in current_admins])
            
            # Provide helpful message with user ID and current admin list
            help_message = (
                "❌ 此功能仅限管理员使用\n\n"
                f"您的用户ID：<code>{user_id}</code>\n"
                f"当前配置的管理员：<code>{admin_list}</code>\n\n"
                "💡 如何添加管理员：\n"
                "1. 使用超级管理员账号发送：\n"
                f"   <code>/addadmin {user_id}</code>\n\n"
                "2. 或在服务器 .env 文件中添加：\n"
                f"   <code>ADMIN_IDS={admin_list},{user_id}</code>\n\n"
                "3. 或联系现有管理员添加您的账号"
            )
            await update.message.reply_text(help_message, parse_mode="HTML")
            return
        
        # For group chats, show group settings menu
        if chat.type in ['group', 'supergroup']:
            # 群组设置菜单 - 使用底部键盘
            from keyboards.management_keyboard import get_group_settings_menu_keyboard
            reply_keyboard = get_group_settings_menu_keyboard()
            message = (
                "⚙️ <b>群组设置菜单</b>\n\n"
                "请选择要执行的操作：\n\n"
                "💡 <i>提示：上方已显示完整指令教程，也可以点击「⚡ 管理员指令教程」再次查看</i>"
            )
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_keyboard)
            return
        
        # For private chats, show admin panel with all management functions
        # This will be handled by the handle_admin_panel function below
        # Don't return here, let it fall through to the handle_admin_panel call
    
    # "📈 统计" and "📊 数据" buttons removed from main menu
    # Statistics functionality is now only available in admin panel as "📊 数据统计"
    
    # Handle management menu buttons (bottom keyboard)
    # "📊 所有群组列表" is now merged into "📋 群组列表"
    # Removed this handler - functionality merged
    
    # "📈 全局统计" is now merged into "📊 数据统计"
    # Removed this handler - functionality merged
    
    if text == "📞 客服管理":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        # Show customer service management menu with bottom keyboard
        from keyboards.management_keyboard import get_customer_service_menu_keyboard
        reply_keyboard = get_customer_service_menu_keyboard()
        message = (
            "📞 <b>客服管理</b>\n\n"
            "请选择要执行的操作：\n\n"
            "• <b>客服账号列表</b>：查看和管理所有客服账号\n"
            "• <b>添加客服账号</b>：添加新的客服账号\n"
            "• <b>分配策略设置</b>：配置客服分配方式\n"
            "• <b>客服统计报表</b>：查看客服工作统计"
        )
        await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_keyboard)
        return
    
    if text == "⚡ 管理员指令教程":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        from handlers.admin_commands_handlers import handle_admin_commands_help
        await handle_admin_commands_help(update, context)
        return
    
    if text == "🔙 返回主菜单":
        # Return to main menu
        from keyboards.reply_keyboard import get_main_reply_keyboard
        user = update.effective_user
        user_info_dict = {
            'id': user.id,
            'first_name': user.first_name or '',
            'username': user.username,
            'language_code': user.language_code
        }
        is_group = chat.type in ['group', 'supergroup']
        reply_keyboard = get_main_reply_keyboard(user.id, is_group=is_group, user_info=user_info_dict)
        message = (
            "🏠 <b>主菜单</b>\n\n"
            "欢迎使用 OTC 群组管理 Bot\n\n"
            "请选择要执行的操作："
        )
        await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_keyboard)
        return
    
    # Old "返回管理菜单" handler removed - now use "返回主菜单" instead
    # The old management menu has been replaced by the unified admin panel
    
    # Handle customer service management menu buttons
    if text == "📋 客服账号列表":
        logger.info(f"User {user_id} clicked '客服账号列表' button")
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        # Display customer service account list directly
        from keyboards.inline_keyboard import get_customer_service_list_keyboard
        from services.customer_service_service import customer_service
        
        try:
            logger.debug(f"Fetching customer service accounts for user {user_id}")
            # Get all accounts
            accounts = customer_service.get_all_accounts(active_only=False)
            logger.info(f"Found {len(accounts)} customer service accounts")
            
            if not accounts:
                message = "📋 <b>客服账号列表</b>\n\n暂无客服账号。\n\n请点击「➕ 添加客服账号」添加第一个客服账号。"
                reply_markup = get_customer_service_list_keyboard([], page=0)
                await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
                logger.info(f"Displayed empty customer service list to user {user_id}")
                return
            
            # Format message (first page)
            page = 0
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
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
            logger.info(f"Successfully displayed customer service list ({len(accounts)} accounts) to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error displaying customer service list for user {user_id}: {e}", exc_info=True)
            await update.message.reply_text(f"❌ 显示客服账号列表时出错: {str(e)}")
        return
    
    if text == "➕ 添加客服账号":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        context.user_data['waiting_for'] = 'customer_service_username'
        await update.message.reply_text(
            "➕ <b>添加客服账号</b>\n\n"
            "请输入客服的 Telegram 用户名（例如：@username）\n\n"
            "💡 <b>支持批量添加</b>：\n"
            "• <b>换行分隔</b>：每行一个用户名（推荐）\n"
            "  示例：<code>@username1\n@username2\n@username3</code>\n\n"
            "• <b>逗号分隔</b>：用逗号分隔多个用户名\n"
            "  示例：<code>@username1, @username2, @username3</code>\n\n"
            "• <b>空格分隔</b>：用空格分隔多个用户名\n"
            "  示例：<code>@username1 @username2 @username3</code>\n\n"
            "• <b>混合格式</b>：可以混合使用以上格式\n"
            "  示例：<code>@username1, @username2\n@username3</code>\n\n"
            "💡 <i>提示：用户名可以带或不带 @ 符号</i>",
            parse_mode="HTML"
        )
        return
    
    if text == "⚙️ 分配策略设置":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        # Display customer service assignment strategy settings
        try:
            from services.customer_service_service import customer_service
            from keyboards.inline_keyboard import get_customer_service_strategy_keyboard
            
            # Get current strategy from settings (default: smart)
            all_settings = db.get_all_settings()
            current_method = all_settings.get('customer_service_strategy', 'smart')
            
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
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
            logger.info(f"Admin {user_id} viewed customer service strategy settings")
        except Exception as e:
            logger.error(f"Error displaying customer service strategy settings: {e}", exc_info=True)
            await update.message.reply_text(f"❌ 显示分配策略设置时出错: {str(e)}")
        return
    
    if text == "📊 客服统计报表":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        await update.message.reply_text("📊 客服统计报表功能正在开发中，请使用指令或稍后再试")
        return
    
    # Handle group settings menu buttons (bottom keyboard)
    if text == "📋 查看群组设置":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        await handle_admin_w0(update, context)
        return
    
    if text == "➕ 设置加价":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        context.user_data['waiting_for'] = 'group_markup'
        await update.message.reply_text(
            "➕ <b>设置群组加价</b>\n\n"
            "请输入加价值（例如：0.5 或 -0.5）：\n\n"
            "💡 <i>提示：正数表示加价，负数表示降价</i>",
            parse_mode="HTML"
        )
        return
    
    if text == "📍 地址管理":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        from handlers.address_handlers import handle_address_list
        await handle_address_list(update, context)
        return
    
    if text == "🔄 重置设置":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        # Reset group settings
        group_id = chat.id
        db.reset_group_settings(group_id)
        await update.message.reply_text(
            "✅ <b>群组设置已重置</b>\n\n"
            "群组将恢复使用全局默认设置。",
            parse_mode="HTML"
        )
        return
    
    if text == "❌ 删除配置":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        # Delete group settings
        group_id = chat.id
        db.delete_group_settings(group_id)
        await update.message.reply_text(
            "✅ <b>群组配置已删除</b>\n\n"
            "群组的独立配置已被清除，将使用全局默认设置。",
            parse_mode="HTML"
        )
        return
    
    if text == "⏳ 待支付交易":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        from handlers.stats_handlers import handle_pending_transactions
        await handle_pending_transactions(update, context, chat.id)
        return
    
    if text == "✅ 待确认交易":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        from handlers.stats_handlers import handle_paid_transactions
        await handle_paid_transactions(update, context, chat.id)
        return
    
    if text == "📊 群组统计":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        from handlers.stats_handlers import handle_group_stats
        await handle_group_stats(update, context)
        return
    
    if text == "📥 导出报表":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        await update.message.reply_text("📥 导出报表功能正在开发中，请使用指令或稍后再试")
        return
    
    if text == "📋 操作日志":
        if not is_admin_user:
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        await update.message.reply_text("📋 操作日志功能正在开发中，请使用指令或稍后再试")
        return
    
    if text in ["🔗 收款地址", "🔗 地址"]:
        chat = update.effective_chat
        
        # 在群组中：直接显示地址（不再显示帮助信息，因为地址消息中已包含使用说明）
        if chat.type in ['group', 'supergroup']:
            # 标记帮助已显示（避免在群组中显示帮助弹窗）
            mark_help_shown(user_id, "🔗 地址", shown=True)
            group_id = chat.id
            usdt_address = None
            address_source = "全局默认"  # 地址来源标识
            
            # 使用新的地址管理系统获取群组地址对象
            try:
                from services.settlement_service import get_settlement_address
                from utils.qr_generator import generate_qr_code_bytes, QRCODE_AVAILABLE
                
                # 获取地址对象（包括待确认的地址）
                # 先尝试获取已确认的地址
                address_obj = db.get_active_address(group_id=group_id, strategy='default')
                
                # 如果没有已确认的地址，尝试获取待确认的地址
                if not address_obj:
                    addresses = db.get_usdt_addresses(group_id=group_id, active_only=False)
                    # 查找待确认的地址
                    for addr in addresses:
                        if addr.get('pending_confirmation'):
                            address_obj = addr
                            break
                
                usdt_address = None
                qr_code_file_id = None
                is_pending = False
                
                if address_obj:
                    usdt_address = address_obj['address']
                    qr_code_file_id = address_obj.get('qr_code_file_id')
                    is_pending = address_obj.get('pending_confirmation', False)
                    address_source = "群组独立"
                    logger.info(f"Using group address from usdt_addresses table for {group_id}: {usdt_address[:15]}... (pending: {is_pending})")
                else:
                    # 如果没有群组地址，使用全局地址
                    global_addr = db.get_usdt_address()
                    if global_addr:
                        usdt_address = global_addr
                        address_source = "全局默认"
                        logger.info(f"Using global address for group {group_id}: {usdt_address[:15]}...")
                    else:
                        logger.info(f"No address found for group {group_id} (neither group nor global)")
            except Exception as e:
                logger.error(f"Error getting address for group {group_id}: {e}", exc_info=True)
                # 尝试获取全局地址作为fallback
                try:
                    usdt_address = db.get_usdt_address()
                    address_source = "全局默认"
                    qr_code_file_id = None
                except:
                    usdt_address = None
                    qr_code_file_id = None
            
            # 构建美化的消息
            if usdt_address:
                # 完整地址显示（用于复制）
                full_address = usdt_address
                # 显示用的地址（中间部分省略）
                if len(usdt_address) > 30:
                    address_display = f"{usdt_address[:15]}...{usdt_address[-15:]}"
                else:
                    address_display = usdt_address
                
                # 构建消息文本（简洁格式，无装饰性横线）
                pending_notice = ""
                if is_pending:
                    pending_notice = "\n⏳ <b>注意：此地址正在等待群组成员确认</b>\n"
                
                message = (
                    f"🔗 <b>USDT 收款地址</b>\n\n"
                    f"📍 <b>当前群组</b>：{chat.title or '未知群组'}\n"
                    f"🏷️  <b>地址类型</b>：{address_source}{pending_notice}\n\n"
                    f"<code>{full_address}</code>\n\n"
                    f"💡 <b>使用提示</b>\n"
                    f"扫描上方二维码或点击地址可快速复制\n"
                    f"请仔细核对地址后再进行转账\n\n"
                    f"🔒 <b>安全提示</b>\n"
                    f"⚠️ 为了账户安全，如需修改当前USDT收款地址，请联系客服进行修改\n"
                    f"📞 管理员可在机器人私聊中修改地址设置"
                )
                
                # 发送二维码和消息
                try:
                    bot = context.bot
                    
                    # 检查qrcode库是否可用
                    if not QRCODE_AVAILABLE:
                        logger.warning("qrcode library not available, sending text only")
                        await send_group_message(update, message + "\n\n⚠️ <i>二维码生成功能不可用，请安装qrcode库</i>", parse_mode="HTML")
                        return
                    
                    # 如果有上传的二维码，使用它；否则自动生成
                    if qr_code_file_id:
                        # 使用已上传的二维码
                        await bot.send_photo(
                            chat_id=group_id,
                            photo=qr_code_file_id,
                            caption=message,
                            parse_mode="HTML"
                        )
                        logger.info(f"Sent address with uploaded QR code for group {group_id}")
                    else:
                        # 自动生成二维码
                        qr_bytes = generate_qr_code_bytes(usdt_address)
                        if qr_bytes:
                            sent_message = await bot.send_photo(
                                chat_id=group_id,
                                photo=qr_bytes,
                                caption=message,
                                parse_mode="HTML"
                            )
                            logger.info(f"Sent address with auto-generated QR code for group {group_id}")
                            
                            # 如果地址已确认，保存生成的二维码file_id到数据库
                            if address_obj and not is_pending and address_obj.get('id'):
                                try:
                                    file_id = sent_message.photo[-1].file_id if sent_message.photo else None
                                    if file_id:
                                        db.update_address_qr_code(address_obj['id'], file_id)
                                        logger.info(f"Saved auto-generated QR code file_id for address {address_obj['id']}")
                                except Exception as save_error:
                                    logger.warning(f"Failed to save QR code file_id: {save_error}")
                        else:
                            # 如果生成失败，只发送文本消息
                            await send_group_message(update, message, parse_mode="HTML")
                            logger.warning(f"Failed to generate QR code, sent text only for group {group_id}")
                except Exception as e:
                    logger.error(f"Error sending address with QR code: {e}", exc_info=True)
                    # 如果发送失败，尝试只发送文本消息
                    try:
                        await send_group_message(update, message, parse_mode="HTML")
                    except Exception as inner_e:
                        logger.error(f"Error sending text message: {inner_e}", exc_info=True)
                        await send_group_message(update, "⚠️ 获取地址信息时出错，请稍后再试", parse_mode="HTML")
            else:
                message = (
                    f"⚠️ <b>地址未设置</b>\n\n"
                    f"📍 <b>当前群组</b>：{chat.title or '未知群组'}\n\n"
                    f"当前群组和全局均未设置USDT收款地址\n\n"
                    f"💡 <b>设置提示</b>\n"
                    f"管理员可在机器人私聊中使用命令设置\n"
                    f"或联系客服协助设置\n\n"
                    f"🔒 <b>安全提示</b>\n"
                    f"⚠️ 为了账户安全，如需设置或修改USDT收款地址，请联系客服进行操作"
                )
                
                try:
                    await send_group_message(update, message, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Error sending address message: {e}", exc_info=True)
                    await send_group_message(update, "⚠️ 获取地址信息时出错，请稍后再试", parse_mode="HTML")
            return
        
        # 在私聊中：显示用户所在的所有群组的USDT地址
        try:
            # 获取所有群组
            all_groups = db.get_all_groups()
            user_id = update.effective_user.id
            bot = context.bot
            
            # 检查用户所在的群组
            user_groups_with_address = []
            for group in all_groups:
                group_id = group['group_id']
                group_title = group.get('group_title', f"群组 {group_id}")
                usdt_address = group.get('usdt_address', '')
                
                # 检查用户是否在该群组中
                try:
                    member = await bot.get_chat_member(group_id, user_id)
                    # 检查用户是否在群组中（不是left或kicked）
                    if member.status not in ['left', 'kicked']:
                        # 使用新的地址管理系统获取群组地址
                        from services.settlement_service import get_settlement_address
                        usdt_address = get_settlement_address(group_id=group_id, strategy='default')
                        
                        # 如果没有群组地址，使用全局地址
                        if not usdt_address:
                            usdt_address = db.get_usdt_address()
                        
                        if usdt_address:
                            user_groups_with_address.append({
                                'group_id': group_id,
                                'group_title': group_title,
                                'usdt_address': usdt_address
                            })
                except Exception as e:
                    # 用户不在该群组中，或者无法访问，跳过
                    logger.debug(f"User {user_id} not in group {group_id}: {e}")
                    continue
            
            # 构建消息
            if user_groups_with_address:
                message = "🔗 <b>您所在群组的USDT收款地址</b>\n\n"
                message += "────────────────────────\n\n"
                
                for idx, group_info in enumerate(user_groups_with_address, 1):
                    group_title = group_info['group_title']
                    address = group_info['usdt_address']
                    address_display = address[:15] + "..." + address[-15:] if len(address) > 30 else address
                    
                    message += f"{idx}. <b>{group_title}</b>\n"
                    message += f"   <code>{address_display}</code>\n\n"
                
                message += "💡 提示：群组优先使用群组地址，否则使用全局地址"
            else:
                # 如果用户不在任何群组中，显示全局地址
                global_address = db.get_usdt_address()
                if global_address:
                    address_display = global_address[:15] + "..." + global_address[-15:] if len(global_address) > 30 else global_address
                    message = f"🔗 <b>USDT 收款地址</b>\n\n"
                    message += f"<code>{address_display}</code>\n\n"
                    message += "💡 提示：您当前不在任何群组中，显示全局默认地址"
                else:
                    message = "⚠️ USDT 收款地址未设置\n\n"
                    message += "💡 提示：请联系管理员设置收款地址"
            
            await update.message.reply_text(message, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error getting user groups addresses: {e}", exc_info=True)
            # 如果出错，显示全局地址作为fallback
            global_address = db.get_usdt_address()
            if global_address:
                address_display = global_address[:15] + "..." + global_address[-15:] if len(global_address) > 30 else global_address
                message = f"🔗 USDT 收款地址:\n\n<code>{address_display}</code>"
            else:
                message = "⚠️ USDT 收款地址未设置"
            await update.message.reply_text(message, parse_mode="HTML")
        
        return
    
    if text in ["📞 联系客服", "📞 客服"]:
        # Handle customer service assignment based on chat type
        if chat.type in ['group', 'supergroup']:
            # In group: assign customer service and directly jump to private chat
            # Skip help message and contact panel, go directly to customer service
            try:
                from services.customer_service_service import customer_service
                
                # Get current assignment strategy from settings
                all_settings = db.get_all_settings()
                assignment_method = all_settings.get('customer_service_strategy', 'smart')
                
                # Get user info
                user = update.effective_user
                username = user.username or f"user_{user.id}"
                
                # Assign customer service account
                service_account = customer_service.assign_service(
                    user_id=user.id,
                    username=username,
                    method=assignment_method
                )
                
                if service_account:
                    # Create inline keyboard with link to customer service
                    # Use https://t.me/username for direct chat opening
                    keyboard = [
                        [InlineKeyboardButton(
                            f"💬 联系客服 @{service_account}",
                            url=f"https://t.me/{service_account}"
                        )]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    # Send minimal message with button - user clicks button to jump directly to customer service chat
                    # No help message, no contact panel, just the jump button
                    await update.message.reply_text(
                        f"💬 <a href='https://t.me/{service_account}'>联系客服 @{service_account}</a>",
                        parse_mode="HTML",
                        reply_markup=reply_markup
                    )
                    logger.info(f"Assigned customer service @{service_account} to user {user.id} in group {chat.id}, direct jump enabled")
                else:
                    # No available customer service - show error message
                    await update.message.reply_text(
                        "⚠️ 当前没有可用的客服账号，请联系管理员：@wushizhifu_jianglai",
                        parse_mode="HTML"
                    )
                    logger.warning(f"No available customer service for user {user.id} in group {chat.id}")
            except Exception as e:
                logger.error(f"Error assigning customer service: {e}", exc_info=True)
                # Fallback to default message
                await update.message.reply_text(
                    "❌ 客服分配失败，请联系管理员：@wushizhifu_jianglai",
                    parse_mode="HTML"
                )
        else:
            # In private chat: show help if needed, then show contact information
            if should_show_help(user_id, "📞 客服"):
                help_message = format_button_help_message("📞 客服")
                if help_message:
                    help_keyboard = get_button_help_keyboard("📞 客服")
                    await update.message.reply_text(help_message, parse_mode="HTML", reply_markup=help_keyboard)
                    mark_help_shown(user_id, "📞 客服", shown=True)
            
            # Show contact information in private chat
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
        
        # Handle admin panel button
        if text in ["⚙️ 管理", "⚙️ 设置"]:
            # Clear any pending context states when clicking management button
            if 'awaiting_admin_id' in context.user_data:
                del context.user_data['awaiting_admin_id']
            await handle_admin_panel(update, context)
            return
        
        # Handle admin panel functions (using reply keyboard)
        if text == "👥 用户管理":
            await handle_admin_users(update, context)
            return
        
        if text == "📊 数据统计":
            await handle_unified_stats(update, context)
            return
        
        if text == "📋 群组管理":
            await handle_group_management(update, context)
            return
        
        if text == "⚙️ 系统设置":
            await handle_system_settings(update, context)
            return
        
        if text == "⚡ 帮助中心":
            await handle_admin_help_center(update, context)
            return
        
        # Handle guided tutorial selections (1-5)
        if text == "1" or text == "1️⃣" or text == "主菜单按钮教程":
            from utils.help_generator import HelpGenerator
            tutorial_text = HelpGenerator.get_main_menu_buttons_help()
            from keyboards.admin_keyboard import get_admin_panel_keyboard
            user = update.effective_user
            user_info = {
                'id': user.id,
                'first_name': user.first_name or '',
                'username': user.username,
                'language_code': user.language_code
            }
            reply_markup = get_admin_panel_keyboard(user_info)
            await send_group_message(update, tutorial_text, parse_mode="HTML", reply_markup=reply_markup)
            return
        
        if text == "2" or text == "2️⃣" or text == "管理员面板按钮教程":
            from utils.help_generator import HelpGenerator
            tutorial_text = HelpGenerator.get_admin_panel_buttons_help()
            from keyboards.admin_keyboard import get_admin_panel_keyboard
            user = update.effective_user
            user_info = {
                'id': user.id,
                'first_name': user.first_name or '',
                'username': user.username,
                'language_code': user.language_code
            }
            reply_markup = get_admin_panel_keyboard(user_info)
            await send_group_message(update, tutorial_text, parse_mode="HTML", reply_markup=reply_markup)
            return
        
        if text == "3" or text == "3️⃣" or text == "群组按钮和命令教程":
            from utils.help_generator import HelpGenerator
            tutorial_text = HelpGenerator.get_group_buttons_help()
            from keyboards.admin_keyboard import get_admin_panel_keyboard
            user = update.effective_user
            user_info = {
                'id': user.id,
                'first_name': user.first_name or '',
                'username': user.username,
                'language_code': user.language_code
            }
            reply_markup = get_admin_panel_keyboard(user_info)
            await send_group_message(update, tutorial_text, parse_mode="HTML", reply_markup=reply_markup)
            return
        
        if text == "4" or text == "4️⃣" or text == "管理员子菜单教程":
            from utils.help_generator import HelpGenerator
            tutorial_text = HelpGenerator.get_admin_submenus_help()
            from keyboards.admin_keyboard import get_admin_panel_keyboard
            user = update.effective_user
            user_info = {
                'id': user.id,
                'first_name': user.first_name or '',
                'username': user.username,
                'language_code': user.language_code
            }
            reply_markup = get_admin_panel_keyboard(user_info)
            await send_group_message(update, tutorial_text, parse_mode="HTML", reply_markup=reply_markup)
            return
        
        if text == "5" or text == "5️⃣" or text == "管理员命令帮助":
            from handlers.admin_commands_handlers import handle_admin_commands_help
            await handle_admin_commands_help(update, context)
            from keyboards.admin_keyboard import get_admin_panel_keyboard
            user = update.effective_user
            user_info = {
                'id': user.id,
                'first_name': user.first_name or '',
                'username': user.username,
                'language_code': user.language_code
            }
            reply_markup = get_admin_panel_keyboard(user_info)
            help_footer = "\n\n💡 返回帮助中心：点击「⚡ 帮助中心」按钮"
            await send_group_message(update, help_footer, parse_mode="HTML", reply_markup=reply_markup)
            return
        
        if text == "🚫 敏感词管理":
            await handle_admin_words(update, context)
            return
        
        if text == "✅ 群组审核":
            await handle_group_verification(update, context)
            return
        
        if text == "📋 群组列表":
            # Merge 群组列表 and 所有群组列表 - use handle_admin_w7 to show all groups
            await handle_admin_w7(update, context)
            return
        
        if text == "⚙️ 群组配置":
            await send_group_message(update,
                "💡 使用命令配置群组：\n"
                "<code>/group_mode &lt;group_id&gt; &lt;mode&gt;</code>\n\n"
                "模式：auto（自动通过）、manual（手动审核）、question（问题验证）\n\n"
                "示例：\n"
                "<code>/group_mode -1001234567890 manual</code>",
                parse_mode="HTML"
            )
            return
        
        if text == "🗑️ 删除群组":
            await send_group_message(update,
                "💡 使用命令删除群组：\n"
                "<code>/delgroup &lt;group_id&gt;</code>\n\n"
                "示例：\n"
                "<code>/delgroup -1001234567890</code>\n\n"
                "⚠️ 删除操作不可恢复，请谨慎操作",
                parse_mode="HTML"
            )
            return
        
        if text == "🔍 搜索群组":
            from utils.help_generator import HelpGenerator
            help_text = HelpGenerator.get_feature_help('group_search')
            await send_group_message(update, help_text, parse_mode="HTML")
            return
        
        # Handle approve/reject all (using reply keyboard)
        if text == "✅ 全部通过":
            await handle_verify_all_approve(update, context)
            return
        
        if text == "❌ 全部拒绝":
            await handle_verify_all_reject(update, context)
            return
        
        # Handle return buttons - old "返回管理面板" removed, use "返回主菜单" instead
        if text == "🔙 返回管理面板":
            # Old panel removed, redirect to main menu instead
            from keyboards.reply_keyboard import get_main_reply_keyboard
            user = update.effective_user
            chat = update.effective_chat
            is_group = chat.type in ['group', 'supergroup']
            user_info = {
                'id': user.id,
                'first_name': user.first_name or '',
                'username': user.username,
                'language_code': user.language_code
            }
            reply_keyboard = get_main_reply_keyboard(user.id, is_group, user_info)
            await send_group_message(update, "✅ 已返回主菜单", reply_markup=reply_keyboard)
            return
        
        if text == "🔙 返回主菜单":
            # Return to main menu
            from keyboards.reply_keyboard import get_main_reply_keyboard
            user = update.effective_user
            chat = update.effective_chat
            is_group = chat.type in ['group', 'supergroup']
            user_info = {
                'id': user.id,
                'first_name': user.first_name or '',
                'username': user.username,
                'language_code': user.language_code
            }
            reply_markup = get_main_reply_keyboard(user.id, is_group, user_info)
            
            # Simple main menu message
            text = (
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  🏠 主菜单\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "欢迎使用 WuShiPay Bot！\n\n"
                "请使用下方按钮进行操作。"
            )
            await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
            return
        
        # Handle admin submenu buttons
        if text == "🔍 搜索用户":
            await handle_admin_user_search(update, context)
            return
        
        if text == "📊 用户报表":
            await handle_admin_user_report(update, context)
            return
        
        if text == "👤 用户详情":
            await send_group_message(update,
                "💡 使用命令查看用户详情：\n"
                "<code>/user_detail &lt;user_id&gt;</code>\n\n"
                "示例：\n"
                "<code>/user_detail 123456789</code>\n\n"
                "将显示用户的详细信息：\n"
                "• 基本信息（用户名、姓名、VIP等级）\n"
                "• 交易统计（交易数、交易额）\n"
                "• 注册信息（注册时间、最后活跃时间）\n"
                "• 账户状态（活跃/禁用）",
                parse_mode="HTML"
            )
            return
        
        if text == "⚙️ 用户操作":
            await send_group_message(update,
                "💡 用户操作功能：\n\n"
                "<b>修改VIP等级：</b>\n"
                "<code>/set_vip &lt;user_id&gt; &lt;level&gt;</code>\n\n"
                "<b>禁用/启用用户：</b>\n"
                "<code>/disable_user &lt;user_id&gt;</code>\n"
                "<code>/enable_user &lt;user_id&gt;</code>\n\n"
                "示例：\n"
                "<code>/set_vip 123456789 1</code> (设置为VIP1)\n"
                "<code>/disable_user 123456789</code> (禁用用户)",
                parse_mode="HTML"
            )
            return
        
        if text == "📊 系统统计":
            await handle_admin_stats(update, context)
            return
        
        if text == "📈 全局统计":
            from handlers.stats_handlers import handle_global_stats
            await handle_global_stats(update, context)
            return
        
        if text == "📅 时间统计":
            await handle_admin_stats_time(update, context)
            return
        
        if text == "📋 详细报表":
            await handle_admin_stats_detail(update, context)
            return
        
        if text == "📋 操作日志":
            await handle_admin_operation_logs(update, context)
            return
        
        if text == "➕ 添加敏感词":
            await send_group_message(update, 
                "💡 使用命令添加敏感词：\n\n"
                "<b>单个添加：</b>\n"
                "<code>/addword &lt;词语&gt; [action]</code>\n\n"
                "<b>批量添加：</b>\n"
                "<code>/addword batch &lt;词语1,词语2,词语3&gt; [action]</code>\n\n"
                "动作：warn（警告）、delete（删除）、ban（封禁）\n\n"
                "<b>示例：</b>\n"
                "• <code>/addword 广告 delete</code>\n"
                "• <code>/addword batch 广告,诈骗,色情 delete</code>\n\n"
                "💡 批量添加最多支持50个敏感词",
                parse_mode="HTML"
            )
            return
        
        if text == "✏️ 编辑敏感词":
            await send_group_message(update,
                "💡 使用命令编辑敏感词：\n"
                "<code>/editword &lt;word_id&gt; &lt;new_action&gt;</code>\n\n"
                "动作：warn（警告）、delete（删除）、ban（封禁）\n\n"
                "示例：\n"
                "<code>/editword 1 delete</code> (将ID为1的敏感词动作改为删除)\n\n"
                "💡 敏感词ID可在敏感词列表中查看",
                parse_mode="HTML"
            )
            return
        
        if text == "🗑️ 删除敏感词":
            await send_group_message(update,
                "💡 使用命令删除敏感词：\n\n"
                "<b>单个删除：</b>\n"
                "<code>/delword &lt;word_id&gt;</code>\n\n"
                "<b>批量删除：</b>\n"
                "<code>/delword batch &lt;id1,id2,id3&gt;</code>\n\n"
                "<b>示例：</b>\n"
                "• <code>/delword 1</code> (删除ID为1的敏感词)\n"
                "• <code>/delword batch 1,2,3</code> (批量删除ID为1,2,3的敏感词)\n\n"
                "💡 敏感词ID可在敏感词列表中查看\n"
                "💡 批量删除最多支持50个敏感词\n"
                "⚠️ 删除操作不可恢复，请谨慎操作",
                parse_mode="HTML"
            )
            return
        
        if text == "📋 导出列表":
            await handle_admin_word_export(update, context)
            return
        
        if text == "📥 批量导入":
            await send_group_message(update,
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  📥 批量导入敏感词\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "<b>使用方法：</b>\n\n"
                "使用命令：<code>/import_words &lt;文本内容&gt;</code>\n\n"
                "<b>支持格式：</b>\n"
                "1. 每行一个词\n"
                "2. 逗号分隔：词,动作\n"
                "3. 多个词用空格分隔\n\n"
                "<b>动作类型：</b>\n"
                "• warn（警告）- 默认\n"
                "• delete（删除）\n"
                "• ban（封禁）\n\n"
                "<b>示例：</b>\n"
                "<code>/import_words 广告\\n诈骗,delete\\n赌博,ban</code>\n\n"
                "💡 最多支持100个敏感词\n"
                "💡 使用 <code>/export_words</code> 查看现有敏感词",
                parse_mode="HTML"
            )
            return
        
        if text == "💾 完整导出":
            await send_group_message(update,
                "💡 使用命令导出数据：\n\n"
                "<b>导出敏感词：</b>\n"
                "<code>/export_words</code>\n\n"
                "<b>导出用户数据：</b>\n"
                "<code>/export_users</code>\n\n"
                "💡 导出数据为CSV格式，可直接导入Excel",
                parse_mode="HTML"
            )
            return
        
        if text == "👤 审核详情":
            await handle_verification_detail(update, context)
            return
        
        if text == "📋 审核历史":
            await handle_verification_history(update, context)
            return
        
        if text == "➕ 添加群组":
            await send_group_message(update,
                "💡 使用命令添加群组：\n"
                "<code>/addgroup &lt;group_id&gt; [group_title]</code>\n\n"
                "示例：\n"
                "<code>/addgroup -1001234567890 测试群组</code>\n\n"
                "注意事项：\n"
                "• 群组ID必须以 -100 开头（超级群组）\n"
                "• 机器人必须是该群组的管理员",
                parse_mode="HTML"
            )
            return
        
        if text == "⚙️ 群组配置":
            await send_group_message(update,
                "💡 使用命令配置群组：\n\n"
                "<b>启用/禁用验证：</b>\n"
                "<code>/group_verify &lt;group_id&gt; enable</code>\n"
                "<code>/group_verify &lt;group_id&gt; disable</code>\n\n"
                "<b>设置验证模式：</b>\n"
                "<code>/group_mode &lt;group_id&gt; question</code> (问题验证)\n"
                "<code>/group_mode &lt;group_id&gt; manual</code> (手动验证)\n\n"
                "示例：\n"
                "<code>/group_verify -1001234567890 enable</code>",
                parse_mode="HTML"
            )
            return
        
        if text == "🗑️ 删除群组":
            await send_group_message(update,
                "💡 使用命令删除群组：\n"
                "<code>/delgroup &lt;group_id&gt;</code>\n\n"
                "示例：\n"
                "<code>/delgroup -1001234567890</code>\n\n"
                "⚠️ 删除操作不可恢复，请谨慎操作",
                parse_mode="HTML"
            )
            return
        
        if text == "➕ 添加管理员":
            if not is_admin_user:
                await send_group_message(update, "❌ 此功能仅限管理员使用")
                return
            await handle_admin_add(update, context)
            return
        
        if text == "🗑️ 删除管理员":
            await send_group_message(update,
                "💡 使用命令删除管理员：\n"
                "<code>/deladmin &lt;user_id&gt;</code>\n\n"
                "示例：\n"
                "<code>/deladmin 123456789</code>\n\n"
                "⚠️ 删除操作不可恢复，请谨慎操作",
                parse_mode="HTML"
            )
            return
        
        if text == "📋 管理员列表":
            if not is_admin_user:
                await send_group_message(update, "❌ 此功能仅限管理员使用")
                return
            await handle_admin_add(update, context)  # handle_admin_add also shows admin list
            return
        
        if text == "🔙 返回主菜单":
            # Return to main menu - show welcome message with main keyboard
            from keyboards.reply_keyboard import get_main_reply_keyboard
            user = update.effective_user
            is_group = chat.type in ['group', 'supergroup']
            user_info = {
                'id': user.id,
                'first_name': user.first_name or '',
                'username': user.username,
                'language_code': user.language_code
            }
            reply_markup = get_main_reply_keyboard(user.id, is_group, user_info)
            await send_group_message(update, "✅ 已返回主菜单", reply_markup=reply_markup)
            return
    
    # Check if message is a number, math expression, or batch amounts (settlement calculation)
    # BUT only if NOT awaiting admin ID input (already checked earlier)
    if 'awaiting_admin_id' not in context.user_data:
        if is_number(text) or is_simple_math(text) or is_batch_amounts(text):
            await handle_math_settlement(update, context, text)
            return
    
    # Otherwise, ignore the message


# ========== Group Management Handlers ==========

async def handle_group_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group verification management (using reply keyboard)"""
    from repositories.group_repository import GroupRepository
    from database import db
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT gm.*, g.group_title 
            FROM group_members gm
            JOIN groups g ON gm.group_id = g.group_id
            WHERE gm.status = 'pending'
            ORDER BY gm.joined_at ASC
            LIMIT 10
        """)
        
        pending = cursor.fetchall()
        cursor.close()
        
        if not pending:
            text = (
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  ✅ 群组审核\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "暂无待审核成员\n\n"
                "所有成员已审核完成"
            )
        else:
            text = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  ✅ 群组审核\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>待审核成员（共 {len(pending)} 人）：</b>\n\n"
            )
            
            for idx, member in enumerate(pending[:10], 1):
                user_id = member['user_id']
                group_title = member['group_title'] if member['group_title'] else f"群组 {member['group_id']}"
                joined_at = member['joined_at'][:16] if member['joined_at'] else 'N/A'
                
                text += (
                    f"{idx}. 用户ID：<code>{user_id}</code>\n"
                    f"   群组：{group_title}\n"
                    f"   加入时间：{joined_at}\n\n"
                )
            
            text += "💡 使用下方按钮进行审核操作"
        
        from keyboards.admin_keyboard import get_admin_submenu_keyboard
        reply_markup = get_admin_submenu_keyboard("verify")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_group_verification: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_group_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group list (using reply keyboard)"""
    from repositories.group_repository import GroupRepository
    from database import db
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT g.*, 
                   COUNT(DISTINCT gm.user_id) as member_count,
                   COUNT(DISTINCT CASE WHEN gm.status = 'pending' THEN gm.user_id END) as pending_count,
                   COUNT(DISTINCT CASE WHEN gm.status = 'verified' THEN gm.user_id END) as verified_count
            FROM groups g
            LEFT JOIN group_members gm ON g.group_id = gm.group_id
            GROUP BY g.group_id
            ORDER BY g.created_at DESC
            LIMIT 20
        """)
        
        groups = cursor.fetchall()
        cursor.close()
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  📋 群组列表\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>已管理群组（共 {len(groups)} 个）：</b>\n\n"
        )
        
        if not groups:
            text += "暂无管理的群组\n\n请先添加群组到管理系统"
        else:
            for idx, group in enumerate(groups[:20], 1):
                group_id = group['group_id']
                group_title = group['group_title'] if group['group_title'] else f"群组 {group_id}"
                verification_enabled = group['verification_enabled'] if group['verification_enabled'] is not None else 0
                member_count = group['member_count'] if group['member_count'] is not None else 0
                pending_count = group['pending_count'] if group['pending_count'] is not None else 0
                verified_count = group['verified_count'] if group['verified_count'] is not None else 0
                
                verification_text = "已开启" if verification_enabled else "已关闭"
                
                text += (
                    f"{idx}. {group_title}\n"
                    f"   ID：<code>{group_id}</code>\n"
                    f"   审核：{verification_text} | "
                    f"成员：{member_count} | "
                    f"已审核：{verified_count} | "
                    f"待审核：{pending_count}\n\n"
                )
            
            if len(groups) >= 20:
                text += f"显示前 20 个群组...\n\n"
        
        from keyboards.admin_keyboard import get_admin_submenu_keyboard
        reply_markup = get_admin_submenu_keyboard("group")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_group_list: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_group_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group settings (using reply keyboard)"""
    from repositories.group_repository import GroupRepository
    from database import db
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT g.*, 
                   COUNT(DISTINCT gm.user_id) as member_count,
                   COUNT(DISTINCT CASE WHEN gm.status = 'pending' THEN gm.user_id END) as pending_count
            FROM groups g
            LEFT JOIN group_members gm ON g.group_id = gm.group_id
            GROUP BY g.group_id
            ORDER BY g.created_at DESC
            LIMIT 10
        """)
        
        groups = cursor.fetchall()
        cursor.close()
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  ⚙️ 群组设置\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        if not groups:
            text += "暂无管理的群组\n\n请先添加群组到管理系统"
        else:
            text += f"<b>已管理群组（共 {len(groups)} 个）：</b>\n\n"
            
            for idx, group in enumerate(groups[:10], 1):
                group_id = group['group_id']
                group_title = group['group_title'] if group['group_title'] else f"群组 {group_id}"
                verification_enabled = group['verification_enabled'] if group['verification_enabled'] is not None else 0
                member_count = group['member_count'] if group['member_count'] is not None else 0
                pending_count = group['pending_count'] if group['pending_count'] is not None else 0
                
                verification_text = "已开启" if verification_enabled else "已关闭"
                
                text += (
                    f"{idx}. {group_title}\n"
                    f"   审核：{verification_text} | "
                    f"成员：{member_count} | "
                    f"待审核：{pending_count}\n\n"
                )
            
            text += "💡 使用命令管理群组：\n"
            text += "• <code>/search_group &lt;条件&gt;</code> - 搜索群组\n"
            text += "• <code>/group_detail &lt;group_id&gt;</code> - 查看群组详情\n"
            text += "• <code>/addgroup &lt;group_id&gt; [group_title]</code> - 添加群组\n"
            text += "• <code>/group_verify &lt;group_id&gt; enable/disable</code> - 启用/禁用验证\n"
            text += "• <code>/group_mode &lt;group_id&gt; question/manual</code> - 设置验证模式\n"
            text += "• 在群组中使用 w2/w3 命令设置群组加价和地址"
        
        from keyboards.admin_keyboard import get_admin_submenu_keyboard
        reply_markup = get_admin_submenu_keyboard("group")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_group_settings: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_verify_all_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle approve all pending members (using reply keyboard)"""
    from repositories.group_repository import GroupRepository
    
    try:
        count = GroupRepository.verify_all_pending_members()
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  ✅ 全部通过\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ 已通过 {count} 位待审核成员\n\n"
            f"所有待审核成员已自动通过验证"
        )
        
        await send_group_message(update, text, parse_mode="HTML")
        
        # Refresh the verification page
        await handle_group_verification(update, context)
        
    except Exception as e:
        logger.error(f"Error in handle_verify_all_approve: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_verify_all_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reject all pending members (using reply keyboard)"""
    from repositories.group_repository import GroupRepository
    
    try:
        count = GroupRepository.reject_all_pending_members()
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  ❌ 全部拒绝\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"❌ 已拒绝 {count} 位待审核成员\n\n"
            f"所有待审核成员已自动拒绝"
        )
        
        await send_group_message(update, text, parse_mode="HTML")
        
        # Refresh the verification page
        await handle_group_verification(update, context)
        
    except Exception as e:
        logger.error(f"Error in handle_verify_all_reject: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


# ========== Admin Panel Handlers ==========

async def handle_unified_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unified statistics menu (combines system stats and global stats)"""
    from telegram import ReplyKeyboardMarkup, KeyboardButton
    
    try:
        text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  📊 数据统计\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>📈 统计功能</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>系统统计</b>：查看系统整体数据\n"
            "📈 <b>全局统计</b>：查看所有群组统计\n"
            "📅 <b>时间统计</b>：按时间段查看数据\n"
            "📋 <b>详细报表</b>：查看详细分析报告\n\n"
            "请选择要查看的统计类型："
        )
        
        keyboard = [
            [
                KeyboardButton("📊 系统统计"),
                KeyboardButton("📈 全局统计")
            ],
            [
                KeyboardButton("📅 时间统计"),
                KeyboardButton("📋 详细报表")
            ],
            [
                KeyboardButton("📋 操作日志"),
                KeyboardButton("🔙 返回主菜单")
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_unified_stats: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_group_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group management menu (combines group list, verification, and settings)"""
    from telegram import ReplyKeyboardMarkup, KeyboardButton
    
    try:
        text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  📋 群组管理\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>🎯 群组功能</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 <b>群组列表</b>：查看所有群组\n"
            "✅ <b>群组审核</b>：审核新成员\n"
            "⚙️ <b>群组配置</b>：管理群组设置\n\n"
            "请选择要执行的操作："
        )
        
        keyboard = [
            [
                KeyboardButton("📋 群组列表"),
                KeyboardButton("✅ 群组审核")
            ],
            [
                KeyboardButton("➕ 添加群组"),
                KeyboardButton("🔍 搜索群组")
            ],
            [
                KeyboardButton("⚙️ 群组配置"),
                KeyboardButton("🗑️ 删除群组")
            ],
            [
                KeyboardButton("🔙 返回主菜单")
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_group_management: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_system_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle system settings menu (combines admin management and system config)"""
    from telegram import ReplyKeyboardMarkup, KeyboardButton
    
    try:
        text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  ⚙️ 系统设置\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>🎯 系统功能</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 <b>管理员管理</b>：添加/删除管理员\n"
            "⚙️ <b>系统配置</b>：系统参数设置\n\n"
            "请选择要执行的操作："
        )
        
        keyboard = [
            [
                KeyboardButton("➕ 添加管理员"),
                KeyboardButton("🗑️ 删除管理员")
            ],
            [
                KeyboardButton("📋 管理员列表"),
                KeyboardButton("🔙 返回主菜单")
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_system_settings: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_help_center(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin help center with guided tutorial"""
    try:
        from utils.help_generator import HelpGenerator
        from keyboards.admin_keyboard import get_admin_panel_keyboard
        
        user = update.effective_user
        user_info = {
            'id': user.id,
            'first_name': user.first_name or '',
            'username': user.username,
            'language_code': user.language_code
        }
        
        # Show guided tutorial menu
        text = HelpGenerator.get_guided_tutorial_menu()
        reply_markup = get_admin_panel_keyboard(user_info)
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_help_center: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin panel entry (using reply keyboard)"""
    from keyboards.admin_keyboard import get_admin_panel_keyboard
    
    try:
        user = update.effective_user
        user_info = {
            'id': user.id,
            'first_name': user.first_name or '',
            'username': user.username,
            'language_code': user.language_code
        }
        
        text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  ⚙️ 管理员面板\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>🎯 管理功能</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👥 <b>用户管理</b>：查看和管理用户\n"
            "📋 <b>群组管理</b>：群组列表、审核、设置\n"
            "🚫 <b>敏感词管理</b>：管理敏感词\n"
            "📊 <b>数据统计</b>：系统统计、全局统计、详细报表\n"
            "📞 <b>客服管理</b>：管理客服账号\n"
            "⚙️ <b>系统设置</b>：管理员管理、系统配置\n"
            "⚡ <b>帮助中心</b>：指令教程、使用帮助\n\n"
            "请选择要管理的功能："
        )
        
        reply_markup = get_admin_panel_keyboard(user_info)
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_panel: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin users management (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'active'")
        active_users = cursor.fetchone()[0]
        
        # Get today's new users
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')")
        today_new = cursor.fetchone()[0]
        
        # Get VIP users
        cursor.execute("SELECT COUNT(*) FROM users WHERE vip_level > 0")
        vip_users = cursor.fetchone()[0]
        
        # Get recent users
        cursor.execute("""
            SELECT user_id, username, first_name, vip_level, created_at 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_users = cursor.fetchall()
        cursor.close()
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  👥 用户管理\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>📊 用户统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"总用户数：{total_users}\n"
            f"活跃用户：{active_users}\n"
            f"今日新增：{today_new}\n"
            f"VIP用户：{vip_users}\n\n"
            f"<b>📋 最近注册用户（前10名）</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        
        if not recent_users:
            text += "暂无用户数据"
        else:
            for idx, user in enumerate(recent_users[:10], 1):
                username = user['username'] if user['username'] else '无'
                username_display = f"@{username}" if username != '无' else "无"
                first_name = user['first_name'] if user['first_name'] else ''
                vip_level = user['vip_level'] if user['vip_level'] is not None else 0
                user_id = user['user_id']
                created_at = user['created_at'][:10] if user['created_at'] else 'N/A'
                
                vip_text = f"VIP{vip_level}" if vip_level > 0 else "普通"
                
                text += (
                    f"{idx}. {username_display} (ID: <code>{user_id}</code>)\n"
                    f"   姓名：{first_name or '未设置'} | {vip_text} | {created_at}\n\n"
                )
        
        text += "\n💡 使用下方按钮查看更多功能"
        
        # Add pagination buttons if needed (for future implementation)
        reply_markup = get_admin_submenu_keyboard("users")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_users: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin statistics (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get transaction statistics
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_transactions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'paid'")
        paid_transactions = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE status = 'paid'")
        total_amount = cursor.fetchone()[0] or 0
        
        # Get today's transactions
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE DATE(created_at) = DATE('now') AND status = 'paid'
        """)
        today_result = cursor.fetchone()
        today_transactions = today_result[0] or 0
        today_amount = float(today_result[1] or 0)
        
        # Get yesterday's transactions
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE DATE(created_at) = DATE('now', '-1 day') AND status = 'paid'
        """)
        yesterday_result = cursor.fetchone()
        yesterday_transactions = yesterday_result[0] or 0
        
        # Get channel statistics
        cursor.execute("""
            SELECT payment_channel, COUNT(*) as count 
            FROM transactions 
            WHERE status = 'paid' 
            GROUP BY payment_channel
        """)
        channel_stats = cursor.fetchall()
        
        # Get user statistics
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')")
        today_new_users = cursor.fetchone()[0]
        
        # Get referral statistics
        cursor.execute("SELECT COUNT(*) FROM referrals WHERE status = 'rewarded'")
        successful_invites = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(total_rewards), 0) FROM referral_codes")
        total_referral_rewards = float(cursor.fetchone()[0] or 0)
        cursor.close()
        
        success_rate = (paid_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  📊 系统统计\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>💎 核心指标</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"总交易数：{total_transactions} 笔\n"
            f"成功交易：{paid_transactions} 笔 ({success_rate:.1f}%)\n"
            f"总交易额：{total_amount:,.2f} CNY\n"
            f"今日交易：{today_transactions} 笔 / {today_amount:,.2f} CNY\n\n"
            f"<b>📈 交易趋势</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"今日：{today_transactions} 笔\n"
            f"昨日：{yesterday_transactions} 笔\n\n"
        )
        
        if channel_stats:
            text += f"<b>💳 支付渠道统计</b>\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            total_paid = sum(stat['count'] for stat in channel_stats)
            for stat in channel_stats:
                channel = stat['payment_channel']
                count = stat['count']
                percentage = (count / total_paid * 100) if total_paid > 0 else 0
                channel_text = "支付宝" if channel == "alipay" else "微信支付"
                text += f"{channel_text}：{count} 笔 ({percentage:.1f}%)\n"
            text += "\n"
        
        text += (
            f"<b>👥 用户统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"总用户：{total_users}\n"
            f"今日新增：{today_new_users}\n\n"
            f"<b>🎁 分享活动统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"成功邀请：{successful_invites} 人\n"
            f"累计奖励：{total_referral_rewards:,.2f} USDT\n\n"
            f"💡 更多详细报表功能开发中..."
        )
        
        reply_markup = get_admin_submenu_keyboard("stats")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_stats: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_stats_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle time-based statistics (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get today's statistics
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE DATE(created_at) = DATE('now') AND status = 'paid'
        """)
        today_result = cursor.fetchone()
        today_count = today_result['count'] or 0
        today_amount = float(today_result['total'] or 0)
        
        # Get yesterday's statistics
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE DATE(created_at) = DATE('now', '-1 day') AND status = 'paid'
        """)
        yesterday_result = cursor.fetchone()
        yesterday_count = yesterday_result['count'] or 0
        yesterday_amount = float(yesterday_result['total'] or 0)
        
        # Get this week's statistics
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE DATE(created_at) >= DATE('now', '-7 days') AND status = 'paid'
        """)
        week_result = cursor.fetchone()
        week_count = week_result['count'] or 0
        week_amount = float(week_result['total'] or 0)
        
        # Get this month's statistics
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE DATE(created_at) >= DATE('now', 'start of month') AND status = 'paid'
        """)
        month_result = cursor.fetchone()
        month_count = month_result['count'] or 0
        month_amount = float(month_result['total'] or 0)
        
        # Get user statistics
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')")
        today_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) >= DATE('now', '-7 days')")
        week_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) >= DATE('now', 'start of month')")
        month_users = cursor.fetchone()[0]
        
        # Calculate growth rates
        today_growth = ((today_amount - yesterday_amount) / yesterday_amount * 100) if yesterday_amount > 0 else 0
        week_growth = ((week_amount - (yesterday_amount * 7)) / (yesterday_amount * 7) * 100) if yesterday_amount > 0 else 0
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  📅 时间统计\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>💳 交易统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>今日</b>\n"
            f"交易：{today_count} 笔 / {today_amount:,.2f} CNY\n"
        )
        
        if yesterday_amount > 0:
            growth_icon = "📈" if today_growth >= 0 else "📉"
            text += f"{growth_icon} 较昨日：{abs(today_growth):.1f}%\n\n"
        else:
            text += "\n"
        
        text += (
            f"<b>昨日</b>\n"
            f"交易：{yesterday_count} 笔 / {yesterday_amount:,.2f} CNY\n\n"
            f"<b>本周</b>\n"
            f"交易：{week_count} 笔 / {week_amount:,.2f} CNY\n"
        )
        
        if yesterday_amount > 0:
            growth_icon = "📈" if week_growth >= 0 else "📉"
            text += f"{growth_icon} 较上周：{abs(week_growth):.1f}%\n\n"
        else:
            text += "\n"
        
        text += (
            f"<b>本月</b>\n"
            f"交易：{month_count} 笔 / {month_amount:,.2f} CNY\n\n"
            f"<b>👥 用户统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"今日新增：{today_users} 人\n"
            f"本周新增：{week_users} 人\n"
            f"本月新增：{month_users} 人\n\n"
            f"💡 统计时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        reply_markup = get_admin_submenu_keyboard("stats")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_stats_time: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_stats_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle detailed statistics report (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get detailed transaction statistics by status
        cursor.execute("""
            SELECT status, COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            GROUP BY status
        """)
        status_stats = cursor.fetchall()
        
        # Get channel statistics
        cursor.execute("""
            SELECT payment_channel, COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE status = 'paid'
            GROUP BY payment_channel
        """)
        channel_stats = cursor.fetchall()
        
        # Get transaction type statistics
        cursor.execute("""
            SELECT transaction_type, COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE status = 'paid'
            GROUP BY transaction_type
        """)
        type_stats = cursor.fetchall()
        
        # Get top users by transaction amount
        cursor.execute("""
            SELECT user_id, COUNT(*) as count, COALESCE(SUM(amount), 0) as total
            FROM transactions
            WHERE status = 'paid'
            GROUP BY user_id
            ORDER BY total DESC
            LIMIT 10
        """)
        top_users = cursor.fetchall()
        cursor.close()
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  📊 详细报表\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>💳 交易状态统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        
        total_all = sum(stat['count'] for stat in status_stats)
        for stat in status_stats:
            status = stat['status']
            count = stat['count']
            amount = float(stat['total'] or 0)
            
            status_text = {
                "paid": "✅ 已支付",
                "pending": "⏳ 待支付",
                "failed": "❌ 失败",
                "cancelled": "🚫 已取消"
            }.get(status, status)
            
            percentage = (count / total_all * 100) if total_all > 0 else 0
            text += f"{status_text}：{count} 笔 ({percentage:.1f}%) / {amount:,.2f} CNY\n"
        
        text += "\n"
        
        if channel_stats:
            text += f"<b>💳 支付渠道统计</b>\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            total_paid = sum(float(stat['total'] or 0) for stat in channel_stats)
            for stat in channel_stats:
                channel = stat['payment_channel']
                count = stat['count']
                amount = float(stat['total'] or 0)
                percentage = (amount / total_paid * 100) if total_paid > 0 else 0
                
                channel_text = "💙 支付宝" if channel == "alipay" else "💚 微信支付"
                text += f"{channel_text}：{count} 笔 / {amount:,.2f} CNY ({percentage:.1f}%)\n"
            text += "\n"
        
        if type_stats:
            text += f"<b>📋 交易类型统计</b>\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for stat in type_stats:
                trans_type = stat['transaction_type']
                count = stat['count']
                amount = float(stat['total'] or 0)
                
                type_text = {"receive": "💰 收款", "pay": "💸 付款"}.get(trans_type, trans_type)
                text += f"{type_text}：{count} 笔 / {amount:,.2f} CNY\n"
            text += "\n"
        
        if top_users:
            text += f"<b>🏆 交易额TOP10用户</b>\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for idx, user in enumerate(top_users[:10], 1):
                user_id = user['user_id']
                count = user['count']
                amount = float(user['total'] or 0)
                text += f"{idx}. ID:<code>{user_id}</code> - {count}笔 / {amount:,.2f} CNY\n"
            text += "\n"
        
            from datetime import datetime
            text += f"💡 报表生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        reply_markup = get_admin_submenu_keyboard("stats")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_stats_detail: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add admin (using reply keyboard) - prompts for admin ID"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        # Set context to await admin ID input
        context.user_data['awaiting_admin_id'] = True
        
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get all admins
        cursor.execute("""
            SELECT a.*, u.username, u.first_name 
            FROM admins a
            LEFT JOIN users u ON a.user_id = u.user_id
            WHERE a.status = 'active'
            ORDER BY a.added_at DESC
        """)
        
        admins = cursor.fetchall()
        cursor.close()
        
        text = (
            f"👤 <b>添加管理员</b>\n\n"
            f"<b>📋 当前管理员（共 {len(admins)} 人）：</b>\n\n"
        )
        
        if not admins:
            text += "暂无管理员\n\n"
        else:
            for idx, admin in enumerate(admins[:10], 1):
                user_id = admin['user_id']
                username = admin['username'] if admin['username'] else '无'
                username_display = f"@{username}" if username != '无' else "无"
                first_name = admin['first_name'] if admin['first_name'] else ''
                role = admin['role'] if admin['role'] else 'admin'
                added_at = admin['added_at'][:10] if admin['added_at'] else 'N/A'
                
                text += (
                    f"{idx}. {username_display} (ID: <code>{user_id}</code>)\n"
                    f"   姓名：{first_name or '未设置'} | 角色：{role} | 添加时间：{added_at}\n\n"
                )
        
        text += (
            f"<b>💡 请输入要添加的管理员ID：</b>\n\n"
            f"例如：<code>123456789</code>\n\n"
            f"⚠️ 只有超级管理员可以添加管理员"
        )
        
        reply_markup = get_admin_submenu_keyboard("add")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_add: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id_text: str):
    """Handle admin ID input after user clicks '添加管理员'"""
    from database import db
    from services.permission_service import PermissionService
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        user = update.effective_user
        
        # Check if user has permission to add admins
        if not PermissionService.can_manage_admins(user.id):
            del context.user_data['awaiting_admin_id']
            await send_group_message(update, 
                "❌ 您没有权限添加管理员\n\n"
                "💡 只有超级管理员可以添加或删除管理员",
                parse_mode="HTML"
            )
            return
        
        # Parse user ID
        try:
            new_admin_id = int(user_id_text.strip())
        except ValueError:
            await send_group_message(update, 
                "❌ 无效的用户ID格式\n\n"
                "💡 请输入数字ID，例如：<code>123456789</code>",
                parse_mode="HTML"
            )
            return
        
        # Check if already admin
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM admins WHERE user_id = ? AND status = 'active'", (new_admin_id,))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            del context.user_data['awaiting_admin_id']
            await send_group_message(update, 
                f"❌ 添加失败\n\n"
                f"用户 <code>{new_admin_id}</code> 已经是管理员",
                parse_mode="HTML"
            )
            return
        
        # Add admin
        from datetime import datetime
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO admins (user_id, role, status, added_by, added_at)
            VALUES (?, 'admin', 'active', ?, ?)
        """, (new_admin_id, user.id, now))
        conn.commit()
        cursor.close()
        
        # Also add to shared database (Bot A)
        try:
            import sys
            from pathlib import Path
            # Try to import AdminRepository
            try:
                from database.admin_repository import AdminRepository
            except ImportError:
                # Add parent directory to path if needed
                parent_dir = Path(__file__).parent.parent.parent
                if str(parent_dir) not in sys.path:
                    sys.path.insert(0, str(parent_dir))
                from database.admin_repository import AdminRepository
            
            AdminRepository.add_admin(new_admin_id, role="admin", added_by=user.id)
        except Exception as e:
            logger.warning(f"Failed to add admin to shared database: {e}")
        
        # Clean up context
        del context.user_data['awaiting_admin_id']
        
        # Success message
        message = (
            f"✅ <b>已添加管理员</b>\n\n"
            f"用户ID：<code>{new_admin_id}</code>\n"
            f"角色：普通管理员\n\n"
            f"📝 此管理员已同步到 Bot A 和 Bot B，无需重启服务即可生效。"
        )
        
        reply_markup = get_admin_submenu_keyboard("add")
        await send_group_message(update, message, parse_mode="HTML", reply_markup=reply_markup)
        
        logger.info(f"Super admin {user.id} added admin {new_admin_id} via UI")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_id_input: {e}", exc_info=True)
        if 'awaiting_admin_id' in context.user_data:
            del context.user_data['awaiting_admin_id']
        await send_group_message(update, "❌ 添加失败，请稍后再试", parse_mode="HTML")


async def handle_admin_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sensitive words management (using reply keyboard)"""
    from repositories.sensitive_words_repository import SensitiveWordsRepository
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        words = SensitiveWordsRepository.get_words()
        
        if not words:
            text = (
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  🚫 敏感词管理\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "暂无敏感词\n\n"
                "请使用 <code>/addword &lt;词语&gt; [action]</code> 添加\n"
                "动作：warn（警告）、delete（删除）、ban（封禁）"
            )
        else:
            text = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  🚫 敏感词管理\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>当前敏感词列表（共 {len(words)} 个）：</b>\n\n"
            )
            
            action_map = {"warn": "警告", "delete": "删除", "ban": "封禁"}
            
            for idx, word in enumerate(words[:15], 1):
                action_text = action_map.get(word['action'], word['action'])
                word_id = word['word_id']
                text += f"{idx}. ID:{word_id} <code>{word['word']}</code> - {action_text}\n"
            
            if len(words) > 15:
                text += f"\n还有 {len(words) - 15} 个...\n\n"
            
            text += "💡 使用命令操作：\n"
            text += "• <code>/delword &lt;word_id&gt;</code> - 删除敏感词\n"
            text += "• <code>/editword &lt;word_id&gt; &lt;action&gt;</code> - 编辑敏感词"
        
        reply_markup = get_admin_submenu_keyboard("words")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_words: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


# ========== Admin Submenu Handlers ==========

async def handle_admin_user_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user search (using reply keyboard) - show search instructions"""
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "  🔍 搜索用户\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>搜索方式：</b>\n"
        "1. 按用户ID搜索\n"
        "2. 按用户名搜索\n"
        "3. 按VIP等级搜索\n"
        "4. 按注册时间搜索\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>操作说明：</b>\n"
        "请使用命令进行搜索：\n\n"
        "<code>/search_user &lt;条件&gt;</code>\n\n"
        "<b>示例：</b>\n"
        "• <code>/search_user 123456789</code> (按ID)\n"
        "• <code>/search_user @username</code> (按用户名)\n"
        "• <code>/search_user vip:1</code> (VIP等级)\n"
        "• <code>/search_user date:2025-12-26</code> (注册日期)\n\n"
        "💡 输入搜索条件后，系统会显示匹配的用户列表"
    )
    
    reply_markup = get_admin_submenu_keyboard("users")
    await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)


async def handle_admin_user_search_result(update: Update, context: ContextTypes.DEFAULT_TYPE, search_query: str):
    """Handle user search result (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        users = []
        search_type = "unknown"
        
        # Parse search query
        if search_query.isdigit():
            # Search by user ID
            user_id = int(search_query)
            cursor.execute("""
                SELECT user_id, username, first_name, vip_level, created_at, status, total_transactions, total_amount
                FROM users 
                WHERE user_id = ?
            """, (user_id,))
            users = cursor.fetchall()
            search_type = "ID"
        elif search_query.startswith("@"):
            # Search by username
            username = search_query[1:].strip()
            cursor.execute("""
                SELECT user_id, username, first_name, vip_level, created_at, status, total_transactions, total_amount
                FROM users 
                WHERE username LIKE ?
                LIMIT 20
            """, (f"%{username}%",))
            users = cursor.fetchall()
            search_type = "用户名"
        elif search_query.startswith("vip:"):
            # Search by VIP level
            try:
                vip_level = int(search_query.split(":")[1].strip())
                cursor.execute("""
                    SELECT user_id, username, first_name, vip_level, created_at, status, total_transactions, total_amount
                    FROM users 
                    WHERE vip_level = ?
                    ORDER BY created_at DESC
                    LIMIT 20
                """, (vip_level,))
                users = cursor.fetchall()
                search_type = f"VIP{vip_level}"
            except ValueError:
                pass
        elif search_query.startswith("date:"):
            # Search by registration date
            try:
                date_str = search_query.split(":")[1].strip()
                cursor.execute("""
                    SELECT user_id, username, first_name, vip_level, created_at, status, total_transactions, total_amount
                    FROM users 
                    WHERE DATE(created_at) = ?
                    ORDER BY created_at DESC
                    LIMIT 20
                """, (date_str,))
                users = cursor.fetchall()
                search_type = f"注册日期 {date_str}"
            except:
                pass
        else:
            # Try to search by username or first_name
            cursor.execute("""
                SELECT user_id, username, first_name, vip_level, created_at, status, total_transactions, total_amount
                FROM users 
                WHERE username LIKE ? OR first_name LIKE ?
                LIMIT 20
            """, (f"%{search_query}%", f"%{search_query}%"))
            users = cursor.fetchall()
            search_type = "关键词"
        
        cursor.close()
        
        if not users:
            text = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  🔍 搜索用户\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>搜索条件：</b>{search_query}\n"
                f"<b>搜索类型：</b>{search_type}\n\n"
                f"❌ 未找到匹配的用户\n\n"
                f"💡 请尝试其他搜索条件"
            )
        else:
            text = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  🔍 搜索用户\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>搜索条件：</b>{search_query}\n"
                f"<b>搜索类型：</b>{search_type}\n"
                f"<b>找到 {len(users)} 个用户：</b>\n\n"
            )
            
            for idx, user in enumerate(users[:10], 1):
                username = user['username'] if user['username'] else '无'
                username_display = f"@{username}" if username != '无' else "无"
                first_name = user['first_name'] if user['first_name'] else ''
                vip_level = user['vip_level'] if user['vip_level'] is not None else 0
                user_id = user['user_id']
                created_at = user['created_at'][:10] if user['created_at'] else 'N/A'
                status = user['status'] if user['status'] else 'active'
                total_transactions = user['total_transactions'] if user['total_transactions'] else 0
                total_amount = float(user['total_amount'] or 0)
                
                vip_text = f"VIP{vip_level}" if vip_level > 0 else "普通"
                status_text = "✅ 活跃" if status == 'active' else "❌ 禁用"
                
                text += (
                    f"{idx}. {username_display} (ID: <code>{user_id}</code>)\n"
                    f"   姓名：{first_name or '未设置'} | {vip_text} | {status_text}\n"
                    f"   注册：{created_at} | 交易：{total_transactions}笔 | 总额：{total_amount:,.2f} CNY\n\n"
                )
            
            if len(users) > 10:
                text += f"显示前 10 个，共找到 {len(users)} 个用户...\n\n"
            
            text += "💡 使用 <code>/user_detail &lt;user_id&gt;</code> 查看用户详情"
        
        reply_markup = get_admin_submenu_keyboard("users")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
        # Log search operation
        try:
            from repositories.admin_logs_repository import AdminLogsRepository
            AdminLogsRepository.log_operation(
                admin_id=update.effective_user.id,
                operation_type="search",
                target_type="user",
                details=f"query={search_query}, results={len(users)}",
                result="success" if users else "no_results"
            )
        except:
            pass  # Don't fail if logging fails
        
    except Exception as e:
        logger.error(f"Error in handle_admin_user_search_result: {e}", exc_info=True)
        await send_group_message(update, "❌ 搜索失败，请稍后再试", parse_mode="HTML")


async def handle_admin_user_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user report (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    from datetime import datetime
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get user growth trend (last 7 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM users
            WHERE DATE(created_at) >= DATE('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        growth_data = cursor.fetchall()
        
        # Get active users (last 7 days, 30 days)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count
            FROM transactions
            WHERE DATE(created_at) >= DATE('now', '-7 days')
        """)
        active_7d = cursor.fetchone()['count'] or 0
        
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count
            FROM transactions
            WHERE DATE(created_at) >= DATE('now', '-30 days')
        """)
        active_30d = cursor.fetchone()['count'] or 0
        
        # Get VIP statistics
        cursor.execute("""
            SELECT vip_level, COUNT(*) as count
            FROM users
            WHERE vip_level > 0
            GROUP BY vip_level
            ORDER BY vip_level ASC
        """)
        vip_stats = cursor.fetchall()
        
        # Get total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Get new users today, this week, this month
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')")
        today_new = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) >= DATE('now', '-7 days')")
        week_new = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) >= DATE('now', 'start of month')")
        month_new = cursor.fetchone()[0]
        cursor.close()
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  📊 用户报表\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>👥 用户概览</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"总用户数：{total_users}\n"
            f"7日活跃：{active_7d}\n"
            f"30日活跃：{active_30d}\n\n"
            f"<b>📈 用户增长</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"今日新增：{today_new} 人\n"
            f"本周新增：{week_new} 人\n"
            f"本月新增：{month_new} 人\n\n"
        )
        
        if growth_data:
            text += f"<b>📅 最近7天增长趋势</b>\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for data in growth_data[:7]:
                date = data['date']
                count = data['count']
                text += f"{date}：{count} 人\n"
            text += "\n"
        
        if vip_stats:
            text += f"<b>👑 VIP用户分布</b>\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            total_vip = sum(stat['count'] for stat in vip_stats)
            for stat in vip_stats:
                level = stat['vip_level']
                count = stat['count']
                percentage = (count / total_vip * 100) if total_vip > 0 else 0
                text += f"VIP{level}：{count} 人 ({percentage:.1f}%)\n"
            text += f"VIP总计：{total_vip} 人\n\n"
        
        text += f"💡 报表生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Add visualization for growth trend
        if growth_data:
            try:
                from services.chart_service import ChartService
                # 修复：sqlite3.Row 不支持 .get()，使用字典式访问
                chart_data = [
                    {'label': item['date'], 'value': float(item['count'] if item['count'] is not None else 0)}
                    for item in growth_data[:7]
                ]
                chart = ChartService.generate_simple_bar(chart_data, 'value', 'label', max_bars=7)
                text += f"\n\n<b>📊 用户增长趋势（最近7天）</b>\n"
                text += f"<pre>{chart}</pre>\n"
            except Exception as e:
                logger.error(f"Error generating growth chart: {e}", exc_info=True)
        
        reply_markup = get_admin_submenu_keyboard("users")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_user_report: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_stats_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle time-based statistics (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    from datetime import datetime
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get today's statistics
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE DATE(created_at) = DATE('now') AND status = 'paid'
        """)
        today_result = cursor.fetchone()
        today_count = today_result['count'] or 0
        today_amount = float(today_result['total'] or 0)
        
        # Get yesterday's statistics
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE DATE(created_at) = DATE('now', '-1 day') AND status = 'paid'
        """)
        yesterday_result = cursor.fetchone()
        yesterday_count = yesterday_result['count'] or 0
        yesterday_amount = float(yesterday_result['total'] or 0)
        
        # Get this week's statistics
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE DATE(created_at) >= DATE('now', '-7 days') AND status = 'paid'
        """)
        week_result = cursor.fetchone()
        week_count = week_result['count'] or 0
        week_amount = float(week_result['total'] or 0)
        
        # Get this month's statistics
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE DATE(created_at) >= DATE('now', 'start of month') AND status = 'paid'
        """)
        month_result = cursor.fetchone()
        month_count = month_result['count'] or 0
        month_amount = float(month_result['total'] or 0)
        
        # Get user statistics
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')")
        today_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) >= DATE('now', '-7 days')")
        week_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) >= DATE('now', 'start of month')")
        month_users = cursor.fetchone()[0]
        
        # Calculate growth rates
        today_growth = ((today_amount - yesterday_amount) / yesterday_amount * 100) if yesterday_amount > 0 else 0
        week_growth = ((week_amount - (yesterday_amount * 7)) / (yesterday_amount * 7) * 100) if yesterday_amount > 0 else 0
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  📅 时间统计\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>💳 交易统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>今日</b>\n"
            f"交易：{today_count} 笔 / {today_amount:,.2f} CNY\n"
        )
        
        if yesterday_amount > 0:
            growth_icon = "📈" if today_growth >= 0 else "📉"
            text += f"{growth_icon} 较昨日：{abs(today_growth):.1f}%\n\n"
        else:
            text += "\n"
        
        text += (
            f"<b>昨日</b>\n"
            f"交易：{yesterday_count} 笔 / {yesterday_amount:,.2f} CNY\n\n"
            f"<b>本周</b>\n"
            f"交易：{week_count} 笔 / {week_amount:,.2f} CNY\n"
        )
        
        if yesterday_amount > 0:
            growth_icon = "📈" if week_growth >= 0 else "📉"
            text += f"{growth_icon} 较上周：{abs(week_growth):.1f}%\n\n"
        else:
            text += "\n"
        
        text += (
            f"<b>本月</b>\n"
            f"交易：{month_count} 笔 / {month_amount:,.2f} CNY\n\n"
            f"<b>👥 用户统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"今日新增：{today_users} 人\n"
            f"本周新增：{week_users} 人\n"
            f"本月新增：{month_users} 人\n\n"
            f"💡 统计时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        reply_markup = get_admin_submenu_keyboard("stats")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_stats_time: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_stats_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle detailed statistics report (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    from datetime import datetime
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get detailed transaction statistics by status
        cursor.execute("""
            SELECT status, COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            GROUP BY status
        """)
        status_stats = cursor.fetchall()
        
        # Get channel statistics
        cursor.execute("""
            SELECT payment_channel, COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE status = 'paid'
            GROUP BY payment_channel
        """)
        channel_stats = cursor.fetchall()
        
        # Get transaction type statistics
        cursor.execute("""
            SELECT transaction_type, COUNT(*) as count, COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE status = 'paid'
            GROUP BY transaction_type
        """)
        type_stats = cursor.fetchall()
        
        # Get top users by transaction amount
        cursor.execute("""
            SELECT user_id, COUNT(*) as count, COALESCE(SUM(amount), 0) as total
            FROM transactions
            WHERE status = 'paid'
            GROUP BY user_id
            ORDER BY total DESC
            LIMIT 10
        """)
        top_users = cursor.fetchall()
        cursor.close()
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  📊 详细报表\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>💳 交易状态统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        
        total_all = sum(stat['count'] for stat in status_stats)
        for stat in status_stats:
            status = stat['status']
            count = stat['count']
            amount = float(stat['total'] or 0)
            
            status_text = {
                "paid": "✅ 已支付",
                "pending": "⏳ 待支付",
                "failed": "❌ 失败",
                "cancelled": "🚫 已取消"
            }.get(status, status)
            
            percentage = (count / total_all * 100) if total_all > 0 else 0
            text += f"{status_text}：{count} 笔 ({percentage:.1f}%) / {amount:,.2f} CNY\n"
        
        text += "\n"
        
        if channel_stats:
            text += f"<b>💳 支付渠道统计</b>\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            total_paid = sum(float(stat['total'] or 0) for stat in channel_stats)
            for stat in channel_stats:
                channel = stat['payment_channel']
                count = stat['count']
                amount = float(stat['total'] or 0)
                percentage = (amount / total_paid * 100) if total_paid > 0 else 0
                
                channel_text = "💙 支付宝" if channel == "alipay" else "💚 微信支付"
                text += f"{channel_text}：{count} 笔 / {amount:,.2f} CNY ({percentage:.1f}%)\n"
            text += "\n"
        
        if type_stats:
            text += f"<b>📋 交易类型统计</b>\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for stat in type_stats:
                trans_type = stat['transaction_type']
                count = stat['count']
                amount = float(stat['total'] or 0)
                
                type_text = {"receive": "💰 收款", "pay": "💸 付款"}.get(trans_type, trans_type)
                text += f"{type_text}：{count} 笔 / {amount:,.2f} CNY\n"
            text += "\n"
        
        if top_users:
            text += f"<b>🏆 交易额TOP10用户</b>\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for idx, user in enumerate(top_users[:10], 1):
                user_id = user['user_id']
                count = user['count']
                amount = float(user['total'] or 0)
                text += f"{idx}. ID:<code>{user_id}</code> - {count}笔 / {amount:,.2f} CNY\n"
            text += "\n"
            
            # Add visualization chart
            try:
                from services.chart_service import ChartService
                chart_data = [
                    {'label': f"用户{user['user_id']}", 'value': float(user['total'] or 0)}
                    for user in top_users[:8]
                ]
                chart = ChartService.generate_simple_bar(chart_data, 'value', 'label', max_bars=8)
                text += f"<b>📊 交易额TOP8可视化</b>\n"
                text += f"<pre>{chart}</pre>\n"
            except Exception as e:
                logger.error(f"Error generating chart: {e}")
        
        text += f"💡 报表生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        reply_markup = get_admin_submenu_keyboard("stats")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_stats_detail: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_admin_word_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sensitive words export (using reply keyboard)"""
    from repositories.sensitive_words_repository import SensitiveWordsRepository
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        words = SensitiveWordsRepository.get_words()
        
        if not words:
            text = (
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  📋 导出列表\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "暂无敏感词可导出"
            )
        else:
            text = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  📋 导出列表\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>敏感词列表（共 {len(words)} 个）：</b>\n\n"
            )
            
            # Format as CSV-like text for easy copying
            action_map = {"warn": "警告", "delete": "删除", "ban": "封禁"}
            
            # Create export text
            export_text = "敏感词,动作\n"
            for word in words:
                action_text = action_map.get(word['action'], word['action'])
                # Escape commas in words
                word_text = word['word'].replace(',', '，')
                export_text += f"{word_text},{action_text}\n"
            
            text = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  📋 导出列表\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>敏感词列表（共 {len(words)} 个）：</b>\n\n"
                f"<code>{export_text[:3000]}</code>\n\n"
            )
            
            if len(export_text) > 3000:
                text += f"💡 列表较长，已截断显示。使用 <code>/export_words</code> 命令获取完整导出\n\n"
            
            text += "💡 复制上方内容可导入到Excel或其他工具\n"
            text += "💡 格式：敏感词,动作（warn/delete/ban）"
        
        reply_markup = get_admin_submenu_keyboard("words")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_word_export: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


# ========== User Detail Handler ==========

async def handle_admin_user_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Handle user detail view (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("""
            SELECT user_id, username, first_name, last_name, vip_level, 
                   status, total_transactions, total_amount, 
                   created_at, last_active_at
            FROM users 
            WHERE user_id = ?
        """, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            await send_group_message(update, f"❌ 用户 {user_id} 不存在", parse_mode="HTML")
            return
        
        # Get transaction statistics
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total
            FROM transactions
            WHERE user_id = ? AND status = 'paid'
        """, (user_id,))
        trans_stats = cursor.fetchone()
        
        # Get referral info
        cursor.execute("""
            SELECT referral_code, total_invites, successful_invites, total_rewards
            FROM referral_codes
            WHERE user_id = ?
        """, (user_id,))
        referral = cursor.fetchone()
        
        cursor.close()
        
        username = user['username'] if user['username'] else '无'
        username_display = f"@{username}" if username != '无' else "无"
        first_name = user['first_name'] if user['first_name'] else ''
        last_name = user['last_name'] if user['last_name'] else ''
        vip_level = user['vip_level'] if user['vip_level'] is not None else 0
        status = user['status'] if user['status'] else 'active'
        total_transactions = user['total_transactions'] if user['total_transactions'] else 0
        total_amount = float(user['total_amount'] or 0)
        created_at = user['created_at'] if user['created_at'] else 'N/A'
        last_active_at = user['last_active_at'] if user['last_active_at'] else 'N/A'
        
        paid_count = trans_stats['count'] if trans_stats else 0
        paid_amount = float(trans_stats['total'] or 0) if trans_stats else 0
        
        vip_text = f"VIP{vip_level}" if vip_level > 0 else "普通"
        status_text = "✅ 活跃" if status == 'active' else "❌ 禁用"
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  👤 用户详情\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>基本信息</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"用户ID：<code>{user_id}</code>\n"
            f"用户名：{username_display}\n"
            f"姓名：{first_name} {last_name}".strip() or "未设置\n"
            f"VIP等级：{vip_text}\n"
            f"账户状态：{status_text}\n\n"
            f"<b>交易统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"总交易数：{total_transactions} 笔\n"
            f"成功交易：{paid_count} 笔\n"
            f"总交易额：{total_amount:,.2f} CNY\n"
            f"成功交易额：{paid_amount:,.2f} CNY\n\n"
        )
        
        if referral:
            text += (
                f"<b>推荐信息</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"推荐码：<code>{referral['referral_code']}</code>\n"
                f"总邀请：{referral['total_invites']} 人\n"
                f"成功邀请：{referral['successful_invites']} 人\n"
                f"累计奖励：{float(referral['total_rewards'] or 0):,.2f} USDT\n\n"
            )
        
        text += (
            f"<b>时间信息</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"注册时间：{created_at[:19] if len(created_at) > 19 else created_at}\n"
            f"最后活跃：{last_active_at[:19] if len(last_active_at) > 19 else last_active_at}\n\n"
            f"💡 使用命令操作：\n"
            f"• <code>/set_vip {user_id} &lt;level&gt;</code> - 修改VIP等级\n"
            f"• <code>/disable_user {user_id}</code> - 禁用用户\n"
            f"• <code>/enable_user {user_id}</code> - 启用用户"
        )
        
        reply_markup = get_admin_submenu_keyboard("users")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_user_detail: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


# ========== Verification Detail and History Handlers ==========

async def handle_verification_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle verification detail view (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get pending members with verification records
        cursor.execute("""
            SELECT gm.*, g.group_title, vr.*
            FROM group_members gm
            JOIN groups g ON gm.group_id = g.group_id
            LEFT JOIN verification_records vr ON gm.group_id = vr.group_id AND gm.user_id = vr.user_id
            WHERE gm.status = 'pending'
            ORDER BY gm.joined_at ASC
            LIMIT 5
        """)
        
        pending = cursor.fetchall()
        cursor.close()
        
        if not pending:
            text = (
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  👤 审核详情\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "暂无待审核成员"
            )
        else:
            text = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  👤 审核详情\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>待审核成员详情（前5名）：</b>\n\n"
            )
            
            for idx, member in enumerate(pending[:5], 1):
                user_id = member['user_id']
                group_title = member['group_title'] if member['group_title'] else f"群组 {member['group_id']}"
                joined_at = member['joined_at'][:16] if member['joined_at'] else 'N/A'
                verification_type = member.get('verification_type', '未知')
                attempt_count = member.get('attempt_count', 0)
                user_answer = member.get('user_answer', '未回答')
                
                text += (
                    f"{idx}. 用户ID：<code>{user_id}</code>\n"
                    f"   群组：{group_title}\n"
                    f"   加入时间：{joined_at}\n"
                    f"   验证类型：{verification_type}\n"
                    f"   尝试次数：{attempt_count}\n"
                    f"   用户答案：{user_answer[:50] if len(user_answer) > 50 else user_answer}\n\n"
                )
            
            if len(pending) > 5:
                text += f"还有 {len(pending) - 5} 个待审核成员...\n\n"
            
            text += "💡 使用命令审核：\n"
            text += "• <code>/pass_user &lt;user_id&gt; &lt;group_id&gt;</code> - 通过审核\n"
            text += "• <code>/reject_user &lt;user_id&gt; &lt;group_id&gt;</code> - 拒绝审核"
        
        reply_markup = get_admin_submenu_keyboard("verify")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_verification_detail: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def handle_verification_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle verification history (using reply keyboard)"""
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get verification statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN result = 'passed' THEN 1 ELSE 0 END) as passed,
                SUM(CASE WHEN result = 'rejected' THEN 1 ELSE 0 END) as rejected,
                SUM(CASE WHEN result = 'pending' THEN 1 ELSE 0 END) as pending
            FROM verification_records
            WHERE created_at >= DATE('now', '-7 days')
        """)
        stats = cursor.fetchone()
        
        # Get recent verification records
        cursor.execute("""
            SELECT vr.*, g.group_title
            FROM verification_records vr
            JOIN groups g ON vr.group_id = g.group_id
            WHERE vr.result != 'pending'
            ORDER BY vr.completed_at DESC
            LIMIT 10
        """)
        records = cursor.fetchall()
        cursor.close()
        
        total = stats['total'] if stats else 0
        passed = stats['passed'] if stats else 0
        rejected = stats['rejected'] if stats else 0
        pending = stats['pending'] if stats else 0
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  📋 审核历史\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>最近7天统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"总审核：{total} 人\n"
            f"通过：{passed} 人 ({pass_rate:.1f}%)\n"
            f"拒绝：{rejected} 人\n"
            f"待审核：{pending} 人\n\n"
            f"<b>最近审核记录（前10条）</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        
        if not records:
            text += "暂无审核记录"
        else:
            for idx, record in enumerate(records[:10], 1):
                user_id = record['user_id']
                group_title = record['group_title'] if record['group_title'] else f"群组 {record['group_id']}"
                result = record['result']
                completed_at = record['completed_at'][:16] if record['completed_at'] else 'N/A'
                
                result_text = {"passed": "✅ 通过", "rejected": "❌ 拒绝"}.get(result, result)
                
                text += (
                    f"{idx}. 用户ID：<code>{user_id}</code>\n"
                    f"   群组：{group_title}\n"
                    f"   结果：{result_text} | 时间：{completed_at}\n\n"
                )
        
        reply_markup = get_admin_submenu_keyboard("verify")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_verification_history: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


# ========== Group Detail Handler ==========

async def handle_admin_group_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int):
    """Handle group detail view (using reply keyboard)"""
    from repositories.group_repository import GroupRepository
    from repositories.verification_repository import VerificationRepository
    from repositories.sensitive_words_repository import SensitiveWordsRepository
    from database import db
    from keyboards.admin_keyboard import get_admin_submenu_keyboard
    
    try:
        # Get group info
        group = GroupRepository.get_group(group_id)
        if not group:
            await send_group_message(update, f"❌ 群组 {group_id} 不存在", parse_mode="HTML")
            return
        
        conn = db.connect()
        cursor = conn.cursor()
        
        # Get member statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'verified' THEN 1 ELSE 0 END) as verified,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM group_members
            WHERE group_id = ?
        """, (group_id,))
        member_stats = cursor.fetchone()
        
        # Get verification config
        config = VerificationRepository.get_verification_config(group_id)
        
        # Get sensitive words count
        sensitive_words = SensitiveWordsRepository.get_words(group_id)
        
        # Get verification statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN result = 'passed' THEN 1 ELSE 0 END) as passed,
                SUM(CASE WHEN result = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM verification_records
            WHERE group_id = ?
        """, (group_id,))
        verify_stats = cursor.fetchone()
        cursor.close()
        
        group_title = group['group_title'] if group['group_title'] else f"群组 {group_id}"
        verification_enabled = group['verification_enabled'] if group['verification_enabled'] else 0
        verification_type = group['verification_type'] if group['verification_type'] else 'none'
        
        total_members = member_stats['total'] if member_stats else 0
        verified_members = member_stats['verified'] if member_stats else 0
        pending_members = member_stats['pending'] if member_stats else 0
        rejected_members = member_stats['rejected'] if member_stats else 0
        
        total_verifications = verify_stats['total'] if verify_stats else 0
        passed_verifications = verify_stats['passed'] if verify_stats else 0
        rejected_verifications = verify_stats['rejected'] if verify_stats else 0
        
        verification_mode = config['verification_mode'] if config else 'question'
        mode_text = "问题验证" if verification_mode == 'question' else "手动验证"
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  ⚙️ 群组详情\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>基本信息</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"群组ID：<code>{group_id}</code>\n"
            f"群组名称：{group_title}\n"
            f"验证状态：{'✅ 已开启' if verification_enabled else '❌ 已关闭'}\n"
            f"验证模式：{mode_text}\n\n"
            f"<b>成员统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"总成员：{total_members} 人\n"
            f"已审核：{verified_members} 人\n"
            f"待审核：{pending_members} 人\n"
            f"已拒绝：{rejected_members} 人\n\n"
            f"<b>验证统计</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"总验证：{total_verifications} 次\n"
            f"通过：{passed_verifications} 次\n"
            f"拒绝：{rejected_verifications} 次\n\n"
            f"<b>敏感词</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"群组敏感词：{len(sensitive_words)} 个\n"
            f"全局敏感词：{len(SensitiveWordsRepository.get_words(None))} 个\n\n"
        )
        
        if config:
            welcome_message = config.get('welcome_message', '')
            if welcome_message:
                text += f"<b>欢迎消息</b>\n"
                text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                text += f"{welcome_message[:100]}{'...' if len(welcome_message) > 100 else ''}\n\n"
        
        text += (
            f"💡 使用命令配置：\n"
            f"• <code>/group_verify {group_id} enable/disable</code> - 启用/禁用验证\n"
            f"• <code>/group_mode {group_id} question/manual</code> - 设置验证模式\n"
            f"• <code>/delgroup {group_id}</code> - 删除群组"
        )
        
        reply_markup = get_admin_submenu_keyboard("group")
        await send_group_message(update, text, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_admin_group_detail: {e}", exc_info=True)
        await send_group_message(update, "❌ 系统错误，请稍后再试", parse_mode="HTML")


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads for QR code"""
    try:
        from handlers.address_handlers import (
            handle_address_photo, 
            handle_address_qr_photo
        )
        
        # Check if editing QR code
        if 'editing_address_qr' in context.user_data:
            await handle_address_qr_photo(update, context)
        else:
            # Adding new address
            await handle_address_photo(update, context)
    except Exception as e:
        logger.error(f"Error in photo_handler: {e}", exc_info=True)


def get_message_handler():
    """Get message handler instance"""
    return MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)


def get_photo_handler():
    """Get photo handler instance for QR code uploads"""
    return MessageHandler(filters.PHOTO, photo_handler)
