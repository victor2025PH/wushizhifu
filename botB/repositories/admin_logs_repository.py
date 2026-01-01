"""
Admin operation logs repository for tracking administrator actions
"""
from typing import List, Optional
from database import db
import logging

logger = logging.getLogger(__name__)


class AdminLogsRepository:
    """Repository for admin operation logs"""
    
    @staticmethod
    def log_operation(
        admin_id: int,
        operation_type: str,
        target_type: str = None,
        target_id: int = None,
        details: str = None,
        result: str = "success"
    ) -> bool:
        """
        Log an admin operation.
        
        Args:
            admin_id: Admin user ID who performed the operation
            operation_type: Type of operation (add, delete, update, search, export, etc.)
            target_type: Type of target (user, group, word, admin, etc.)
            target_id: ID of the target (user_id, group_id, word_id, etc.)
            details: Additional details about the operation (stored in description field)
            result: Operation result (success, failed, error)
            
        Returns:
            True if logged successfully
        """
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            # Get admin info
            cursor.execute("""
                SELECT username, first_name FROM users WHERE user_id = ?
            """, (admin_id,))
            user_info = cursor.fetchone()
            username = user_info['username'] if user_info else None
            first_name = user_info['first_name'] if user_info else None
            
            # Prepare description field (combine details and result)
            description = details or ""
            if result and result != "success":
                description = f"{description} [结果: {result}]" if description else f"[结果: {result}]"
            
            cursor.execute("""
                INSERT INTO operation_logs (
                    operation_type, user_id, username, first_name,
                    target_type, target_id, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                operation_type,
                admin_id,
                username or '',
                first_name or '',
                target_type or '',
                str(target_id) if target_id else '',
                description
            ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error logging operation: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
    
    @staticmethod
    def get_logs(
        admin_id: int = None,
        operation_type: str = None,
        target_type: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Get operation logs with filters.
        
        Args:
            admin_id: Filter by admin ID
            operation_type: Filter by operation type
            target_type: Filter by target type
            limit: Maximum number of logs to return
            offset: Offset for pagination
            
        Returns:
            List of operation log dictionaries
        """
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            conditions = []
            params = []
            
            if admin_id:
                conditions.append("user_id = ?")
                params.append(admin_id)
            
            if operation_type:
                conditions.append("operation_type = ?")
                params.append(operation_type)
            
            if target_type:
                conditions.append("target_type = ?")
                params.append(target_type)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT * FROM operation_logs
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            cursor.execute(query, tuple(params))
            logs = cursor.fetchall()
            return [dict(log) for log in logs]
        finally:
            cursor.close()
    
    @staticmethod
    def get_log_stats(admin_id: int = None, days: int = 7) -> dict:
        """
        Get operation log statistics.
        
        Args:
            admin_id: Filter by admin ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with statistics
        """
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            conditions = ["created_at >= DATE('now', '-' || ? || ' days')"]
            params = [days]
            
            if admin_id:
                conditions.append("user_id = ?")
                params.append(admin_id)
            
            where_clause = " AND ".join(conditions)
            
            # Get operation type statistics
            cursor.execute(f"""
                SELECT operation_type, COUNT(*) as count
                FROM operation_logs
                WHERE {where_clause}
                GROUP BY operation_type
                ORDER BY count DESC
            """, tuple(params))
            type_stats = cursor.fetchall()
            
            # Get total count
            cursor.execute(f"""
                SELECT COUNT(*) as total
                FROM operation_logs
                WHERE {where_clause}
            """, tuple(params))
            total = cursor.fetchone()['total']
            
            return {
                'total': total,
                'by_type': {stat['operation_type']: stat['count'] for stat in type_stats}
            }
        finally:
            cursor.close()
