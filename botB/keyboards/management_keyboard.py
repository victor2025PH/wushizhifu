"""
Management keyboard layouts for Bot B
Provides reply keyboards for management menus
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton
from typing import Optional
from admin_checker import is_admin


def get_management_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Get management menu keyboard with all management options.
    
    Returns:
        ReplyKeyboardMarkup with management menu buttons (2 per row)
    """
    keyboard = [
        [
            KeyboardButton("📊 所有群组列表"),
            KeyboardButton("📈 全局统计")
        ],
        [
            KeyboardButton("👥 客服管理"),
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
            KeyboardButton("🔙 返回管理菜单")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="请选择操作..."
    )

