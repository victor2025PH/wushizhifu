"""
Calculator-related keyboards
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_calculator_type_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting calculator type"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 费率计算", callback_data="calc_fee"),
        ],
        [
            InlineKeyboardButton(text="💱 汇率转换", callback_data="calc_exchange"),
        ],
        [
            InlineKeyboardButton(text="🔙 返回主页", callback_data="main_menu")
        ]
    ])


def get_calculator_channel_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting payment channel in calculator"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 支付宝", callback_data="calc_channel_alipay"),
            InlineKeyboardButton(text="🍀 微信", callback_data="calc_channel_wechat")
        ],
        [
            InlineKeyboardButton(text="🔙 返回", callback_data="calculator")
        ]
    ])


def get_calculator_result_keyboard(use_for_order: bool = False) -> InlineKeyboardMarkup:
    """Keyboard after calculator result"""
    buttons = []
    if use_for_order:
        buttons.append([
            InlineKeyboardButton(text="✅ 使用此金额创建订单", callback_data="use_calc_amount")
        ])
    buttons.append([
        InlineKeyboardButton(text="🔄 重新计算", callback_data="calculator"),
        InlineKeyboardButton(text="🔙 返回主页", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

