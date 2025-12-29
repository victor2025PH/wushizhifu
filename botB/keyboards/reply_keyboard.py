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
        import logging
        logger = logging.getLogger(__name__)
        
        if user_info and user_info.get('id'):
            user_id_value = user_info.get('id')
            # Convert to string and validate
            if user_id_value and str(user_id_value).strip() and str(user_id_value) != 'None':
                # Build parameters - only include non-empty values
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
                
                # URL encode parameters
                if params.get('user_id'):
                    param_string = urlencode(params, doseq=False)
                    final_url = f"{base_url}&{param_string}"
                    logger.info(f"✅ Generated WebApp URL with user params: user_id={params.get('user_id')}, first_name={params.get('first_name', 'N/A')}, url_length={len(final_url)}")
                    logger.debug(f"Full URL: {final_url}")
                    return final_url
                else:
                    logger.warning(f"⚠️ user_id is empty after processing. user_info={user_info}")
        else:
            logger.warning(f"⚠️ WebApp URL generated without user_info. user_info={user_info}, user_id={user_id}")
        
        logger.info(f"Using base URL without user params: {base_url}")
        return base_url
    
    # Use the same layout for both group and private chat
    # Group and private chat layout - 3 buttons per row (unified)
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
    # IMPORTANT: WebApp buttons are NOT allowed in group chats by Telegram API
    # So we only add them in private chats, or remove them in groups
    if user_id and is_admin(user_id):
        # Use different button labels based on chat type for clarity
        admin_button_text = "⚙️ 设置" if is_group else "⚙️ 管理"
        stats_button_text = "📈 统计" if is_group else "📊 数据"
        
        if is_group:
            # In groups, don't use WebApp button - Telegram API doesn't allow it
            keyboard.append([
                KeyboardButton(admin_button_text),
                KeyboardButton(stats_button_text),
                KeyboardButton("")  # Empty placeholder since WebApp button not allowed
            ])
        else:
            # In private chats, WebApp button is allowed
            keyboard.append([
                KeyboardButton(admin_button_text),
                KeyboardButton(stats_button_text),
                KeyboardButton(
                    "💎 打开应用",
                    web_app=WebAppInfo(url=get_webapp_url())
                )
            ])
    else:
        # If not admin, handle based on chat type
        if is_group:
            # In groups, don't add WebApp button - just add empty row or skip
            # Or add a regular button as alternative
            keyboard.append([
                KeyboardButton(""),  # Empty button as placeholder
                KeyboardButton(""),  # Empty button as placeholder
                KeyboardButton("")   # Empty button as placeholder
            ])
        else:
            # In private chats, WebApp button is allowed
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

