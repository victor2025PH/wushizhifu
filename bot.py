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
from handlers.admin_handlers import router as admin_router
from handlers.group_handlers import router as group_router
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


async def on_startup(bot: Bot):
    """Actions to perform on bot startup"""
    # Initialize database
    try:
        init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise
    
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
    
    # Include routers (order matters)
    dp.include_router(user_router)
    dp.include_router(payment_router)
    dp.include_router(calculator_router)
    dp.include_router(transaction_router)
    dp.include_router(admin_router)
    dp.include_router(group_router)
    
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

