"""
Admin panel keyboard layouts for Bot B
All management functions use reply keyboard (bottom buttons)
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from typing import Optional
from urllib.parse import urlencode
from config import Config


def get_admin_panel_keyboard(user_info: Optional[dict] = None) -> ReplyKeyboardMarkup:
    """
    Get admin panel reply keyboard with all management functions.
    Layout: 3 buttons per row
    
    Args:
        user_info: Optional user info dict for WebApp URL generation
    """
    def get_webapp_url():
        base_url = Config.get_miniapp_url("dashboard")
        import logging
        logger = logging.getLogger(__name__)
        
        if user_info and user_info.get('id'):
            user_id_value = user_info.get('id')
            if user_id_value and str(user_id_value).strip() and str(user_id_value) != 'None':
                params = {
                    'user_id': str(user_id_value).strip(),
                }
                
                first_name = (user_info.get('first_name') or '').strip()
                if first_name:
                    params['first_name'] = first_name
                
                username = (user_info.get('username') or '').strip()
                if username:
                    params['user_name'] = username
                
                language_code = (user_info.get('language_code') or '').strip()
                if language_code:
                    params['language_code'] = language_code
                
                if params.get('user_id'):
                    param_string = urlencode(params, doseq=False)
                    final_url = f"{base_url}&{param_string}"
                    logger.info(f"Generated WebApp URL for admin panel: user_id={params.get('user_id')}")
                    return final_url
        
        return base_url
    
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
            KeyboardButton("📊 所有群组列表"),
            KeyboardButton("📈 全局统计")
        ],
        [
            KeyboardButton("👥 客服管理"),
            KeyboardButton("⚡ 管理员指令教程"),
            KeyboardButton(
                "💎 打开应用",
                web_app=WebAppInfo(url=get_webapp_url())
            )
        ],
        [
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
