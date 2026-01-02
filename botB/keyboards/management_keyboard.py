"""
Management keyboard layouts for Bot B
Provides reply keyboards for management menus
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton
from typing import Optional
from admin_checker import is_admin


def get_management_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Get management menu keyboard - now returns main menu keyboard.
    Old panel removed, use main menu instead.
    
    Returns:
        ReplyKeyboardMarkup with main menu buttons
    """
    # Use main reply keyboard instead of old management panel
    from keyboards.reply_keyboard import get_main_reply_keyboard
    # Note: This function is deprecated, should use get_main_reply_keyboard directly
    # Keeping for backward compatibility but returning main menu
    return get_main_reply_keyboard()


def get_customer_service_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Get customer service management menu keyboard.
    
    Returns:
        ReplyKeyboardMarkup with customer service management buttons (2 per row)
    """
    keyboard = [
        [
            KeyboardButton("📋 客服账号列表"),
            KeyboardButton("➕ 添加客服账号")
        ],
        [
            KeyboardButton("⚙️ 分配策略设置"),
            KeyboardButton("📊 客服统计报表")
        ],
        [
            KeyboardButton("🔙 返回主菜单")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="请选择操作..."
    )


def get_group_settings_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Get reply keyboard for group settings menu.
    
    Returns:
        ReplyKeyboardMarkup with group settings options (2 per row where applicable)
    """
    keyboard = [
        [
            KeyboardButton("📋 查看群组设置")
        ],
        [
            KeyboardButton("➕ 设置加价"),
            KeyboardButton("📍 地址管理")
        ],
        [
            KeyboardButton("🔄 重置设置"),
            KeyboardButton("❌ 删除配置")
        ],
        [
            KeyboardButton("⏳ 待支付交易"),
            KeyboardButton("✅ 待确认交易")
        ],
        [
            KeyboardButton("📊 群组统计"),
            KeyboardButton("📥 导出报表")
        ],
        [
            KeyboardButton("📋 操作日志")
        ],
        [
            KeyboardButton("⚡ 管理员指令教程")
        ],
        [
            KeyboardButton("🔙 返回主菜单")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="请选择操作..."
    )

