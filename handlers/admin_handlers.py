"""
Admin-related handlers (only visible to admins)
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from keyboards.main_kb import get_admin_keyboard, get_main_keyboard
from database.admin_repository import AdminRepository
from database.user_repository import UserRepository
from database.sensitive_words_repository import SensitiveWordsRepository
from database.group_repository import GroupRepository

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return AdminRepository.is_admin(user_id)


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Handle /admin command"""
    try:
        user_id = message.from_user.id
        
        if not is_admin(user_id):
            await message.answer("❌ 您不是管理員，無權限訪問此功能")
            return
        
        text = (
            "*⚙️ 管理員面板*\n\n"
            "請選擇要管理的功能："
        )
        
        await message.answer(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=get_admin_keyboard()
        )
        
        logger.info(f"Admin {user_id} accessed admin panel")
        
    except Exception as e:
        logger.error(f"Error in cmd_admin: {e}", exc_info=True)


@router.callback_query(F.data.startswith("admin_"))
async def callback_admin_menu(callback: CallbackQuery):
    """Handle admin menu callbacks"""
    try:
        user_id = callback.from_user.id
        
        if not is_admin(user_id):
            await callback.answer("❌ 您不是管理員", show_alert=True)
            return
        
        action = callback.data.split("_", 1)[1]
        
        if action == "users":
            await handle_admin_users(callback)
        elif action == "stats":
            await handle_admin_stats(callback)
        elif action == "words":
            await handle_admin_words(callback)
        elif action == "verify":
            await handle_admin_verify(callback)
        elif action == "group":
            await handle_admin_group(callback)
        elif action == "add":
            await handle_admin_add(callback)
        
    except Exception as e:
        logger.error(f"Error in callback_admin_menu: {e}", exc_info=True)
        await callback.answer("❌ 系統錯誤，請稍後再試", show_alert=True)


async def handle_admin_users(callback: CallbackQuery):
    """Handle admin users management"""
    from database.db import db
    
    cursor = db.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM users WHERE status = 'active'")
    active_users = cursor.fetchone()[0]
    
    text = (
        f"*👥 用戶管理*\n\n"
        f"總用戶數：{total_users}\n"
        f"活躍用戶：{active_users}\n\n"
        "功能開發中..."
    )
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


async def handle_admin_stats(callback: CallbackQuery):
    """Handle admin statistics"""
    from database.db import db
    from database.transaction_repository import TransactionRepository
    
    cursor = db.execute("SELECT COUNT(*) FROM transactions")
    total_transactions = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT COUNT(*) FROM transactions WHERE status = 'paid'")
    paid_transactions = cursor.fetchone()[0]
    
    cursor = db.execute("SELECT SUM(amount) FROM transactions WHERE status = 'paid'")
    total_amount = cursor.fetchone()[0] or 0
    
    text = (
        f"*📊 系統統計*\n\n"
        f"總交易數：{total_transactions}\n"
        f"成功交易：{paid_transactions}\n"
        f"總交易金額：¥{total_amount:,.2f}\n\n"
        "更多統計功能開發中..."
    )
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


async def handle_admin_words(callback: CallbackQuery):
    """Handle sensitive words management"""
    words = SensitiveWordsRepository.get_words()
    
    if not words:
        text = "*🚫 敏感詞管理*\n\n暫無敏感詞\n\n請使用 /addword <詞語> 添加"
    else:
        text = f"*🚫 敏感詞管理*\n\n*當前敏感詞列表 \\(共 {len(words)} 個\\)：*\n\n"
        for word in words[:10]:
            action_text = {"warn": "警告", "delete": "刪除", "ban": "封禁"}.get(word['action'], word['action'])
            text += f"• `{word['word']}` \\- {action_text}\n"
        
        if len(words) > 10:
            text += f"\n還有 {len(words) - 10} 個..."
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


async def handle_admin_verify(callback: CallbackQuery):
    """Handle group verification management"""
    # Get pending members from all groups
    from database.db import db
    
    cursor = db.execute("""
        SELECT gm.*, g.group_title 
        FROM group_members gm
        JOIN groups g ON gm.group_id = g.group_id
        WHERE gm.status = 'pending'
        ORDER BY gm.joined_at ASC
        LIMIT 10
    """)
    
    pending = cursor.fetchall()
    
    if not pending:
        text = "*✅ 群組審核*\n\n暫無待審核成員"
    else:
        text = f"*✅ 群組審核*\n\n*待審核成員 \\(共 {len(pending)} 人\\)：*\n\n"
        for member in pending:
            text += f"用戶ID：{member['user_id']}\n"
            text += f"群組：{member['group_title'] or member['group_id']}\n"
            text += f"加入時間：{member['joined_at']}\n\n"
        
        text += "功能開發中，請使用數據庫直接管理"
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


async def handle_admin_group(callback: CallbackQuery):
    """Handle group settings"""
    text = (
        "*⚙️ 群組設置*\n\n"
        "功能開發中...\n\n"
        "請使用命令管理群組設置"
    )
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


async def handle_admin_add(callback: CallbackQuery):
    """Handle add admin"""
    text = (
        "*👤 添加管理員*\n\n"
        "請使用命令：\n"
        "`/addadmin <user_id>`\n\n"
        "例如：\n"
        "`/addadmin 123456789`"
    )
    
    await callback.message.edit_text(
        text=text,
        parse_mode="MarkdownV2",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


@router.message(Command("addadmin"))
async def cmd_add_admin(message: Message):
    """Add admin command"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ 您不是管理員，無權限執行此操作")
            return
        
        args = message.text.split()
        if len(args) < 2:
            await message.answer("❌ 請提供用戶ID\n格式：`/addadmin <user_id>`", parse_mode="MarkdownV2")
            return
        
        try:
            user_id = int(args[1])
            if AdminRepository.add_admin(user_id, added_by=message.from_user.id):
                await message.answer(f"✅ 已添加管理員：{user_id}")
            else:
                await message.answer(f"❌ 添加失敗（可能已是管理員）")
        except ValueError:
            await message.answer("❌ 無效的用戶ID")
            
    except Exception as e:
        logger.error(f"Error in cmd_add_admin: {e}", exc_info=True)


@router.message(Command("addword"))
async def cmd_add_word(message: Message):
    """Add sensitive word command"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ 您不是管理員，無權限執行此操作")
            return
        
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            await message.answer("❌ 請提供敏感詞\n格式：`/addword <詞語> [action]`\n動作：warn, delete, ban", parse_mode="MarkdownV2")
            return
        
        word = args[1]
        action = args[2] if len(args) > 2 else "warn"
        
        if action not in ["warn", "delete", "ban"]:
            action = "warn"
        
        if SensitiveWordsRepository.add_word(None, word, action, message.from_user.id):
            await message.answer(f"✅ 已添加敏感詞：`{word}` (動作：{action})", parse_mode="MarkdownV2")
        else:
            await message.answer("❌ 添加失敗（可能已存在）")
            
    except Exception as e:
        logger.error(f"Error in cmd_add_word: {e}", exc_info=True)


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """Return to main menu"""
    from services.message_service import MessageService
    from services.user_service import UserService
    
    try:
        user = callback.from_user
        is_new = UserService.is_new_user(user.id)
        welcome_text = MessageService.generate_welcome_message(user, is_new)
        
        await callback.message.edit_text(
            text=welcome_text,
            parse_mode="MarkdownV2",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_main_menu: {e}", exc_info=True)
        await callback.answer("❌ 系統錯誤", show_alert=True)

