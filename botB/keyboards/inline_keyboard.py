"""
Inline keyboard layouts for Bot B
"""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


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

