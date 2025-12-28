"""
Transaction service for managing transactions
"""
import uuid
from typing import List, Optional
from datetime import datetime
from database.transaction_repository import TransactionRepository
from database.user_repository import UserRepository
from database.rate_repository import RateRepository
from database.db import db
import logging

logger = logging.getLogger(__name__)


class TransactionService:
    """Service for transaction operations"""
    
    @staticmethod
    def generate_order_id() -> str:
        """Generate unique order ID"""
        return f"WS{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def create_transaction(user_id: int, transaction_type: str, payment_channel: str,
                          amount: float, description: Optional[str] = None) -> dict:
        """
        Create a new transaction.
        
        Args:
            user_id: User ID
            transaction_type: receive, pay, refund
            payment_channel: alipay, wechat
            amount: Transaction amount
            description: Transaction description
            
        Returns:
            Transaction data dictionary
        """
        try:
            # Get user VIP level
            user = UserRepository.get_user(user_id)
            vip_level = user.get('vip_level', 0) if user else 0
            
            # Calculate fee
            fee, actual_amount = RateRepository.calculate_fee(amount, payment_channel, vip_level)
            
            # Generate order ID
            order_id = TransactionService.generate_order_id()
            
            # Create transaction
            transaction = TransactionRepository.create_transaction(
                user_id=user_id,
                order_id=order_id,
                transaction_type=transaction_type,
                payment_channel=payment_channel,
                amount=amount,
                fee=fee,
                actual_amount=actual_amount,
                currency="CNY",
                description=description
            )
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            raise
    
    @staticmethod
    def get_user_transactions(user_id: int, limit: int = 10, offset: int = 0,
                             transaction_type: Optional[str] = None,
                             status: Optional[str] = None) -> List[dict]:
        """Get user transactions"""
        return TransactionRepository.get_user_transactions(
            user_id, limit, offset, transaction_type, status
        )
    
    @staticmethod
    def get_transaction(order_id: str) -> Optional[dict]:
        """Get transaction by order ID"""
        return TransactionRepository.get_transaction(order_id)
    
    @staticmethod
    def update_transaction_status(order_id: str, status: str):
        """Update transaction status"""
        TransactionRepository.update_transaction_status(order_id, status, datetime.utcnow())
        
        # Update user statistics if paid
        if status == "paid":
            transaction = TransactionRepository.get_transaction(order_id)
            if transaction:
                user_id = transaction['user_id']
                amount = float(transaction['amount'])
                
                # Update user statistics
                UserRepository.update_statistics(user_id, amount)
                
                # Check if this is user's first transaction and trigger referral rewards
                try:
                    from database.referral_repository import ReferralRepository
                    from database.transaction_repository import TransactionRepository as TR
                    
                    # Check if this is first successful transaction
                    previous_paid = TR.get_user_transactions(
                        user_id, limit=1, status='paid'
                    )
                    
                    # If this is the only paid transaction, it's the first one
                    if len(previous_paid) == 1 and previous_paid[0]['order_id'] == order_id:
                        # Trigger referral rewards
                        ReferralRepository.update_referral_status(
                            user_id, 'rewarded', amount
                        )
                        
                        # Give new user reward (5 USDT)
                        ReferralRepository.create_reward(
                            user_id, 'new_user_bonus', 5.0, None,
                            "新用户首次交易红包"
                        )
                        
                        logger.info(f"Triggered referral rewards for user {user_id}, first transaction {order_id}")
                except Exception as e:
                    logger.error(f"Error triggering referral rewards: {e}", exc_info=True)

