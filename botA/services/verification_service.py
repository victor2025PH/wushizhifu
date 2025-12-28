"""
Verification service for group member verification
"""
import logging
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from database.verification_repository import VerificationRepository
from database.group_repository import GroupRepository
from database.user_repository import UserRepository
from database.db import db

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for handling group member verification"""
    
    @staticmethod
    def get_random_question(group_id: int, difficulty: Optional[str] = None) -> Optional[dict]:
        """Get a random verification question for a group"""
        questions = VerificationRepository.get_questions(group_id=group_id, difficulty=difficulty, limit=1)
        if not questions:
            # Fallback to global questions
            questions = VerificationRepository.get_questions(group_id=None, difficulty=difficulty, limit=1)
        return questions[0] if questions else None
    
    @staticmethod
    def format_question_message(question: dict) -> str:
        """Format question as a message"""
        question_text = question['question_text']
        hint = question.get('hint', '')
        max_attempts = question.get('max_attempts', 3)
        time_limit = question.get('time_limit', 300)
        
        text = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  🎯 欢迎加入群组！\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"为了确保群组安全，请完成以下验证：\n\n"
            f"❓ *验证问题：*\n"
            f"{question_text}\n\n"
        )
        
        if question.get('options'):
            import json
            try:
                options = json.loads(question['options'])
                text += "*选项：*\n"
                for idx, option in enumerate(options, 1):
                    text += f"{idx}\\. {option}\n"
                text += "\n"
            except:
                pass
        
        if hint:
            text += f"💡 *提示：* {hint}\n\n"
        
        text += (
            f"*说明：*\n"
            f"• 请在 {time_limit // 60} 分钟内回答\n"
            f"• 可以发送答案内容或选项编号\n"
            f"• 答错可重试，最多 {max_attempts} 次机会\n\n"
            f"⚠️ 未在规定时间内回答将被移出群组"
        )
        
        return text
    
    @staticmethod
    def check_user_answer(group_id: int, user_id: int, user_answer: str) -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        Check user's answer to verification question
        
        Returns:
            (is_correct, verification_record, error_message)
        """
        record = VerificationRepository.get_verification_record(group_id, user_id)
        if not record:
            return False, None, "未找到审核记录，请重新加入群组"
        
        question_id = record.get('question_id')
        if not question_id:
            return False, record, "问题ID缺失"
        
        question = VerificationRepository.get_question(question_id)
        if not question:
            return False, record, "问题不存在"
        
        # Check attempts
        attempt_count = record.get('attempt_count', 0)
        max_attempts = question.get('max_attempts', 3)
        
        if attempt_count >= max_attempts:
            VerificationRepository.update_verification_record(
                record['record_id'],
                user_answer=user_answer,
                is_correct=False,
                result='rejected'
            )
            return False, record, f"已超过最大尝试次数（{max_attempts}次）"
        
        # Check timeout
        created_at = datetime.strptime(record['created_at'], "%Y-%m-%d %H:%M:%S")
        time_limit = question.get('time_limit', 300)
        elapsed = (datetime.utcnow() - created_at).total_seconds()
        
        if elapsed > time_limit:
            VerificationRepository.update_verification_record(
                record['record_id'],
                user_answer=user_answer,
                is_correct=False,
                result='rejected'
            )
            return False, record, "回答超时"
        
        # Check answer
        is_correct = VerificationRepository.check_answer(question_id, user_answer)
        
        if is_correct:
            # Answer is correct
            VerificationRepository.update_verification_record(
                record['record_id'],
                user_answer=user_answer,
                is_correct=True,
                result='passed'
            )
            return True, record, None
        else:
            # Answer is wrong
            attempt_count += 1
            remaining = max_attempts - attempt_count
            
            if remaining > 0:
                VerificationRepository.update_verification_record(
                    record['record_id'],
                    user_answer=user_answer,
                    is_correct=False,
                    result='pending' if remaining > 0 else 'rejected',
                    increment_attempt=True
                )
                return False, record, f"答案不正确，请重试（剩余 {remaining} 次机会）"
            else:
                VerificationRepository.update_verification_record(
                    record['record_id'],
                    user_answer=user_answer,
                    is_correct=False,
                    result='rejected',
                    increment_attempt=True
                )
                return False, record, f"答案不正确，已达到最大尝试次数"
    
    @staticmethod
    def start_verification(group_id: int, user_id: int) -> Optional[dict]:
        """Start verification process for a new member"""
        # Get group config
        config = VerificationRepository.get_verification_config(group_id)
        if not config:
            # Create default config
            VerificationRepository.create_or_update_config(group_id)
            config = VerificationRepository.get_verification_config(group_id)
        
        verification_mode = config.get('verification_mode', 'question') if config else 'question'
        
        # Get question if using question mode
        question = None
        question_id = None
        
        if verification_mode == 'question':
            question = VerificationService.get_random_question(group_id)
            if question:
                question_id = question['question_id']
        
        # Create verification record with question_id
        record_id = VerificationRepository.create_verification_record(
            group_id=group_id,
            user_id=user_id,
            verification_type=verification_mode,
            question_id=question_id
        )
        
        if not record_id:
            return None
        
        if question:
            return {
                'record_id': record_id,
                'question': question,
                'type': 'question'
            }
        
        return {
            'record_id': record_id,
            'question': None,
            'type': verification_mode
        }
    
    @staticmethod
    def complete_verification(group_id: int, user_id: int, passed: bool) -> bool:
        """Complete verification process"""
        try:
            if passed:
                # Verify member
                GroupRepository.verify_member(group_id, user_id)
                
                # Update record
                record = VerificationRepository.get_verification_record(group_id, user_id)
                if record:
                    VerificationRepository.update_verification_record(
                        record['record_id'],
                        result='passed'
                    )
            else:
                # Reject member
                record = VerificationRepository.get_verification_record(group_id, user_id)
                if record:
                    VerificationRepository.update_verification_record(
                        record['record_id'],
                        result='rejected'
                    )
                # Remove member from group (would need bot instance)
                # This should be handled by the handler
            
            return True
        except Exception as e:
            logger.error(f"Error completing verification: {e}", exc_info=True)
            return False

