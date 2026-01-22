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
    
    # Optimized layout - prioritize most used features
    # Row 1: Most used - Rate query (prominent)
    # Row 2: Transaction related
    # Row 3: Support
    # Row 4: Admin (if applicable)
    
    keyboard = [
        # Row 1: Most used feature - prominent
        [
            KeyboardButton("💱 查匯率")
        ],
        # Row 2: Transaction related features
        [
            KeyboardButton("💰 結算"),
            KeyboardButton("📜 我的賬單"),
            KeyboardButton("🔗 地址")
        ],
        # Row 3: Support
        [
            KeyboardButton("📞 聯繫客服")
        ]
    ]
    
    # Add admin buttons and WebApp button if needed
    # IMPORTANT: WebApp buttons are NOT allowed in group chats by Telegram API
    # So we only add them in private chats, or remove them in groups
    if user_id and is_admin(user_id):
        admin_button_text = "⚙️ 群組設置" if is_group else "⚙️ 管理後台"
        
        # In private chat, add WebApp button
        if not is_group:
            # Add WebApp button to support row
            keyboard[2].append(KeyboardButton(
                "💎 打開應用",
                web_app=WebAppInfo(url=get_webapp_url())
            ))
        
        # Add admin button in separate row
        keyboard.append([
            KeyboardButton(admin_button_text)
        ])
    else:
        # Non-admin users
        if not is_group:
            # In private chats, add WebApp button to support row
            keyboard[2].append(KeyboardButton(
                "💎 打開應用",
                web_app=WebAppInfo(url=get_webapp_url())
            ))
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="輸入人民幣金額開始結算（如：10000 或 20000-200）"
    )

