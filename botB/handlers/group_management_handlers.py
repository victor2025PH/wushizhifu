"""
Group management handlers (adapted from Bot A)
Handles group verification, sensitive words filtering, and new member processing
"""
import logging
from telegram import Update
from telegram.ext import MessageHandler, ChatMemberHandler, filters, ContextTypes
from telegram.constants import ChatMemberStatus
from repositories.group_repository import GroupRepository
from repositories.sensitive_words_repository import SensitiveWordsRepository
from repositories.verification_repository import VerificationRepository
from services.verification_service import VerificationService

logger = logging.getLogger(__name__)


async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages in groups (verification answers and sensitive word filtering)"""
    try:
        message = update.message
        if not message:
            return
        
        # Skip if message is from bot or command
        if message.from_user.is_bot:
            return
        
        if not message.text:
            return
        
        group_id = message.chat.id
        user_id = message.from_user.id
        
        # Check if group has verification enabled before checking user status
        group = GroupRepository.get_group(group_id)
        verification_enabled = group and group.get('verification_enabled', False)
        
        # Check if user is pending verification (only if verification is enabled)
        if verification_enabled and not GroupRepository.is_member_verified(group_id, user_id):
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
                    
                    await message.reply_text(welcome_msg)
                    logger.info(f"User {user_id} passed verification in group {group_id}")
                else:
                    # Answer is wrong or other error
                    if error_msg:
                        await message.reply_text(f"❌ {error_msg}")
                    
                    # Check if rejected
                    if updated_record and updated_record.get('result') == 'rejected':
                        try:
                            await context.bot.ban_chat_member(chat_id=group_id, user_id=user_id)
                            await message.reply_text(f"⏰ 验证失败，用户已被移出群组")
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
                    await message.reply_text(
                        f"⚠️ 您尚未完成验证，请在私聊中回答问题或等待管理员审核"
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
                await message.reply_text(f"⚠️ 消息包含敏感詞：`{sensitive_word['word']}`，已自動刪除", parse_mode="MarkdownV2")
                logger.info(f"Deleted message in group {group_id} due to sensitive word: {sensitive_word['word']}")
            
            elif action == 'ban':
                try:
                    await message.delete()
                    await context.bot.ban_chat_member(chat_id=group_id, user_id=message.from_user.id)
                    await message.reply_text(f"🚫 用戶因使用敏感詞 `{sensitive_word['word']}` 已被封禁", parse_mode="MarkdownV2")
                    logger.info(f"Banned user {message.from_user.id} in group {group_id} due to sensitive word")
                except Exception as e:
                    logger.error(f"Error banning user: {e}")
            
            elif action == 'warn':
                await message.reply_text(f"⚠️ 請注意，消息包含敏感詞：`{sensitive_word['word']}`", parse_mode="MarkdownV2")
    
    except Exception as e:
        logger.error(f"Error in handle_group_message: {e}", exc_info=True)


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle member status changes in group (join/leave/kick)"""
    try:
        chat_member = update.chat_member
        if not chat_member:
            return
        
        # 獲取狀態變化信息
        new_status = chat_member.new_chat_member.status if chat_member.new_chat_member else None
        old_status = chat_member.old_chat_member.status if chat_member.old_chat_member else None
        
        group_id = chat_member.chat.id
        member = chat_member.new_chat_member.user
        member_name = member.first_name or member.username or '成員'
        
        # 跳過機器人
        if member.is_bot:
            return
        
        # 判斷狀態變化方向
        is_joining = (
            new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] and
            old_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED, None]
        )
        is_leaving = (
            new_status == ChatMemberStatus.LEFT and
            old_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR, ChatMemberStatus.RESTRICTED]
        )
        is_kicked = (
            new_status == ChatMemberStatus.KICKED and
            old_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR, ChatMemberStatus.RESTRICTED]
        )
        
        # ========== 處理成員加入 ==========
        if is_joining:
            logger.info(f"Member {member.id} ({member_name}) joined group {group_id}")
            
            # Get group settings
            group = GroupRepository.get_group(group_id)
            
            if group and group.get('verification_enabled'):
                # Add to pending verification
                GroupRepository.add_member(group_id, member.id, status='pending')
                
                # Get verification config
                config = VerificationRepository.get_verification_config(group_id)
                verification_mode = config.get('verification_mode', 'question') if config else 'question'
                
                if verification_mode == 'question':
                    # Start question-based verification
                    verification_result = VerificationService.start_verification(group_id, member.id)
                    
                    if verification_result and verification_result.get('question'):
                        question = verification_result['question']
                        question_message = VerificationService.format_question_message(question)
                        
                        # Send question to user via private message
                        try:
                            await context.bot.send_message(
                                chat_id=member.id,
                                text=question_message,
                                parse_mode="HTML"
                            )
                        except Exception as e:
                            logger.warning(f"Could not send private message to user {member.id}: {e}")
                            # Fallback: send in group
                            await context.bot.send_message(
                                chat_id=group_id,
                                text=question_message,
                                parse_mode="HTML"
                            )
                        
                        logger.info(f"Sent verification question to user {member.id} in group {group_id}")
                    else:
                        # Fallback to manual verification
                        await context.bot.send_message(
                            chat_id=group_id,
                            text=(
                                f"👋 歡迎 {member_name} 加入群組！\n"
                                f"⏳ 您的加入請求正在審核中，請等待管理員審核。"
                            )
                        )
                else:
                    # Manual verification mode
                    await context.bot.send_message(
                        chat_id=group_id,
                        text=(
                            f"👋 歡迎 {member_name} 加入群組！\n"
                            f"⏳ 您的加入請求正在審核中，請等待管理員審核。"
                        )
                    )
                
                logger.info(f"New member {member.id} joined group {group_id}, pending verification")
            else:
                # No verification required
                GroupRepository.add_member(group_id, member.id, status='verified')
                
                await context.bot.send_message(
                    chat_id=group_id,
                    text=f"👋 歡迎 {member_name} 加入群組！"
                )
        
        # ========== 處理成員離開 ==========
        elif is_leaving:
            logger.info(f"Member {member.id} ({member_name}) left group {group_id}")
            # 可選：發送離開消息（目前不發送，避免打擾）
            # await context.bot.send_message(
            #     chat_id=group_id,
            #     text=f"👋 {member_name} 離開了群組"
            # )
        
        # ========== 處理成員被踢 ==========
        elif is_kicked:
            logger.info(f"Member {member.id} ({member_name}) was kicked from group {group_id}")
            # 可選：發送被踢消息（目前不發送，避免打擾）
            # await context.bot.send_message(
            #     chat_id=group_id,
            #     text=f"🚫 {member_name} 已被移出群組"
            # )
    
    except Exception as e:
        logger.error(f"Error in handle_new_member: {e}", exc_info=True)


def get_group_message_handler():
    """Get message handler for group messages"""
    return MessageHandler(
        filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND,
        handle_group_message
    )


def get_new_member_handler():
    """Get chat member handler for new members"""
    return ChatMemberHandler(handle_new_member, chat_member_types=ChatMemberHandler.CHAT_MEMBER)
