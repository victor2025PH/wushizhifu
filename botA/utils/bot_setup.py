"""
Bot setup utilities for configuring bot commands and menu buttons
"""
import logging
from aiogram import Bot
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo
from config import Config

logger = logging.getLogger(__name__)


async def setup_bot_commands(bot: Bot):
    """
    Set up bot commands that appear in the command menu.
    
    Args:
        bot: Bot instance
    """
    try:
        commands = [
            BotCommand(command="start", description="开始使用"),
            BotCommand(command="help", description="帮助信息"),
        ]
        
        await bot.set_my_commands(commands)
        logger.info("✅ Bot commands set successfully")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}", exc_info=True)


async def setup_menu_button(bot: Bot):
    """
    Set up menu button that appears in bot profile and chat header.
    This creates the "打开应用" button.
    
    Args:
        bot: Bot instance
    """
    try:
        menu_button = MenuButtonWebApp(
            text="打开应用",
            web_app=WebAppInfo(url=Config.get_miniapp_url("dashboard"))
        )
        await bot.set_chat_menu_button(menu_button=menu_button)
        logger.info(f"✅ Menu button set: '打开应用' -> {Config.get_miniapp_url('dashboard')}")
    except Exception as e:
        logger.error(f"Failed to set menu button: {e}", exc_info=True)


async def setup_bot_info(bot: Bot):
    """
    Set up bot information including description.
    
    Args:
        bot: Bot instance
    """
    try:
        description = (
            "伍拾支付 - Telegram 生态中领先的数字资产支付解决方案\n\n"
            "功能：\n"
            "• 支付宝/微信支付通道\n"
            "• USDT 充值提现\n"
            "• 汇率计算器\n"
            "• 交易记录查询\n\n"
            "点击「打开应用」开始使用"
        )
        
        short_description = "数字资产支付解决方案 - 安全便捷的支付服务"
        
        await bot.set_my_description(description=description)
        await bot.set_my_short_description(short_description=short_description)
        logger.info("✅ Bot description set successfully")
    except Exception as e:
        logger.warning(f"Failed to set bot description (may require BotFather): {e}")

