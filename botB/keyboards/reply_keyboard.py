"""
Reply keyboard layouts for Bot B
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from typing import Optional
from urllib.parse import urlencode
from admin_checker import is_admin
from config import Config


def get_main_reply_keyboard(user_id: Optional[int] = None, is_group: bool = False, user_info: Optional[dict] = None) -> ReplyKeyboardMarkup:
    """
    Get main reply keyboard with three buttons per row.
    
    Args:
        user_id: Optional user ID to check admin status
        is_group: Whether this is a group chat
        user_info: Optional user info dict with id, first_name, username, etc.
    
    Returns:
        ReplyKeyboardMarkup with main menu buttons (3 per row)
    """
    keyboard = []
    
    # Generate WebApp URL with user info as fallback (for ReplyKeyboard buttons)
    # This helps when initData is not available from ReplyKeyboard WebApp buttons
    def get_webapp_url():
        base_url = Config.get_miniapp_url("dashboard")
        if user_info and user_info.get('id'):
            # Add user info as URL parameters (as fallback when initData is missing)
            params = {
                'user_id': str(user_info.get('id')),
                'first_name': user_info.get('first_name', '') or '',
            }
            if user_info.get('username'):
                params['user_name'] = user_info.get('username')
            if user_info.get('language_code'):
                params['language_code'] = user_info.get('language_code')
            
            # Ensure we have user_id
            if params.get('user_id') and params['user_id'] != 'None':
                param_string = urlencode(params, safe='')
                final_url = f"{base_url}&{param_string}"
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Generated WebApp URL with user params: {final_url[:100]}...")
                return final_url
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"WebApp URL generated without user_info. user_info={user_info}")
        return base_url
    
    if is_group:
        # Group layout - 3 buttons per row
        keyboard = [
            [
                KeyboardButton("💱 汇率"),
                KeyboardButton("📊 今日"),
                KeyboardButton("📜 历史")
            ],
            [
                KeyboardButton("💰 结算"),
                KeyboardButton("🔗 地址"),
                KeyboardButton("📞 客服")
            ]
        ]
        
        # Add admin buttons if admin (3 per row)
        if user_id and is_admin(user_id):
            keyboard.append([
                KeyboardButton("⚙️ 设置"),
                KeyboardButton("📈 统计"),
                KeyboardButton(
                    "💎 打开应用",
                    web_app=WebAppInfo(url=get_webapp_url())
                )
            ])
        else:
            # If not admin, add "打开应用" button in a row of 3
            keyboard.append([
                KeyboardButton(
                    "💎 打开应用",
                    web_app=WebAppInfo(url=get_webapp_url())
                ),
                KeyboardButton(""),  # Empty button as placeholder
                KeyboardButton("")   # Empty button as placeholder
            ])
    else:
        # Private chat layout - 3 buttons per row
        keyboard = [
            [
                KeyboardButton("💱 汇率"),
                KeyboardButton("💰 结算"),
                KeyboardButton("📜 我的账单")
            ],
            [
                KeyboardButton("🔔 预警"),
                KeyboardButton("🔗 地址"),
                KeyboardButton("📞 客服")
            ]
        ]
        
        # Add admin buttons if admin (3 per row)
        if user_id and is_admin(user_id):
            keyboard.append([
                KeyboardButton("⚙️ 管理"),
                KeyboardButton("📊 数据"),
                KeyboardButton(
                    "💎 打开应用",
                    web_app=WebAppInfo(url=get_webapp_url())
                )
            ])
        else:
            # If not admin, add "打开应用" button in a row of 3
            keyboard.append([
                KeyboardButton(
                    "💎 打开应用",
                    web_app=WebAppInfo(url=get_webapp_url())
                ),
                KeyboardButton(""),  # Empty button as placeholder
                KeyboardButton("")   # Empty button as placeholder
            ])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="输入人民币金额或算式（如：20000-200）..."
    )

