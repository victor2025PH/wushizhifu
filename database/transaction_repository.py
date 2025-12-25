"""
Transaction repository for database operations
"""
from typing import List, Optional
from datetime import datetime, timedelta
from database.db import db
import logging

logger = logging.getLogger(__name__)


class TransactionRepository:
    """Repository for transaction database operations"""
    
    @staticmethod
    def create_transaction(user_id: int, order_id: str, transaction_type: str,
                          payment_channel: str, amount: float, fee: float,
                          actual_amount: float, currency: str = "CNY",
                          description: Optional[str] = None,
                          expired_minutes: int = 30) -> dict:
        """
        Create a new transaction.
        
        Args:
            user_id: User ID
            order_id: Unique order ID
            transaction_type: receive, pay, refund
            payment_channel: alipay, wechat
            amount: Transaction amount
            fee: Fee amount
            actual_amount: Actual amount
            currency: Currency code
            description: Transaction description
            expired_minutes: Expiration time in minutes
            
        Returns:
            Transaction data dictionary
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.utcnow()
            expired_at = now + timedelta(minutes=expired_minutes)
            
            cursor.execute("""
                INSERT INTO transactions 
                (user_id, order_id, transaction_type, payment_channel,
                 amount, fee, actual_amount, currency, status, description,
                 created_at, expired_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)
            """, (user_id, order_id, transaction_type, payment_channel,
                  amount, fee, actual_amount, currency, description,
                  now.strftime("%Y-%m-%d %H:%M:%S"),
                  expired_at.strftime("%Y-%m-%d %H:%M:%S"),
                  now.strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            
            cursor.execute("SELECT * FROM transactions WHERE order_id = ?", (order_id,))
            transaction = cursor.fetchone()
            
            return dict(transaction) if transaction else {}
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            conn.rollback()
            raise
    
    @staticmethod
    def get_transaction(order_id: str) -> Optional[dict]:
        """Get transaction by order ID"""
        cursor = db.execute(
            "SELECT * FROM transactions WHERE order_id = ?",
            (order_id,)
        )
        transaction = cursor.fetchone()
        return dict(transaction) if transaction else None
    
    @staticmethod
    def get_user_transactions(user_id: int, limit: int = 10, offset: int = 0,
                              transaction_type: Optional[str] = None,
                              status: Optional[str] = None) -> List[dict]:
        """
        Get user transactions with filters.
        
        Args:
            user_id: User ID
            limit: Maximum number of records
            offset: Offset for pagination
            transaction_type: Filter by type (receive, pay, refund)
            status: Filter by status (pending, paid, failed, etc.)
            
        Returns:
            List of transaction dictionaries
        """
        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [user_id]
        
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor = db.execute(query, tuple(params))
        transactions = cursor.fetchall()
        
        return [dict(t) for t in transactions]
    
    @staticmethod
    def update_transaction_status(order_id: str, status: str,
                                  paid_at: Optional[datetime] = None):
        """Update transaction status"""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        paid_at_str = paid_at.strftime("%Y-%m-%d %H:%M:%S") if paid_at else None
        
        db.execute("""
            UPDATE transactions 
            SET status = ?, paid_at = ?, updated_at = ?
            WHERE order_id = ?
        """, (status, paid_at_str, now, order_id))
        db.commit()
    
    @staticmethod
    def get_transaction_count(user_id: int, transaction_type: Optional[str] = None) -> int:
        """Get total transaction count for user"""
        query = "SELECT COUNT(*) FROM transactions WHERE user_id = ?"
        params = [user_id]
        
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)
        
        cursor = db.execute(query, tuple(params))
        return cursor.fetchone()[0]

