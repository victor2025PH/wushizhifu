"""
OTC Group Management Bot (Bot B)
Main entry point using python-telegram-bot (version 20+ async)
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import Config
from database import db
from handlers.message_handlers import get_message_handler
from handlers.callback_handlers import get_callback_handler
from admin_checker import is_admin as check_admin

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show welcome message with reply keyboard"""
    from keyboards.reply_keyboard import get_main_reply_keyboard
    from config import Config
    from services.onboarding_service import handle_new_user_onboarding
    from database import db
    
    user = update.effective_user
    is_admin_user = check_admin(user.id)
    
    # Check if new user and show onboarding
    if not db.is_onboarding_completed(user.id):
        onboarding_shown = await handle_new_user_onboarding(update, context)
        if onboarding_shown:
            # Update last active
            db.update_user_last_active(user.id)
            return  # Onboarding flow started
    
    # Update last active timestamp
    db.update_user_last_active(user.id)
    
    # 构建欢迎消息
    welcome_message = (
        f"👋 <b>欢迎使用 OTC 群组管理 Bot</b>\n\n"
        f"你好，{user.first_name}！\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📖 <b>机器人介绍</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"这是一个专业的 OTC（场外交易）群组管理机器人，提供：\n"
        f"• 💱 实时汇率查询（Binance P2P 数据源）\n"
        f"• 🧮 自动结算账单计算\n"
        f"• 📊 快速价格查询\n"
        f"• 🔗 USDT 收款地址管理\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 <b>使用方法</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>方式一：快捷按钮</b>\n"
        f"使用下方快捷按钮快速操作\n\n"
        f"<b>方式二：直接输入</b>\n"
        f"• 发送人民币金额（如：<code>20000</code>）自动计算应结算的 USDT\n"
        f"• 发送算式（如：<code>20000-200</code>）先计算人民币，再换算为 USDT\n\n"
        f"💡 <i>示例：输入 <code>20000-200</code> 表示应收 19800 元人民币，系统会按当前汇率计算应结算的 USDT 数量</i>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>快捷指令</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    # 添加管理员专用指令说明
    if is_admin_user:
        welcome_message += (
            f"<b>管理员专用：</b>\n"
            f"• <code>w01</code> - 查看价格详情\n"
            f"• <code>w02 [数字]</code> - 设置加价（如：w02 0.5）\n"
            f"• <code>w03 [数字]</code> - 设置降价（如：w03 0.3）\n"
            f"• <code>w04</code> - 查看 USDT 地址\n"
            f"• <code>w08</code> - 重置加价为 0\n\n"
        )
    
    welcome_message += (
        f"<b>所有用户：</b>\n"
        f"• <code>/start</code> - 显示此帮助信息\n"
        f"• <code>/help</code> - 查看详细帮助\n"
        f"• <code>/price</code> - 查询当前汇率\n"
        f"• <code>/settings</code> - 查看设置\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📞 <b>需要帮助？</b>\n"
        f"点击下方「📞 联系人工」按钮或发送 /help\n\n"
        f"祝您使用愉快！✨"
    )
    
    is_group = update.effective_chat.type in ['group', 'supergroup']
    reply_markup = get_main_reply_keyboard(user.id, is_group)
    await update.message.reply_text(
        welcome_message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show detailed help"""
    from config import Config
    from keyboards.reply_keyboard import get_main_reply_keyboard
    
    user = update.effective_user
    is_admin_user = check_admin(user.id)
    
    help_text = (
        "📚 <b>Bot B 完整帮助指南</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 <b>标准命令</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<code>/start</code> - 启动 Bot，显示欢迎信息和菜单\n"
        "<code>/help</code> - 显示此帮助信息\n"
        "<code>/price</code> - 获取当前 USDT/CNY 汇率\n"
        "<code>/settings</code> - 查看当前系统设置\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 <b>快捷按钮</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "使用聊天框底部的快捷按钮：\n"
        "• 📊 查看汇率 - 快速查询当前汇率\n"
        "• 🔗 收款地址 - 查看 USDT 收款地址\n"
        "• 📞 联系人工 - 联系客服支持\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 <b>自动结算计算</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "直接发送人民币金额或算式，自动计算应结算的 USDT 数量：\n"
        "• 纯数字（人民币）：<code>20000</code>\n"
        "• 加法：<code>10000+5000</code> = 15000 元\n"
        "• 减法：<code>20000-200</code> = 19800 元\n"
        "• 乘法：<code>2000*10</code> = 20000 元\n"
        "• 除法：<code>20000/2</code> = 10000 元\n\n"
        "💡 系统会自动将计算后的人民币金额，按当前汇率换算为应结算的 USDT 数量\n\n"
    )
    
    if is_admin_user:
        help_text += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 <b>管理员快捷命令</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "<code>w01</code> - 查看价格详情（Binance P2P + 加价）\n"
            "<code>w02 [数字]</code> - 设置管理员加价\n"
            "  示例：<code>w02 0.5</code> 或 <code>w02 -0.2</code>\n\n"
            "<code>w03 [数字]</code> - 设置降价\n"
            "  示例：<code>w03 0.3</code>\n\n"
            "<code>w04</code> - 查看 USDT 收款地址\n"
            "<code>w08</code> - 重置管理员加价为 0\n\n"
        )
    
    help_text += (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <b>使用技巧</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "• 结算账单会自动包含 USDT 收款地址\n"
        "• 点击账单下方的「✅ 已核对」按钮可确认\n"
        "• 所有价格均来自 Binance P2P 实时数据（CoinGecko 作为备用）\n"
        "• 支持小数计算（如：<code>100.5+50.25</code>）\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📞 <b>技术支持</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "如遇问题，请联系：\n"
        "• 客服：@wushizhifu_jianglai\n"
        "• 工作时间：7×24小时"
    )
    
    is_group = update.effective_chat.type in ['group', 'supergroup']
    reply_markup = get_main_reply_keyboard(user.id, is_group)
    await update.message.reply_text(
        help_text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command - fetch and display P2P leaderboard"""
    from handlers.p2p_handlers import handle_p2p_price_command
    
    # Use new P2P leaderboard feature
    await handle_p2p_price_command(update, context, payment_method="alipay")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command - display current settings"""
    admin_markup = db.get_admin_markup()
    usdt_address = db.get_usdt_address()
    
    address_display = usdt_address if usdt_address else "未设置"
    if usdt_address and len(usdt_address) > 20:
        address_display = f"{usdt_address[:10]}...{usdt_address[-10:]}"
    
    message = (
        f"⚙️ 当前设置\n\n"
        f"📈 管理员加价：{admin_markup:.4f} CNY\n"
        f"💼 USDT 收款地址：{address_display}\n"
    )
    
    await update.message.reply_text(message)


def main():
    """Main function to start the bot"""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("settings", settings_command))
    # Register price alert command handlers
    from handlers.price_alert_handlers import handle_list_alerts, handle_price_history
    
    async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        await handle_list_alerts(update, context)
    
    async def price_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /price_history command"""
        hours = 24
        if context.args and len(context.args) > 0:
            try:
                hours = int(context.args[0])
                if hours not in [24, 168, 720]:
                    hours = 24
            except ValueError:
                pass
        await handle_price_history(update, context, hours=hours)
    
    application.add_handler(CommandHandler("alerts", alerts_command))
    application.add_handler(CommandHandler("price_history", price_history_command))
    
    # Register chart command handlers (P5 feature)
    from handlers.chart_handlers import (
        handle_chart_trend, handle_chart_volume,
        handle_chart_users, handle_chart_price
    )
    
    async def chart_trend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chart_trend command"""
        days = 7
        if context.args and len(context.args) > 0:
            try:
                days = int(context.args[0])
                if days not in [7, 30]:
                    days = 7
            except ValueError:
                pass
        await handle_chart_trend(update, context, days=days)
    
    async def chart_volume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chart_volume command"""
        days = 7
        if context.args and len(context.args) > 0:
            try:
                days = int(context.args[0])
            except ValueError:
                pass
        await handle_chart_volume(update, context, days=days)
    
    async def chart_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chart_users command"""
        top_n = 10
        if context.args and len(context.args) > 0:
            try:
                top_n = int(context.args[0])
                if top_n < 1 or top_n > 20:
                    top_n = 10
            except ValueError:
                pass
        await handle_chart_users(update, context, top_n=top_n)
    
    async def chart_price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chart_price command"""
        days = 7
        if context.args and len(context.args) > 0:
            try:
                days = int(context.args[0])
                if days not in [1, 7, 30]:
                    days = 7
            except ValueError:
                pass
        await handle_chart_price(update, context, days=days)
    
    application.add_handler(CommandHandler("chart_trend", chart_trend_command))
    application.add_handler(CommandHandler("chart_volume", chart_volume_command))
    application.add_handler(CommandHandler("chart_users", chart_users_command))
    application.add_handler(CommandHandler("chart_price", chart_price_command))
    
    # Register message handler (for admin shortcuts and math/settlement)
    application.add_handler(get_message_handler())
    
    # Register callback handler (for inline keyboard buttons)
    application.add_handler(get_callback_handler())
    
    # Register job queue for price alert monitoring
    from telegram.ext import JobQueue
    job_queue = application.job_queue
    
    # Schedule price alert monitoring (every 5 minutes)
    async def monitor_alerts_callback(context: ContextTypes.DEFAULT_TYPE):
        from services.price_alert_service import monitor_price_alerts
        await monitor_price_alerts(context)
    
    if job_queue:
        job_queue.run_repeating(
            monitor_alerts_callback,
            interval=300,  # 5 minutes
            first=60  # Start after 1 minute
        )
        logger.info("Price alert monitoring scheduled (every 5 minutes)")
    
    logger.info("Bot B (OTC Group Management) starting...")
    logger.info(f"Database initialized at: {db.db_path}")
    logger.info(f"Admin markup: {db.get_admin_markup()}")
    logger.info(f"USDT address: {db.get_usdt_address() or 'Not set'}")
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

