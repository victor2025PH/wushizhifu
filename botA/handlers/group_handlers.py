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
from database.verification_repository import VerificationRepository
from services.verification_service import VerificationService
from utils.text_utils import escape_markdown_v2

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.chat.type.in_(["group", "supergroup"]))
async def handle_group_message(message: Message):
    """Handle messages in groups (verification answers and sensitive word filtering)"""
    try:
        # Skip if message is from bot or command
        if message.from_user.is_bot:
            return
        
        if not message.text:
            return
        
        group_id = message.chat.id
        user_id = message.from_user.id
        
        # Check if user is pending verification
        if not GroupRepository.is_member_verified(group_id, user_id):
            # Check if user has a pending verification record
            record = VerificationRepository.get_verification_record(group_id, user_id)
            if record and record.get('result') == 'pending':
                # This is a verification answer
                is_correct, updated_record, error_msg = VerificationService.check_user_answer(
                    group_id, user_id, message.text
                )
                
                if is_correct:
                    # Answer is correct, verify member
                    GroupRepository.verify_member(group_id, user_id)
                    
                    # Send welcome message
                    config = VerificationRepository.get_verification_config(group_id)
                    welcome_msg = "✅ 验证通过！欢迎加入群组！"
                    if config and config.get('welcome_message'):
                        welcome_msg = config['welcome_message']
                    
                    await message.reply(welcome_msg)
                    logger.info(f"User {user_id} passed verification in group {group_id}")
                else:
                    # Answer is wrong or other error
                    if error_msg:
                        await message.reply(f"❌ {error_msg}")
                    
                    # Check if rejected
                    if updated_record and updated_record.get('result') == 'rejected':
                        try:
                            await message.chat.ban(user_id=user_id)
                            await message.answer(f"⏰ 验证失败，用户已被移出群组")
                            logger.info(f"User {user_id} rejected and removed from group {group_id}")
                        except Exception as e:
                            logger.error(f"Error removing user from group: {e}")
                    
                    logger.info(f"User {user_id} verification attempt in group {group_id}: {error_msg}")
                
                # Don't process as regular message - delete the message
                try:
                    await message.delete()
                except:
                    pass
                return
            else:
                # User is pending but no verification record - restrict messaging
                try:
                    await message.delete()
                    await message.answer(
                        f"⚠️ 您尚未完成验证，请在私聊中回答问题或等待管理员审核",
                        reply_to_message_id=message.message_id if message.message_id else None
                    )
                except:
                    pass
                return
        
        # Check if message is a command (skip sensitive word check for commands)
        if message.text.startswith('/'):
            return
        
        # Check sensitive words
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
            
            # Get verification config
            config = VerificationRepository.get_verification_config(group_id)
            verification_mode = config.get('verification_mode', 'question') if config else 'question'
            
            if verification_mode == 'question':
                # Start question-based verification
                verification_result = VerificationService.start_verification(group_id, user.id)
                
                if verification_result and verification_result.get('question'):
                    question = verification_result['question']
                    question_message = VerificationService.format_question_message(question)
                    
                    # Send question to user via private message
                    try:
                        await event.bot.send_message(
                            chat_id=user.id,
                            text=question_message,
                            parse_mode="MarkdownV2"
                        )
                    except Exception as e:
                        logger.warning(f"Could not send private message to user {user.id}: {e}")
                        # Fallback: send in group
                        await event.answer(question_message, parse_mode="MarkdownV2")
                    
                    logger.info(f"Sent verification question to user {user.id} in group {group_id}")
                else:
                    # Fallback to manual verification
                    await event.answer(
                        f"👋 歡迎 {user.first_name or user.username or '新成員'} 加入群組！\n"
                        f"⏳ 您的加入請求正在審核中，請等待管理員審核。"
                    )
            else:
                # Manual verification mode
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

