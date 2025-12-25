"""
Transaction record-related keyboards
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_transaction_filter_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for filtering transactions"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 今天", callback_data="filter_today"),
            InlineKeyboardButton(text="📆 本周", callback_data="filter_week"),
            InlineKeyboardButton(text="📊 本月", callback_data="filter_month")
        ],
        [
            InlineKeyboardButton(text="💰 收款", callback_data="filter_receive"),
            InlineKeyboardButton(text="💸 付款", callback_data="filter_pay")
        ],
        [
            InlineKeyboardButton(text="💳 支付宝", callback_data="filter_alipay"),
            InlineKeyboardButton(text="🍀 微信", callback_data="filter_wechat")
        ],
        [
            InlineKeyboardButton(text="📋 全部记录", callback_data="filter_all"),
            InlineKeyboardButton(text="🔙 返回主页", callback_data="main_menu")
        ]
    ])


def get_transaction_list_keyboard(page: int = 0, has_next: bool = False) -> InlineKeyboardMarkup:
    """Keyboard for transaction list pagination"""
    buttons = []
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ 上一页", callback_data=f"trans_page_{page-1}"))
    if has_next:
        nav_buttons.append(InlineKeyboardButton(text="下一页 ➡️", callback_data=f"trans_page_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([
        InlineKeyboardButton(text="🔙 返回主页", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_transaction_detail_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Keyboard for transaction detail page"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📜 返回列表", callback_data="transactions"),
            InlineKeyboardButton(text="🔙 返回主页", callback_data="main_menu")
        ]
    ])

