"""
QR Code generator utility for USDT addresses
"""
import io
import logging
from typing import Optional
from telegram import Bot

logger = logging.getLogger(__name__)

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    logger.warning("qrcode library not available. QR code generation will be disabled.")


async def generate_and_send_qr_code(bot: Bot, chat_id: int, address: str, caption: str = None) -> Optional[str]:
    """
    Generate QR code for address and send it to Telegram.
    Returns the file_id of the sent photo for caching.
    
    Args:
        bot: Telegram Bot instance
        chat_id: Chat ID to send QR code to
        address: USDT address to encode in QR code
        caption: Optional caption for the photo
        
    Returns:
        file_id of the sent photo, or None if failed
    """
    if not QRCODE_AVAILABLE:
        logger.error("qrcode library not available, cannot generate QR code")
        return None
    
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(address)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Send to Telegram
        message = await bot.send_photo(
            chat_id=chat_id,
            photo=img_bytes,
            caption=caption,
            parse_mode="HTML" if caption else None
        )
        
        # Get file_id from the sent photo
        if message.photo:
            file_id = message.photo[-1].file_id  # Get largest photo
            logger.info(f"QR code generated and sent for address: {address[:20]}...")
            return file_id
        
        return None
        
    except Exception as e:
        logger.error(f"Error generating QR code: {e}", exc_info=True)
        return None


def generate_qr_code_bytes(address: str) -> Optional[io.BytesIO]:
    """
    Generate QR code image as BytesIO object.
    
    Args:
        address: USDT address to encode in QR code
        
    Returns:
        BytesIO object with PNG image, or None if failed
    """
    if not QRCODE_AVAILABLE:
        logger.error("qrcode library not available, cannot generate QR code")
        return None
    
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(address)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
        
    except Exception as e:
        logger.error(f"Error generating QR code bytes: {e}", exc_info=True)
        return None
