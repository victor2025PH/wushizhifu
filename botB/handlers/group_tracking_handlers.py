"""
群組追蹤處理器
處理機器人加入/離開群組的事件，自動記錄到資料庫
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ChatMemberHandler
from telegram.constants import ChatMemberStatus
from database import db

logger = logging.getLogger(__name__)


async def handle_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    處理 ChatMemberUpdated 事件
    當機器人被加入或離開群組時自動記錄
    """
    try:
        if not update.chat_member:
            return
        
        chat_member = update.chat_member
        
        # 只處理機器人自己的狀態變化
        try:
            bot_id = context.bot.id
        except Exception as e:
            logger.error(f"無法獲取 bot.id: {e}")
            return
        
        if not chat_member.new_chat_member or not chat_member.new_chat_member.user:
            return
        
        # 檢查是否是機器人自己的狀態變化
        if chat_member.new_chat_member.user.id != bot_id:
            return
        
        new_status = chat_member.new_chat_member.status
        old_status = chat_member.old_chat_member.status if chat_member.old_chat_member else None
        
        chat = chat_member.chat
        if not chat or chat.type not in ['group', 'supergroup']:
            return
        
        group_id = chat.id
        group_title = getattr(chat, 'title', None) or f"群組 {group_id}"
        
        # 機器人被加入群組
        if new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            if old_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED, None]:
                # 機器人剛被加入群組
                db.ensure_group_exists(group_id, group_title)
                logger.info(f"✅ 機器人被加入群組: {group_id} - {group_title}")
                
                # 更新群組標題和狀態
                conn = db.connect()
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        UPDATE group_settings 
                        SET group_title = ?,
                            is_active = 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE group_id = ?
                    """, (group_title, group_id))
                    conn.commit()
                except Exception as e:
                    logger.error(f"更新群組資訊失敗: {e}")
        
        # 機器人離開或被踢出群組
        elif new_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
            # 標記群組為非活躍狀態，但不刪除記錄
            conn = db.connect()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE group_settings 
                    SET is_active = 0,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE group_id = ?
                """, (group_id,))
                conn.commit()
                logger.info(f"⚠️ 機器人離開群組: {group_id} - {group_title}")
            except Exception as e:
                logger.error(f"更新群組狀態失敗: {e}")
    
    except Exception as e:
        logger.error(f"處理 ChatMemberUpdated 事件失敗: {e}", exc_info=True)


def get_chat_member_handler():
    """獲取 ChatMemberHandler"""
    return ChatMemberHandler(handle_chat_member_update)
