"""
Payment-related keyboards
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_payment_type_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting payment type"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 收款", callback_data="payment_receive"),
            InlineKeyboardButton(text="💸 付款", callback_data="payment_pay")
        ],
        [
            InlineKeyboardButton(text="🔙 返回", callback_data="main_menu")
        ]
    ])


def get_amount_quick_keyboard(amount: float = None) -> InlineKeyboardMarkup:
    """Keyboard with quick amount buttons"""
    buttons = []
    quick_amounts = [100, 500, 1000, 5000]
    
    # First row: quick amounts
    row = []
    for amt in quick_amounts[:2]:
        row.append(InlineKeyboardButton(
            text=f"¥{amt}",
            callback_data=f"amount_{amt}"
        ))
    buttons.append(row)
    
    row = []
    for amt in quick_amounts[2:]:
        row.append(InlineKeyboardButton(
            text=f"¥{amt}",
            callback_data=f"amount_{amt}"
        ))
    buttons.append(row)
    
    # Second row: calculator and back
    buttons.append([
        InlineKeyboardButton(text="🧮 使用计算器", callback_data="calculator_from_payment"),
        InlineKeyboardButton(text="🔙 返回", callback_data="payment_type")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_order_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Keyboard for confirming order"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ 确认创建订单", callback_data=f"confirm_order_{order_id}"),
        ],
        [
            InlineKeyboardButton(text="🧮 使用计算器", callback_data="calculator_from_payment"),
            InlineKeyboardButton(text="🔙 返回修改", callback_data="payment_type")
        ]
    ])


def get_order_detail_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Keyboard for order details"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 查看详情", callback_data=f"order_detail_{order_id}"),
        ],
        [
            InlineKeyboardButton(text="📜 交易记录", callback_data="transactions"),
            InlineKeyboardButton(text="🔙 返回主页", callback_data="main_menu")
        ]
    ])

