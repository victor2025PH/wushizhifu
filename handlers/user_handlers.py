"""
User interaction handlers for WuShiPay Telegram Bot
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.main_kb import get_main_keyboard
from services.user_service import UserService
from services.message_service import MessageService

# Create router for user handlers
user_router = Router()
logger = logging.getLogger(__name__)


@user_router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Handle /start command.
    Sends professional personalized welcome message.
    """
    try:
        user = message.from_user
        
        # Check if user is new
        is_new_user = UserService.is_new_user(user.id)
        
        # Generate professional welcome message
        welcome_text = MessageService.generate_welcome_message(user, is_new_user)
        
        # Send message
        await message.answer(
            text=welcome_text,
            parse_mode="MarkdownV2",
            reply_markup=get_main_keyboard()
        )
        
        # Log user interaction
        logger.info(f"User {user.id} ({user.username or 'no username'}) sent /start command (new: {is_new_user})")
        
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}", exc_info=True)
        await message.answer(
            "❌ 抱歉，系統暫時無法處理您的請求。請稍後再試或聯繫客服。"
        )


@user_router.callback_query(F.data == "pay_ali")
async def callback_pay_ali(callback: CallbackQuery):
    """Handle Alipay payment channel callback"""
    try:
        await callback.answer("正在啟動支付寶通道...", show_alert=False)
        # TODO: Implement Alipay payment flow
        logger.info(f"User {callback.from_user.id} selected Alipay payment channel")
    except Exception as e:
        logger.error(f"Error in callback_pay_ali: {e}", exc_info=True)
        await callback.answer("❌ 系統錯誤，請稍後再試", show_alert=True)


@user_router.callback_query(F.data == "pay_wechat")
async def callback_pay_wechat(callback: CallbackQuery):
    """Handle WeChat payment channel callback"""
    try:
        await callback.answer("正在啟動微信支付通道...", show_alert=False)
        # TODO: Implement WeChat payment flow
        logger.info(f"User {callback.from_user.id} selected WeChat payment channel")
    except Exception as e:
        logger.error(f"Error in callback_pay_wechat: {e}", exc_info=True)
        await callback.answer("❌ 系統錯誤，請稍後再試", show_alert=True)


@user_router.callback_query(F.data == "rates")
async def callback_rates(callback: CallbackQuery):
    """Handle rates information callback"""
    try:
        rates_text = MessageService.generate_rates_message()
        
        await callback.message.edit_text(
            text=rates_text,
            parse_mode="MarkdownV2",
            reply_markup=get_main_keyboard()
        )
        await callback.answer("費率信息已更新")
        
        logger.info(f"User {callback.from_user.id} requested rates information")
        
    except Exception as e:
        logger.error(f"Error in callback_rates: {e}", exc_info=True)
        await callback.answer("❌ 獲取費率信息失敗，請稍後再試", show_alert=True)


@user_router.callback_query(F.data == "statistics")
async def callback_statistics(callback: CallbackQuery):
    """Handle statistics callback"""
    try:
        from database.user_repository import UserRepository
        from database.transaction_repository import TransactionRepository
        from utils.text_utils import escape_markdown_v2
        
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        if user:
            total_trans = TransactionRepository.get_transaction_count(user_id)
            total_receive = TransactionRepository.get_transaction_count(user_id, "receive")
            total_pay = TransactionRepository.get_transaction_count(user_id, "pay")
            
            # Format amount - remove commas for MarkdownV2, or escape them
            total_amount = user.get('total_amount', 0) or 0
            amount_formatted = f"{total_amount:,.2f}".replace(',', '\\,')
            
            text = (
                f"*📊 我的統計*\n\n"
                f"總交易數：{total_trans}\n"
                f"收款次數：{total_receive}\n"
                f"付款次數：{total_pay}\n"
                f"VIP 等級：{user.get('vip_level', 0)}\n"
                f"累計交易額：¥{amount_formatted}\n\n"
                "更多統計功能開發中\\.\\.\\."
            )
        else:
            text = "*📊 我的統計*\n\n暫無數據"
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_statistics: {e}", exc_info=True)
        await callback.answer("❌ 獲取統計信息失敗，請稍後再試", show_alert=True)


@user_router.callback_query(F.data == "settings")
async def callback_settings(callback: CallbackQuery):
    """Handle settings callback"""
    try:
        from database.admin_repository import AdminRepository
        
        user_id = callback.from_user.id
        is_admin = AdminRepository.is_admin(user_id)
        
        text = (
            "*⚙️ 設置*\n\n"
            "功能開發中...\n\n"
        )
        
        if is_admin:
            text += "您擁有管理員權限，可使用 `\\/admin` 命令訪問管理面板"
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings: {e}", exc_info=True)
        await callback.answer("❌ 系統錯誤，請稍後再試", show_alert=True)

