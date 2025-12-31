"""
Verification repository for database operations (adapted for Bot B)
"""
from typing import List, Optional, Dict
from datetime import datetime
from database import db
import logging
import json

logger = logging.getLogger(__name__)


class VerificationRepository:
    """Repository for verification system database operations"""
    
    @staticmethod
    def create_question(
        group_id: Optional[int],
        question_text: str,
        question_type: str,
        correct_answer: str,
        options: Optional[str] = None,
        difficulty: str = 'medium',
        hint: Optional[str] = None,
        max_attempts: int = 3,
        time_limit: int = 300
    ) -> Optional[int]:
        """Create a verification question"""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO verification_questions 
                (group_id, question_text, question_type, correct_answer, options, 
                 difficulty, hint, max_attempts, time_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (group_id, question_text, question_type, correct_answer, options,
                  difficulty, hint, max_attempts, time_limit))
            conn.commit()
            question_id = cursor.lastrowid
            logger.info(f"Created verification question {question_id}")
            return question_id
        except Exception as e:
            logger.error(f"Error creating verification question: {e}", exc_info=True)
            conn.rollback()
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def get_questions(group_id: Optional[int] = None, difficulty: Optional[str] = None, limit: int = 10) -> List[dict]:
        """Get verification questions"""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            query = """
                SELECT * FROM verification_questions 
                WHERE is_active = 1 AND (group_id = ? OR group_id IS NULL)
            """
            params = [group_id]
            
            if difficulty:
                query += " AND difficulty = ?"
                params.append(difficulty)
            
            query += " ORDER BY RANDOM() LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            questions = cursor.fetchall()
            return [dict(q) for q in questions]
        finally:
            cursor.close()
    
    @staticmethod
    def get_question(question_id: int) -> Optional[dict]:
        """Get a question by ID"""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM verification_questions WHERE question_id = ?", (question_id,))
            question = cursor.fetchone()
            return dict(question) if question else None
        finally:
            cursor.close()
    
    @staticmethod
    def check_answer(question_id: int, user_answer: str) -> bool:
        """Check if user answer is correct"""
        question = VerificationRepository.get_question(question_id)
        if not question:
            return False
        
        correct_answers = question['correct_answer'].split('|')
        user_answer_lower = user_answer.strip().lower()
        
        # Check if user answer matches any correct answer
        for correct in correct_answers:
            if user_answer_lower == correct.strip().lower():
                return True
            # For single choice, check if user answered with option number
            if question['question_type'] == 'single_choice' and question['options']:
                try:
                    options = json.loads(question['options'])
                    if user_answer_lower.isdigit():
                        option_index = int(user_answer_lower) - 1
                        if 0 <= option_index < len(options):
                            if options[option_index].lower() in [c.lower() for c in correct_answers]:
                                return True
                except:
                    pass
        
        return False
    
    @staticmethod
    def create_verification_record(
        group_id: int,
        user_id: int,
        verification_type: str,
        question_id: Optional[int] = None,
        ai_score: Optional[int] = None
    ) -> Optional[int]:
        """Create a verification record"""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            # Delete any existing pending record for this user in this group
            cursor.execute("""
                DELETE FROM verification_records 
                WHERE group_id = ? AND user_id = ? AND result = 'pending'
            """, (group_id, user_id))
            
            cursor.execute("""
                INSERT INTO verification_records 
                (group_id, user_id, verification_type, question_id, ai_score, result)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """, (group_id, user_id, verification_type, question_id, ai_score))
            conn.commit()
            record_id = cursor.lastrowid
            return record_id
        except Exception as e:
            logger.error(f"Error creating verification record: {e}", exc_info=True)
            conn.rollback()
            return None
        finally:
            cursor.close()
    
    @staticmethod
    def update_verification_record(
        record_id: int,
        user_answer: Optional[str] = None,
        is_correct: Optional[bool] = None,
        result: str = 'pending',
        increment_attempt: bool = False
    ) -> bool:
        """Update verification record"""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            
            if increment_attempt:
                cursor.execute("""
                    UPDATE verification_records 
                    SET user_answer = ?, is_correct = ?, result = ?, 
                        attempt_count = attempt_count + 1,
                        completed_at = ?
                    WHERE record_id = ?
                """, (user_answer, is_correct, result, now if result != 'pending' else None, record_id))
            else:
                cursor.execute("""
                    UPDATE verification_records 
                    SET user_answer = ?, is_correct = ?, result = ?, completed_at = ?
                    WHERE record_id = ?
                """, (user_answer, is_correct, result, now if result != 'pending' else None, record_id))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating verification record: {e}", exc_info=True)
            conn.rollback()
            return False
        finally:
            cursor.close()
    
    @staticmethod
    def get_verification_record(group_id: int, user_id: int) -> Optional[dict]:
        """Get verification record for a user in a group"""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM verification_records 
                WHERE group_id = ? AND user_id = ? AND result = 'pending'
                ORDER BY created_at DESC LIMIT 1
            """, (group_id, user_id))
            record = cursor.fetchone()
            return dict(record) if record else None
        finally:
            cursor.close()
    
    @staticmethod
    def get_verification_config(group_id: int) -> Optional[dict]:
        """Get verification config for a group"""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM verification_configs WHERE group_id = ?", (group_id,))
            config = cursor.fetchone()
            return dict(config) if config else None
        finally:
            cursor.close()
    
    @staticmethod
    def create_or_update_config(
        group_id: int,
        verification_mode: str = 'question',
        auto_approve_threshold: int = 80,
        question_threshold_min: int = 60,
        question_threshold_max: int = 80,
        welcome_message: Optional[str] = None
    ) -> bool:
        """Create or update verification config"""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO verification_configs 
                (group_id, verification_mode, auto_approve_threshold, 
                 question_threshold_min, question_threshold_max, welcome_message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(group_id) DO UPDATE SET
                    verification_mode = excluded.verification_mode,
                    auto_approve_threshold = excluded.auto_approve_threshold,
                    question_threshold_min = excluded.question_threshold_min,
                    question_threshold_max = excluded.question_threshold_max,
                    welcome_message = excluded.welcome_message,
                    updated_at = excluded.updated_at
            """, (group_id, verification_mode, auto_approve_threshold,
                  question_threshold_min, question_threshold_max, welcome_message, now, now))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating/updating verification config: {e}", exc_info=True)
            conn.rollback()
            return False
        finally:
            cursor.close()
    
    @staticmethod
    def get_verification_stats(group_id: int, days: int = 7) -> dict:
        """Get verification statistics for a group"""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN result = 'passed' THEN 1 ELSE 0 END) as passed,
                    SUM(CASE WHEN result = 'rejected' THEN 1 ELSE 0 END) as rejected,
                    SUM(CASE WHEN result = 'pending' THEN 1 ELSE 0 END) as pending,
                    AVG(CASE WHEN ai_score IS NOT NULL THEN ai_score ELSE NULL END) as avg_score
                FROM verification_records 
                WHERE group_id = ? AND created_at >= datetime('now', '-' || ? || ' days')
            """, (group_id, days))
            stats = cursor.fetchone()
            return dict(stats) if stats else {'total': 0, 'passed': 0, 'rejected': 0, 'pending': 0, 'avg_score': 0}
        finally:
            cursor.close()
