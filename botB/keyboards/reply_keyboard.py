"""
Reply keyboard layouts for Bot B
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton
from typing import Optional
from admin_checker import is_admin


def get_main_reply_keyboard(user_id: Optional[int] = None, is_group: bool = False) -> ReplyKeyboardMarkup:
    """
    Get main reply keyboard with three buttons per row.
    
    Args:
        user_id: Optional user ID to check admin status
        is_group: Whether this is a group chat
    
    Returns:
        ReplyKeyboardMarkup with main menu buttons (3 per row)
    """
    keyboard = []
    
    if is_group:
        # Group layout - 3 buttons per row
        keyboard = [
            [
                KeyboardButton("💱 汇率"),
                KeyboardButton("📊 今日"),
                KeyboardButton("📜 历史")
            ],
            [
                KeyboardButton("💰 结算"),
                KeyboardButton("🔗 地址"),
                KeyboardButton("📞 客服")
            ]
        ]
        
        # Add admin buttons if admin (3 per row)
        if user_id and is_admin(user_id):
            keyboard.append([
                KeyboardButton("⚙️ 设置"),
                KeyboardButton("📈 统计")
            ])
    else:
        # Private chat layout - 3 buttons per row
        keyboard = [
            [
                KeyboardButton("💱 汇率"),
                KeyboardButton("💰 结算"),
                KeyboardButton("📜 我的账单")
            ],
            [
                KeyboardButton("🔔 预警"),
                KeyboardButton("🔗 地址"),
                KeyboardButton("📞 客服")
            ]
        ]
        
        # Add admin buttons if admin (3 per row)
        if user_id and is_admin(user_id):
            keyboard.append([
                KeyboardButton("⚙️ 管理"),
                KeyboardButton("📊 数据")
            ])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="输入人民币金额或算式（如：20000-200）..."
    )

