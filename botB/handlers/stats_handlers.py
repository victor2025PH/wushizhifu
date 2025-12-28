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

