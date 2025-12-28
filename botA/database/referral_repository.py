"""
Referral repository for database operations
"""
import logging
import random
import string
from typing import Optional, List, Dict
from datetime import datetime
from database.db import db

logger = logging.getLogger(__name__)


class ReferralRepository:
    """Repository for referral database operations"""
    
    @staticmethod
    def generate_referral_code(user_id: int) -> str:
        """Generate unique referral code for user"""
        prefix = "WSP"
        code = f"{prefix}{user_id}"
        return code
    
    @staticmethod
    def get_or_create_referral_code(user_id: int) -> str:
        """Get or create referral code for user"""
        cursor = db.execute(
            "SELECT referral_code FROM referral_codes WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return result['referral_code']
        
        # Create new referral code
        code = ReferralRepository.generate_referral_code(user_id)
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        db.execute("""
            INSERT INTO referral_codes 
            (user_id, referral_code, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, code, now, now))
        db.commit()
        
        return code
    
    @staticmethod
    def get_referral_by_code(code: str) -> Optional[Dict]:
        """Get referral code info by code"""
        cursor = db.execute("""
            SELECT * FROM referral_codes WHERE referral_code = ?
        """, (code,))
        result = cursor.fetchone()
        return dict(result) if result else None
    
    @staticmethod
    def create_referral(referrer_id: int, referred_id: int, referral_code: str) -> bool:
        """Create referral relationship"""
        try:
            # Check if already exists
            cursor = db.execute("""
                SELECT referral_id FROM referrals WHERE referred_id = ?
            """, (referred_id,))
            if cursor.fetchone():
                return False
            
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            db.execute("""
                INSERT INTO referrals 
                (referrer_id, referred_id, referral_code, status, created_at, updated_at)
                VALUES (?, ?, ?, 'pending', ?, ?)
            """, (referrer_id, referred_id, referral_code, now, now))
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating referral: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_referral_stats(user_id: int) -> Dict:
        """Get referral statistics for user"""
        cursor = db.execute("""
            SELECT * FROM referral_codes WHERE user_id = ?
        """, (user_id,))
        code_info = cursor.fetchone()
        
        if not code_info:
            return {
                'total_invites': 0,
                'successful_invites': 0,
                'total_rewards': 0.0,
                'lottery_entries': 0,
                'referral_code': None
            }
        
        return {
            'total_invites': code_info['total_invites'] or 0,
            'successful_invites': code_info['successful_invites'] or 0,
            'total_rewards': float(code_info['total_rewards'] or 0),
            'lottery_entries': code_info['lottery_entries'] or 0,
            'referral_code': code_info['referral_code']
        }
    
    @staticmethod
    def update_referral_status(referred_id: int, status: str, transaction_amount: float = 0.0):
        """Update referral status when user completes first transaction"""
        try:
            # Check if referral exists and not already rewarded
            cursor = db.execute("""
                SELECT * FROM referrals WHERE referred_id = ? AND status NOT IN ('rewarded', 'first_transaction')
            """, (referred_id,))
            referral = cursor.fetchone()
            
            if not referral:
                return False
            
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            referrer_id = referral['referrer_id']
            referral_id = referral['referral_id']
            
            # Calculate rewards
            invite_reward = 10.0  # Base invite reward
            dividend_reward = min(transaction_amount * 0.01, 100.0)  # 1% dividend, max 100
            total_reward = invite_reward + dividend_reward
            
            # Update referral status
            db.execute("""
                UPDATE referrals 
                SET status = ?, first_transaction_at = ?, reward_amount = ?, updated_at = ?
                WHERE referral_id = ?
            """, (status, now, total_reward, now, referral_id))
            
            # Update referral code stats
            db.execute("""
                UPDATE referral_codes 
                SET successful_invites = successful_invites + 1,
                    total_rewards = total_rewards + ?,
                    updated_at = ?
                WHERE user_id = ?
            """, (total_reward, now, referrer_id))
            
            # Check if should give lottery entry (every 5 successful invites)
            cursor = db.execute("""
                SELECT successful_invites FROM referral_codes WHERE user_id = ?
            """, (referrer_id,))
            code_info = cursor.fetchone()
            if code_info and (code_info['successful_invites'] % 5 == 0):
                db.execute("""
                    UPDATE referral_codes 
                    SET lottery_entries = lottery_entries + 1
                    WHERE user_id = ?
                """, (referrer_id,))
            
            db.commit()
            
            # Create reward records
            ReferralRepository.create_reward(
                referrer_id, 'invite', invite_reward, referral_id,
                f"邀请好友奖励"
            )
            if dividend_reward > 0:
                ReferralRepository.create_reward(
                    referrer_id, 'dividend', dividend_reward, referral_id,
                    f"交易分红奖励（交易额 1%）"
                )
            
            return True
        except Exception as e:
            logger.error(f"Error updating referral status: {e}", exc_info=True)
            db.rollback()
            return False
    
    @staticmethod
    def create_reward(user_id: int, reward_type: str, amount: float, 
                     referral_id: Optional[int] = None, description: str = "") -> bool:
        """Create reward record"""
        try:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            db.execute("""
                INSERT INTO referral_rewards 
                (user_id, reward_type, amount, referral_id, description, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """, (user_id, reward_type, amount, referral_id, description, now))
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating reward: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_user_rewards(user_id: int, limit: int = 10) -> List[Dict]:
        """Get user reward records"""
        cursor = db.execute("""
            SELECT * FROM referral_rewards 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (user_id, limit))
        return [dict(r) for r in cursor.fetchall()]
    
    @staticmethod
    def get_monthly_ranking(month: str = None, limit: int = 10) -> List[Dict]:
        """Get monthly ranking"""
        if not month:
            month = datetime.utcnow().strftime("%Y-%m")
        
        cursor = db.execute("""
            SELECT r.*, u.username 
            FROM monthly_rankings r
            LEFT JOIN users u ON r.user_id = u.user_id
            WHERE r.month = ?
            ORDER BY r.invite_count DESC, r.created_at ASC
            LIMIT ?
        """, (month, limit))
        return [dict(r) for r in cursor.fetchall()]
    
    @staticmethod
    def draw_lottery(user_id: int) -> Optional[Dict]:
        """Draw lottery for user"""
        # Check if user has lottery entries
        cursor = db.execute("""
            SELECT lottery_entries FROM referral_codes WHERE user_id = ?
        """, (user_id,))
        code_info = cursor.fetchone()
        
        if not code_info or code_info['lottery_entries'] <= 0:
            return None
        
        # Lottery prizes and probabilities
        prizes = [
            (1, 500.0, 0.10),   # 一等奖
            (2, 100.0, 0.20),   # 二等奖
            (3, 50.0, 0.30),    # 三等奖
            (4, 10.0, 0.40),    # 幸运奖
        ]
        
        # Draw prize
        rand = random.random()
        cumulative = 0.0
        selected_prize = None
        
        for level, amount, prob in prizes:
            cumulative += prob
            if rand <= cumulative:
                selected_prize = (level, amount)
                break
        
        if not selected_prize:
            selected_prize = (4, 10.0)  # Default to 幸运奖
        
        prize_level, prize_amount = selected_prize
        
        # Create lottery entry
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        db.execute("""
            INSERT INTO lottery_entries 
            (user_id, prize_level, prize_amount, status, created_at)
            VALUES (?, ?, ?, 'pending', ?)
        """, (user_id, prize_level, prize_amount, now))
        
        # Deduct lottery entry
        db.execute("""
            UPDATE referral_codes 
            SET lottery_entries = lottery_entries - 1
            WHERE user_id = ?
        """, (user_id,))
        
        # Create reward
        ReferralRepository.create_reward(
            user_id, 'lottery', prize_amount, None,
            f"抽奖奖励（{'一等奖' if prize_level == 1 else '二等奖' if prize_level == 2 else '三等奖' if prize_level == 3 else '幸运奖'}）"
        )
        
        db.commit()
        
        return {
            'prize_level': prize_level,
            'prize_amount': prize_amount
        }

