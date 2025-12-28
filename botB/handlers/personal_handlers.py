"""
Personal handlers for Bot B
Handles personal bills and statistics for individual users
"""
import logging
import datetime
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from database import db
from keyboards.inline_keyboard import get_bills_history_keyboard

logger = logging.getLogger(__name__)


async def handle_personal_bills(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1):
    """
    Handle personal bills query (user's own transactions).
    
    Args:
        update: Telegram update object
        context: Context object
        page: Page number (1-based)
    """
    try:
        user_id = update.effective_user.id
        limit = 10  # 10 transactions per page
        offset = (page - 1) * limit
        
        # Get user's transactions
        transactions = db.get_transactions_by_user(user_id, limit=limit, offset=offset)
        total_count = db.count_transactions_by_user(user_id)
        
        if not transactions:
            await update.message.reply_text("📭 您暂无交易记录\n\n开始使用结算功能后，您的交易记录将显示在这里")
            return
        
        total_pages = (total_count + limit - 1) // limit
        
        # Build message
        message = f"📜 <b>我的账单</b>\n\n"
        message += "────────────────────────\n"
        message += f"用户: {update.effective_user.first_name or '未知'}\n"
        message += f"总计: {total_count} 笔交易\n"
        message += f"\n📋 账单列表（第 {page} 页，共 {total_pages} 页）:\n\n"
        
        for idx, tx in enumerate(transactions, 1):
            date_str = tx['created_at'][:16] if len(tx['created_at']) > 16 else tx['created_at']
            group_info = ""
            if tx['group_id']:
                # Could fetch group title, but for now just show it's from a group
                group_info = " [群组]"
            
            message += f"{idx}. {date_str}{group_info}\n"
            message += f"   {tx['cny_amount']:,.2f} CNY → {tx['usdt_amount']:,.2f} USDT"
            if tx['status'] != 'pending':
                status_emoji = "✅" if tx['status'] == 'confirmed' else "⏳"
                message += f" {status_emoji}"
            message += "\n\n"
        
        # For personal bills, we can reuse the bills keyboard but adapt it
        # Since there's no group_id for personal bills, we'll use user_id instead
        # Note: This is a workaround, ideally we should have a separate keyboard
        reply_markup = None  # Can be added later if needed
        
        await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_personal_bills: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_personal_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle personal statistics display.
    
    Shows user's own transaction statistics (today, this month, all time).
    """
    try:
        user_id = update.effective_user.id
        today = datetime.date.today()
        
        # Today stats
        today_str = today.strftime('%Y-%m-%d')
        today_stats = db.get_user_stats(user_id, date=today_str)
        
        # This month stats
        month_start = today.replace(day=1)
        month_start_str = month_start.strftime('%Y-%m-%d')
        month_end_str = today.strftime('%Y-%m-%d')
        month_stats = db.get_user_stats(user_id, start_date=month_start_str, end_date=month_end_str)
        
        # All time stats
        all_time_stats = db.get_user_stats(user_id)
        
        message = f"📊 <b>我的交易统计</b>\n\n"
        message += "────────────────────────\n"
        message += f"用户: {update.effective_user.first_name or '未知'}\n"
        message += f"统计时间: {today.strftime('%Y-%m-%d')}\n\n"
        
        # Today stats
        message += "<b>📈 今日统计:</b>\n"
        message += f"• 交易次数: {today_stats['count']} 笔\n"
        message += f"• 总金额: {today_stats['total_cny']:,.2f} CNY\n"
        message += f"• 应结算: {today_stats['total_usdt']:,.2f} USDT\n\n"
        
        # Month stats
        message += "<b>📈 本月统计:</b>\n"
        message += f"• 交易次数: {month_stats['count']} 笔\n"
        message += f"• 总金额: {month_stats['total_cny']:,.2f} CNY\n"
        message += f"• 应结算: {month_stats['total_usdt']:,.2f} USDT\n\n"
        
        # All time stats
        message += "<b>📈 累计统计:</b>\n"
        message += f"• 总交易次数: {all_time_stats['count']} 笔\n"
        message += f"• 总金额: {all_time_stats['total_cny']:,.2f} CNY\n"
        if all_time_stats['count'] > 0:
            message += f"• 平均每笔: {all_time_stats['avg_cny']:,.2f} CNY\n"
        message += f"• 应结算: {all_time_stats['total_usdt']:,.2f} USDT\n"
        
        if all_time_stats.get('last_active'):
            last_active = all_time_stats['last_active'][:16] if len(all_time_stats['last_active']) > 16 else all_time_stats['last_active']
            message += f"\n📅 最近交易: {last_active}"
        
        await update.message.reply_text(message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in handle_personal_stats: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")

