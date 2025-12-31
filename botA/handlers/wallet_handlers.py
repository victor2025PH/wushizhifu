"""
Wallet-related handlers
"""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from keyboards.main_kb import get_main_keyboard
from database.admin_repository import AdminRepository
from database.user_repository import UserRepository
from database.transaction_repository import TransactionRepository
from services.transaction_service import TransactionService
from database.db import db
from utils.text_utils import escape_markdown_v2, format_amount_markdown, format_number_markdown, format_separator, format_datetime_markdown

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "wallet")
async def callback_wallet(callback: CallbackQuery):
    """Handle wallet menu"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        user_id = callback.from_user.id
        
        # Get user info
        user = UserRepository.get_user(user_id)
        if not user:
            await callback.answer("❌ 用户信息不存在", show_alert=True)
            return
        
        # Calculate balance from transactions (if balance field doesn't exist)
        # For now, we'll calculate from completed transactions
        cursor = db.execute("""
            SELECT transaction_type, actual_amount 
            FROM transactions 
            WHERE user_id = ? AND status = 'paid'
        """, (user_id,))
        transactions = cursor.fetchall()
        
        balance = 0.0
        for trans in transactions:
            if trans['transaction_type'] == 'receive':
                balance += float(trans['actual_amount'])
            elif trans['transaction_type'] == 'pay':
                balance -= float(trans['actual_amount'])
        
        # Get today's statistics
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = db.execute("""
            SELECT transaction_type, actual_amount 
            FROM transactions 
            WHERE user_id = ? AND status = 'paid' 
            AND DATE(created_at) = DATE('now')
        """, (user_id,))
        today_transactions = cursor.fetchall()
        
        today_receive = sum(float(t['actual_amount']) for t in today_transactions 
                           if t['transaction_type'] == 'receive')
        today_pay = sum(float(t['actual_amount']) for t in today_transactions 
                       if t['transaction_type'] == 'pay')
        
        balance_str = format_number_markdown(balance, 2)
        today_receive_str = format_amount_markdown(today_receive)
        today_pay_str = format_number_markdown(today_pay, 2)
        total_transactions = format_number_markdown(user.get('total_transactions', 0))
        total_amount_str = format_amount_markdown(user.get('total_amount', 0))
        separator = format_separator(30)
        
        text = (
            "*💰 我的钱包*\n\n"
            f"总余额：`{balance_str}` USDT\n"
            f"可用余额：`{balance_str}` USDT\n"
            f"冻结余额：`0\\.00` USDT\n\n"
            f"{separator}\n"
            "*今日统计*\n"
            f"{separator}\n"
            f"💳 充值：{today_receive_str}\n"
            f"📤 提现：`{today_pay_str}` USDT\n\n"
            f"📊 累计交易：{total_transactions} 笔\n"
            f"💰 累计金额：{total_amount_str}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 充值", callback_data="wallet_deposit"),
                InlineKeyboardButton(text="📤 提现", callback_data="wallet_withdraw")
            ],
            [
                InlineKeyboardButton(text="📜 交易记录", callback_data="transactions"),
                InlineKeyboardButton(text="📊 钱包明细", callback_data="wallet_details")
            ],
            [
                InlineKeyboardButton(text="🔙 返回主菜单", callback_data="main_menu")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_wallet: {e}", exc_info=True)
        await callback.answer("❌ 获取钱包信息失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "wallet_deposit")
async def callback_wallet_deposit(callback: CallbackQuery):
    """Handle wallet deposit"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        text = (
            "*💳 充值*\n\n"
            "请选择支付通道："
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 支付宝充值", callback_data="pay_ali"),
                InlineKeyboardButton(text="🍀 微信充值", callback_data="pay_wechat")
            ],
            [
                InlineKeyboardButton(text="🔙 返回钱包", callback_data="wallet")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_wallet_deposit: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "wallet_withdraw")
async def callback_wallet_withdraw(callback: CallbackQuery):
    """Handle wallet withdraw"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        # Calculate balance
        cursor = db.execute("""
            SELECT transaction_type, actual_amount 
            FROM transactions 
            WHERE user_id = ? AND status = 'paid'
        """, (user_id,))
        transactions = cursor.fetchall()
        
        balance = sum(float(t['actual_amount']) for t in transactions 
                     if t['transaction_type'] == 'receive')
        balance -= sum(float(t['actual_amount']) for t in transactions 
                      if t['transaction_type'] == 'pay')
        
        balance_str = format_number_markdown(balance, 2)
        
        if balance <= 0:
            text = (
                "*📤 提现*\n\n"
                "❌ 余额不足，无法提现\n\n"
                f"当前余额：`{balance_str}` USDT"
            )
        else:
            text = (
                "*📤 提现*\n\n"
                f"当前可用余额：`{balance_str}` USDT\n\n"
                "请输入提现金额（USDT）：\n"
                "最小提现金额：10 USDT\n"
                "最大提现金额：无限制"
            )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回钱包", callback_data="wallet")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_wallet_withdraw: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "wallet_details")
async def callback_wallet_details(callback: CallbackQuery):
    """Handle wallet details with enhanced display"""
    # Skip if callback is from a group (Bot A should be silent in groups)
    if callback.message.chat.type in ['group', 'supergroup']:
        await callback.answer()
        return
    
    try:
        user_id = callback.from_user.id
        
        # Get user info
        user = UserRepository.get_user(user_id)
        if not user:
            await callback.answer("❌ 用户信息不存在", show_alert=True)
            return
        
        # Calculate balance and today's statistics
        cursor = db.execute("""
            SELECT transaction_type, actual_amount 
            FROM transactions 
            WHERE user_id = ? AND status = 'paid'
        """, (user_id,))
        all_transactions = cursor.fetchall()
        
        balance = 0.0
        for trans in all_transactions:
            if trans['transaction_type'] == 'receive':
                balance += float(trans['actual_amount'])
            elif trans['transaction_type'] == 'pay':
                balance -= float(trans['actual_amount'])
        
        # Get today's statistics
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = db.execute("""
            SELECT transaction_type, actual_amount 
            FROM transactions 
            WHERE user_id = ? AND status = 'paid' 
            AND DATE(created_at) = DATE('now')
        """, (user_id,))
        today_transactions = cursor.fetchall()
        
        today_receive = sum(float(t['actual_amount']) for t in today_transactions 
                           if t['transaction_type'] == 'receive')
        today_pay = sum(float(t['actual_amount']) for t in today_transactions 
                       if t['transaction_type'] == 'pay')
        
        # Get recent transactions
        transactions = TransactionRepository.get_user_transactions(user_id, limit=10)
        
        # Build header with account overview
        separator = format_separator(30)
        balance_str = format_amount_markdown(balance, currency="USDT")
        today_receive_str = format_amount_markdown(today_receive)
        today_pay_str = format_amount_markdown(today_pay, currency="USDT")
        
        if not transactions:
            text = (
                f"{separator}\n"
                f"  *📊 钱包明细*\n"
                f"{separator}\n\n"
                
                f"*💎 账户概览*\n"
                f"{separator}\n"
                f"💰 *当前余额*：{balance_str}\n"
                f"📈 *今日收入*：{today_receive_str}\n"
                f"📉 *今日支出*：{today_pay_str}\n\n"
                
                f"{separator}\n\n"
                f"*📋 交易记录*\n"
                f"{separator}\n\n"
                f"暂无交易记录\n\n"
                f"开始您的第一笔交易吧！💫"
            )
        else:
            text = (
                f"{separator}\n"
                f"  *📊 钱包明细*\n"
                f"{separator}\n\n"
                
                f"*💎 账户概览*\n"
                f"{separator}\n"
                f"💰 *当前余额*：{balance_str}\n"
                f"📈 *今日收入*：{today_receive_str}\n"
                f"📉 *今日支出*：{today_pay_str}\n\n"
                
                f"*📋 最近交易记录*\n"
                f"{separator}\n\n"
            )
            
            for trans in transactions[:10]:
                status_icon = "✅" if trans['status'] == 'paid' else "⏳" if trans['status'] == 'pending' else "❌"
                type_icon = "💳" if trans['transaction_type'] == 'receive' else "📤"
                
                # Fix: Properly escape the amount sign
                amount_sign = "+" if trans['transaction_type'] == 'receive' else "-"
                amount_sign_escaped = escape_markdown_v2(amount_sign)
                
                amount_str = format_amount_markdown(trans['actual_amount'])
                order_id_short = escape_markdown_v2(trans['order_id'][:16] + "...")
                
                # Fix: Use format_datetime_markdown for proper date formatting
                created_at_formatted = format_datetime_markdown(trans['created_at'])
                
                text += (
                    f"{status_icon} {type_icon} {amount_sign_escaped}{amount_str}\n"
                    f"   {created_at_formatted} \\| `{order_id_short}`\n\n"
                )
            
            if len(transactions) >= 10:
                text += f"\n_显示最近 10 笔交易，查看全部记录请点击下方按钮_"
        
        # Add update timestamp to ensure content changes on refresh
        current_time = datetime.now().strftime('%m-%d %H:%M:%S')
        time_stamp = escape_markdown_v2(f"最后更新：{current_time}")
        text += f"\n\n{separator}\n{time_stamp}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📜 查看全部记录", callback_data="transactions"),
                InlineKeyboardButton(text="🔄 刷新", callback_data="wallet_details")
            ],
            [
                InlineKeyboardButton(text="🔙 返回钱包", callback_data="wallet")
            ]
        ])
        
        # Give feedback when refreshing
        await callback.answer("🔄 刷新中...")
        
        try:
            await callback.message.edit_text(
                text=text,
                parse_mode="MarkdownV2",
                reply_markup=keyboard
            )
        except TelegramBadRequest as e:
            # Handle "message is not modified" error gracefully
            if "message is not modified" in str(e).lower():
                await callback.answer("✅ 数据已是最新", show_alert=False)
                logger.debug(f"Message not modified (expected when content unchanged): {e}")
            else:
                # Re-raise other TelegramBadRequest errors
                raise
        
    except Exception as e:
        logger.error(f"Error in callback_wallet_details: {e}", exc_info=True)
        await callback.answer("❌ 获取钱包明细失败，请稍后再试", show_alert=True)

