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

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome_message = (
        f"👋 欢迎使用 OTC 群组管理 Bot！\n\n"
        f"你好，{user.first_name}！\n\n"
        f"这是一个用于管理 OTC 交易群组的机器人。\n\n"
        f"使用 /help 查看可用命令。"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📚 可用命令：\n\n"
        "/start - 启动 Bot\n"
        "/help - 显示帮助信息\n"
        "/price - 获取当前 USDT/CNY 价格\n"
        "/settings - 查看当前设置\n"
        "\n"
        "更多功能开发中..."
    )
    await update.message.reply_text(help_text)


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command - fetch and display USDT/CNY price"""
    from services.price_service import get_price_with_markup
    
    await update.message.reply_text("⏳ 正在获取价格...")
    
    final_price, error_msg, base_price = get_price_with_markup()
    
    if final_price is None:
        message = f"❌ 获取价格失败\n\n{error_msg or '未知错误'}"
    else:
        markup = db.get_admin_markup()
        message = (
            f"💱 USDT/CNY 价格信息\n\n"
            f"📊 基础价格：{base_price:.4f} CNY\n"
            f"➕ 管理员加价：{markup:.4f} CNY\n"
            f"💰 最终价格：{final_price:.4f} CNY\n"
        )
        if error_msg:
            message += f"\n⚠️ 注意：{error_msg}"
    
    await update.message.reply_text(message)


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
    
    logger.info("Bot B (OTC Group Management) starting...")
    logger.info(f"Database initialized at: {db.db_path}")
    logger.info(f"Admin markup: {db.get_admin_markup()}")
    logger.info(f"USDT address: {db.get_usdt_address() or 'Not set'}")
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

