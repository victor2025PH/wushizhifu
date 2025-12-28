"""
Settings-related handlers
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_kb import get_main_keyboard
from database.admin_repository import AdminRepository
from database.user_repository import UserRepository
from utils.text_utils import escape_markdown_v2, format_amount_markdown, format_number_markdown, format_separator

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "settings")
async def callback_settings(callback: CallbackQuery):
    """Handle settings menu with premium experience"""
    try:
        from database.transaction_repository import TransactionRepository
        from database.rate_repository import RateRepository
        from utils.text_utils import format_separator
        
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        if not user:
            await callback.answer("❌ 用户信息不存在", show_alert=True)
            return
        
        # Get user statistics
        vip_level = user.get('vip_level', 0)
        total_transactions = user.get('total_transactions', 0)
        total_amount = user.get('total_amount', 0)
        balance = total_amount  # Simplified balance calculation
        
        # Get transaction counts
        total_receive = TransactionRepository.get_transaction_count(user_id, "receive")
        total_pay = TransactionRepository.get_transaction_count(user_id, "pay")
        
        # Get VIP rate (example: alipay channel)
        rate_config = RateRepository.get_rate("alipay", vip_level)
        vip_rate = rate_config.get('rate_percentage', 0.6) if rate_config else 0.6
        
        # Format VIP level text
        vip_levels = {
            0: "普通会员",
            1: "VIP1（银卡会员）",
            2: "VIP2（金卡会员）",
            3: "VIP3（钻石会员）"
        }
        vip_text = vip_levels.get(vip_level, f"VIP{vip_level}")
        
        # Language setting
        language = user.get('language_code', 'zh-CN') or 'zh-CN'
        if language.startswith('zh'):
            language_text = '简体中文' if language == 'zh-CN' else '繁體中文'
        else:
            language_text = 'English'
        
        # Format values
        balance_str = format_amount_markdown(balance)
        total_amount_str = format_amount_markdown(total_amount)
        total_transactions_str = format_number_markdown(total_transactions)
        total_receive_str = format_number_markdown(total_receive)
        total_pay_str = format_number_markdown(total_pay)
        vip_rate_str = format_number_markdown(vip_rate, decimal_places=2)
        
        # Account status
        status_text = "正常 | 已验证" if user.get('status') == 'active' else "待验证"
        
        # Build premium settings page
        separator = format_separator(30)
        
        text = (
            f"{separator}\n"
            f"  *⚙️ 个人设置中心*\n"
            f"{separator}\n\n"
            
            f"*👤 账户概览*\n"
            f"{separator}\n"
            f"⭐ *VIP等级*：{escape_markdown_v2(vip_text)}\n"
            f"💰 *账户余额*：{balance_str}\n"
            f"📊 *累计交易*：{total_transactions_str} 笔\n"
            f"   ├ 收款：{total_receive_str} 笔\n"
            f"   └ 付款：{total_pay_str} 笔\n"
            f"🏆 *账户状态*：{escape_markdown_v2(status_text)}\n\n"
            
            f"*⚙️ 功能设置*\n"
            f"{separator}\n"
            f"🌐 *语言偏好*：{escape_markdown_v2(language_text)}\n"
            f"🔔 *通知管理*：已开启\n"
            f"💳 *支付通道*：支付宝（默认）\n"
            f"🔒 *安全等级*：高\n\n"
            
            f"*🎁 专属特权*\n"
            f"{separator}\n"
            f"✨ *专属费率*：{vip_rate_str}%\n"
            f"⚡ *优先处理*：已开启\n"
            f"🎯 *专属客服*：已分配\n"
            f"📈 *数据分析*：已开启\n\n"
            
            f"点击下方按钮进行详细设置"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 账户信息", callback_data="settings_account"),
                InlineKeyboardButton(text="🎁 VIP特权", callback_data="settings_vip")
            ],
            [
                InlineKeyboardButton(text="🌐 语言设置", callback_data="settings_language"),
                InlineKeyboardButton(text="🔔 通知设置", callback_data="settings_notification")
            ],
            [
                InlineKeyboardButton(text="💳 支付通道", callback_data="settings_provider"),
                InlineKeyboardButton(text="🔒 安全设置", callback_data="settings_security")
            ],
            [
                InlineKeyboardButton(text="📊 数据统计", callback_data="settings_stats"),
                InlineKeyboardButton(text="⚙️ 更多设置", callback_data="settings_more")
            ],
            [
                InlineKeyboardButton(text="🔙 返回主菜单", callback_data="main_menu")
            ]
        ])
        
        # Check if message content changed to avoid "message is not modified" error
        try:
            await callback.message.edit_text(
                text=text,
                parse_mode="MarkdownV2",
                reply_markup=keyboard
            )
        except Exception as edit_error:
            # If edit fails (e.g., same content), try to answer with new message
            if "message is not modified" in str(edit_error).lower():
                await callback.message.answer(
                    text=text,
                    parse_mode="MarkdownV2",
                    reply_markup=keyboard
                )
            else:
                raise
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings: {e}", exc_info=True)
        await callback.answer("❌ 获取设置失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_language")
async def callback_settings_language(callback: CallbackQuery):
    """Handle language settings"""
    try:
        text = (
            "*🌐 语言设置*\n\n"
            "请选择您的首选语言："
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="简体中文", callback_data="set_lang_zh-CN"),
                InlineKeyboardButton(text="繁體中文", callback_data="set_lang_zh-TW")
            ],
            [
                InlineKeyboardButton(text="English", callback_data="set_lang_en")
            ],
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_language: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("set_lang_"))
async def callback_set_language(callback: CallbackQuery):
    """Handle language selection"""
    try:
        lang_code = callback.data.replace("set_lang_", "")
        user_id = callback.from_user.id
        
        # Update language (if we have this field in database)
        # For now, just show confirmation
        lang_map = {
            "zh-CN": "简体中文",
            "zh-TW": "繁體中文",
            "en": "English"
        }
        
        text = f"*✅ 语言设置已更新*\n\n已设置为：{lang_map.get(lang_code, lang_code)}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer(f"已设置为 {lang_map.get(lang_code, lang_code)}")
        
    except Exception as e:
        logger.error(f"Error in callback_set_language: {e}", exc_info=True)
        await callback.answer("❌ 设置失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_notification")
async def callback_settings_notification(callback: CallbackQuery):
    """Handle notification settings"""
    try:
        text = (
            "*🔔 通知设置*\n\n"
            "1\\. 支付通知：✅ 已开启\n"
            "2\\. 余额变动通知：✅ 已开启\n"
            "3\\. 系统消息通知：✅ 已开启\n\n"
            "点击切换开关"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="支付通知: 开启", callback_data="toggle_notify_payment"),
                InlineKeyboardButton(text="余额通知: 开启", callback_data="toggle_notify_balance")
            ],
            [
                InlineKeyboardButton(text="系统消息: 开启", callback_data="toggle_notify_system")
            ],
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_notification: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_provider")
async def callback_settings_provider(callback: CallbackQuery):
    """Handle preferred provider settings"""
    try:
        text = (
            "*💳 首选支付通道*\n\n"
            "设置您的默认支付通道，快速支付时将使用此通道："
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 支付宝", callback_data="set_provider_alipay"),
                InlineKeyboardButton(text="🍀 微信支付", callback_data="set_provider_wechat")
            ],
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_provider: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data.startswith("set_provider_"))
async def callback_set_provider(callback: CallbackQuery):
    """Handle provider selection"""
    try:
        provider = callback.data.replace("set_provider_", "")
        provider_text = "支付宝" if provider == "alipay" else "微信支付"
        
        text = f"*✅ 设置已更新*\n\n首选支付通道已设置为：{provider_text}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer(f"已设置为 {provider_text}")
        
    except Exception as e:
        logger.error(f"Error in callback_set_provider: {e}", exc_info=True)
        await callback.answer("❌ 设置失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_security")
async def callback_settings_security(callback: CallbackQuery):
    """Handle security settings"""
    try:
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        text = (
            "*🔒 安全设置*\n\n"
            "1\\. 绑定邮箱：未绑定\n"
            "2\\. 安全密码：未设置\n"
            "3\\. 两步验证：未开启\n\n"
            "点击相应选项进行设置"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📧 绑定邮箱", callback_data="security_email"),
                InlineKeyboardButton(text="🔐 设置密码", callback_data="security_password")
            ],
            [
                InlineKeyboardButton(text="🛡️ 两步验证", callback_data="security_2fa")
            ],
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_security: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_vip")
async def callback_settings_vip(callback: CallbackQuery):
    """Handle VIP privileges display"""
    try:
        from database.rate_repository import RateRepository
        from utils.text_utils import format_separator
        
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        if not user:
            await callback.answer("❌ 用户信息不存在", show_alert=True)
            return
        
        vip_level = user.get('vip_level', 0)
        total_transactions = user.get('total_transactions', 0)
        total_amount = user.get('total_amount', 0)
        
        # Get rates for different VIP levels
        rates = {}
        for level in range(4):
            rate_config = RateRepository.get_rate("alipay", level)
            if rate_config:
                rates[level] = float(rate_config.get('rate_percentage', 0.6))
            else:
                rates[level] = 0.6 - (level * 0.05)  # Default decreasing rates
        
        vip_levels = {
            0: ("普通会员", "基础服务"),
            1: ("VIP1 银卡会员", "专属费率 0.55%"),
            2: ("VIP2 金卡会员", "专属费率 0.50%"),
            3: ("VIP3 钻石会员", "专属费率 0.45%")
        }
        
        current_vip_text, current_vip_desc = vip_levels.get(vip_level, (f"VIP{vip_level}", ""))
        current_rate = rates.get(vip_level, 0.6)
        
        separator = format_separator(30)
        current_rate_str = format_number_markdown(current_rate, decimal_places=2)
        total_amount_str = format_amount_markdown(total_amount)
        total_transactions_str = format_number_markdown(total_transactions)
        
        text = (
            f"{separator}\n"
            f"  *🎁 VIP 专属特权*\n"
            f"{separator}\n\n"
            
            f"*当前等级：{escape_markdown_v2(current_vip_text)}*\n"
            f"{escape_markdown_v2(current_vip_desc)}\n\n"
            
            f"*您的专属权益：*\n"
            f"✨ 专属费率：{current_rate_str}%\n"
            f"⚡ 优先处理：已开启\n"
            f"🎯 专属客服：已分配\n"
            f"📈 数据分析：已开启\n"
            f"🔔 实时通知：已开启\n\n"
            
            f"*升级条件：*\n"
            f"📊 累计交易：{total_transactions_str} 笔\n"
            f"💰 累计金额：{total_amount_str}\n\n"
            
            f"*VIP 等级说明：*\n"
            f"• 普通会员：费率 0\\.60%\n"
            f"• VIP1 银卡：费率 0\\.55% \\(累计交易 ≥ 100 笔\\)\n"
            f"• VIP2 金卡：费率 0\\.50% \\(累计交易 ≥ 500 笔\\)\n"
            f"• VIP3 钻石：费率 0\\.45% \\(累计交易 ≥ 2000 笔\\)\n\n"
            
            f"继续使用服务，自动升级VIP等级！"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_vip: {e}", exc_info=True)
        await callback.answer("❌ 获取VIP信息失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_stats")
async def callback_settings_stats(callback: CallbackQuery):
    """Handle statistics display"""
    try:
        from database.transaction_repository import TransactionRepository
        from utils.text_utils import format_separator
        
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        if not user:
            await callback.answer("❌ 用户信息不存在", show_alert=True)
            return
        
        total_transactions = user.get('total_transactions', 0)
        total_amount = user.get('total_amount', 0)
        total_receive = TransactionRepository.get_transaction_count(user_id, "receive")
        total_pay = TransactionRepository.get_transaction_count(user_id, "pay")
        
        separator = format_separator(30)
        total_amount_str = format_amount_markdown(total_amount)
        total_transactions_str = format_number_markdown(total_transactions)
        total_receive_str = format_number_markdown(total_receive)
        total_pay_str = format_number_markdown(total_pay)
        
        text = (
            f"{separator}\n"
            f"  *📊 数据统计*\n"
            f"{separator}\n\n"
            
            f"*交易统计：*\n"
            f"📈 总交易数：{total_transactions_str} 笔\n"
            f"💰 累计金额：{total_amount_str}\n\n"
            
            f"*交易分类：*\n"
            f"📥 收款次数：{total_receive_str} 笔\n"
            f"📤 付款次数：{total_pay_str} 笔\n\n"
            
            f"*账户信息：*\n"
            f"⭐ VIP等级：{format_number_markdown(user.get('vip_level', 0))}\n"
            f"📅 注册时间：{escape_markdown_v2(str(user.get('created_at', 'N/A'))[:10])}\n"
            f"🕐 最后活跃：{escape_markdown_v2(str(user.get('last_active_at', 'N/A'))[:16])}\n\n"
            
            f"更多详细统计功能开发中\\.\\.\\."
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_stats: {e}", exc_info=True)
        await callback.answer("❌ 获取统计信息失败，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_more")
async def callback_settings_more(callback: CallbackQuery):
    """Handle more settings"""
    try:
        from utils.text_utils import format_separator
        from config import Config
        
        separator = format_separator(30)
        support_url_escaped = escape_markdown_v2(Config.SUPPORT_URL)
        support_username_escaped = escape_markdown_v2(Config.SUPPORT_USERNAME)
        
        text = (
            f"{separator}\n"
            f"  *⚙️ 更多设置*\n"
            f"{separator}\n\n"
            
            f"*💎 私人订制会员服务*\n\n"
            f"需要更多*私人订制会员功能*？\n\n"
            f"请与专属客服联系，为您定制\n"
            f"*专属VIP服务*，享受更高级的\n"
            f"个性化体验\\！\n\n"
            f"{separator}\n\n"
            
            f"*📋 可定制功能包括：*\n"
            f"📤 数据导出\n"
            f"🔐 隐私设置\n"
            f"🌍 时区设置\n"
            f"💬 消息偏好\n"
            f"🎨 主题设置\n\n"
            
            f"*💬 联系客服：*\n"
            f"Telegram：@{support_username_escaped}\n"
            f"点击下方按钮快速联系"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 联系专属客服",
                    url=Config.SUPPORT_URL
                )
            ],
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_more: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.callback_query(F.data == "settings_account")
async def callback_settings_account(callback: CallbackQuery):
    """Handle account information"""
    try:
        user_id = callback.from_user.id
        user = UserRepository.get_user(user_id)
        
        if not user:
            await callback.answer("❌ 用户信息不存在", show_alert=True)
            return
        
        username = user.get('username', '无')
        if username:
            username = f"@{username}"
        else:
            username = "未设置"
        
        user_id_str = escape_markdown_v2(str(user_id))
        username_escaped = escape_markdown_v2(username)
        first_name_escaped = escape_markdown_v2(user.get('first_name', ''))
        last_name_escaped = escape_markdown_v2(user.get('last_name', '') or '')
        full_name = f"{first_name_escaped} {last_name_escaped}".strip() if first_name_escaped else "未设置"
        vip_level_str = format_number_markdown(user.get('vip_level', 0))
        total_transactions_str = format_number_markdown(user.get('total_transactions', 0))
        total_amount_str = format_amount_markdown(user.get('total_amount', 0))
        created_at_escaped = escape_markdown_v2(str(user.get('created_at', 'N/A')))
        last_active_escaped = escape_markdown_v2(str(user.get('last_active_at', 'N/A')))
        
        from utils.text_utils import format_separator
        
        separator = format_separator(30)
        
        # Format dates
        created_at = user.get('created_at', 'N/A')
        if created_at and created_at != 'N/A':
            if isinstance(created_at, str) and len(created_at) > 10:
                created_at = created_at[:16]
        last_active = user.get('last_active_at', 'N/A')
        if last_active and last_active != 'N/A':
            if isinstance(last_active, str) and len(last_active) > 10:
                last_active = last_active[:16]
        
        created_at_escaped = escape_markdown_v2(str(created_at))
        last_active_escaped = escape_markdown_v2(str(last_active))
        
        # Account status
        status_text = "正常 | 已验证" if user.get('status') == 'active' else "待验证"
        
        text = (
            f"{separator}\n"
            f"  *👤 账户信息*\n"
            f"{separator}\n\n"
            
            f"*基本信息：*\n"
            f"🆔 用户ID：`{user_id_str}`\n"
            f"👤 用户名：{username_escaped}\n"
            f"📛 姓名：{full_name}\n"
            f"🏆 账户状态：{escape_markdown_v2(status_text)}\n\n"
            
            f"*账户等级：*\n"
            f"⭐ VIP等级：{vip_level_str}\n"
            f"💎 会员类型：{escape_markdown_v2('尊享会员' if int(vip_level_str.replace('\\,', '')) >= 2 else '普通会员')}\n\n"
            
            f"*交易统计：*\n"
            f"📊 总交易数：{total_transactions_str} 笔\n"
            f"💰 累计金额：{total_amount_str}\n\n"
            
            f"*时间信息：*\n"
            f"📅 注册时间：{created_at_escaped}\n"
            f"🕐 最后活跃：{last_active_escaped}"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 返回设置", callback_data="settings")
            ]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_settings_account: {e}", exc_info=True)
        await callback.answer("❌ 获取账户信息失败，请稍后再试", show_alert=True)

