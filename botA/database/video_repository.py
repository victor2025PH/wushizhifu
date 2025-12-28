"""
Video repository for database operations
"""
from typing import Optional, Dict
from datetime import datetime
from database.db import db
import logging

logger = logging.getLogger(__name__)


class VideoRepository:
    """Repository for video config database operations"""
    
    @staticmethod
    def save_video_config(
        video_type: str,
        channel_id: int,
        message_id: int,
        file_id: str,
        file_unique_id: Optional[str] = None,
        file_size: Optional[int] = None,
        duration: Optional[int] = None,
        thumbnail_file_id: Optional[str] = None,
        updated_by: Optional[int] = None
    ) -> bool:
        """
        Save or update video configuration.
        
        Args:
            video_type: 'wechat' or 'alipay'
            channel_id: Telegram channel ID
            message_id: Message ID in channel
            file_id: Telegram file ID
            file_unique_id: Telegram file unique ID
            file_size: Video file size in bytes
            duration: Video duration in seconds
            thumbnail_file_id: Thumbnail file ID (optional)
            updated_by: Admin user ID who updated this
            
        Returns:
            True if successful
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if config exists
            cursor.execute("SELECT id FROM video_configs WHERE video_type = ?", (video_type,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing config
                cursor.execute("""
                    UPDATE video_configs 
                    SET channel_id = ?, message_id = ?, file_id = ?,
                        file_unique_id = ?, file_size = ?, duration = ?,
                        thumbnail_file_id = ?, updated_at = ?, updated_by = ?
                    WHERE video_type = ?
                """, (channel_id, message_id, file_id, file_unique_id, 
                      file_size, duration, thumbnail_file_id, now, updated_by, video_type))
                logger.info(f"Updated video config: {video_type}")
            else:
                # Insert new config
                cursor.execute("""
                    INSERT INTO video_configs 
                    (video_type, channel_id, message_id, file_id, file_unique_id,
                     file_size, duration, thumbnail_file_id, updated_at, updated_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (video_type, channel_id, message_id, file_id, file_unique_id,
                      file_size, duration, thumbnail_file_id, now, updated_by))
                logger.info(f"Created video config: {video_type}")
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving video config {video_type}: {e}", exc_info=True)
            conn.rollback()
            return False
    
    @staticmethod
    def get_video_config_by_type(video_type: str) -> Optional[Dict]:
        """
        Get video configuration by type.
        
        Args:
            video_type: 'wechat' or 'alipay'
            
        Returns:
            Video config dictionary or None
        """
        cursor = db.execute(
            "SELECT * FROM video_configs WHERE video_type = ?",
            (video_type,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def get_all_video_configs() -> list:
        """
        Get all video configurations.
        
        Returns:
            List of video config dictionaries
        """
        cursor = db.execute("SELECT * FROM video_configs ORDER BY video_type")
        return [dict(row) for row in cursor.fetchall()]

