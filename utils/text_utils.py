"""
Text utilities for message formatting and escaping
"""
import re


def escape_markdown_v2(text: str) -> str:
    """
    Escape special characters for MarkdownV2 format.
    Characters that need escaping: _ * [ ] ( ) ~ ` > # + - = | { } . !
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for MarkdownV2
    """
    if not text:
        return ""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    escaped = ""
    for char in text:
        if char in special_chars:
            escaped += "\\" + char
        else:
            escaped += char
    return escaped


def get_user_display_name(user) -> str:
    """
    Get user's display name for greeting.
    Priority: first_name + last_name > first_name > username > "尊貴的客戶"
    
    Args:
        user: Telegram User object
        
    Returns:
        Escaped display name for MarkdownV2
    """
    if user.first_name:
        name = user.first_name
        if user.last_name:
            name += " " + user.last_name
        return escape_markdown_v2(name)
    elif user.username:
        return escape_markdown_v2(user.username)
    else:
        return "尊貴的客戶"


def format_user_info(user) -> dict:
    """
    Format user information into a structured dict.
    
    Args:
        user: Telegram User object
        
    Returns:
        Dictionary with formatted user information
    """
    return {
        "id": user.id,
        "username": user.username if user.username else None,
        "first_name": user.first_name if user.first_name else None,
        "last_name": user.last_name if user.last_name else None,
        "full_name": f"{user.first_name} {user.last_name}".strip() if user.first_name else None,
        "display_name": get_user_display_name(user),
        "is_premium": getattr(user, "is_premium", False),
        "language_code": getattr(user, "language_code", None)
    }

