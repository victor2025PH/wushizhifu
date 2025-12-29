"""
Inline keyboard layouts for Bot B
"""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional


def get_button_help_keyboard(button_text: str) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for button help message.
    
    Args:
        button_text: Button text
        
    Returns:
        InlineKeyboardMarkup with close help button
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ 我知道了，不再显示", callback_data=f"close_help_{button_text}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_groups_list_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for groups list.
    
    Returns:
        InlineKeyboardMarkup with refresh button
    """
    keyboard = [
        [
            InlineKeyboardButton("🔄 刷新列表", callback_data="global_groups_list")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_settlement_bill_keyboard(transaction_id: str = None, transaction_status: str = None, 
                                is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for settlement bill based on transaction status.
    
    Args:
        transaction_id: Transaction ID for callback data
        transaction_status: Transaction status (pending, paid, confirmed, cancelled)
        is_admin: Whether the user is an admin
        
    Returns:
        InlineKeyboardMarkup with appropriate buttons
    """
    keyboard = []
    
    if transaction_status == 'pending':
        # Pending: User can mark as paid or cancel
        keyboard.append([
            InlineKeyboardButton("💰 已支付", callback_data=f"mark_paid_{transaction_id}" if transaction_id else "mark_paid"),
            InlineKeyboardButton("❌ 取消", callback_data=f"cancel_tx_{transaction_id}" if transaction_id else "cancel_tx")
        ])
    elif transaction_status == 'paid':
        # Paid: Admin can confirm, user can see status
        if is_admin:
            keyboard.append([
                InlineKeyboardButton("✅ 确认交易", callback_data=f"confirm_tx_{transaction_id}" if transaction_id else "confirm_tx")
            ])
    elif transaction_status == 'confirmed':
        # Confirmed: No action buttons needed
        keyboard.append([
            InlineKeyboardButton("✅ 已确认", callback_data="none")
        ])
    elif transaction_status == 'cancelled':
        # Cancelled: No action buttons needed
        keyboard.append([
            InlineKeyboardButton("❌ 已取消", callback_data="none")
        ])
    else:
        # Default: Pending state buttons
        keyboard.append([
            InlineKeyboardButton("💰 已支付", callback_data=f"mark_paid_{transaction_id}" if transaction_id else "mark_paid"),
            InlineKeyboardButton("❌ 取消", callback_data=f"cancel_tx_{transaction_id}" if transaction_id else "cancel_tx")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_payment_hash_input_keyboard(transaction_id: str) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for payment hash input.
    
    Args:
        transaction_id: Transaction ID
        
    Returns:
        InlineKeyboardMarkup with skip button
    """
    keyboard = [
        [
            InlineKeyboardButton("⏭️ 跳过（不填写）", callback_data=f"skip_payment_hash_{transaction_id}")
        ],
        [
            InlineKeyboardButton("❌ 取消", callback_data=f"cancel_tx_{transaction_id}")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_pending_transactions_keyboard(group_id: int = None, page: int = 1) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for pending transactions list (admin view).
    
    Args:
        group_id: Optional group ID
        page: Page number
        
    Returns:
        InlineKeyboardMarkup with navigation buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("🔄 刷新", callback_data=f"refresh_pending_{group_id}_{page}" if group_id else f"refresh_pending_{page}")
        ]
    ]
    
    if group_id:
        keyboard.append([
            InlineKeyboardButton("🔙 返回", callback_data=f"group_stats_{group_id}")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_paid_transactions_keyboard(group_id: int = None, page: int = 1) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for paid transactions list (admin view - waiting for confirmation).
    
    Args:
        group_id: Optional group ID
        page: Page number
        
    Returns:
        InlineKeyboardMarkup with navigation buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ 批量确认", callback_data=f"batch_confirm_{group_id}" if group_id else "batch_confirm"),
            InlineKeyboardButton("🔄 刷新", callback_data=f"refresh_paid_{group_id}_{page}" if group_id else f"refresh_paid_{page}")
        ]
    ]
    
    if group_id:
        keyboard.append([
            InlineKeyboardButton("🔙 返回", callback_data=f"group_stats_{group_id}")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_alerts_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for price alerts menu.
    
    Returns:
        InlineKeyboardMarkup with alert menu options
    """
    keyboard = [
        [
            InlineKeyboardButton("➕ 创建预警", callback_data="alert_create"),
            InlineKeyboardButton("📋 我的预警", callback_data="alerts_list")
        ],
        [
            InlineKeyboardButton("📊 价格历史", callback_data="price_history_24"),
            InlineKeyboardButton("🔙 返回", callback_data="main_menu")
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
            InlineKeyboardButton("📍 地址管理", callback_data="address_list")
        ],
        [
            InlineKeyboardButton("🔄 重置设置", callback_data="group_settings_reset"),
            InlineKeyboardButton("❌ 删除配置", callback_data="group_settings_delete")
        ],
        [
            InlineKeyboardButton("⏳ 待支付交易", callback_data="pending_transactions"),
            InlineKeyboardButton("✅ 待确认交易", callback_data="paid_transactions")
        ],
        [
            InlineKeyboardButton("📊 群组统计", callback_data="group_stats"),
            InlineKeyboardButton("📥 导出报表", callback_data="export_stats")
        ],
        [
            InlineKeyboardButton("📋 操作日志", callback_data="view_logs"),
        ],
        [
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
    
    # Filter buttons
    keyboard.append([
        InlineKeyboardButton("🔍 高级筛选", callback_data=f"filter_menu_{group_id}")
    ])
    
    # Pagination buttons
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"bills_page_{group_id}_{page-1}"))
    nav_row.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"bills_page_{group_id}_{page+1}"))
    keyboard.append(nav_row)
    
    # Export buttons
    keyboard.append([
        InlineKeyboardButton("📥 导出 CSV", callback_data=f"export_csv_{group_id}"),
        InlineKeyboardButton("📥 导出 Excel", callback_data=f"export_excel_{group_id}")
    ])
    
    # Action buttons
    keyboard.append([
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


def get_onboarding_keyboard(step: int) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for onboarding steps.
    
    Args:
        step: Current step number (1-4)
        
    Returns:
        InlineKeyboardMarkup with navigation buttons
    """
    keyboard = []
    
    if step < 4:
        # Show next button
        keyboard.append([
            InlineKeyboardButton("下一步 →", callback_data=f"onboarding_step_{step + 1}")
        ])
    
    if step > 1:
        # Show previous button
        keyboard.append([
            InlineKeyboardButton("← 上一步", callback_data=f"onboarding_step_{step - 1}")
        ])
    
    if step == 4:
        # Show complete button
        keyboard.append([
            InlineKeyboardButton("✅ 完成引导，开始使用", callback_data="onboarding_complete")
        ])
    
    keyboard.append([
        InlineKeyboardButton("⏭️ 跳过引导", callback_data="onboarding_skip")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

