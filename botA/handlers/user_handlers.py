"""
User interaction handlers for WuShiPay Telegram Bot
"""
import asyncio
import logging
from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from config import Config
from keyboards.main_kb import get_main_keyboard
from services.user_service import UserService
from services.message_service import MessageService
from database.admin_repository import AdminRepository

# Create router for user handlers
user_router = Router()
logger = logging.getLogger(__name__)


@user_router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Handle /start command with progressive welcome experience.
    Implements step-by-step progressive display for enhanced UX.
    Also handles referral code from /start?ref=CODE
    """
    try:
        user = message.from_user
        
        # Check if user is new
        is_new_user = UserService.is_new_user(user.id)
        
        # Check for referral code in command args
        referral_code = None
        if message.text and len(message.text.split()) > 1:
            args = message.text.split()[1]
            if args.startswith("ref_"):
                referral_code = args[4:]  # Remove "ref_" prefix
        
        # Handle referral if code exists and user is new
        if referral_code and is_new_user:
            try:
                from database.referral_repository import ReferralRepository
                
                # Get referrer info
                code_info = ReferralRepository.get_referral_by_code(referral_code)
                if code_info:
                    referrer_id = code_info['user_id']
                    # Create referral relationship
                    ReferralRepository.create_referral(referrer_id, user.id, referral_code)
                    logger.info(f"User {user.id} registered via referral code {referral_code} from {referrer_id}")
            except Exception as e:
                logger.error(f"Error processing referral code: {e}", exc_info=True)
        
        # Check if user is admin
        is_admin = AdminRepository.is_admin(user.id)
        
        # === STEP 1: Send LOGO Image with transparent background ===
        logo_path = MessageService.get_logo_path()
        loading_msg = None
        
        if logo_path:
            try:
                # Send LOGO as photo to show transparent background properly
                logo_file = FSInputFile(logo_path)
                await message.answer_photo(
                    photo=logo_file
                )
                logger.info(f"Successfully sent LOGO from {logo_path}")
                
                # Send caption as separate message for cleaner look
                await asyncio.sleep(0.3)
                await message.answer(
                    text=MessageService.generate_logo_caption(),
                    parse_mode="MarkdownV2"
                )
            except Exception as e:
                logger.warning(f"Could not send logo image: {e}", exc_info=True)
        else:
            logger.warning("Logo file not found, skipping image step")
        
        # Delay before next step (1 second per block)
        await asyncio.sleep(1.0)
        
        # === STEP 2: Personalized Welcome Message ===
        try:
            welcome_card = MessageService.generate_welcome_card(user, is_new_user)
            await message.answer(
                text=welcome_card,
                parse_mode="MarkdownV2"
            )
        except Exception as e:
            logger.error(f"Error sending welcome card: {e}", exc_info=True)
        
        await asyncio.sleep(1.0)
        
        # === STEP 3: System Status Panel ===
        try:
            status_panel = MessageService.generate_system_status_panel()
            await message.answer(
                text=status_panel,
                parse_mode="MarkdownV2"
            )
        except Exception as e:
            logger.error(f"Error sending status panel: {e}", exc_info=True)
        
        await asyncio.sleep(1.0)
        
        # === STEP 4: Service Highlights (Direct Display) ===
        try:
            highlights = MessageService.generate_service_highlights()
            await message.answer(
                text=highlights,
                parse_mode="MarkdownV2"
            )
        except Exception as e:
            logger.error(f"Error sending highlights: {e}", exc_info=True)
        
        await asyncio.sleep(1.0)
        
        # === STEP 5: Exchange Rate Card ===
        try:
            rate_card = MessageService.generate_exchange_rate_card()
            await message.answer(
                text=rate_card,
                parse_mode="MarkdownV2"
            )
        except Exception as e:
            logger.error(f"Error sending rate card: {e}", exc_info=True)
        
        await asyncio.sleep(1.0)
        
        # === STEP 7: Action Prompt + Keyboard ===
        try:
            action_prompt = MessageService.generate_action_prompt()
            
            # Add referral welcome message if applicable
            if referral_code and is_new_user:
                action_prompt += "\n\n🎁 *您已通过好友邀请注册，首次交易可获得 5 USDT 红包\\!*"
            
            await message.answer(
                text=action_prompt,
                parse_mode="MarkdownV2",
                reply_markup=get_main_keyboard(user_id=user.id, is_admin=is_admin)
            )
        except Exception as e:
            logger.error(f"Error sending action prompt: {e}", exc_info=True)
        
        # Log user interaction
        logger.info(f"User {user.id} ({user.username or 'no username'}) sent /start command (new: {is_new_user}, ref: {referral_code or 'none'})")
        
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}", exc_info=True)
        try:
            await message.answer(
                "❌ 抱歉，系统暂时无法处理您的请求。请稍后再试或联系客服。"
            )
        except:
            pass


@user_router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Handle /help command.
    Provides usage instructions for the bot.
    """
    try:
        user = message.from_user
        is_admin = AdminRepository.is_admin(user.id)
        
        help_text = (
            "*📖 伍拾支付 Bot 使用指南*\n\n"
            "*主要功能：*\n"
            "• 💎 *启动收银台*：打开 MiniApp 主界面\n"
            "• 💳 *支付宝/微信支付*：选择支付通道\n"
            "• 📜 *交易记录*：查看历史交易\n"
            "• 🧮 *汇率计算器*：计算手续费和汇率\n"
            "• 💰 *我的钱包*：查看钱包信息\n"
            "• ⚙️ *个人设置*：账户设置\n"
            "• 📊 *统计信息*：查看交易统计\n"
            "• 💬 *客服支持*：联系人工客服\n"
            "• 🤖 *AI 助手*：智能客服助手\n\n"
        )
        
        if is_admin:
            help_text += "*管理员功能：*\n"
            help_text += "• ⚙️ *管理面板*：访问管理功能\n"
            help_text += "• `/admin`：打开管理面板\n\n"
        
        help_text += (
            "*常用命令：*\n"
            "• `/start` - 开始使用\n"
            "• `/help` - 显示帮助信息\n\n"
            "*提示：*\n"
            "点击「💎 启动伍拾收银台」按钮可快速打开 MiniApp\\。\n"
            "也可以点击聊天界面顶部的「打开应用」按钮\\。"
        )
        
        await message.answer(
            text=help_text,
            parse_mode="MarkdownV2",
            reply_markup=get_main_keyboard(user_id=user.id, is_admin=is_admin)
        )
        
        logger.info(f"User {user.id} ({user.username or 'no username'}) sent /help command")
        
    except Exception as e:
        logger.error(f"Error in cmd_help: {e}", exc_info=True)
        await message.answer("❌ 抱歉，无法显示帮助信息。请稍后再试。")


# 支付按鈕現在使用 web_app 跳轉到 MiniApp，不再需要這些回調


@user_router.callback_query(F.data == "rates")
async def callback_rates(callback: CallbackQuery):
    """Handle rates information callback"""
    try:
        rates_text = MessageService.generate_rates_message()
        
        is_admin = AdminRepository.is_admin(callback.from_user.id)
        
        await callback.message.edit_text(
            text=rates_text,
            parse_mode="MarkdownV2",
            reply_markup=get_main_keyboard(user_id=callback.from_user.id, is_admin=is_admin)
        )
        await callback.answer("費率信息已更新")
        
        logger.info(f"User {callback.from_user.id} requested rates information")
        
    except Exception as e:
        logger.error(f"Error in callback_rates: {e}", exc_info=True)
        await callback.answer("❌ 获取费率信息失败，请稍后再试", show_alert=True)


@user_router.callback_query(F.data == "statistics")
async def callback_statistics(callback: CallbackQuery):
    """Handle statistics callback"""
    try:
        from database.user_repository import UserRepository
        from database.transaction_repository import TransactionRepository
        from utils.text_utils import escape_markdown_v2, format_amount_markdown, format_number_markdown
        
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        if user:
            total_trans = TransactionRepository.get_transaction_count(user_id)
            total_receive = TransactionRepository.get_transaction_count(user_id, "receive")
            total_pay = TransactionRepository.get_transaction_count(user_id, "pay")
            
            total_amount_str = format_amount_markdown(user.get('total_amount', 0))
            total_trans_str = format_number_markdown(total_trans)
            total_receive_str = format_number_markdown(total_receive)
            total_pay_str = format_number_markdown(total_pay)
            vip_level_str = format_number_markdown(user.get('vip_level', 0))
            
            text = (
                f"*📊 我的统计*\n\n"
                f"总交易数：{total_trans_str}\n"
                f"收款次数：{total_receive_str}\n"
                f"付款次数：{total_pay_str}\n"
                f"VIP 等级：{vip_level_str}\n"
                f"累计交易额：{total_amount_str}\n\n"
                "更多统计功能开发中\\.\\.\\."
            )
        else:
            text = "*📊 我的統計*\n\n暫無數據"
        
        # Get admin status for keyboard
        is_admin = AdminRepository.is_admin(callback.from_user.id)
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_main_keyboard(user_id=callback.from_user.id, is_admin=is_admin)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_statistics: {e}", exc_info=True)
        await callback.answer("❌ 获取统计信息失败，请稍后再试", show_alert=True)


# Settings callback moved to settings_handlers.py to avoid conflicts

