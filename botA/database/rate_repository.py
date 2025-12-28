"""
Rate configuration repository for database operations
"""
from typing import Optional
from database.db import db
import logging

logger = logging.getLogger(__name__)


class RateRepository:
    """Repository for rate configuration database operations"""
    
    @staticmethod
    def get_rate(channel: str, vip_level: int = 0) -> Optional[dict]:
        """
        Get rate configuration.
        
        Args:
            channel: Payment channel (alipay, wechat)
            vip_level: VIP level (0-3)
            
        Returns:
            Rate configuration dict or None
        """
        cursor = db.execute("""
            SELECT * FROM rate_configs 
            WHERE channel = ? AND vip_level = ? AND is_active = 1
            LIMIT 1
        """, (channel, vip_level))
        
        rate = cursor.fetchone()
        return dict(rate) if rate else None
    
    @staticmethod
    def calculate_fee(amount: float, channel: str, vip_level: int = 0) -> tuple:
        """
        Calculate fee and actual amount.
        
        Args:
            amount: Transaction amount
            channel: Payment channel
            vip_level: VIP level
            
        Returns:
            Tuple of (fee, actual_amount)
        """
        rate_config = RateRepository.get_rate(channel, vip_level)
        
        if not rate_config:
            # Default rate 0.6%
            rate = 0.0060
        else:
            rate = float(rate_config['rate_percentage'])
        
        fee = round(amount * rate, 2)
        actual_amount = round(amount - fee, 2)
        
        return fee, actual_amount

