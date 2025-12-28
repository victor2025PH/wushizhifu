"""
Message handlers for Bot B
Handles admin shortcuts and math/settlement processing
"""
import re
import logging
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from config import Config
from database import db
from services.price_service import get_price_with_markup
from services.settlement_service import calculate_settlement, format_settlement_bill
from services.math_service import is_number, is_simple_math

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """
    Check if user is admin.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is admin
    """
    # Check if user ID is in initial admins list
    return user_id in Config.INITIAL_ADMINS


async def handle_admin_w01(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w01: Get current CoinGecko price + Admin Markup"""
    try:
        final_price, error_msg, base_price = get_price_with_markup()
        admin_markup = db.get_admin_markup()
        
        if final_price is None:
            message = f"❌ 获取价格失败\n\n{error_msg or '未知错误'}"
        else:
            message = (
                f"💱 当前价格信息\n\n"
                f"📊 CoinGecko 基础价格: {base_price:.4f} CNY\n"
                f"➕ 管理员加价: {admin_markup:.4f} CNY\n"
                f"💰 最终价格: {final_price:.4f} CNY\n"
            )
            if error_msg:
                message += f"\n⚠️ 注意: {error_msg}"
        
        await update.message.reply_text(message)
        logger.info(f"Admin {update.effective_user.id} executed w01")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w01: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w02(update: Update, context: ContextTypes.DEFAULT_TYPE, markup_value: float):
    """Handle w02 [number]: Set admin_markup"""
    try:
        if db.set_admin_markup(markup_value):
            message = f"✅ 管理员加价已设置为: {markup_value:.4f} CNY"
        else:
            message = "❌ 设置失败"
        
        await update.message.reply_text(message)
        logger.info(f"Admin {update.effective_user.id} set markup to {markup_value}")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w02: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w03(update: Update, context: ContextTypes.DEFAULT_TYPE, markdown_value: float):
    """Handle w03 [number]: Set markdown (negative markup)"""
    try:
        # Markdown is negative markup
        markup_value = -abs(markdown_value)  # Ensure negative
        if db.set_admin_markup(markup_value):
            message = f"✅ 降价已设置为: {markup_value:.4f} CNY (加价: {markup_value:.4f} CNY)"
        else:
            message = "❌ 设置失败"
        
        await update.message.reply_text(message)
        logger.info(f"Admin {update.effective_user.id} set markdown to {markdown_value}")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w03: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w04(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w04: Get usdt_address"""
    try:
        usdt_address = db.get_usdt_address()
        
        if usdt_address:
            message = f"💼 USDT 收款地址:\n\n<code>{usdt_address}</code>"
        else:
            message = "⚠️ USDT 收款地址未设置"
        
        await update.message.reply_text(message, parse_mode="HTML")
        logger.info(f"Admin {update.effective_user.id} executed w04")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w04: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_admin_w08(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle w08: Reset markup to 0"""
    try:
        if db.set_admin_markup(0.0):
            message = "✅ 管理员加价已重置为 0"
        else:
            message = "❌ 重置失败"
        
        await update.message.reply_text(message)
        logger.info(f"Admin {update.effective_user.id} executed w08 (reset markup)")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_w08: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 错误: {str(e)}")


async def handle_math_settlement(update: Update, context: ContextTypes.DEFAULT_TYPE, amount_text: str):
    """Handle math expression and calculate settlement"""
    try:
        # Calculate settlement
        settlement_data, error_msg = calculate_settlement(amount_text)
        
        if settlement_data is None:
            await update.message.reply_text(f"❌ {error_msg}")
            return
        
        # Get USDT address
        from database import db
        usdt_address = db.get_usdt_address()
        
        # Format and send settlement bill
        bill_message = format_settlement_bill(settlement_data, usdt_address)
        
        # Add inline keyboard for confirmation
        from keyboards.inline_keyboard import get_settlement_bill_keyboard
        reply_markup = get_settlement_bill_keyboard()
        
        await update.message.reply_text(
            bill_message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        logger.info(f"User {update.effective_user.id} calculated settlement: {amount_text}")
        
    except Exception as e:
        logger.error(f"Error in handle_math_settlement: {e}", exc_info=True)
        await update.message.reply_text(f"❌ 计算错误: {str(e)}")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main message handler - processes all text messages
    Handles admin shortcuts, reply keyboard buttons, and math/settlement calculations
    """
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Handle reply keyboard buttons
    if text == "📊 查看汇率":
        # Same as w01 for admins, or just show price for regular users
        if is_admin(user_id):
            await handle_admin_w01(update, context)
        else:
            # Show price without markup details for regular users
            final_price, error_msg, base_price = get_price_with_markup()
            if final_price is None:
                message = f"❌ 获取价格失败\n\n{error_msg or '未知错误'}"
            else:
                message = f"💱 当前汇率: {final_price:.4f} CNY"
                if error_msg:
                    message += f"\n⚠️ 注意: {error_msg}"
            await update.message.reply_text(message)
        return
    
    if text == "🔗 收款地址":
        # Same as w04
        await handle_admin_w04(update, context)
        return
    
    if text == "📞 联系人工":
        contact_message = (
            "📞 <b>联系人工客服</b>\n\n"
            "如有任何问题，请联系管理员：\n"
            "@wushizhifu_jianglai\n\n"
            "或使用以下方式：\n"
            "• 工作时间：7×24小时\n"
            "• 响应时间：通常在5分钟内"
        )
        await update.message.reply_text(contact_message, parse_mode="HTML")
        return
    
    # Check for admin shortcuts (only for admins)
    if is_admin(user_id):
        # w01: Get price + markup
        if text == "w01":
            await handle_admin_w01(update, context)
            return
        
        # w02 [number]: Set markup
        w02_match = re.match(r'^w02\s+(-?\d+\.?\d*)$', text)
        if w02_match:
            try:
                markup_value = float(w02_match.group(1))
                await handle_admin_w02(update, context, markup_value)
                return
            except ValueError:
                await update.message.reply_text("❌ w02 格式错误，应为: w02 [数字]")
                return
        
        # w03 [number]: Set markdown (negative markup)
        w03_match = re.match(r'^w03\s+(\d+\.?\d*)$', text)
        if w03_match:
            try:
                markdown_value = float(w03_match.group(1))
                await handle_admin_w03(update, context, markdown_value)
                return
            except ValueError:
                await update.message.reply_text("❌ w03 格式错误，应为: w03 [数字]")
                return
        
        # w04: Get USDT address
        if text == "w04":
            await handle_admin_w04(update, context)
            return
        
        # w08: Reset markup
        if text == "w08":
            await handle_admin_w08(update, context)
            return
    
    # Check if message is a number or math expression
    if is_number(text) or is_simple_math(text):
        await handle_math_settlement(update, context, text)
        return
    
    # Otherwise, ignore the message (or handle as needed)


def get_message_handler():
    """Get message handler instance"""
    return MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)

