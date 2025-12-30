"""
WuShiPay Telegram Bot - Entry Point
A high-end Fintech Telegram Bot for Alipay/WeChat payment gateway
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import Config
from database.models import init_database
from database.db import db
from handlers.user_handlers import user_router
from handlers.payment_handlers import router as payment_router
from handlers.calculator_handlers import router as calculator_router
from handlers.transaction_handlers import router as transaction_router
from handlers.wallet_handlers import router as wallet_router
from handlers.settings_handlers import router as settings_router
from handlers.referral_handlers import router as referral_router
from handlers.admin_handlers import router as admin_router
from handlers.group_handlers import router as group_router
from handlers.ai_handlers import router as ai_router
from utils.bot_setup import setup_bot_commands, setup_menu_button, setup_bot_info
from middleware.user_tracking import UserTrackingMiddleware
from middleware.group_middleware import GroupMiddleware

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

# Reduce aiogram dispatcher log noise (Bad Gateway and timeout errors are normal and handled automatically)
# These errors occur occasionally due to Telegram API server issues and are automatically retried
logging.getLogger("aiogram.dispatcher").setLevel(logging.ERROR)  # Only log ERROR level for dispatcher
logging.getLogger("aiogram").setLevel(logging.WARNING)  # Reduce INFO level logs from aiogram


async def on_startup(bot: Bot):
    """Actions to perform on bot startup"""
    # Initialize database
    try:
        init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise
    
    # Clear any existing webhook to avoid conflicts with polling
    logger.info("🔍 检查 Webhook 状态...")
    try:
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Webhook 信息: url={webhook_info.url}, pending_update_count={webhook_info.pending_update_count}")
        
        if webhook_info.url:
            logger.warning(f"⚠️ 检测到 Webhook: {webhook_info.url}，正在清除以避免冲突...")
            result = await bot.delete_webhook(drop_pending_updates=True)
            if result:
                logger.info("✅ Webhook 已成功清除")
            else:
                logger.warning("⚠️ Webhook 清除可能失败")
            
            # Wait longer for Telegram API to fully process and release connections
            logger.info("⏳ 等待 Telegram API 释放连接（5秒）...")
            import asyncio
            await asyncio.sleep(5)
            logger.info("✅ 等待完成")
        else:
            logger.info("✅ 没有发现 Webhook（使用 Polling 模式）")
    except Exception as e:
        logger.error(f"❌ 检查/清除 Webhook 时出错: {e}", exc_info=True)
    
    # Set up bot commands, menu button, and description
    try:
        await setup_bot_commands(bot)
        await setup_menu_button(bot)
        await setup_bot_info(bot)
    except Exception as e:
        logger.warning(f"⚠️ Some bot setup operations failed: {e}")
    
    bot_info = await bot.get_me()
    logger.info("=" * 50)
    logger.info(f"🤖 Bot: @{bot_info.username} ({bot_info.first_name})")
    logger.info(f"🆔 Bot ID: {bot_info.id}")
    logger.info("=" * 50)
    logger.info("✅ WuShiPay System Initialized Successfully")
    logger.info("📊 User tracking middleware enabled")
    logger.info("👥 Group middleware enabled")
    logger.info("🔒 Security protocols active")
    logger.info("=" * 50)


async def on_shutdown(bot: Bot):
    """Actions to perform on bot shutdown"""
    logger.info("=" * 50)
    logger.info("🛑 WuShiPay System Shutting Down...")
    db.close()
    logger.info("✅ Database connection closed")
    logger.info("=" * 50)


async def main():
    """Main function to initialize and run the bot"""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=Config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
    )
    dp = Dispatcher()
    
    # Register middleware (order matters - first registered = first executed)
    dp.message.middleware(UserTrackingMiddleware())
    dp.callback_query.middleware(UserTrackingMiddleware())
    dp.message.middleware(GroupMiddleware())
    
    # Include routers (order matters - AI router should be last to catch all non-command messages)
    from handlers.channel_video_handler import router as channel_video_router
    dp.include_router(user_router)
    dp.include_router(payment_router)
    dp.include_router(calculator_router)
    dp.include_router(transaction_router)
    dp.include_router(wallet_router)
    dp.include_router(settings_router)
    dp.include_router(referral_router)
    dp.include_router(admin_router)
    dp.include_router(group_router)
    dp.include_router(channel_video_router)  # Channel video handler
    dp.include_router(ai_router)  # AI router should be last
    
    # Register startup/shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Startup log
    print("🚀 WuShiPay System Starting...")
    logger.info("🚀 WuShiPay System Starting...")
    
    # Start polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"❌ Critical error during polling: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("✅ Bot session closed")


if __name__ == "__main__":
    asyncio.run(main())

