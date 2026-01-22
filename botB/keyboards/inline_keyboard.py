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
        InlineKeyboardMarkup with refresh button and back to main menu
    """
    keyboard = [
        [
            InlineKeyboardButton("🔄 刷新列表", callback_data="global_groups_list")
        ],
        [
            InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_groups_list_keyboard_with_edit(groups: list, page: int = 1, per_page: int = 10) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for groups list with edit buttons for each group.
    Supports pagination.
    
    Args:
        groups: List of group dictionaries (all groups)
        page: Current page number (1-based)
        per_page: Number of groups per page
        
    Returns:
        InlineKeyboardMarkup with edit buttons for each group, pagination and refresh button
    """
    keyboard = []
    
    # Calculate pagination
    total_groups = len(groups)
    total_pages = max(1, (total_groups + per_page - 1) // per_page)  # Ceiling division
    page = max(1, min(page, total_pages))  # Ensure page is within valid range
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_groups = groups[start_idx:end_idx]
    
    # Add edit and delete buttons for each group on this page
    for group in page_groups:
        group_id = group['group_id']
        group_title = group.get('group_title', f"群组 {group_id}")
        # Truncate title if too long
        if len(group_title) > 15:
            group_title = group_title[:12] + "..."
        
        # 每行顯示編輯和刪除按鈕（兩個按鈕並排）
        keyboard.append([
            InlineKeyboardButton(
                f"✏️ {group_title[:12]}",
                callback_data=f"group_select_{group_id}"
            ),
            InlineKeyboardButton(
                "🗑️ 删除",
                callback_data=f"group_delete_{group_id}"
            )
        ])
    
    # Add pagination buttons if there are multiple pages
    if total_pages > 1:
        pagination_row = []
        
        # Previous page button
        if page > 1:
            pagination_row.append(
                InlineKeyboardButton("⬅️ 上一页", callback_data=f"groups_page_{page - 1}")
            )
        
        # Page indicator (not clickable)
        pagination_row.append(
            InlineKeyboardButton(f"第 {page}/{total_pages} 页", callback_data="page_info")
        )
        
        # Next page button
        if page < total_pages:
            pagination_row.append(
                InlineKeyboardButton("下一页 ➡️", callback_data=f"groups_page_{page + 1}")
            )
        
        keyboard.append(pagination_row)
    
    # Add refresh button
    keyboard.append([
        InlineKeyboardButton("🔄 刷新列表", callback_data="global_groups_list")
    ])
    
    # Add back button to return to main menu
    keyboard.append([
        InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")
    ])
    
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




def get_group_settings_menu(pending_count: int = 0, paid_count: int = 0) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for group settings menu (restructured).
    
    Args:
        pending_count: Number of pending transactions
        paid_count: Number of paid transactions waiting for confirmation
    
    Returns:
        InlineKeyboardMarkup with organized group settings options
    """
    # Format count badges
    pending_badge = f" ({pending_count})" if pending_count > 0 else ""
    paid_badge = f" ({paid_count})" if paid_count > 0 else ""
    
    keyboard = [
        # === 交易管理 ===
        [
            InlineKeyboardButton(f"⏳ 待支付{pending_badge}", callback_data="pending_transactions"),
            InlineKeyboardButton(f"✅ 待確認{paid_badge}", callback_data="paid_transactions")
        ],
        # === 數據統計 ===
        [
            InlineKeyboardButton("📊 群組統計", callback_data="group_stats"),
            InlineKeyboardButton("📥 導出報表", callback_data="export_stats")
        ],
        # === 基礎設置 ===
        [
            InlineKeyboardButton("➕ 設置加價", callback_data="group_settings_markup"),
            InlineKeyboardButton("📍 地址管理", callback_data="address_list")
        ],
        # === 群組配置 ===
        [
            InlineKeyboardButton("📋 查看設置", callback_data="group_settings_view"),
            InlineKeyboardButton("🔔 通知設置", callback_data="notification_settings")
        ],
        # === 高級功能 ===
        [
            InlineKeyboardButton("📋 操作日誌", callback_data="view_logs"),
            InlineKeyboardButton("⚡ 指令教程", callback_data="admin_commands_help")
        ],
        # === 危險操作 ===
        [
            InlineKeyboardButton("🔄 重置設置", callback_data="group_settings_reset"),
            InlineKeyboardButton("❌ 刪除配置", callback_data="group_settings_delete")
        ],
        # === 返回 ===
        [
            InlineKeyboardButton("🔙 返回主菜單", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_notification_settings_keyboard(settings: dict) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for notification settings.
    
    Args:
        settings: Current notification settings dict
        
    Returns:
        InlineKeyboardMarkup with notification toggle buttons
    """
    welcome_status = "✅" if settings.get('welcome_enabled', True) else "❌"
    leave_status = "✅" if settings.get('leave_enabled', False) else "❌"
    kick_status = "✅" if settings.get('kick_enabled', True) else "❌"
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{welcome_status} 歡迎消息", 
                callback_data="toggle_welcome"
            )
        ],
        [
            InlineKeyboardButton(
                f"{leave_status} 離開通知", 
                callback_data="toggle_leave"
            )
        ],
        [
            InlineKeyboardButton(
                f"{kick_status} 踢出通知", 
                callback_data="toggle_kick"
            )
        ],
        [
            InlineKeyboardButton("✏️ 自定義歡迎語", callback_data="edit_welcome_message")
        ],
        [
            InlineKeyboardButton("🔙 返回設置", callback_data="group_settings_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# get_global_management_menu() removed - old panel no longer used


def get_customer_service_management_menu() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for customer service management menu.
    
    Returns:
        InlineKeyboardMarkup with customer service management options
    """
    keyboard = [
        [
            InlineKeyboardButton("📋 客服账号列表", callback_data="customer_service_list"),
            InlineKeyboardButton("➕ 添加客服账号", callback_data="customer_service_add")
        ],
        [
            InlineKeyboardButton("⚙️ 分配策略设置", callback_data="customer_service_strategy"),
            InlineKeyboardButton("📊 客服统计报表", callback_data="customer_service_stats")
        ],
        [
            InlineKeyboardButton("🔙 返回主菜单", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_customer_service_list_keyboard(accounts: list, page: int = 0, per_page: int = 10) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for customer service account list.
    
    Args:
        accounts: List of account dictionaries
        page: Current page (0-indexed)
        per_page: Items per page
        
    Returns:
        InlineKeyboardMarkup with account buttons and navigation
    """
    keyboard = []
    
    # Calculate pagination
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_accounts = accounts[start_idx:end_idx]
    
    # Add account buttons (max 10 per page)
    for account in page_accounts:
        account_id = account['id']
        display_name = account['display_name']
        is_active = account['is_active']
        
        # Truncate display name if too long
        if len(display_name) > 20:
            display_name = display_name[:17] + "..."
        
        status_icon = "✅" if is_active else "❌"
        button_text = f"{status_icon} {display_name}"
        
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"customer_service_edit_{account_id}"
            )
        ])
    
    # Pagination buttons
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"customer_service_list_page_{page-1}"))
    if end_idx < len(accounts):
        nav_row.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"customer_service_list_page_{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
    
    # Action buttons
    keyboard.append([
        InlineKeyboardButton("➕ 添加客服", callback_data="customer_service_add"),
        InlineKeyboardButton("🔙 返回", callback_data="customer_service_management")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_customer_service_edit_keyboard(account_id: int) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for editing a customer service account.
    
    Args:
        account_id: Account ID
        
    Returns:
        InlineKeyboardMarkup with edit options
    """
    keyboard = [
        [
            InlineKeyboardButton("✏️ 编辑信息", callback_data=f"customer_service_edit_info_{account_id}")
        ],
        [
            InlineKeyboardButton("🔄 启用/禁用", callback_data=f"customer_service_toggle_{account_id}")
        ],
        [
            InlineKeyboardButton("🗑️ 删除账号", callback_data=f"customer_service_delete_{account_id}")
        ],
        [
            InlineKeyboardButton("🔙 返回列表", callback_data="customer_service_list")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_customer_service_strategy_keyboard(current_method: str = 'smart') -> InlineKeyboardMarkup:
    """
    Get inline keyboard for assignment strategy settings.
    
    Args:
        current_method: Current assignment method
        
    Returns:
        InlineKeyboardMarkup with strategy options
    """
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if current_method == 'smart' else '○'} 智能混合分配",
                callback_data="customer_service_strategy_set_smart"
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_method == 'round_robin' else '○'} 简单轮询",
                callback_data="customer_service_strategy_set_round_robin"
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_method == 'least_busy' else '○'} 最少任务优先",
                callback_data="customer_service_strategy_set_least_busy"
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_method == 'weighted' else '○'} 权重分配",
                callback_data="customer_service_strategy_set_weighted"
            )
        ],
        [
            InlineKeyboardButton("🔙 返回", callback_data="customer_service_management")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_quick_settlement_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for quick settlement with common amount templates.
    
    Returns:
        InlineKeyboardMarkup with quick amount buttons
    """
    keyboard = [
        # Row 1: Small amounts
        [
            InlineKeyboardButton("1,000", callback_data="quick_amount_1000"),
            InlineKeyboardButton("2,000", callback_data="quick_amount_2000"),
            InlineKeyboardButton("5,000", callback_data="quick_amount_5000"),
        ],
        # Row 2: Medium amounts
        [
            InlineKeyboardButton("10,000", callback_data="quick_amount_10000"),
            InlineKeyboardButton("20,000", callback_data="quick_amount_20000"),
            InlineKeyboardButton("50,000", callback_data="quick_amount_50000"),
        ],
        # Row 3: Large amounts
        [
            InlineKeyboardButton("100,000", callback_data="quick_amount_100000"),
            InlineKeyboardButton("200,000", callback_data="quick_amount_200000"),
        ],
        # Row 4: Custom input hint
        [
            InlineKeyboardButton("✏️ 自定義金額（直接輸入）", callback_data="custom_amount_hint"),
        ],
        # Row 5: Cancel
        [
            InlineKeyboardButton("❌ 取消", callback_data="cancel_settlement"),
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_commands_help_keyboard(is_group: bool = False) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for admin commands help.
    
    Args:
        is_group: Whether this is a group chat
        
    Returns:
        InlineKeyboardMarkup with back button
    """
    if is_group:
        callback_data = "group_settings_menu"
    else:
        callback_data = "main_menu"  # Changed from global_management_menu to main_menu
    
    keyboard = [
        [
            InlineKeyboardButton("🔙 返回主菜单", callback_data=callback_data)
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


def get_group_edit_keyboard(group_id: int) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for editing a specific group's settings.
    
    Args:
        group_id: The group ID to edit
        
    Returns:
        InlineKeyboardMarkup with edit options for the group
    """
    keyboard = [
        [
            InlineKeyboardButton("📈 编辑上浮汇率", callback_data=f"group_edit_markup_{group_id}")
        ],
        [
            InlineKeyboardButton("📍 地址管理", callback_data="address_list")
        ],
        [
            InlineKeyboardButton("🔙 返回群组列表", callback_data="global_groups_list")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

