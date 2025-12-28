"""
Reply keyboard layouts for Bot B
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Get main reply keyboard with persistent menu buttons.
    
    Returns:
        ReplyKeyboardMarkup with main menu buttons
    """
    keyboard = [
        [
            KeyboardButton("📊 查看汇率"),
            KeyboardButton("🔗 收款地址")
        ],
        [
            KeyboardButton("📞 联系人工")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="输入数字或算式自动计算结算账单"
    )

