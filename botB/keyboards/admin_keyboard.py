"""
Admin panel keyboard layouts for Bot B
All management functions use reply keyboard (bottom buttons)
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton
from typing import Optional


def get_admin_panel_keyboard() -> ReplyKeyboardMarkup:
    """
    Get admin panel reply keyboard with all management functions.
    Layout: 3 buttons per row
    """
    keyboard = [
        [
            KeyboardButton("👥 用户管理"),
            KeyboardButton("📊 系统统计"),
            KeyboardButton("👤 添加管理员")
        ],
        [
            KeyboardButton("🚫 敏感词管理"),
            KeyboardButton("✅ 群组审核"),
            KeyboardButton("⚙️ 群组设置")
        ],
        [
            KeyboardButton("📋 群组列表"),
            KeyboardButton("🔙 返回主菜单")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_admin_submenu_keyboard(submenu: str = None) -> ReplyKeyboardMarkup:
    """
    Get submenu keyboard for admin functions.
    
    Args:
        submenu: Submenu type (e.g., "users", "stats", "words", "verify", "group")
    """
    keyboard = []
    
    if submenu == "users":
        # User management submenu
        keyboard = [
            [
                KeyboardButton("🔍 搜索用户"),
                KeyboardButton("📊 用户报表")
            ],
            [
                KeyboardButton("👤 用户详情"),
                KeyboardButton("⚙️ 用户操作")
            ],
            [
                KeyboardButton("🔙 返回管理面板")
            ]
        ]
    elif submenu == "stats":
        # Statistics submenu
        keyboard = [
            [
                KeyboardButton("📅 时间统计"),
                KeyboardButton("📊 详细报表")
            ],
            [
                KeyboardButton("📋 操作日志"),
                KeyboardButton("🔙 返回管理面板")
            ]
        ]
    elif submenu == "words":
        # Sensitive words submenu
        keyboard = [
            [
                KeyboardButton("➕ 添加敏感词"),
                KeyboardButton("✏️ 编辑敏感词")
            ],
            [
                KeyboardButton("🗑️ 删除敏感词"),
                KeyboardButton("📋 导出列表")
            ],
            [
                KeyboardButton("💾 完整导出"),
                KeyboardButton("🔙 返回管理面板")
            ]
        ]
    elif submenu == "verify":
        # Group verification submenu
        keyboard = [
            [
                KeyboardButton("✅ 全部通过"),
                KeyboardButton("❌ 全部拒绝")
            ],
            [
                KeyboardButton("👤 审核详情"),
                KeyboardButton("📋 审核历史")
            ],
            [
                KeyboardButton("🔙 返回管理面板")
            ]
        ]
    elif submenu == "group":
        # Group settings submenu
        keyboard = [
            [
                KeyboardButton("➕ 添加群组"),
                KeyboardButton("📋 群组列表")
            ],
            [
                KeyboardButton("🔍 搜索群组"),
                KeyboardButton("⚙️ 群组配置")
            ],
            [
                KeyboardButton("🗑️ 删除群组"),
                KeyboardButton("🔙 返回管理面板")
            ]
        ]
    elif submenu == "add":
        # Add admin submenu
        keyboard = [
            [
                KeyboardButton("➕ 添加管理员"),
                KeyboardButton("🗑️ 删除管理员")
            ],
            [
                KeyboardButton("🔙 返回管理面板")
            ]
        ]
    else:
        # Default: return to admin panel
        keyboard = [
            [
                KeyboardButton("🔙 返回管理面板")
            ]
        ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
