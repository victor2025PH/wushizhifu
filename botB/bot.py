"""
OTC Group Management Bot (Bot B)
Main entry point using python-telegram-bot (version 20+ async)
"""
import logging
import asyncio
from telegram import Update, BotCommand, MenuButtonWebApp, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from config import Config
from database import db
from handlers.message_handlers import get_message_handler, handle_price_button, handle_today_bills_button
from handlers.callback_handlers import get_callback_handler
from handlers.group_tracking_handlers import get_chat_member_handler
from admin_checker import is_admin as check_admin

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 降低 httpx 日志级别，减少 getUpdates 轮询日志
logging.getLogger("httpx").setLevel(logging.WARNING)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show welcome message with reply keyboard"""
    from keyboards.reply_keyboard import get_main_reply_keyboard
    from config import Config
    from services.onboarding_service import handle_new_user_onboarding
    from database import db
    
    user = update.effective_user
    is_admin_user = check_admin(user.id)
    chat = update.effective_chat
    
    # Auto-track groups: ensure group exists in database when bot receives group messages
    # This allows "所有群组列表" to detect all groups bot is in
    if chat.type in ['group', 'supergroup']:
        db.ensure_group_exists(chat.id, chat.title)
    
    # Check if new user and show onboarding
    if not db.is_onboarding_completed(user.id):
        onboarding_shown = await handle_new_user_onboarding(update, context)
        if onboarding_shown:
            # Update last active
            db.update_user_last_active(user.id)
            return  # Onboarding flow started
    
    # Update last active timestamp
    db.update_user_last_active(user.id)
    
    # 构建欢迎消息
    welcome_message = (
        f"👋 <b>欢迎使用 OTC 群组管理 Bot</b>\n\n"
        f"你好，{user.first_name}！\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📖 <b>机器人介绍</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"这是一个专业的 OTC（场外交易）群组管理机器人，提供：\n"
        f"• 💱 实时汇率查询（Binance P2P 数据源）\n"
        f"• 🧮 自动结算账单计算\n"
        f"• 📊 快速价格查询\n"
        f"• 🔗 USDT 收款地址管理\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 <b>使用方法</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>方式一：快捷按钮</b>\n"
        f"使用下方快捷按钮快速操作\n\n"
        f"<b>方式二：直接输入</b>\n"
        f"• 发送人民币金额（如：<code>20000</code>）自动计算应结算的 USDT\n"
        f"• 发送算式（如：<code>20000-200</code>）先计算人民币，再换算为 USDT\n\n"
        f"💡 <i>示例：输入 <code>20000-200</code> 表示应收 19800 元人民币，系统会按当前汇率计算应结算的 USDT 数量</i>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>常用命令</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"• <code>/start</code> - 显示此帮助信息\n"
        f"• <code>/help</code> - 查看详细帮助\n"
        f"• <code>/price</code> - 查询当前汇率\n"
        f"• <code>/settlement</code> - 结算计算\n"
        f"• <code>/address</code> - 查看USDT地址\n"
        f"• <code>/support</code> - 联系客服\n\n"
        f"💡 <i>提示：使用菜单按钮（输入框左侧）可以快速访问所有命令</i>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📞 <b>需要帮助？</b>\n"
        f"点击下方「📞 客服」按钮或发送 /help\n\n"
        f"💡 <b>按钮帮助：</b>\n"
        f"点击任意按钮时会显示功能介绍和使用教程\n"
        f"可以关闭帮助提示，也可在此重新打开\n\n"
    )
    
    if is_admin_user:
        welcome_message += (
            f"🔐 <b>管理员提示：</b>\n"
            f"点击「⚙️ 管理」或「⚙️ 设置」按钮查看管理员功能和指令教程\n\n"
        )
    
    welcome_message += "祝您使用愉快！✨"
    
    is_group = update.effective_chat.type in ['group', 'supergroup']
    # Pass user info to keyboard so it can be included in WebApp URL
    user_info = {
        'id': user.id,
        'first_name': user.first_name or '',
        'username': user.username,
        'language_code': user.language_code
    }
    reply_markup = get_main_reply_keyboard(user.id, is_group, user_info)
    
    # Add inline keyboard for resetting help
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    from services.button_help_service import reset_all_help
    help_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 重新显示所有按钮帮助", callback_data="reset_all_help")]
    ])
    
    await update.message.reply_text(
        welcome_message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    
    # Send help reset option separately
    await update.message.reply_text(
        "💡 <b>按钮帮助设置</b>\n\n"
        "如果您之前关闭了按钮帮助提示，可以点击下方按钮重新打开：",
        parse_mode="HTML",
        reply_markup=help_keyboard
    )


async def admin_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin_help command - show admin commands help"""
    from admin_checker import is_admin
    from utils.help_generator import HelpGenerator
    
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ 此命令仅管理员可用")
        return
    
    help_text = HelpGenerator.get_admin_command_help()
    await update.message.reply_text(help_text, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show detailed help"""
    from config import Config
    from keyboards.reply_keyboard import get_main_reply_keyboard
    
    user = update.effective_user
    is_admin_user = check_admin(user.id)
    chat = update.effective_chat
    
    # Auto-track groups
    if chat.type in ['group', 'supergroup']:
        db.ensure_group_exists(chat.id, chat.title)
    
    help_text = (
        "📚 <b>Bot B 完整帮助指南</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 <b>标准命令</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<code>/start</code> - 启动 Bot，显示欢迎信息和菜单\n"
        "<code>/help</code> - 显示此帮助信息\n"
        "<code>/price</code> - 获取当前 USDT/CNY 汇率\n"
        "<code>/settings</code> - 查看当前系统设置\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 <b>快捷按钮</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "使用聊天框底部的快捷按钮：\n"
        "• 📊 查看汇率 - 快速查询当前汇率\n"
        "• 🔗 收款地址 - 查看 USDT 收款地址\n"
        "• 📞 联系人工 - 联系客服支持\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 <b>自动结算计算</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "直接发送人民币金额或算式，自动计算应结算的 USDT 数量：\n"
        "• 纯数字（人民币）：<code>20000</code>\n"
        "• 加法：<code>10000+5000</code> = 15000 元\n"
        "• 减法：<code>20000-200</code> = 19800 元\n"
        "• 乘法：<code>2000*10</code> = 20000 元\n"
        "• 除法：<code>20000/2</code> = 10000 元\n\n"
        "💡 系统会自动将计算后的人民币金额，按当前汇率换算为应结算的 USDT 数量\n\n"
    )
    
    if is_admin_user:
        help_text += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 <b>管理员功能</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "管理员可使用「⚙️ 管理」或「⚙️ 设置」按钮访问管理员功能。\n"
            "在管理菜单中可以查看完整的管理员指令教程。\n\n"
        )
    
    help_text += (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <b>使用技巧</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "• 结算账单会自动包含 USDT 收款地址\n"
        "• 点击账单下方的「✅ 已核对」按钮可确认\n"
        "• 所有价格均来自 Binance P2P 实时数据（CoinGecko 作为备用）\n"
        "• 支持小数计算（如：<code>100.5+50.25</code>）\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📞 <b>技术支持</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "如遇问题，请联系：\n"
        "• 客服：@wushizhifu_jianglai\n"
        "• 工作时间：7×24小时"
    )
    
    is_group = update.effective_chat.type in ['group', 'supergroup']
    # Pass user info to keyboard so it can be included in WebApp URL
    user_info = {
        'id': user.id,
        'first_name': user.first_name or '',
        'username': user.username,
        'language_code': user.language_code
    }
    reply_markup = get_main_reply_keyboard(user.id, is_group, user_info)
    await update.message.reply_text(
        help_text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command - fetch and display P2P leaderboard"""
    from handlers.p2p_handlers import handle_p2p_price_command
    
    # Use new P2P leaderboard feature
    await handle_p2p_price_command(update, context, payment_method="alipay")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command - display current settings"""
    # Auto-track groups
    chat = update.effective_chat
    if chat.type in ['group', 'supergroup']:
        db.ensure_group_exists(chat.id, chat.title)
    
    admin_markup = db.get_admin_markup()
    usdt_address = db.get_usdt_address()
    
    address_display = usdt_address if usdt_address else "未设置"
    if usdt_address and len(usdt_address) > 20:
        address_display = f"{usdt_address[:10]}...{usdt_address[-10:]}"
    
    message = (
        f"⚙️ 当前设置\n\n"
        f"📈 管理员加价：{admin_markup:.4f} USDT\n"
        f"💼 USDT 收款地址：{address_display}\n"
    )
    
    await update.message.reply_text(message)


async def settlement_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settlement or /结算 command - open settlement menu"""
    from handlers.template_handlers import handle_template_menu
    await handle_template_menu(update, context)


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /today or /今日 command - show today's bills"""
    await handle_today_bills_button(update, context)


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history or /历史 command - show history bills"""
    from handlers.bills_handlers import handle_history_bills
    await handle_history_bills(update, context, page=1)


async def address_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /address or /地址 command - show USDT address"""
    chat = update.effective_chat
    group_id = chat.id if chat.type in ['group', 'supergroup'] else None
    usdt_address = None
    
    if group_id:
        group_setting = db.get_group_setting(group_id)
        if group_setting and group_setting.get('usdt_address'):
            usdt_address = group_setting['usdt_address']
    
    if not usdt_address:
        usdt_address = db.get_usdt_address()
    
    if usdt_address:
        address_display = usdt_address[:15] + "..." + usdt_address[-15:] if len(usdt_address) > 30 else usdt_address
        message = f"🔗 USDT 收款地址:\n\n<code>{address_display}</code>"
    else:
        message = "⚠️ USDT 收款地址未设置"
    
    await update.message.reply_text(message, parse_mode="HTML")


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /support or /客服 command - show support info"""
    # Auto-track groups
    chat = update.effective_chat
    if chat.type in ['group', 'supergroup']:
        db.ensure_group_exists(chat.id, chat.title)
    
    contact_message = (
        "📞 <b>联系人工客服</b>\n\n"
        "如有任何问题，请联系管理员：\n"
        "@wushizhifu_jianglai\n\n"
        "或使用以下方式：\n"
        "• 工作时间：7×24小时\n"
        "• 响应时间：通常在5分钟内"
    )
    await update.message.reply_text(contact_message, parse_mode="HTML")


async def mybills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mybills or /我的账单 command - show personal bills (private chat only)"""
    chat = update.effective_chat
    
    # Auto-track groups (even though this command is private-only, track if called in group)
    if chat.type in ['group', 'supergroup']:
        db.ensure_group_exists(chat.id, chat.title)
        await update.message.reply_text("❌ 此功能仅在私聊中可用")
        return
    
    from handlers.personal_handlers import handle_personal_bills
    await handle_personal_bills(update, context, page=1)




async def post_init(application: Application) -> None:
    """Set up bot commands menu and menu button after application is initialized"""
    # Define commands for menu button
    commands = [
        BotCommand("start", "启动机器人，显示欢迎信息"),
        BotCommand("price", "查看实时汇率（Binance P2P）"),
        BotCommand("settlement", "结算计算（打开结算菜单）"),
        BotCommand("today", "查看今日账单（群组）"),
        BotCommand("history", "查看历史账单（群组）"),
        BotCommand("address", "查看USDT收款地址"),
        BotCommand("support", "联系人工客服"),
        BotCommand("mybills", "我的账单（私聊）"),
        BotCommand("help", "查看详细帮助"),
        BotCommand("settings", "查看当前设置"),
    ]
    
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands menu has been set up")
    
    # Set up menu button (聊天界面右上角的按钮)
    # This is important for MiniApp to correctly receive user initData
    try:
        menu_button = MenuButtonWebApp(
            text="💎 打开应用",
            web_app=WebAppInfo(url=Config.get_miniapp_url("dashboard"))
        )
        await application.bot.set_chat_menu_button(menu_button=menu_button)
        logger.info(f"✅ Menu button set: '💎 打开应用' -> {Config.get_miniapp_url('dashboard')}")
    except Exception as e:
        logger.error(f"Failed to set menu button: {e}", exc_info=True)
    
    # 方案一：啟動時同步群組 - 驗證資料庫中所有已知群組
    # 延遲 30 秒後執行，避免在啟動時立即執行導致網絡超時
    async def delayed_sync():
        await asyncio.sleep(30)  # 等待 30 秒，讓機器人完全啟動
        try:
            from services.group_sync_service import sync_groups_on_startup
            await sync_groups_on_startup(application.bot)
        except Exception as e:
            logger.error(f"啟動時同步群組失敗: {e}", exc_info=True)
    
    asyncio.create_task(delayed_sync())


def main():
    """Main function to start the bot"""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).post_init(post_init).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin_help", admin_help_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
    # Register common function commands
    # Note: Telegram Bot API only supports commands with letters, numbers, and underscores
    # Chinese commands are handled in message_handler instead
    application.add_handler(CommandHandler("settlement", settlement_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("address", address_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("mybills", mybills_command))
    
    # Register admin commands
    async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command - show admin panel"""
        from handlers.message_handlers import handle_admin_panel
        await handle_admin_panel(update, context)
    
    async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addadmin command - add admin"""
        from admin_checker import is_admin
        from database import db
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供用户ID\n格式：`/addadmin <user_id>`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            user_id = int(args[0])
            conn = db.connect()
            cursor = conn.cursor()
            
            # Check if already admin
            cursor.execute("SELECT COUNT(*) FROM admins WHERE user_id = ? AND status = 'active'", (user_id,))
            if cursor.fetchone()[0] > 0:
                await update.message.reply_text("❌ 添加失败（可能已是管理员）")
                cursor.close()
                return
            
            # Check permission
            from services.permission_service import PermissionService
            if not PermissionService.can_manage_admins(user.id):
                await update.message.reply_text(
                    "❌ 您没有权限添加管理员\n\n"
                    "💡 只有超级管理员可以添加或删除管理员"
                )
                return
            
            # Add admin (default role is 'admin')
            from datetime import datetime
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO admins (user_id, role, status, added_by, added_at)
                VALUES (?, 'admin', 'active', ?, ?)
            """, (user_id, user.id, now))
            conn.commit()
            cursor.close()
            
            # Also add to shared database
            from database.admin_repository import AdminRepository
            AdminRepository.add_admin(user_id, role="admin", added_by=user.id)
            
            await update.message.reply_text(
                f"✅ 已添加管理员：{user_id}\n"
                f"角色：普通管理员\n\n"
                f"📝 此管理员已同步到 Bot A 和 Bot B，无需重启服务即可生效。"
            )
            logger.info(f"Super admin {user.id} added admin {user_id}")
            
        except ValueError:
            await update.message.reply_text("❌ 无效的用户ID")
        except Exception as e:
            logger.error(f"Error in addadmin_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 添加失败，请稍后再试")
    
    async def addword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addword command - add sensitive word(s)"""
        from admin_checker import is_admin
        from repositories.sensitive_words_repository import SensitiveWordsRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供敏感词\n格式：`/addword <词语> [action]`\n"
                "批量添加：`/addword batch <词语1,词语2,词语3> [action]`\n"
                "动作：warn, delete, ban",
                parse_mode="MarkdownV2"
            )
            return
        
        # Check if batch mode
        if args[0].lower() == "batch" and len(args) >= 2:
            # Batch add mode
            words_str = args[1]
            action = args[2] if len(args) > 2 else "warn"
            
            if action not in ["warn", "delete", "ban"]:
                action = "warn"
            
            # Split by comma or newline
            words = [w.strip() for w in words_str.replace('\n', ',').split(',') if w.strip()]
            
            if not words:
                await update.message.reply_text("❌ 未找到有效的敏感词")
                return
            
            if len(words) > 50:
                await update.message.reply_text("❌ 批量添加最多支持50个敏感词")
                return
            
            # Add words
            success_count = 0
            failed_count = 0
            for word in words:
                if SensitiveWordsRepository.add_word(None, word, action, user.id):
                    success_count += 1
                else:
                    failed_count += 1
            
            await update.message.reply_text(
                f"✅ 批量添加完成\n"
                f"成功：{success_count} 个\n"
                f"失败：{failed_count} 个（可能已存在）\n"
                f"动作：{action}",
                parse_mode="MarkdownV2"
            )
            logger.info(f"Admin {user.id} batch added {success_count} sensitive words")
            return
        
        # Single word mode
        word = args[0]
        action = args[1] if len(args) > 1 else "warn"
        
        if action not in ["warn", "delete", "ban"]:
            action = "warn"
        
        if SensitiveWordsRepository.add_word(None, word, action, user.id):
            # Log operation
            from repositories.admin_logs_repository import AdminLogsRepository
            AdminLogsRepository.log_operation(
                admin_id=user.id,
                operation_type="add_word",
                target_type="sensitive_word",
                details=f"word={word}, action={action}",
                result="success"
            )
            await update.message.reply_text(
                f"✅ 已添加敏感词：`{word}` (动作：{action})",
                parse_mode="MarkdownV2"
            )
        else:
            # Log failed operation
            from repositories.admin_logs_repository import AdminLogsRepository
            AdminLogsRepository.log_operation(
                admin_id=user.id,
                operation_type="add_word",
                target_type="sensitive_word",
                details=f"word={word}, action={action}",
                result="failed"
            )
            await update.message.reply_text("❌ 添加失败（可能已存在）")
    
    async def addgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addgroup command - add group"""
        from admin_checker import is_admin
        from repositories.group_repository import GroupRepository
        from repositories.verification_repository import VerificationRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供群组ID\n格式：`/addgroup <group_id> [group_title]`\n\n"
                "示例：`/addgroup -1001234567890 测试群组`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            group_id = int(args[0])
            group_title = args[1] if len(args) > 1 else None
            
            # Validate group ID format (should start with -100 for supergroups)
            if group_id > 0:
                await update.message.reply_text("❌ 群组ID格式错误，超级群组ID应以 -100 开头")
                return
            
            # Try to get group info from bot
            try:
                chat = await context.bot.get_chat(group_id)
                if not group_title:
                    group_title = chat.title
                
                # Check if bot is admin in the group
                bot_member = await context.bot.get_chat_member(group_id, context.bot.id)
                if bot_member.status not in ['administrator', 'creator']:
                    await update.message.reply_text("❌ 机器人不是该群组的管理员，无法添加")
                    return
                
            except Exception as e:
                logger.warning(f"Could not verify group info: {e}")
                # Continue anyway, might be a permission issue
            
            # Add group to database
            group = GroupRepository.create_or_update_group(
                group_id=group_id,
                group_title=group_title,
                verification_enabled=False,
                verification_type='none'
            )
            
            # Create default verification config
            VerificationRepository.create_or_update_config(group_id)
            
            await update.message.reply_text(
                f"✅ 已成功添加群组：{group_title or '未命名群组'}\n"
                f"群组ID：`{group_id}`\n\n"
                f"请在群组设置中配置审核规则",
                parse_mode="MarkdownV2"
            )
            logger.info(f"Admin {user.id} added group {group_id}")
            
        except ValueError:
            await update.message.reply_text("❌ 无效的群组ID，请输入数字")
        except Exception as e:
            logger.error(f"Error adding group: {e}", exc_info=True)
            await update.message.reply_text("❌ 添加失败，请检查群组ID和机器人权限")
    
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("addadmin", addadmin_command))
    application.add_handler(CommandHandler("addword", addword_command))
    application.add_handler(CommandHandler("addgroup", addgroup_command))
    
    # User search command
    async def search_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search_user command - search users"""
        from admin_checker import is_admin
        from handlers.message_handlers import handle_admin_user_search_result
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供搜索条件\n格式：`/search_user <条件>`\n\n"
                "示例：\n"
                "• `/search_user 123456789` (按ID)\n"
                "• `/search_user @username` (按用户名)\n"
                "• `/search_user vip:1` (VIP等级)\n"
                "• `/search_user date:2025-12-26` (注册日期)",
                parse_mode="MarkdownV2"
            )
            return
        
        search_query = " ".join(args)
        await handle_admin_user_search_result(update, context, search_query)
    
    application.add_handler(CommandHandler("search_user", search_user_command))
    
    # User detail command
    async def user_detail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /user_detail command - show user details"""
        from admin_checker import is_admin
        from handlers.message_handlers import handle_admin_user_detail
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供用户ID\n格式：`/user_detail <user_id>`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            user_id = int(args[0])
            await handle_admin_user_detail(update, context, user_id)
        except ValueError:
            await update.message.reply_text("❌ 无效的用户ID")
        except Exception as e:
            logger.error(f"Error in user_detail_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 查看失败，请稍后再试")
    
    # Set VIP command
    async def set_vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /set_vip command - set user VIP level"""
        from admin_checker import is_admin
        from database import db
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 2:
            await update.message.reply_text(
                "❌ 请提供用户ID和VIP等级\n格式：`/set_vip <user_id> <level>`\n\n"
                "示例：`/set_vip 123456789 1`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            user_id = int(args[0])
            vip_level = int(args[1])
            
            if vip_level < 0 or vip_level > 10:
                await update.message.reply_text("❌ VIP等级必须在 0-10 之间")
                return
            
            conn = db.connect()
            cursor = conn.cursor()
            
            # Update VIP level
            cursor.execute("""
                UPDATE users 
                SET vip_level = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (vip_level, user_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                await update.message.reply_text(
                    f"✅ 已设置用户 {user_id} 的VIP等级为 {vip_level}"
                )
                logger.info(f"Admin {user.id} set VIP level {vip_level} for user {user_id}")
            else:
                await update.message.reply_text("❌ 用户不存在")
            
            cursor.close()
            
        except ValueError:
            await update.message.reply_text("❌ 无效的用户ID或VIP等级")
        except Exception as e:
            logger.error(f"Error in set_vip_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 设置失败，请稍后再试")
    
    # Disable/Enable user commands
    async def disable_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /disable_user command - disable user"""
        from admin_checker import is_admin
        from database import db
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供用户ID\n格式：`/disable_user <user_id>`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            user_id = int(args[0])
            conn = db.connect()
            cursor = conn.cursor()
            
            try:
                # Check for confirmation
                from services.confirmation_service import ConfirmationService
                confirmation = ConfirmationService.get_confirmation(user.id)
                
                if confirmation and confirmation['operation'] == 'disable_user' and confirmation['data'].get('user_id') == user_id:
                    # Confirmed, proceed
                    ConfirmationService.confirm_operation(user.id)  # Clear confirmation
                    
                    cursor.execute("""
                        UPDATE users 
                        SET status = 'disabled', updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """, (user_id,))
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        # Log operation
                        from repositories.admin_logs_repository import AdminLogsRepository
                        AdminLogsRepository.log_operation(
                            admin_id=user.id,
                            operation_type="update_user",
                            target_type="user",
                            target_id=user_id,
                            details="disable_user",
                            result="success"
                        )
                        await update.message.reply_text(f"✅ 已禁用用户 {user_id}")
                        logger.info(f"Admin {user.id} disabled user {user_id}")
                    else:
                        await update.message.reply_text("❌ 用户不存在")
                else:
                    # First time, require confirmation
                    ConfirmationService.create_confirmation(
                        user.id,
                        'disable_user',
                        {'user_id': user_id}
                    )
                    await update.message.reply_text(
                        f"⚠️ <b>确认禁用用户</b>\n\n"
                        f"您将要禁用用户：<code>{user_id}</code>\n\n"
                        f"请再次执行相同命令确认：\n"
                        f"<code>/disable_user {user_id}</code>\n\n"
                        f"或者发送 <code>/confirm</code> 确认禁用",
                        parse_mode="HTML"
                    )
            finally:
                cursor.close()
            
        except ValueError:
            from utils.error_helper import ErrorHelper
            error_msg = ErrorHelper.get_user_friendly_error('invalid_user_id', {'command': '/disable_user'})
            await update.message.reply_text(error_msg, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error in disable_user_command: {e}", exc_info=True)
            from utils.error_helper import ErrorHelper
            error_msg = ErrorHelper.get_user_friendly_error('system_error')
            await update.message.reply_text(error_msg, parse_mode="HTML")
    
    # Batch user operations
    async def batch_set_vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /batch_set_vip command - batch set VIP level for multiple users"""
        from admin_checker import is_admin
        from services.batch_user_service import BatchUserService
        from services.confirmation_service import ConfirmationService
        from repositories.admin_logs_repository import AdminLogsRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            from utils.error_helper import ErrorHelper
            error_msg = ErrorHelper.get_user_friendly_error('permission_denied')
            await update.message.reply_text(error_msg, parse_mode="HTML")
            return
        
        args = context.args
        if not args or len(args) < 2:
            await update.message.reply_text(
                "❌ <b>格式错误</b>\n\n"
                "💡 <b>使用方法：</b>\n"
                "<code>/batch_set_vip &lt;user_ids&gt; &lt;vip_level&gt;</code>\n\n"
                "<b>参数说明：</b>\n"
                "• user_ids: 用户ID列表，用逗号分隔（最多50个）\n"
                "• vip_level: VIP等级（0-10）\n\n"
                "<b>示例：</b>\n"
                "• <code>/batch_set_vip 123456789,987654321,111222333 1</code>\n"
                "• <code>/batch_set_vip 123456789,987654321 0</code>\n\n"
                "⚠️ 此操作需要确认",
                parse_mode="HTML"
            )
            return
        
        try:
            user_ids_str = args[0]
            vip_level = int(args[1])
            
            # Validate VIP level
            if vip_level < 0 or vip_level > 10:
                from utils.error_helper import ErrorHelper
                error_msg = ErrorHelper.get_user_friendly_error('invalid_vip_level')
                await update.message.reply_text(error_msg, parse_mode="HTML")
                return
            
            # Parse and validate user IDs
            try:
                user_ids = BatchUserService.validate_user_ids(user_ids_str)
            except ValueError as e:
                await update.message.reply_text(
                    f"❌ <b>用户ID格式错误</b>\n\n"
                    f"💡 <b>错误：</b>{str(e)}\n\n"
                    f"<b>正确格式：</b>用逗号分隔的数字，例如：<code>123456789,987654321</code>\n"
                    f"最多支持50个用户",
                    parse_mode="HTML"
                )
                return
            
            # Check for confirmation
            confirmation = ConfirmationService.get_confirmation(user.id)
            confirmation_key = f"batch_set_vip_{vip_level}_{','.join(map(str, sorted(user_ids)))}"
            
            if confirmation and confirmation['operation'] == 'batch_set_vip' and confirmation['data'].get('key') == confirmation_key:
                # Confirmed, proceed
                ConfirmationService.confirm_operation(user.id)
                
                result = BatchUserService.batch_set_vip(user_ids, vip_level)
                
                # Log operation
                AdminLogsRepository.log_operation(
                    admin_id=user.id,
                    operation_type="batch_update_user",
                    target_type="user",
                    target_id=0,
                    details=f"batch_set_vip level={vip_level} count={result['success_count']}",
                    result="success" if result['failed_count'] == 0 else "partial"
                )
                
                # Format result message
                message = (
                    f"✅ <b>批量设置VIP完成</b>\n\n"
                    f"成功：{result['success_count']} 个用户\n"
                )
                
                if result['failed_count'] > 0:
                    message += f"失败：{result['failed_count']} 个用户\n"
                    if result['failed_users']:
                        failed_list = ', '.join(map(str, result['failed_users'][:10]))
                        if len(result['failed_users']) > 10:
                            failed_list += f" 等{len(result['failed_users'])}个"
                        message += f"失败用户ID：{failed_list}\n"
                
                message += f"\nVIP等级已设置为：{vip_level}"
                
                await update.message.reply_text(message, parse_mode="HTML")
                logger.info(f"Admin {user.id} batch set VIP level {vip_level} for {result['success_count']} users")
            else:
                # First time, require confirmation
                ConfirmationService.create_confirmation(
                    user.id,
                    'batch_set_vip',
                    {'key': confirmation_key, 'user_ids': user_ids, 'vip_level': vip_level}
                )
                
                await update.message.reply_text(
                    f"⚠️ <b>确认批量设置VIP</b>\n\n"
                    f"您将要为 <b>{len(user_ids)}</b> 个用户设置VIP等级为 <code>{vip_level}</code>\n\n"
                    f"用户ID：<code>{user_ids_str}</code>\n\n"
                    f"⚠️ 此操作将影响多个用户，请确认无误！\n\n"
                    f"请再次执行相同命令确认：\n"
                    f"<code>/batch_set_vip {user_ids_str} {vip_level}</code>\n\n"
                    f"或者发送 <code>/confirm</code> 确认操作",
                    parse_mode="HTML"
                )
        
        except ValueError:
            from utils.error_helper import ErrorHelper
            error_msg = ErrorHelper.get_user_friendly_error('invalid_vip_level')
            await update.message.reply_text(error_msg, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error in batch_set_vip_command: {e}", exc_info=True)
            from utils.error_helper import ErrorHelper
            error_msg = ErrorHelper.get_user_friendly_error('unknown_error')
            await update.message.reply_text(error_msg, parse_mode="HTML")
    
    async def batch_disable_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /batch_disable_users command - batch disable/enable multiple users"""
        from admin_checker import is_admin
        from services.batch_user_service import BatchUserService
        from services.confirmation_service import ConfirmationService
        from repositories.admin_logs_repository import AdminLogsRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            from utils.error_helper import ErrorHelper
            error_msg = ErrorHelper.get_user_friendly_error('permission_denied')
            await update.message.reply_text(error_msg, parse_mode="HTML")
            return
        
        args = context.args
        if not args or len(args) < 2:
            await update.message.reply_text(
                "❌ <b>格式错误</b>\n\n"
                "💡 <b>使用方法：</b>\n"
                "<code>/batch_disable_users &lt;user_ids&gt; &lt;disable|enable&gt;</code>\n\n"
                "💡 <b>或者：</b>\n"
                "<code>/batch_enable_users &lt;user_ids&gt;</code>\n\n"
                "<b>参数说明：</b>\n"
                "• user_ids: 用户ID列表，用逗号分隔（最多50个）\n"
                "• disable/enable: 禁用或启用\n\n"
                "<b>示例：</b>\n"
                "• <code>/batch_disable_users 123456789,987654321 disable</code>\n"
                "• <code>/batch_enable_users 123456789,987654321</code>\n\n"
                "⚠️ 此操作需要确认",
                parse_mode="HTML"
            )
            return
        
        try:
            user_ids_str = args[0]
            action = args[1].lower() if len(args) > 1 else 'disable'
            
            if action not in ['disable', 'enable']:
                await update.message.reply_text("❌ 操作必须是 disable 或 enable")
                return
            
            disable = action == 'disable'
            
            # Parse and validate user IDs
            try:
                user_ids = BatchUserService.validate_user_ids(user_ids_str)
            except ValueError as e:
                await update.message.reply_text(
                    f"❌ <b>用户ID格式错误</b>\n\n"
                    f"💡 <b>错误：</b>{str(e)}\n\n"
                    f"<b>正确格式：</b>用逗号分隔的数字，例如：<code>123456789,987654321</code>\n"
                    f"最多支持50个用户",
                    parse_mode="HTML"
                )
                return
            
            # Check for confirmation
            confirmation = ConfirmationService.get_confirmation(user.id)
            confirmation_key = f"batch_{action}_{','.join(map(str, sorted(user_ids)))}"
            
            if confirmation and confirmation['operation'] == f'batch_{action}_users' and confirmation['data'].get('key') == confirmation_key:
                # Confirmed, proceed
                ConfirmationService.confirm_operation(user.id)
                
                result = BatchUserService.batch_disable_users(user_ids, disable)
                
                # Log operation
                AdminLogsRepository.log_operation(
                    admin_id=user.id,
                    operation_type="batch_update_user",
                    target_type="user",
                    target_id=0,
                    details=f"batch_{action} count={result['success_count']}",
                    result="success" if result['failed_count'] == 0 else "partial"
                )
                
                # Format result message
                action_text = "禁用" if disable else "启用"
                message = (
                    f"✅ <b>批量{action_text}完成</b>\n\n"
                    f"成功：{result['success_count']} 个用户\n"
                )
                
                if result['failed_count'] > 0:
                    message += f"失败：{result['failed_count']} 个用户\n"
                    if result['failed_users']:
                        failed_list = ', '.join(map(str, result['failed_users'][:10]))
                        if len(result['failed_users']) > 10:
                            failed_list += f" 等{len(result['failed_users'])}个"
                        message += f"失败用户ID：{failed_list}\n"
                
                await update.message.reply_text(message, parse_mode="HTML")
                logger.info(f"Admin {user.id} batch {action} {result['success_count']} users")
            else:
                # First time, require confirmation
                ConfirmationService.create_confirmation(
                    user.id,
                    f'batch_{action}_users',
                    {'key': confirmation_key, 'user_ids': user_ids, 'disable': disable}
                )
                
                action_text = "禁用" if disable else "启用"
                await update.message.reply_text(
                    f"⚠️ <b>确认批量{action_text}用户</b>\n\n"
                    f"您将要{action_text} <b>{len(user_ids)}</b> 个用户\n\n"
                    f"用户ID：<code>{user_ids_str}</code>\n\n"
                    f"⚠️ 此操作将影响多个用户，请确认无误！\n\n"
                    f"请再次执行相同命令确认：\n"
                    f"<code>/batch_disable_users {user_ids_str} {action}</code>\n\n"
                    f"或者发送 <code>/confirm</code> 确认操作",
                    parse_mode="HTML"
                )
        
        except Exception as e:
            logger.error(f"Error in batch_disable_users_command: {e}", exc_info=True)
            from utils.error_helper import ErrorHelper
            error_msg = ErrorHelper.get_user_friendly_error('unknown_error')
            await update.message.reply_text(error_msg, parse_mode="HTML")
    
    async def batch_enable_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /batch_enable_users command - batch enable multiple users (alias for batch_disable_users enable)"""
        # Redirect to batch_disable_users with enable action
        if context.args:
            context.args = [context.args[0], 'enable'] + list(context.args[1:])
        else:
            context.args = ['', 'enable']
        await batch_disable_users_command(update, context)
    
    async def batch_export_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /batch_export_users command - export data for specified users"""
        from admin_checker import is_admin
        from services.batch_user_service import BatchUserService
        from repositories.admin_logs_repository import AdminLogsRepository
        from io import BytesIO
        
        user = update.effective_user
        
        if not is_admin(user.id):
            from utils.error_helper import ErrorHelper
            error_msg = ErrorHelper.get_user_friendly_error('permission_denied')
            await update.message.reply_text(error_msg, parse_mode="HTML")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ <b>格式错误</b>\n\n"
                "💡 <b>使用方法：</b>\n"
                "<code>/batch_export_users &lt;user_ids&gt;</code>\n\n"
                "<b>参数说明：</b>\n"
                "• user_ids: 用户ID列表，用逗号分隔（最多100个）\n\n"
                "<b>示例：</b>\n"
                "• <code>/batch_export_users 123456789,987654321,111222333</code>\n\n"
                "💡 导出的数据为CSV格式，可直接导入Excel",
                parse_mode="HTML"
            )
            return
        
        try:
            user_ids_str = args[0]
            
            # Parse and validate user IDs
            try:
                user_ids = BatchUserService.validate_user_ids(user_ids_str)
            except ValueError as e:
                await update.message.reply_text(
                    f"❌ <b>用户ID格式错误</b>\n\n"
                    f"💡 <b>错误：</b>{str(e)}\n\n"
                    f"<b>正确格式：</b>用逗号分隔的数字，例如：<code>123456789,987654321</code>\n"
                    f"最多支持100个用户",
                    parse_mode="HTML"
                )
                return
            
            if len(user_ids) > 100:
                await update.message.reply_text(
                    "❌ <b>用户数量超限</b>\n\n"
                    "💡 批量导出最多支持100个用户\n"
                    "请分批导出或使用 <code>/export_users</code> 导出全部用户",
                    parse_mode="HTML"
                )
                return
            
            users_data, count = BatchUserService.batch_export_users(user_ids)
            
            if not users_data:
                await update.message.reply_text("❌ 未找到任何用户数据")
                return
            
            # Format as CSV
            export_text = "用户ID,用户名,姓名,VIP等级,状态,交易数,交易额,注册时间\n"
            for user_data in users_data:
                username = (user_data['username'] or '').replace(',', '，')
                first_name = (user_data['first_name'] or '').replace(',', '，')
                status = user_data['status'] or 'active'
                created_at = user_data['created_at'] or ''
                if created_at and len(created_at) > 19:
                    created_at = created_at[:19]  # Truncate to datetime format
                
                export_text += (
                    f"{user_data['user_id']},{username},{first_name},"
                    f"{user_data['vip_level']},{status},"
                    f"{user_data['total_transactions'] or 0},{user_data['total_amount'] or 0},"
                    f"{created_at}\n"
                )
            
            # Send as document if too long, otherwise as text
            if len(export_text) > 4000:
                # Create CSV file
                csv_buffer = BytesIO()
                csv_buffer.write(export_text.encode('utf-8-sig'))  # UTF-8 with BOM for Excel
                csv_buffer.seek(0)
                
                await update.message.reply_document(
                    document=csv_buffer,
                    filename=f"batch_users_export_{len(user_ids)}_users.csv",
                    caption=f"✅ 已导出 {count} 个用户的数据\n\n💡 CSV格式，可直接导入Excel"
                )
            else:
                await update.message.reply_text(
                    f"✅ <b>导出完成</b>\n\n"
                    f"已导出 {count} 个用户的数据\n\n"
                    f"<code>{export_text}</code>",
                    parse_mode="HTML"
                )
            
            # Log operation
            AdminLogsRepository.log_operation(
                admin_id=user.id,
                operation_type="export",
                target_type="user",
                target_id=0,
                details=f"batch_export count={count}",
                result="success"
            )
            logger.info(f"Admin {user.id} batch exported {count} users")
        
        except ValueError as e:
            if "100" in str(e):
                await update.message.reply_text(
                    "❌ <b>用户数量超限</b>\n\n"
                    "💡 批量导出最多支持100个用户",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(f"❌ {str(e)}", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error in batch_export_users_command: {e}", exc_info=True)
            from utils.error_helper import ErrorHelper
            error_msg = ErrorHelper.get_user_friendly_error('unknown_error')
            await update.message.reply_text(error_msg, parse_mode="HTML")
    
    async def enable_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /enable_user command - enable user"""
        from admin_checker import is_admin
        from database import db
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供用户ID\n格式：`/enable_user <user_id>`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            user_id = int(args[0])
            conn = db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET status = 'active', updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                await update.message.reply_text(f"✅ 已启用用户 {user_id}")
                logger.info(f"Admin {user.id} enabled user {user_id}")
            else:
                await update.message.reply_text("❌ 用户不存在")
            
            cursor.close()
            
        except ValueError:
            await update.message.reply_text("❌ 无效的用户ID")
        except Exception as e:
            logger.error(f"Error in enable_user_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 操作失败，请稍后再试")
    
    # Delete word command
    async def delword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /delword command - delete sensitive word(s)"""
        from admin_checker import is_admin
        from repositories.sensitive_words_repository import SensitiveWordsRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供敏感词ID\n格式：`/delword <word_id>`\n"
                "批量删除：`/delword batch <id1,id2,id3>`\n\n"
                "💡 敏感词ID可在敏感词列表中查看",
                parse_mode="MarkdownV2"
            )
            return
        
        # Check if batch mode
        if args[0].lower() == "batch" and len(args) >= 2:
            # Batch delete mode
            ids_str = args[1]
            try:
                # Split by comma or space
                ids = [int(id_str.strip()) for id_str in ids_str.replace(',', ' ').split() if id_str.strip()]
                
                if not ids:
                    await update.message.reply_text("❌ 未找到有效的敏感词ID")
                    return
                
                if len(ids) > 50:
                    await update.message.reply_text("❌ 批量删除最多支持50个敏感词")
                    return
                
                # Delete words
                success_count = 0
                failed_count = 0
                for word_id in ids:
                    if SensitiveWordsRepository.remove_word(word_id):
                        success_count += 1
                    else:
                        failed_count += 1
                
                await update.message.reply_text(
                    f"✅ 批量删除完成\n"
                    f"成功：{success_count} 个\n"
                    f"失败：{failed_count} 个",
                    parse_mode="MarkdownV2"
                )
                logger.info(f"Admin {user.id} batch deleted {success_count} sensitive words")
            except ValueError:
                await update.message.reply_text("❌ 无效的敏感词ID格式")
            except Exception as e:
                logger.error(f"Error in delword_command (batch): {e}", exc_info=True)
                await update.message.reply_text("❌ 批量删除失败，请稍后再试")
            return
        
        # Single word mode
        try:
            word_id = int(args[0])
            
            # Get word info before deleting
            word_info = SensitiveWordsRepository.get_word_by_id(word_id)
            if not word_info:
                await update.message.reply_text("❌ 敏感词不存在")
                return
            
            if SensitiveWordsRepository.remove_word(word_id):
                # Log operation
                from repositories.admin_logs_repository import AdminLogsRepository
                AdminLogsRepository.log_operation(
                    admin_id=user.id,
                    operation_type="delete_word",
                    target_type="sensitive_word",
                    target_id=word_id,
                    details=f"word={word_info['word']}",
                    result="success"
                )
                await update.message.reply_text(
                    f"✅ 已删除敏感词：`{word_info['word']}`",
                    parse_mode="MarkdownV2"
                )
                logger.info(f"Admin {user.id} deleted sensitive word {word_id}")
            else:
                await update.message.reply_text("❌ 删除失败")
                
        except ValueError:
            await update.message.reply_text("❌ 无效的敏感词ID")
        except Exception as e:
            logger.error(f"Error in delword_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 删除失败，请稍后再试")
    
    # Edit word command
    async def editword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /editword command - edit sensitive word"""
        from admin_checker import is_admin
        from repositories.sensitive_words_repository import SensitiveWordsRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 2:
            await update.message.reply_text(
                "❌ 请提供敏感词ID和动作\n格式：`/editword <word_id> <action>`\n\n"
                "动作：warn（警告）、delete（删除）、ban（封禁）\n\n"
                "示例：`/editword 1 delete`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            word_id = int(args[0])
            action = args[1].lower()
            
            if action not in ["warn", "delete", "ban"]:
                await update.message.reply_text("❌ 无效的动作，必须是 warn、delete 或 ban")
                return
            
            # Get word info before editing
            word_info = SensitiveWordsRepository.get_word_by_id(word_id)
            if not word_info:
                await update.message.reply_text("❌ 敏感词不存在")
                return
            
            if SensitiveWordsRepository.update_word(word_id, action=action):
                # Log operation
                from repositories.admin_logs_repository import AdminLogsRepository
                AdminLogsRepository.log_operation(
                    admin_id=user.id,
                    operation_type="update_word",
                    target_type="sensitive_word",
                    target_id=word_id,
                    details=f"word={word_info['word']}, new_action={action}",
                    result="success"
                )
                action_text = {"warn": "警告", "delete": "删除", "ban": "封禁"}.get(action, action)
                await update.message.reply_text(
                    f"✅ 已更新敏感词：`{word_info['word']}`\n"
                    f"新动作：{action_text}",
                    parse_mode="MarkdownV2"
                )
                logger.info(f"Admin {user.id} edited sensitive word {word_id} to action {action}")
            else:
                await update.message.reply_text("❌ 更新失败")
                
        except ValueError:
            await update.message.reply_text("❌ 无效的敏感词ID")
        except Exception as e:
            logger.error(f"Error in editword_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 更新失败，请稍后再试")
    
    # Delete admin command
    async def deladmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /deladmin command - delete admin"""
        from admin_checker import is_admin
        from database import db
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供用户ID\n格式：`/deladmin <user_id>`\n\n"
                "⚠️ 删除操作不可恢复",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            user_id = int(args[0])
            
            # Prevent self-deletion
            if user_id == user.id:
                await update.message.reply_text("❌ 不能删除自己")
                return
            
            conn = db.connect()
            cursor = conn.cursor()
            
            # Check if admin exists
            cursor.execute("SELECT * FROM admins WHERE user_id = ? AND status = 'active'", (user_id,))
            admin = cursor.fetchone()
            if not admin:
                await update.message.reply_text("❌ 管理员不存在或已被删除")
                cursor.close()
                return
            
            # Check permission
            from services.permission_service import PermissionService
            if not PermissionService.can_manage_admins(user.id):
                await update.message.reply_text(
                    "❌ 您没有权限删除管理员\n\n"
                    "💡 只有超级管理员可以添加或删除管理员"
                )
                return
            
            # Cannot delete self
            if user_id == user.id:
                from utils.error_helper import ErrorHelper
                error_msg = ErrorHelper.get_user_friendly_error('self_operation')
                await update.message.reply_text(error_msg, parse_mode="HTML")
                return
            
            # Check for confirmation
            from services.confirmation_service import ConfirmationService
            confirmation = ConfirmationService.get_confirmation(user.id)
            
            # Check if this is a confirmation (user_id matches and operation matches)
            if confirmation and confirmation['operation'] == 'delete_admin' and confirmation['data'].get('user_id') == user_id:
                # This is a confirmation, proceed with deletion
                ConfirmationService.confirm_operation(user.id)  # Clear confirmation
                
                cursor.execute("""
                    UPDATE admins 
                    SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()
                cursor.close()
                
                # Also delete from shared database
                from database.admin_repository import AdminRepository
                AdminRepository.remove_admin(user_id)
                
                # Log operation
                from repositories.admin_logs_repository import AdminLogsRepository
                AdminLogsRepository.log_operation(
                    admin_id=user.id,
                    operation_type="delete_admin",
                    target_type="admin",
                    target_id=user_id,
                    details=f"deleted admin {user_id}",
                    result="success"
                )
                await update.message.reply_text(
                    f"✅ 已删除管理员：{user_id}\n\n"
                    f"📝 此操作已同步到 Bot A 和 Bot B"
                )
                logger.info(f"Super admin {user.id} deleted admin {user_id}")
            else:
                # First time, require confirmation
                ConfirmationService.create_confirmation(
                    user.id,
                    'delete_admin',
                    {'user_id': user_id}
                )
                cursor.close()
                await update.message.reply_text(
                    f"⚠️ <b>确认删除管理员</b>\n\n"
                    f"您将要删除管理员：<code>{user_id}</code>\n\n"
                    f"⚠️ 此操作不可恢复！\n\n"
                    f"请再次执行相同命令确认：\n"
                    f"<code>/deladmin {user_id}</code>\n\n"
                    f"或者发送 <code>/confirm</code> 确认删除",
                    parse_mode="HTML"
                )
            
        except ValueError:
            await update.message.reply_text("❌ 无效的用户ID")
        except Exception as e:
            logger.error(f"Error in deladmin_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 删除失败，请稍后再试")
    
    # Confirm command
    async def confirm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /confirm command - confirm pending operations"""
        from admin_checker import is_admin
        from services.confirmation_service import ConfirmationService
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        confirmation = ConfirmationService.confirm_operation(user.id)
        
        if not confirmation:
            await update.message.reply_text(
                "❌ 没有待确认的操作\n\n"
                "💡 请先执行需要确认的操作（如删除、禁用等）"
            )
            return
        
        operation = confirmation['operation']
        data = confirmation['data']
        
        # Handle different operations
        if operation == 'delete_admin':
            user_id = data.get('user_id')
            if user_id:
                # Execute delete admin
                from database import db
                conn = db.connect()
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE admins 
                    SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()
                cursor.close()
                
                from database.admin_repository import AdminRepository
                AdminRepository.remove_admin(user_id)
                
                from repositories.admin_logs_repository import AdminLogsRepository
                AdminLogsRepository.log_operation(
                    admin_id=user.id,
                    operation_type="delete_admin",
                    target_type="admin",
                    target_id=user_id,
                    details=f"deleted admin {user_id}",
                    result="success"
                )
                
                await update.message.reply_text(
                    f"✅ 已确认删除管理员：{user_id}\n\n"
                    f"📝 此操作已同步到 Bot A 和 Bot B"
                )
                logger.info(f"Super admin {user.id} confirmed deletion of admin {user_id}")
        elif operation == 'disable_user':
            user_id = data.get('user_id')
            if user_id:
                # Execute disable user
                from database import db
                conn = db.connect()
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE users 
                    SET status = 'disabled', updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()
                cursor.close()
                
                from repositories.admin_logs_repository import AdminLogsRepository
                AdminLogsRepository.log_operation(
                    admin_id=user.id,
                    operation_type="update_user",
                    target_type="user",
                    target_id=user_id,
                    details="disable_user",
                    result="success"
                )
                
                await update.message.reply_text(f"✅ 已确认禁用用户 {user_id}")
                logger.info(f"Admin {user.id} confirmed disabling user {user_id}")
        elif operation == 'batch_set_vip':
            user_ids = data.get('user_ids')
            vip_level = data.get('vip_level')
            if user_ids and vip_level is not None:
                # Execute batch set VIP
                from services.batch_user_service import BatchUserService
                result = BatchUserService.batch_set_vip(user_ids, vip_level)
                
                from repositories.admin_logs_repository import AdminLogsRepository
                AdminLogsRepository.log_operation(
                    admin_id=user.id,
                    operation_type="batch_update_user",
                    target_type="user",
                    target_id=0,
                    details=f"batch_set_vip level={vip_level} count={result['success_count']}",
                    result="success" if result['failed_count'] == 0 else "partial"
                )
                
                message = (
                    f"✅ 已确认批量设置VIP\n\n"
                    f"成功：{result['success_count']} 个用户\n"
                )
                if result['failed_count'] > 0:
                    message += f"失败：{result['failed_count']} 个用户\n"
                message += f"\nVIP等级已设置为：{vip_level}"
                
                await update.message.reply_text(message, parse_mode="HTML")
                logger.info(f"Admin {user.id} confirmed batch set VIP level {vip_level} for {result['success_count']} users")
        elif operation == 'batch_disable_users' or operation == 'batch_enable_users':
            user_ids = data.get('user_ids')
            disable = data.get('disable', True)
            if user_ids:
                # Execute batch disable/enable
                from services.batch_user_service import BatchUserService
                result = BatchUserService.batch_disable_users(user_ids, disable)
                
                from repositories.admin_logs_repository import AdminLogsRepository
                action = 'disable' if disable else 'enable'
                AdminLogsRepository.log_operation(
                    admin_id=user.id,
                    operation_type="batch_update_user",
                    target_type="user",
                    target_id=0,
                    details=f"batch_{action} count={result['success_count']}",
                    result="success" if result['failed_count'] == 0 else "partial"
                )
                
                action_text = "禁用" if disable else "启用"
                message = (
                    f"✅ 已确认批量{action_text}用户\n\n"
                    f"成功：{result['success_count']} 个用户\n"
                )
                if result['failed_count'] > 0:
                    message += f"失败：{result['failed_count']} 个用户\n"
                
                await update.message.reply_text(message, parse_mode="HTML")
                logger.info(f"Admin {user.id} confirmed batch {action} {result['success_count']} users")
        elif operation == 'delete_group':
            group_id = data.get('group_id')
            if group_id:
                # Execute delete group
                from repositories.group_repository import GroupRepository
                if GroupRepository.delete_group(group_id):
                    from repositories.admin_logs_repository import AdminLogsRepository
                    AdminLogsRepository.log_operation(
                        admin_id=user.id,
                        operation_type="delete_group",
                        target_type="group",
                        target_id=group_id,
                        details=f"deleted group {group_id}",
                        result="success"
                    )
                    await update.message.reply_text(
                        f"✅ 已确认删除群组：{group_id}\n\n"
                        f"⚠️ 群组数据已从管理系统中移除",
                        parse_mode="MarkdownV2"
                    )
                    logger.info(f"Admin {user.id} confirmed deletion of group {group_id}")
                else:
                    await update.message.reply_text("❌ 删除群组失败")
        else:
            await update.message.reply_text(f"❌ 未知的操作类型：{operation}")
    
    # Delete group command
    async def delgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /delgroup command - delete group"""
        from admin_checker import is_admin
        from repositories.group_repository import GroupRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供群组ID\n格式：`/delgroup <group_id>`\n\n"
                "⚠️ 删除操作不可恢复",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            group_id = int(args[0])
            
            # Check for confirmation
            from services.confirmation_service import ConfirmationService
            confirmation = ConfirmationService.get_confirmation(user.id)
            
            if confirmation and confirmation['operation'] == 'delete_group' and confirmation['data'].get('group_id') == group_id:
                # Confirmed, proceed
                ConfirmationService.confirm_operation(user.id)  # Clear confirmation
                
                if GroupRepository.delete_group(group_id):
                    # Log operation
                    from repositories.admin_logs_repository import AdminLogsRepository
                    AdminLogsRepository.log_operation(
                        admin_id=user.id,
                        operation_type="delete_group",
                        target_type="group",
                        target_id=group_id,
                        details=f"deleted group {group_id}",
                        result="success"
                    )
                    await update.message.reply_text(
                        f"✅ 已删除群组：{group_id}\n\n"
                        f"⚠️ 群组数据已从管理系统中移除",
                        parse_mode="MarkdownV2"
                    )
                    logger.info(f"Admin {user.id} deleted group {group_id}")
                else:
                    await update.message.reply_text("❌ 群组不存在或删除失败")
            else:
                # First time, require confirmation
                ConfirmationService.create_confirmation(
                    user.id,
                    'delete_group',
                    {'group_id': group_id}
                )
                await update.message.reply_text(
                    f"⚠️ <b>确认删除群组</b>\n\n"
                    f"您将要删除群组：<code>{group_id}</code>\n\n"
                    f"⚠️ 此操作不可恢复！\n\n"
                    f"请再次执行相同命令确认：\n"
                    f"<code>/delgroup {group_id}</code>\n\n"
                    f"或者发送 <code>/confirm</code> 确认删除",
                    parse_mode="HTML"
                )
                
        except ValueError:
            await update.message.reply_text("❌ 无效的群组ID")
        except Exception as e:
            logger.error(f"Error in delgroup_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 删除失败，请稍后再试")
    
    # Group verify command
    async def group_verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /group_verify command - enable/disable group verification"""
        from admin_checker import is_admin
        from repositories.group_repository import GroupRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 2:
            await update.message.reply_text(
                "❌ 请提供群组ID和操作\n格式：`/group_verify <group_id> <enable|disable>`\n\n"
                "示例：`/group_verify -1001234567890 enable`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            group_id = int(args[0])
            action = args[1].lower()
            
            if action not in ["enable", "disable"]:
                await update.message.reply_text("❌ 操作必须是 enable 或 disable")
                return
            
            enabled = action == "enable"
            GroupRepository.set_verification_enabled(group_id, enabled)
            
            # Log operation
            from repositories.admin_logs_repository import AdminLogsRepository
            AdminLogsRepository.log_operation(
                admin_id=user.id,
                operation_type="update_group",
                target_type="group",
                target_id=group_id,
                details=f"verification_enabled={enabled}",
                result="success"
            )
            action_text = "启用" if enabled else "禁用"
            await update.message.reply_text(
                f"✅ 已{action_text}群组 {group_id} 的验证功能",
                parse_mode="MarkdownV2"
            )
            logger.info(f"Admin {user.id} {'enabled' if enabled else 'disabled'} verification for group {group_id}")
            
        except ValueError:
            await update.message.reply_text("❌ 无效的群组ID")
        except Exception as e:
            logger.error(f"Error in group_verify_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 操作失败，请稍后再试")
    
    # Group mode command
    async def group_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /group_mode command - set group verification mode"""
        from admin_checker import is_admin
        from repositories.verification_repository import VerificationRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 2:
            await update.message.reply_text(
                "❌ 请提供群组ID和验证模式\n格式：`/group_mode <group_id> <question|manual>`\n\n"
                "示例：`/group_mode -1001234567890 question`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            group_id = int(args[0])
            mode = args[1].lower()
            
            if mode not in ["question", "manual"]:
                await update.message.reply_text("❌ 验证模式必须是 question 或 manual")
                return
            
            VerificationRepository.create_or_update_config(group_id, verification_mode=mode)
            
            mode_text = "问题验证" if mode == "question" else "手动验证"
            await update.message.reply_text(
                f"✅ 已设置群组 {group_id} 的验证模式为：{mode_text}",
                parse_mode="MarkdownV2"
            )
            logger.info(f"Admin {user.id} set verification mode {mode} for group {group_id}")
            
        except ValueError:
            await update.message.reply_text("❌ 无效的群组ID")
        except Exception as e:
            logger.error(f"Error in group_mode_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 操作失败，请稍后再试")
    
    # Pass/Reject user commands for verification
    async def pass_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pass_user command - approve user verification"""
        from admin_checker import is_admin
        from repositories.group_repository import GroupRepository
        from repositories.verification_repository import VerificationRepository
        from database import db
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 2:
            await update.message.reply_text(
                "❌ 请提供用户ID和群组ID\n格式：`/pass_user <user_id> <group_id>`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            user_id = int(args[0])
            group_id = int(args[1])
            
            # Verify member
            GroupRepository.verify_member(group_id, user_id)
            
            # Update verification record
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE verification_records 
                SET result = 'passed', completed_at = CURRENT_TIMESTAMP
                WHERE group_id = ? AND user_id = ? AND result = 'pending'
            """, (group_id, user_id))
            conn.commit()
            cursor.close()
            
            # Log operation
            from repositories.admin_logs_repository import AdminLogsRepository
            AdminLogsRepository.log_operation(
                admin_id=user.id,
                operation_type="verify_user",
                target_type="user",
                target_id=user_id,
                details=f"group_id={group_id}, result=passed",
                result="success"
            )
            await update.message.reply_text(
                f"✅ 已通过用户 {user_id} 在群组 {group_id} 的审核",
                parse_mode="MarkdownV2"
            )
            logger.info(f"Admin {user.id} approved user {user_id} in group {group_id}")
            
        except ValueError:
            await update.message.reply_text("❌ 无效的用户ID或群组ID")
        except Exception as e:
            logger.error(f"Error in pass_user_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 操作失败，请稍后再试")
    
    async def reject_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reject_user command - reject user verification"""
        from admin_checker import is_admin
        from repositories.group_repository import GroupRepository
        from database import db
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 2:
            await update.message.reply_text(
                "❌ 请提供用户ID和群组ID\n格式：`/reject_user <user_id> <group_id>`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            user_id = int(args[0])
            group_id = int(args[1])
            
            # Reject member
            GroupRepository.reject_member(group_id, user_id)
            
            # Update verification record
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE verification_records 
                SET result = 'rejected', completed_at = CURRENT_TIMESTAMP
                WHERE group_id = ? AND user_id = ? AND result = 'pending'
            """, (group_id, user_id))
            conn.commit()
            cursor.close()
            
            await update.message.reply_text(
                f"❌ 已拒绝用户 {user_id} 在群组 {group_id} 的审核",
                parse_mode="MarkdownV2"
            )
            logger.info(f"Admin {user.id} rejected user {user_id} in group {group_id}")
            
        except ValueError:
            await update.message.reply_text("❌ 无效的用户ID或群组ID")
        except Exception as e:
            logger.error(f"Error in reject_user_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 操作失败，请稍后再试")
    
    # Group detail command
    async def group_detail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /group_detail command - show group details"""
        from admin_checker import is_admin
        from handlers.message_handlers import handle_admin_group_detail
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args or len(args) < 1:
            await update.message.reply_text(
                "❌ 请提供群组ID\n格式：`/group_detail <group_id>`",
                parse_mode="MarkdownV2"
            )
            return
        
        try:
            group_id = int(args[0])
            await handle_admin_group_detail(update, context, group_id)
        except ValueError:
            await update.message.reply_text("❌ 无效的群组ID")
        except Exception as e:
            logger.error(f"Error in group_detail_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 查看失败，请稍后再试")
    
    # Register all new commands
    application.add_handler(CommandHandler("user_detail", user_detail_command))
    application.add_handler(CommandHandler("set_vip", set_vip_command))
    application.add_handler(CommandHandler("disable_user", disable_user_command))
    application.add_handler(CommandHandler("enable_user", enable_user_command))
    application.add_handler(CommandHandler("batch_set_vip", batch_set_vip_command))
    application.add_handler(CommandHandler("batch_disable_users", batch_disable_users_command))
    application.add_handler(CommandHandler("batch_enable_users", batch_enable_users_command))
    application.add_handler(CommandHandler("batch_export_users", batch_export_users_command))
    application.add_handler(CommandHandler("delword", delword_command))
    application.add_handler(CommandHandler("editword", editword_command))
    application.add_handler(CommandHandler("deladmin", deladmin_command))
    application.add_handler(CommandHandler("delgroup", delgroup_command))
    application.add_handler(CommandHandler("confirm", confirm_command))
    application.add_handler(CommandHandler("group_verify", group_verify_command))
    application.add_handler(CommandHandler("group_mode", group_mode_command))
    application.add_handler(CommandHandler("pass_user", pass_user_command))
    application.add_handler(CommandHandler("reject_user", reject_user_command))
    application.add_handler(CommandHandler("group_detail", group_detail_command))
    
    # Export data commands
    async def export_words_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /export_words command - export sensitive words"""
        from admin_checker import is_admin
        from repositories.sensitive_words_repository import SensitiveWordsRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        try:
            words = SensitiveWordsRepository.get_words()
            
            if not words:
                await update.message.reply_text("❌ 暂无敏感词可导出")
                return
            
            # Format as CSV
            action_map = {"warn": "警告", "delete": "删除", "ban": "封禁"}
            export_text = "ID,敏感词,动作\n"
            for word in words:
                action_text = action_map.get(word['action'], word['action'])
                word_text = word['word'].replace(',', '，')
                export_text += f"{word['word_id']},{word_text},{action_text}\n"
            
            # Telegram message limit is 4096 characters, send in parts if needed
            if len(export_text) <= 4000:
                await update.message.reply_text(
                    f"📋 敏感词导出列表（共 {len(words)} 个）：\n\n"
                    f"<code>{export_text}</code>\n\n"
                    f"💡 复制内容可导入到Excel",
                    parse_mode="HTML"
                )
            else:
                # Split into multiple messages
                lines = export_text.split('\n')
                header = lines[0] + '\n'
                remaining = '\n'.join(lines[1:])
                
                # Send header first
                await update.message.reply_text(
                    f"📋 敏感词导出列表（共 {len(words)} 个）：\n\n"
                    f"<code>{header}</code>",
                    parse_mode="HTML"
                )
                
                # Send data in chunks
                data_lines = remaining.split('\n')
                chunk = ""
                for line in data_lines:
                    if len(chunk + line + '\n') > 3500:
                        if chunk:
                            await update.message.reply_text(
                                f"<code>{chunk}</code>",
                                parse_mode="HTML"
                            )
                        chunk = line + '\n'
                    else:
                        chunk += line + '\n'
                
                if chunk.strip():
                    await update.message.reply_text(
                        f"<code>{chunk}</code>\n\n"
                        f"💡 导出完成",
                        parse_mode="HTML"
                    )
            
            # Log operation
            from repositories.admin_logs_repository import AdminLogsRepository
            AdminLogsRepository.log_operation(
                admin_id=user.id,
                operation_type="export",
                target_type="sensitive_word",
                details=f"count={len(words)}",
                result="success"
            )
            logger.info(f"Admin {user.id} exported {len(words)} sensitive words")
            
        except Exception as e:
            logger.error(f"Error in export_words_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 导出失败，请稍后再试")
    
    async def export_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /export_users command - export users data"""
        from admin_checker import is_admin
        from database import db
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        try:
            conn = db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, username, first_name, vip_level, status, 
                       total_transactions, total_amount, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT 1000
            """)
            users = cursor.fetchall()
            cursor.close()
            
            if not users:
                await update.message.reply_text("❌ 暂无用户数据可导出")
                return
            
            # Format as CSV
            export_text = "用户ID,用户名,姓名,VIP等级,状态,交易数,交易额,注册时间\n"
            for user_data in users:
                username = (user_data['username'] or '').replace(',', '，')
                first_name = (user_data['first_name'] or '').replace(',', '，')
                status_text = "活跃" if user_data['status'] == 'active' else "禁用"
                export_text += (
                    f"{user_data['user_id']},{username},{first_name},"
                    f"{user_data['vip_level'] or 0},{status_text},"
                    f"{user_data['total_transactions'] or 0},{user_data['total_amount'] or 0},"
                    f"{user_data['created_at'] or ''}\n"
                )
            
            # Send in parts if too long
            if len(export_text) <= 4000:
                await update.message.reply_text(
                    f"📋 用户数据导出（共 {len(users)} 条）：\n\n"
                    f"<code>{export_text}</code>\n\n"
                    f"💡 复制内容可导入到Excel",
                    parse_mode="HTML"
                )
            else:
                # Send header first
                header = "用户ID,用户名,姓名,VIP等级,状态,交易数,交易额,注册时间\n"
                await update.message.reply_text(
                    f"📋 用户数据导出（共 {len(users)} 条）：\n\n"
                    f"<code>{header}</code>",
                    parse_mode="HTML"
                )
                
                # Send data in chunks
                data_lines = export_text[len(header):].split('\n')
                chunk = ""
                for line in data_lines:
                    if len(chunk + line + '\n') > 3500:
                        if chunk:
                            await update.message.reply_text(
                                f"<code>{chunk}</code>",
                                parse_mode="HTML"
                            )
                        chunk = line + '\n'
                    else:
                        chunk += line + '\n'
                
                if chunk.strip():
                    await update.message.reply_text(
                        f"<code>{chunk}</code>\n\n"
                        f"💡 导出完成",
                        parse_mode="HTML"
                    )
            
            # Log operation
            from repositories.admin_logs_repository import AdminLogsRepository
            AdminLogsRepository.log_operation(
                admin_id=user.id,
                operation_type="export",
                target_type="user",
                details=f"count={len(users)}",
                result="success"
            )
            logger.info(f"Admin {user.id} exported {len(users)} users")
            
        except Exception as e:
            logger.error(f"Error in export_users_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 导出失败，请稍后再试")
    
    async def import_words_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Import sensitive words from text"""
        from repositories.sensitive_words_repository import SensitiveWordsRepository
        from services.import_service import parse_sensitive_words_import
        from repositories.admin_logs_repository import AdminLogsRepository
        
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text("❌ 您不是管理员，无权限执行此操作")
            return
        
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ 请提供要导入的敏感词文本\n\n"
                "格式：`/import_words <文本内容>`\n\n"
                "支持格式：\n"
                "1. 每行一个词：`/import_words 词1\\n词2\\n词3`\n"
                "2. 逗号分隔（词,动作）：`/import_words 词1,delete\\n词2,warn`\n"
                "3. 多个词用空格分隔：`/import_words 词1 词2 词3`\n\n"
                "动作：warn（警告）、delete（删除）、ban（封禁）\n"
                "默认动作：warn\n\n"
                "示例：\n"
                "`/import_words 广告\\n诈骗,delete\\n赌博,ban`\n\n"
                "💡 也可以直接发送包含敏感词的文本消息，然后转发给机器人",
                parse_mode="MarkdownV2"
            )
            return
        
        # Join all arguments as text
        import_text = " ".join(args)
        # Also check if message has text (for multi-line input)
        if update.message.text and len(update.message.text.split('\n', 1)) > 1:
            # Use full message text if it contains newlines (likely formatted input)
            import_text = update.message.text.split(' ', 1)[1] if ' ' in update.message.text else update.message.text
        
        try:
            # Parse words from text
            words_data = parse_sensitive_words_import(import_text)
            
            if not words_data:
                await update.message.reply_text("❌ 未找到有效的敏感词")
                return
            
            if len(words_data) > 100:
                await update.message.reply_text("❌ 批量导入最多支持100个敏感词")
                return
            
            # Import words
            success_count = 0
            failed_count = 0
            
            for word, action in words_data:
                if SensitiveWordsRepository.add_word(None, word, action, user.id):
                    success_count += 1
                else:
                    failed_count += 1
            
            # Log operation
            AdminLogsRepository.log_operation(
                admin_id=user.id,
                operation_type="import_word",
                target_type="sensitive_word",
                details=f"count={len(words_data)}, success={success_count}, failed={failed_count}",
                result="success" if success_count > 0 else "failed"
            )
            
            await update.message.reply_text(
                f"✅ 批量导入完成\n"
                f"总数：{len(words_data)} 个\n"
                f"成功：{success_count} 个\n"
                f"失败：{failed_count} 个（可能已存在）\n\n"
                f"💡 使用 <code>/export_words</code> 查看所有敏感词",
                parse_mode="HTML"
            )
            logger.info(f"Admin {user.id} imported {success_count} sensitive words")
            
        except Exception as e:
            logger.error(f"Error in import_words_command: {e}", exc_info=True)
            await update.message.reply_text("❌ 导入失败，请检查格式后重试")
    
    application.add_handler(CommandHandler("export_words", export_words_command))
    application.add_handler(CommandHandler("export_users", export_users_command))
    application.add_handler(CommandHandler("import_words", import_words_command))
    
    # Chart command handlers are disabled - chart_handlers.py requires functions that don't exist in chart_service.py
    # If needed, these can be re-implemented using ChartService.generate_simple_bar() or other text-based chart methods
    # For now, commenting out to prevent import errors
    # from handlers.chart_handlers import (
    #     handle_chart_trend, handle_chart_volume,
    #     handle_chart_users, handle_chart_price
    # )
    # 
    # async def chart_trend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     """Handle /chart_trend command"""
    #     days = 7
    #     if context.args and len(context.args) > 0:
    #         try:
    #             days = int(context.args[0])
    #             if days not in [7, 30]:
    #                 days = 7
    #         except ValueError:
    #             pass
    #     await handle_chart_trend(update, context, days=days)
    # 
    # async def chart_volume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     """Handle /chart_volume command"""
    #     days = 7
    #     if context.args and len(context.args) > 0:
    #         try:
    #             days = int(context.args[0])
    #         except ValueError:
    #             pass
    #     await handle_chart_volume(update, context, days=days)
    # 
    # async def chart_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     """Handle /chart_users command"""
    #     top_n = 10
    #     if context.args and len(context.args) > 0:
    #         try:
    #             top_n = int(context.args[0])
    #             if top_n < 1 or top_n > 20:
    #                 top_n = 10
    #         except ValueError:
    #             pass
    #     await handle_chart_users(update, context, top_n=top_n)
    # 
    # async def chart_price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     """Handle /chart_price command"""
    #     days = 7
    #     if context.args and len(context.args) > 0:
    #         try:
    #             days = int(context.args[0])
    #             if days not in [1, 7, 30]:
    #                 days = 7
    #         except ValueError:
    #             pass
    #     await handle_chart_price(update, context, days=days)
    # 
    # application.add_handler(CommandHandler("chart_trend", chart_trend_command))
    # application.add_handler(CommandHandler("chart_volume", chart_volume_command))
    # application.add_handler(CommandHandler("chart_users", chart_users_command))
    # application.add_handler(CommandHandler("chart_price", chart_price_command))
    
    # Register message handler (for admin shortcuts and math/settlement)
    application.add_handler(get_message_handler())
    
    # Register callback handler (for inline keyboard buttons)
    application.add_handler(get_callback_handler())
    
    # 方案三：註冊 ChatMemberUpdated 事件處理器，自動追蹤機器人加入/離開群組
    application.add_handler(get_chat_member_handler())
    
    # Register group management handlers (verification and sensitive words)
    from handlers.group_management_handlers import get_group_message_handler, get_new_member_handler
    application.add_handler(get_group_message_handler())
    application.add_handler(get_new_member_handler())
    
    # 添加全局錯誤處理器，處理網絡超時等錯誤
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """處理未捕獲的錯誤"""
        from telegram.error import TimedOut, NetworkError, RetryAfter
        
        error = context.error
        if isinstance(error, (TimedOut, NetworkError)):
            logger.warning(f"網絡錯誤（已忽略）: {error}")
            return  # 網絡錯誤不影響機器人運行
        elif isinstance(error, RetryAfter):
            logger.warning(f"Telegram API 速率限制: {error}")
            return
        else:
            logger.error(f"未處理的錯誤: {error}", exc_info=error)
    
    application.add_error_handler(error_handler)
    
    # Note: Chat member tracking is handled in multiple ways:
    # 1. ChatMemberUpdated events (when bot is added/removed from groups)
    # 2. Message handler via ensure_group_exists() (when bot receives messages from groups)
    
    
    logger.info("Bot B (OTC Group Management) starting...")
    logger.info(f"Database initialized at: {db.db_path}")
    logger.info(f"Admin markup: {db.get_admin_markup()}")
    logger.info(f"USDT address: {db.get_usdt_address() or 'Not set'}")
    
    # Start the bot
    # Reduce long polling timeout to avoid connection being closed by intermediate devices
    # Default timeout is 20s, reducing to 10s helps prevent NAT/firewall from closing idle connections
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        timeout=10,  # Reduce from default 20s to 10s to prevent connection timeout issues
        poll_interval=1.0  # Add 1s interval between polls to avoid excessive requests
    )


if __name__ == "__main__":
    main()

