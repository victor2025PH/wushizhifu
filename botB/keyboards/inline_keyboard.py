"""
Inline keyboard layouts for Bot B
"""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional


def get_settlement_bill_keyboard(bill_id: str = None) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for settlement bill.
    
    Args:
        bill_id: Optional bill ID for callback data
        
    Returns:
        InlineKeyboardMarkup with confirmation button
    """
    callback_data = f"confirm_bill_{bill_id}" if bill_id else "confirm_bill"
    
    keyboard = [
        [
            InlineKeyboardButton("✅ 已核对", callback_data=callback_data)
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_group_settings_menu() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for group settings menu.
    
    Returns:
        InlineKeyboardMarkup with group settings options
    """
    keyboard = [
        [
            InlineKeyboardButton("📋 查看群组设置", callback_data="group_settings_view")
        ],
        [
            InlineKeyboardButton("➕ 设置加价", callback_data="group_settings_markup"),
            InlineKeyboardButton("📍 设置地址", callback_data="group_settings_address")
        ],
        [
            InlineKeyboardButton("🔄 重置设置", callback_data="group_settings_reset"),
            InlineKeyboardButton("❌ 删除配置", callback_data="group_settings_delete")
        ],
        [
            InlineKeyboardButton("📊 群组统计", callback_data="group_stats"),
            InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_global_management_menu() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for global management menu.
    
    Returns:
        InlineKeyboardMarkup with global management options
    """
    keyboard = [
        [
            InlineKeyboardButton("📋 查看全局设置", callback_data="global_settings_view")
        ],
        [
            InlineKeyboardButton("➕ 设置全局加价", callback_data="global_settings_markup"),
            InlineKeyboardButton("📍 设置全局地址", callback_data="global_settings_address")
        ],
        [
            InlineKeyboardButton("📊 所有群组列表", callback_data="global_groups_list"),
            InlineKeyboardButton("📈 全局统计", callback_data="global_stats")
        ],
        [
            InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_bills_history_keyboard(group_id: int, page: int = 1, start_date: str = None, end_date: str = None) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for bills history pagination.
    
    Args:
        group_id: Telegram group ID
        page: Current page number (1-based)
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        InlineKeyboardMarkup with pagination buttons
    """
    keyboard = []
    
    # Date filter buttons
    keyboard.append([
        InlineKeyboardButton("📅 按日期筛选", callback_data=f"bills_filter_date_{group_id}_{page}"),
        InlineKeyboardButton("🔍 搜索", callback_data=f"bills_search_{group_id}_{page}")
    ])
    
    # Pagination buttons
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"bills_page_{group_id}_{page-1}"))
    nav_row.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"bills_page_{group_id}_{page+1}"))
    keyboard.append(nav_row)
    
    # Action buttons
    keyboard.append([
        InlineKeyboardButton("📥 导出", callback_data=f"bills_export_{group_id}"),
        InlineKeyboardButton("🔙 返回", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirmation_keyboard(action: str, data: str = "") -> InlineKeyboardMarkup:
    """
    Get inline keyboard for confirmation dialog.
    
    Args:
        action: Action type (e.g., "delete_group_settings", "reset_group_settings")
        data: Optional additional data
        
    Returns:
        InlineKeyboardMarkup with confirm/cancel buttons
    """
    callback_confirm = f"confirm_{action}_{data}".rstrip("_")
    callback_cancel = f"cancel_{action}"
    
    keyboard = [
        [
            InlineKeyboardButton("✅ 确认", callback_data=callback_confirm),
            InlineKeyboardButton("❌ 取消", callback_data=callback_cancel)
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_transaction_detail_keyboard(transaction_id: str, group_id: int, return_page: int = 1) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for transaction detail view.
    
    Args:
        transaction_id: Transaction ID
        group_id: Telegram group ID
        return_page: Page number to return to
        
    Returns:
        InlineKeyboardMarkup with return button
    """
    keyboard = [
        [
            InlineKeyboardButton("🔙 返回列表", callback_data=f"bills_page_{group_id}_{return_page}")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

