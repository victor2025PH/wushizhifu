"""
Main keyboard layouts for WuShiPay Telegram Bot
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard() -> InlineKeyboardMarkup:
    """
    Returns the main inline keyboard for the bot (方案 A - 簡潔版).
    
    Layout:
    - Row 1: Launch Mini App button
    - Row 2: Alipay and WeChat payment channels
    - Row 3: Transaction records and Calculator
    - Row 4: Statistics and Settings
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # Row 1: Launch Mini App
        [
            InlineKeyboardButton(
                text="💎 启动伍拾收银台 | Launch App",
                web_app={"url": "https://google.com"}
            )
        ],
        # Row 2: Payment channels
        [
            InlineKeyboardButton(
                text="💳 支付宝通道",
                callback_data="pay_ali"
            ),
            InlineKeyboardButton(
                text="🍀 微信通道",
                callback_data="pay_wechat"
            )
        ],
        # Row 3: Transaction records and Calculator
        [
            InlineKeyboardButton(
                text="📜 交易记录",
                callback_data="transactions"
            ),
            InlineKeyboardButton(
                text="🧮 计算器",
                callback_data="calculator"
            )
        ],
        # Row 4: Statistics and Settings
        [
            InlineKeyboardButton(
                text="📊 统计",
                callback_data="statistics"
            ),
            InlineKeyboardButton(
                text="⚙️ 设置",
                callback_data="settings"
            )
        ]
    ])
    
    return keyboard


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """
    Returns the admin keyboard (only visible to admins).
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👥 用户管理",
                callback_data="admin_users"
            ),
            InlineKeyboardButton(
                text="📊 系统统计",
                callback_data="admin_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 添加管理员",
                callback_data="admin_add"
            ),
            InlineKeyboardButton(
                text="🚫 敏感词管理",
                callback_data="admin_words"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ 群组审核",
                callback_data="admin_verify"
            ),
            InlineKeyboardButton(
                text="⚙️ 群组设置",
                callback_data="admin_group"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 返回主菜单",
                callback_data="main_menu"
            )
        ]
    ])
    
    return keyboard

