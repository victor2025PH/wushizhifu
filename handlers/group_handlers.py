"""
Group-related handlers (group verification, sensitive words filtering)
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER, ADMINISTRATOR, CREATOR
from database.group_repository import GroupRepository
from database.sensitive_words_repository import SensitiveWordsRepository
from database.admin_repository import AdminRepository

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.chat.type.in_(["group", "supergroup"]))
async def handle_group_message(message: Message):
    """Handle messages in groups (sensitive word filtering)"""
    try:
        # Skip if message is from bot or command
        if message.from_user.is_bot or message.text and message.text.startswith('/'):
            return
        
        if not message.text:
            return
        
        # Check sensitive words
        group_id = message.chat.id
        sensitive_word = SensitiveWordsRepository.check_message(message.text, group_id)
        
        if sensitive_word:
            action = sensitive_word.get('action', 'warn')
            
            if action == 'delete':
                await message.delete()
                await message.answer(f"⚠️ 消息包含敏感詞：`{sensitive_word['word']}`，已自動刪除", parse_mode="MarkdownV2")
                logger.info(f"Deleted message in group {group_id} due to sensitive word: {sensitive_word['word']}")
            
            elif action == 'ban':
                try:
                    await message.delete()
                    await message.chat.ban(user_id=message.from_user.id)
                    await message.answer(f"🚫 用戶因使用敏感詞 `{sensitive_word['word']}` 已被封禁", parse_mode="MarkdownV2")
                    logger.info(f"Banned user {message.from_user.id} in group {group_id} due to sensitive word")
                except Exception as e:
                    logger.error(f"Error banning user: {e}")
            
            elif action == 'warn':
                await message.reply(f"⚠️ 請注意，消息包含敏感詞：`{sensitive_word['word']}`", parse_mode="MarkdownV2")
    
    except Exception as e:
        logger.error(f"Error in handle_group_message: {e}", exc_info=True)


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=(KICKED | LEFT) >> (MEMBER | ADMINISTRATOR | CREATOR)))
async def handle_new_member(event: ChatMemberUpdated):
    """Handle new member joining group"""
    try:
        group_id = event.chat.id
        user = event.new_chat_member.user
        
        if user.is_bot:
            return
        
        # Get group settings
        group = GroupRepository.get_group(group_id)
        
        if group and group.get('verification_enabled'):
            # Add to pending verification
            GroupRepository.add_member(group_id, user.id, status='pending')
            
            # Notify admins
            await event.answer(
                f"👋 歡迎 {user.first_name or user.username or '新成員'} 加入群組！\n"
                f"⏳ 您的加入請求正在審核中，請等待管理員審核。"
            )
            
            logger.info(f"New member {user.id} joined group {group_id}, pending verification")
        else:
            # No verification required
            GroupRepository.add_member(group_id, user.id, status='verified')
            
            await event.answer(
                f"👋 歡迎 {user.first_name or user.username or '新成員'} 加入群組！"
            )
    
    except Exception as e:
        logger.error(f"Error in handle_new_member: {e}", exc_info=True)

