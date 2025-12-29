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


def get_exchange_direction_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting exchange direction"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="USDT → CNY", callback_data="exchange_usdt_cny"),
            InlineKeyboardButton(text="CNY → USDT", callback_data="exchange_cny_usdt")
        ],
        [
            InlineKeyboardButton(text="🔙 返回", callback_data="calculator")
        ]
    ])


def get_p2p_exchange_keyboard(payment_method: str, page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Keyboard for P2P exchange rate leaderboard with payment method and pagination"""
    keyboard = []
    
    # Payment method buttons
    keyboard.append([
        InlineKeyboardButton("💳 银行卡", callback_data=f"p2p_exchange_bank_1"),
        InlineKeyboardButton("🔵 支付宝", callback_data=f"p2p_exchange_ali_1"),
        InlineKeyboardButton("🟢 微信", callback_data=f"p2p_exchange_wx_1")
    ])
    
    # Pagination buttons (only show if more than one page)
    if total_pages > 1:
        pagination_row = []
        if page > 1:
            # Map payment method to callback code
            pm_code = "bank" if payment_method == "bank" else "ali" if payment_method == "alipay" else "wx"
            pagination_row.append(InlineKeyboardButton("◀️ 上一页", callback_data=f"p2p_exchange_{pm_code}_{page - 1}"))
        if page < total_pages:
            pm_code = "bank" if payment_method == "bank" else "ali" if payment_method == "alipay" else "wx"
            pagination_row.append(InlineKeyboardButton("下一页 ▶️", callback_data=f"p2p_exchange_{pm_code}_{page + 1}"))
        if pagination_row:
            keyboard.append(pagination_row)
    
    # Back button
    keyboard.append([
        InlineKeyboardButton("🔙 返回计算器", callback_data="calculator")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


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

