"""
Main keyboard layouts for WuShiPay Telegram Bot
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import Config
from database.admin_repository import AdminRepository


def get_main_keyboard(user_id: int = None, is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Returns the main inline keyboard for the bot.
    
    Layout:
    - Row 1: Launch Mini App button
    - Row 2: Alipay and WeChat payment channels (跳轉到 MiniApp)
    - Row 3: Transaction records and Calculator (跳轉到 MiniApp)
    - Row 4: Wallet and Settings (跳轉到 MiniApp)
    - Row 5: Statistics (Bot 內顯示)
    - Row 6: Support and AI Assistant
    - Row 7: Admin Panel (僅管理員可見)
    
    Args:
        user_id: User ID for admin check (optional, used if is_admin not provided)
        is_admin: Whether user is admin (if not provided, will check using user_id)
    """
    # If is_admin not provided but user_id is, check admin status
    if not is_admin and user_id is not None:
        is_admin = AdminRepository.is_admin(user_id)
    keyboard_rows = []
    
    # Row 1: Launch Mini App
    keyboard_rows.append([
        InlineKeyboardButton(
            text="💎 启动伍拾收银台",
            web_app=WebAppInfo(url=Config.get_miniapp_url("dashboard"))
        )
    ])
    
    # Row 2: Payment channels (Bot 内部功能)
    keyboard_rows.append([
        InlineKeyboardButton(
            text="💳 支付宝",
            callback_data="pay_ali"
        ),
        InlineKeyboardButton(
            text="🍀 微信支付",
            callback_data="pay_wechat"
        )
    ])
    
    # Row 3: Transaction records and Calculator (Bot 内部功能)
    keyboard_rows.append([
        InlineKeyboardButton(
            text="📜 交易记录",
            callback_data="transactions"
        ),
        InlineKeyboardButton(
            text="🧮 汇率计算器",
            callback_data="calculator"
        )
    ])
    
    # Row 4: Wallet and Settings (Bot 内部功能)
    keyboard_rows.append([
        InlineKeyboardButton(
            text="💰 我的钱包",
            callback_data="wallet"
        ),
        InlineKeyboardButton(
            text="⚙️ 个人设置",
            callback_data="settings"
        )
    ])
    
    # Row 5: Statistics and Referral (Bot 內顯示)
    keyboard_rows.append([
        InlineKeyboardButton(
            text="📊 统计信息",
            callback_data="statistics"
        ),
        InlineKeyboardButton(
            text="🎁 分享有礼",
            callback_data="referral_main"
        )
    ])
    
    # Row 6: Support and AI Assistant
    keyboard_rows.append([
        InlineKeyboardButton(
            text="💬 客服支持",
            url=Config.SUPPORT_URL
        ),
        InlineKeyboardButton(
            text="🤖 AI 助手",
            callback_data="ai_chat"
        )
    ])
    
    # Row 7: Admin Panel (僅管理員可見)
    if is_admin:
        keyboard_rows.append([
            InlineKeyboardButton(
                text="⚙️ 管理面板",
                callback_data="admin_panel"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
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

