"""
Statistics handlers for Bot B
Handles group and global statistics
"""
import logging
import datetime
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from database import db
from admin_checker import is_admin
from services.export_service import export_stats_to_excel, generate_export_filename

logger = logging.getLogger(__name__)


async def handle_group_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle group statistics display.
    
    Shows today, this week, and this month statistics.
    """
    try:
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("❌ 此功能仅在群组中可用")
            return
        
        group_id = chat.id
        today = datetime.date.today()
        
        # Today stats
        today_str = today.strftime('%Y-%m-%d')
        today_stats = db.get_transaction_stats_by_group(group_id, date=today_str)
        
        # This week stats
        week_start = today - datetime.timedelta(days=today.weekday())
        week_start_str = week_start.strftime('%Y-%m-%d')
        week_end_str = today.strftime('%Y-%m-%d')
        week_stats = db.get_transaction_stats_by_group(group_id, start_date=week_start_str, end_date=week_end_str)
        
        # This month stats
        month_start = today.replace(day=1)
        month_start_str = month_start.strftime('%Y-%m-%d')
        month_end_str = today.strftime('%Y-%m-%d')
        month_stats = db.get_transaction_stats_by_group(group_id, start_date=month_start_str, end_date=month_end_str)
        
        message = f"📈 <b>群组统计信息</b>\n\n"
        message += "────────────────────────\n"
        message += f"群组: {chat.title or '未知群组'}\n"
        message += f"统计时间: {today.strftime('%Y-%m-%d')}\n\n"
        
        # Today stats
        message += "<b>📊 今日统计:</b>\n"
        message += f"• 交易次数: {today_stats['count']} 笔\n"
        message += f"• 总金额: {today_stats['total_cny']:,.2f} CNY\n"
        message += f"• 平均金额: {today_stats['avg_cny']:,.2f} CNY\n"
        message += f"• 应结算: {today_stats['total_usdt']:,.2f} USDT\n\n"
        
        # Week stats
        message += "<b>📊 本周统计:</b>\n"
        message += f"• 交易次数: {week_stats['count']} 笔\n"
        message += f"• 总金额: {week_stats['total_cny']:,.2f} CNY\n"
        if week_stats['count'] > 0:
            message += f"• 日均交易: {week_stats['count'] / (today.weekday() + 1):.1f} 笔\n"
        message += f"• 应结算: {week_stats['total_usdt']:,.2f} USDT\n\n"
        
        # Month stats
        message += "<b>📊 本月统计:</b>\n"
        message += f"• 交易次数: {month_stats['count']} 笔\n"
        message += f"• 总金额: {month_stats['total_cny']:,.2f} CNY\n"
        message += f"• 应结算: {month_stats['total_usdt']:,.2f} USDT\n"
        message += f"• 活跃用户: {month_stats['unique_users']} 人\n\n"
        
        if month_stats.get('last_active'):
            last_active = month_stats['last_active'][:16] if len(month_stats['last_active']) > 16 else month_stats['last_active']
            message += f"📅 最近活跃: {last_active}"
        
        await update.message.reply_text(message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in handle_group_stats: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_global_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle global statistics display.
    
    Shows today and this month statistics across all groups.
    """
    try:
        today = datetime.date.today()
        
        # Today stats
        today_str = today.strftime('%Y-%m-%d')
        today_stats = db.get_global_stats(start_date=today_str, end_date=today_str)
        
        # This month stats
        month_start = today.replace(day=1)
        month_start_str = month_start.strftime('%Y-%m-%d')
        month_end_str = today.strftime('%Y-%m-%d')
        month_stats = db.get_global_stats(start_date=month_start_str, end_date=month_end_str)
        
        # Get group distribution
        all_groups = db.get_all_groups()
        groups_with_custom_settings = len([g for g in all_groups if g.get('markup', 0) != 0 or g.get('usdt_address')])
        
        message = f"📈 <b>全局统计数据</b>\n\n"
        message += "────────────────────────\n"
        message += f"统计时间: {today.strftime('%Y-%m-%d')}\n\n"
        
        # Today stats
        message += "<b>📊 今日汇总:</b>\n"
        message += f"• 总交易次数: {today_stats['count']} 笔\n"
        message += f"• 总金额: {today_stats['total_cny']:,.2f} CNY\n"
        message += f"• 应结算: {today_stats['total_usdt']:,.2f} USDT\n"
        message += f"• 活跃群组: {today_stats['active_groups']} 个\n\n"
        
        # Month stats
        message += "<b>📊 本月汇总:</b>\n"
        message += f"• 总交易次数: {month_stats['count']} 笔\n"
        message += f"• 总金额: {month_stats['total_cny']:,.2f} CNY\n"
        message += f"• 应结算: {month_stats['total_usdt']:,.2f} USDT\n\n"
        
        # Group distribution
        message += "<b>📊 群组分布:</b>\n"
        message += f"• 已配置群组: {len(all_groups)} 个\n"
        message += f"• 使用全局设置: {len(all_groups) - groups_with_custom_settings} 个\n"
        message += f"• 使用独立设置: {groups_with_custom_settings} 个"
        
        await update.message.reply_text(message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in handle_global_stats: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_pending_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: Optional[int] = None):
    """
    Handle display of pending transactions (waiting for payment).
    
    Admin can view all pending transactions in a group or globally.
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await (update.callback_query or update.message).reply_text("❌ 此功能仅限管理员使用")
            return
        
        # Get pending transactions
        pending_txs = db.get_pending_transactions(group_id=group_id, limit=20)
        
        if not pending_txs:
            message = "✅ <b>无待支付交易</b>\n\n当前没有待支付的交易记录。"
            if update.callback_query:
                await update.callback_query.answer(message, show_alert=True)
                await update.callback_query.edit_message_text(message, parse_mode="HTML")
            else:
                await update.message.reply_text(message, parse_mode="HTML")
            return
        
        message = f"⏳ <b>待支付交易列表</b>\n\n"
        if group_id:
            chat = update.effective_chat
            message += f"群组: {chat.title or '未知群组'}\n"
        else:
            message += "范围: 全部群组\n"
        message += f"共 {len(pending_txs)} 笔待支付交易\n"
        message += "────────────────────────\n\n"
        
        for idx, tx in enumerate(pending_txs, 1):
            time_str = tx['created_at'][:16] if len(tx['created_at']) > 16 else tx['created_at']
            user_name = tx['first_name'] or tx['username'] or f"用户{tx['user_id']}"
            message += (
                f"{idx}. <code>{tx['transaction_id']}</code>\n"
                f"   {tx['cny_amount']:,.2f} CNY → {tx['usdt_amount']:,.2f} USDT\n"
                f"   用户: {user_name} | {time_str}\n\n"
            )
        
        message += "<i>提示: 用户标记已支付后，交易将出现在"待确认"列表中。</i>"
        
        from keyboards.inline_keyboard import get_pending_transactions_keyboard
        reply_markup = get_pending_transactions_keyboard(group_id)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await update.callback_query.answer()
        else:
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
        logger.info(f"Admin {user_id} viewed pending transactions (group_id: {group_id})")
        
    except Exception as e:
        logger.error(f"Error in handle_pending_transactions: {e}", exc_info=True)
        await (update.callback_query or update.message).reply_text(f"❌ 错误: {str(e)}")


async def handle_paid_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: Optional[int] = None):
    """
    Handle display of paid transactions waiting for confirmation.
    
    Admin can view and confirm paid transactions.
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await (update.callback_query or update.message).reply_text("❌ 此功能仅限管理员使用")
            return
        
        # Get paid transactions
        paid_txs = db.get_paid_transactions(group_id=group_id, limit=20)
        
        if not paid_txs:
            message = "✅ <b>无待确认交易</b>\n\n当前没有待确认的交易记录。"
            if update.callback_query:
                await update.callback_query.answer(message, show_alert=True)
                await update.callback_query.edit_message_text(message, parse_mode="HTML")
            else:
                await update.message.reply_text(message, parse_mode="HTML")
            return
        
        message = f"✅ <b>待确认交易列表</b>\n\n"
        if group_id:
            chat = update.effective_chat
            message += f"群组: {chat.title or '未知群组'}\n"
        else:
            message += "范围: 全部群组\n"
        message += f"共 {len(paid_txs)} 笔待确认交易\n"
        message += "────────────────────────\n\n"
        
        for idx, tx in enumerate(paid_txs, 1):
            time_str = tx['created_at'][:16] if len(tx['created_at']) > 16 else tx['created_at']
            paid_time = tx['paid_at'][:16] if tx.get('paid_at') and len(tx['paid_at']) > 16 else (tx.get('paid_at') or '未知')
            user_name = tx['first_name'] or tx['username'] or f"用户{tx['user_id']}"
            payment_hash_display = ""
            if tx.get('payment_hash'):
                ph = tx['payment_hash']
                payment_hash_display = f"\n   哈希: <code>{ph[:15]}...</code>"
            
            message += (
                f"{idx}. <code>{tx['transaction_id']}</code>\n"
                f"   {tx['cny_amount']:,.2f} CNY → {tx['usdt_amount']:,.2f} USDT\n"
                f"   用户: {user_name}\n"
                f"   创建: {time_str} | 支付: {paid_time}{payment_hash_display}\n\n"
            )
        
        message += "<i>提示: 点击交易编号可查看详情并确认。</i>"
        
        from keyboards.inline_keyboard import get_paid_transactions_keyboard
        reply_markup = get_paid_transactions_keyboard(group_id)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await update.callback_query.answer()
        else:
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
        logger.info(f"Admin {user_id} viewed paid transactions (group_id: {group_id})")
        
    except Exception as e:
        logger.error(f"Error in handle_paid_transactions: {e}", exc_info=True)
        await (update.callback_query or update.message).reply_text(f"❌ 错误: {str(e)}")


async def handle_export_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: Optional[int] = None):
    """
    Handle export statistics to Excel.
    
    Args:
        update: Telegram update object
        context: Context object
        group_id: Optional group ID (None for global stats)
    """
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await (update.callback_query or update.message).reply_text("❌ 此功能仅限管理员使用")
            return
        
        # Show processing message
        if update.callback_query:
            await update.callback_query.answer("📥 正在生成统计报表...", show_alert=False)
            await update.callback_query.message.reply_text("⏳ 正在准备统计报表，请稍候...")
        else:
            processing_msg = await update.message.reply_text("⏳ 正在准备统计报表，请稍候...")
        
        today = datetime.date.today()
        
        # Collect statistics
        stats_data = {}
        
        if group_id:
            # Group statistics
            today_str = today.strftime('%Y-%m-%d')
            week_start = today - datetime.timedelta(days=today.weekday())
            week_start_str = week_start.strftime('%Y-%m-%d')
            week_end_str = today.strftime('%Y-%m-%d')
            month_start = today.replace(day=1)
            month_start_str = month_start.strftime('%Y-%m-%d')
            month_end_str = today.strftime('%Y-%m-%d')
            
            stats_data['today'] = db.get_transaction_stats_by_group(group_id, date=today_str)
            stats_data['week'] = db.get_transaction_stats_by_group(group_id, start_date=week_start_str, end_date=week_end_str)
            stats_data['month'] = db.get_transaction_stats_by_group(group_id, start_date=month_start_str, end_date=month_end_str)
            
            chat = update.effective_chat if hasattr(update, 'effective_chat') else None
            group_name = chat.title if chat else f"群组{group_id}"
        else:
            # Global statistics
            today_str = today.strftime('%Y-%m-%d')
            month_start = today.replace(day=1)
            month_start_str = month_start.strftime('%Y-%m-%d')
            month_end_str = today.strftime('%Y-%m-%d')
            
            stats_data['today'] = db.get_global_stats(start_date=today_str, end_date=today_str)
            stats_data['month'] = db.get_global_stats(start_date=month_start_str, end_date=month_end_str)
            group_name = "全局统计"
        
        # Export to Excel
        try:
            file_data = export_stats_to_excel(stats_data, group_name)
            filename = generate_export_filename('stats', 'excel')
            
            # Send file
            file_data.seek(0)
            if update.callback_query:
                await update.callback_query.message.reply_document(
                    document=file_data,
                    filename=filename,
                    caption=(
                        f"📥 <b>统计报表导出完成</b>\n\n"
                        f"统计范围: {group_name}\n"
                        f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ),
                    parse_mode="HTML"
                )
            else:
                if 'processing_msg' in locals():
                    await processing_msg.delete()
                await update.message.reply_document(
                    document=file_data,
                    filename=filename,
                    caption=(
                        f"📥 <b>统计报表导出完成</b>\n\n"
                        f"统计范围: {group_name}\n"
                        f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ),
                    parse_mode="HTML"
                )
            
            logger.info(f"Admin {user_id} exported statistics (group_id: {group_id})")
            
            # Log export operation
            from services.audit_service import log_admin_operation, OperationType
            log_admin_operation(
                OperationType.EXPORT_STATS,
                update,
                target_type='group' if group_id else 'global',
                target_id=str(group_id) if group_id else None,
                description=f"导出统计报表: {group_name}"
            )
            
        except Exception as e:
            logger.error(f"Error during stats export: {e}", exc_info=True)
            error_msg = f"❌ 导出失败: {str(e)}"
            if update.callback_query:
                await update.callback_query.message.reply_text(error_msg)
            else:
                if 'processing_msg' in locals():
                    await processing_msg.edit_text(error_msg)
                else:
                    await update.message.reply_text(error_msg)
        
    except Exception as e:
        logger.error(f"Error in handle_export_stats: {e}", exc_info=True)
        await (update.callback_query or update.message).reply_text(f"❌ 错误: {str(e)}")

