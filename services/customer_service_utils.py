"""
Customer Service Utility Functions (Shared)
Helper functions for customer service features
"""
from typing import Optional
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup as AiogramInlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton as AiogramInlineKeyboardButton


def get_customer_service_contact_keyboard(service_account: str, use_aiogram: bool = False) -> InlineKeyboardMarkup:
    """
    Get inline keyboard for contacting a specific customer service.
    
    Args:
        service_account: Customer service username (without @)
        use_aiogram: If True, return aiogram types; if False, return python-telegram-bot types
        
    Returns:
        InlineKeyboardMarkup with contact button
    """
    if use_aiogram:
        keyboard = [
            [AiogramInlineKeyboardButton(
                text=f"💬 联系客服 @{service_account}",
                url=f"https://t.me/{service_account}"
            )]
        ]
        return AiogramInlineKeyboardMarkup(inline_keyboard=keyboard)
    else:
        keyboard = [
            [InlineKeyboardButton(
                text=f"💬 联系客服 @{service_account}",
                url=f"https://t.me/{service_account}"
            )]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
