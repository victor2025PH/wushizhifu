"""
Chart handlers for Bot B
Handles chart generation and display requests
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.chart_service import (
    generate_transaction_trend_chart,
    generate_transaction_volume_chart,
    generate_user_distribution_chart,
    generate_price_trend_chart
)
from admin_checker import is_admin

logger = logging.getLogger(__name__)


async def handle_chart_trend(update: Update, context: ContextTypes.DEFAULT_TYPE, days: int = 7):
    """
    Handle transaction trend chart request.
    
    Args:
        update: Telegram update object
        context: Context object
        days: Number of days to show (7 or 30)
    """
    try:
        chat = update.effective_chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        
        # Check if admin (for global charts)
        if not group_id and not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        # Generate chart
        chart_bytes = generate_transaction_trend_chart(group_id=group_id, days=days)
        
        if chart_bytes is None:
            await update.message.reply_text("❌ 无法生成图表：没有足够的数据")
            return
        
        # Send chart as photo
        await update.message.reply_photo(
            photo=chart_bytes,
            caption=f"📈 交易趋势图 - 最近 {days} 天"
        )
        
        logger.info(f"Sent transaction trend chart ({days} days) to {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_chart_trend: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 生成图表时出错: {str(e)}")


async def handle_chart_volume(update: Update, context: ContextTypes.DEFAULT_TYPE, days: int = 7):
    """
    Handle transaction volume chart request.
    
    Args:
        update: Telegram update object
        context: Context object
        days: Number of days to show
    """
    try:
        chat = update.effective_chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        
        # Check if admin (for global charts)
        if not group_id and not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        # Generate chart
        chart_bytes = generate_transaction_volume_chart(group_id=group_id, days=days)
        
        if chart_bytes is None:
            await update.message.reply_text("❌ 无法生成图表：没有足够的数据")
            return
        
        # Send chart as photo
        await update.message.reply_photo(
            photo=chart_bytes,
            caption=f"📊 交易量统计 - 最近 {days} 天"
        )
        
        logger.info(f"Sent transaction volume chart ({days} days) to {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_chart_volume: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 生成图表时出错: {str(e)}")


async def handle_chart_users(update: Update, context: ContextTypes.DEFAULT_TYPE, top_n: int = 10):
    """
    Handle user distribution chart request.
    
    Args:
        update: Telegram update object
        context: Context object
        top_n: Number of top users to show
    """
    try:
        chat = update.effective_chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        
        # Check if admin (for global charts)
        if not group_id and not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        # Generate chart
        chart_bytes = generate_user_distribution_chart(group_id=group_id, top_n=top_n)
        
        if chart_bytes is None:
            await update.message.reply_text("❌ 无法生成图表：没有足够的数据")
            return
        
        # Send chart as photo
        await update.message.reply_photo(
            photo=chart_bytes,
            caption=f"👥 用户分布图 - Top {top_n} 用户"
        )
        
        logger.info(f"Sent user distribution chart (top {top_n}) to {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_chart_users: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 生成图表时出错: {str(e)}")


async def handle_chart_price(update: Update, context: ContextTypes.DEFAULT_TYPE, days: int = 7):
    """
    Handle price trend chart request.
    
    Args:
        update: Telegram update object
        context: Context object
        days: Number of days to show
    """
    try:
        # Generate chart
        chart_bytes = generate_price_trend_chart(days=days)
        
        if chart_bytes is None:
            await update.message.reply_text("❌ 无法生成图表：没有价格历史数据")
            return
        
        # Send chart as photo
        await update.message.reply_photo(
            photo=chart_bytes,
            caption=f"💱 价格趋势图 - 最近 {days} 天"
        )
        
        logger.info(f"Sent price trend chart ({days} days) to {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in handle_chart_price: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 生成图表时出错: {str(e)}")

