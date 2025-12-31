"""
群組同步服務
在啟動時驗證並同步資料庫中的群組資訊
"""
import logging
import asyncio
from typing import List, Dict, Optional
from database import db
from telegram.error import TimedOut, NetworkError, RetryAfter

logger = logging.getLogger(__name__)


async def sync_groups_on_startup(bot) -> Dict[str, int]:
    """
    啟動時同步群組：驗證資料庫中所有已知群組，更新群組資訊
    
    Args:
        bot: Telegram Bot 實例
        
    Returns:
        統計資訊字典：{'total': 總數, 'verified': 驗證成功, 'failed': 驗證失敗, 'updated': 更新數量}
    """
    logger.info("🔄 開始同步群組資訊...")
    
    stats = {
        'total': 0,
        'verified': 0,
        'failed': 0,
        'updated': 0
    }
    
    try:
        # 從資料庫獲取所有已知群組
        conn = db.connect()
        cursor = conn.cursor()
        
        # 獲取所有群組（包括非活躍的）
        cursor.execute("""
            SELECT DISTINCT group_id, group_title, is_active
            FROM group_settings
            ORDER BY updated_at DESC
        """)
        groups_from_settings = cursor.fetchall()
        
        # 獲取有交易記錄的群組
        cursor.execute("""
            SELECT DISTINCT group_id
            FROM otc_transactions
            WHERE group_id IS NOT NULL
        """)
        groups_from_transactions = [row[0] for row in cursor.fetchall()]
        
        # 合併所有群組 ID（去重）
        all_group_ids = set()
        group_titles = {}
        
        for row in groups_from_settings:
            group_id = row['group_id']
            all_group_ids.add(group_id)
            group_titles[group_id] = row['group_title']
        
        for group_id in groups_from_transactions:
            all_group_ids.add(group_id)
        
        stats['total'] = len(all_group_ids)
        
        if stats['total'] == 0:
            logger.info("📭 資料庫中沒有群組記錄")
            return stats
        
        logger.info(f"📊 找到 {stats['total']} 個群組記錄，開始驗證...")
        
        # 驗證每個群組（限制每次驗證的數量，避免 API 限制）
        verified_groups = []
        failed_groups = []
        
        # 分批處理，每批 10 個（減少並發，避免超時），避免觸發速率限制
        group_list = list(all_group_ids)
        batch_size = 10  # 減少批次大小
        
        for i in range(0, len(group_list), batch_size):
            batch = group_list[i:i + batch_size]
            
            # 並發驗證這批群組（使用 return_exceptions 捕獲所有異常）
            tasks = [verify_group(bot, group_id, group_titles.get(group_id)) for group_id in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for group_id, result in zip(batch, results):
                if isinstance(result, Exception):
                    failed_groups.append(group_id)
                    logger.debug(f"❌ 群組 {group_id} 驗證失敗: {result}")
                    stats['failed'] += 1
                elif result:
                    verified_groups.append((group_id, result))
                    stats['verified'] += 1
                else:
                    failed_groups.append(group_id)
                    stats['failed'] += 1
            
            # 批次之間添加延遲，避免觸發速率限制
            if i + batch_size < len(group_list):
                await asyncio.sleep(2)  # 增加延遲時間
        
        # 更新資料庫中的群組資訊
        for group_id, group_info in verified_groups:
            try:
                conn = db.connect()
                cursor = conn.cursor()
                
                # 檢查是否需要更新
                cursor.execute("""
                    SELECT group_title, is_active FROM group_settings WHERE group_id = ?
                """, (group_id,))
                existing = cursor.fetchone()
                
                # 獲取驗證時獲取的實際標題
                new_title = group_info.get('title')
                
                # 添加日誌記錄，追蹤標題獲取情況
                if new_title:
                    logger.info(f"📝 群組 {group_id} 驗證獲取的標題: '{new_title}'")
                else:
                    logger.warning(f"⚠️ 群組 {group_id} 驗證成功但未獲取到標題")
                
                if existing:
                    old_title = existing['group_title']
                    logger.debug(f"📋 群組 {group_id} 資料庫中的標題: '{old_title}'")
                    
                    # 驗證成功意味著機器人在群組中，必須確保 is_active = 1
                    # 檢查是否需要更新
                    title_changed = False
                    if new_title and new_title != old_title:
                        title_changed = True
                        logger.info(f"🔄 群組 {group_id} 標題變化: '{old_title}' -> '{new_title}'")
                    
                    status_changed = existing['is_active'] != 1
                    
                    # 驗證成功時，無論如何都要更新 updated_at 和確保 is_active = 1
                    if title_changed or status_changed:
                        # 確保使用有效的標題
                        update_title = new_title if new_title else old_title
                        
                        # 更新群組標題和狀態
                        cursor.execute("""
                            UPDATE group_settings 
                            SET group_title = ?,
                                is_active = 1,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE group_id = ?
                        """, (update_title, group_id))
                        conn.commit()
                        stats['updated'] += 1
                        logger.info(f"✅ 更新群組 {group_id}: 標題={title_changed}, 狀態={status_changed}, 新標題='{update_title}'")
                    else:
                        # 即使標題和狀態都沒變，也要更新 updated_at（表示驗證成功）
                        # 這確保了資料庫記錄是最新的
                        cursor.execute("""
                            UPDATE group_settings 
                            SET updated_at = CURRENT_TIMESTAMP,
                                is_active = 1
                            WHERE group_id = ?
                        """, (group_id,))
                        conn.commit()
                        stats['updated'] += 1
                        logger.debug(f"✅ 更新群組 {group_id} 的驗證時間戳（標題未變: '{old_title}'）")
                else:
                    # 群組不在 group_settings 中，創建記錄
                    # 確保使用有效的標題
                    create_title = new_title if new_title else f"群組 {group_id}"
                    logger.info(f"🆕 創建新群組記錄 {group_id}，標題: '{create_title}'")
                    db.ensure_group_exists(group_id, create_title)
                    # 確保新創建的記錄 is_active = 1
                    cursor.execute("""
                        UPDATE group_settings 
                        SET is_active = 1,
                            group_title = ?
                        WHERE group_id = ?
                    """, (create_title, group_id))
                    conn.commit()
                    stats['updated'] += 1
                
            except Exception as e:
                logger.error(f"更新群組 {group_id} 資訊失敗: {e}")
        
        # 標記無法訪問的群組為非活躍
        for group_id in failed_groups:
            try:
                cursor.execute("""
                    UPDATE group_settings 
                    SET is_active = 0,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE group_id = ?
                """, (group_id,))
                conn.commit()
            except Exception as e:
                logger.error(f"標記群組 {group_id} 為非活躍失敗: {e}")
        
        logger.info(
            f"✅ 群組同步完成: 總數 {stats['total']}, "
            f"驗證成功 {stats['verified']}, 驗證失敗 {stats['failed']}, 更新 {stats['updated']}"
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"同步群組時發生錯誤: {e}", exc_info=True)
        return stats


async def verify_group(bot, group_id: int, known_title: str = None, max_retries: int = 2) -> Optional[Dict]:
    """
    驗證單個群組，檢查機器人是否仍在群組中並獲取群組資訊
    
    Args:
        bot: Telegram Bot 實例
        group_id: 群組 ID
        known_title: 已知的群組標題（可選）
        max_retries: 最大重試次數
        
    Returns:
        群組資訊字典，如果無法訪問則返回 None
    """
    for attempt in range(max_retries + 1):
        try:
            # 使用 get_chat 驗證群組是否存在且機器人可以訪問
            # 添加超時處理
            chat = await asyncio.wait_for(
                bot.get_chat(group_id),
                timeout=10.0  # 10秒超時
            )
            
            # 檢查是否是群組或超級群組
            if chat.type not in ['group', 'supergroup']:
                return None
            
            # 獲取實際的群組標題
            actual_title = chat.title if chat.title else None
            if actual_title:
                logger.debug(f"✅ 群組 {group_id} 驗證成功，標題: '{actual_title}'")
            else:
                logger.warning(f"⚠️ 群組 {group_id} 驗證成功但標題為空")
            
            return {
                'group_id': group_id,
                'title': actual_title,
                'type': chat.type,
                'accessible': True
            }
            
        except (TimedOut, NetworkError, asyncio.TimeoutError) as e:
            # 網絡超時或錯誤，重試
            if attempt < max_retries:
                wait_time = (attempt + 1) * 2  # 遞增等待時間：2秒、4秒
                logger.debug(f"群組 {group_id} 驗證超時，{wait_time}秒後重試 (嘗試 {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
                continue
            else:
                logger.debug(f"群組 {group_id} 驗證失敗（超時）: {e}")
                return None
                
        except RetryAfter as e:
            # Telegram API 要求等待
            wait_time = e.retry_after + 1
            logger.warning(f"Telegram API 速率限制，等待 {wait_time} 秒...")
            await asyncio.sleep(wait_time)
            if attempt < max_retries:
                continue
            else:
                return None
                
        except Exception as e:
            # 其他錯誤（如群組不存在、無權訪問等）
            error_msg = str(e).lower()
            
            # 群組不存在或被刪除
            if 'chat not found' in error_msg or 'not found' in error_msg or 'chat_id is empty' in error_msg:
                logger.info(f"🗑️ 群組 {group_id} 不存在（chat not found），將標記為非活躍")
                return None
            
            # 機器人無權訪問或被踢出
            if 'unauthorized' in error_msg or 'forbidden' in error_msg or 'bot was kicked' in error_msg:
                logger.info(f"🚫 群組 {group_id} 機器人無權訪問或被移除，將標記為非活躍")
                return None
            
            # 其他錯誤記錄但不重試
            logger.debug(f"群組 {group_id} 驗證失敗: {e}")
            return None
    
    return None
