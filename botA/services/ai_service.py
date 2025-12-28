"""
AI Service for handling OpenAI and Gemini API calls with automatic fallback
"""
import os
import logging
from typing import Optional, List, Dict
from config import Config

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI chat functionality with OpenAI (priority) and Gemini (fallback)"""
    
    # Knowledge base content (简体中文)
    KNOWLEDGE_BASE = """
你是伍拾支付（WuShiPay）的智能客服助手。伍拾支付是 Telegram 生态中领先的数字资产支付解决方案提供商。

公司核心优势：
- 99.9% 交易成功率
- 金融级资金安全（多重签名冷钱包）
- 7×24小时 1对1 专属客服
- 极速到账，毫秒级响应

主要功能：
- 支付宝/微信支付通道
- USDT 充值提现
- 汇率计算器
- 交易记录查询
- 统计信息查看

常见问题：
- 如何充值：在"我的钱包"页面查看 USDT 充值地址，向该地址转入 USDT 即可
- 如何提现：在"我的钱包"页面选择提现，输入提现地址和金额
- 提现时间：通常 1-3 个工作日内到账
- 费率：根据用户 VIP 等级收取不同费率，可在计算器中查看
- 客服联系：Telegram @wushizhifu_jianglai

重要提示：
- 请根据用户使用的语言进行回复。如果用户使用简体中文，请用简体中文回复；如果用户使用繁体中文，请用繁体中文回复；如果用户使用英文，请用英文回复；其他语言请尽量使用用户的语言回复。
- 默认使用简体中文回复。
- 请以友好、专业、简洁的方式回答用户问题。
- 如果无法回答或需要人工协助，请明确告知用户可以点击"转人工客服"按钮联系 @wushizhifu_jianglai。
"""
    
    def __init__(self):
        """Initialize AI service with OpenAI (priority) and Gemini (fallback)"""
        self.openai_available = False
        self.gemini_available = False
        self.openai_client = None
        self.gemini_model = None
        self.current_provider = None
        
        # Try to initialize OpenAI first (priority)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=openai_key)
                self.openai_available = True
                self.current_provider = "openai"
                logger.info("✅ OpenAI service initialized successfully")
            except ImportError:
                logger.warning("openai package not installed, install with: pip install openai")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI service: {e}")
        
        # Try to initialize Gemini as fallback
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                # Try gemini-1.5-pro-latest first, fallback to gemini-pro if not available
                try:
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')
                except Exception:
                    # Fallback to gemini-pro for v1beta compatibility
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
                self.gemini_available = True
                if not self.openai_available:
                    self.current_provider = "gemini"
                    logger.info("✅ Gemini service initialized successfully (as primary)")
                else:
                    logger.info("✅ Gemini service initialized successfully (as fallback)")
            except ImportError:
                logger.warning("google-generativeai package not installed, install with: pip install google-generativeai")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini service: {e}")
        
        if not self.openai_available and not self.gemini_available:
            logger.warning("⚠️ No AI service available. Please configure OPENAI_API_KEY or GEMINI_API_KEY")
    
    def is_available(self) -> bool:
        """Check if any AI service is available"""
        return self.openai_available or self.gemini_available
    
    def _generate_with_openai(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[str]:
        """Generate response using OpenAI"""
        if not self.openai_available or not self.openai_client:
            return None
        
        try:
            openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            
            # Build system message with language instruction
            language_instruction = self._get_language_instruction(user_language)
            system_message = self.KNOWLEDGE_BASE + "\n\n" + language_instruction
            
            # Build messages for OpenAI API
            messages = [{"role": "system", "content": system_message}]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages
                    role = "user" if msg.get("role") == "user" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API (new SDK format)
            response = self.openai_client.chat.completions.create(
                model=openai_model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"OpenAI response generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}", exc_info=True)
            return None
    
    def _generate_with_gemini(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_language: Optional[str] = None
    ) -> Optional[str]:
        """Generate response using Gemini"""
        if not self.gemini_available or not self.gemini_model:
            return None
        
        try:
            # Build prompt with knowledge base, language instruction, and conversation history
            language_instruction = self._get_language_instruction(user_language)
            prompt = self.KNOWLEDGE_BASE + "\n\n" + language_instruction + "\n\n"
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages
                    role = "用戶" if msg.get("role") == "user" else "助手"
                    prompt += f"{role}：{msg.get('content', '')}\n"
            
            prompt += f"\n用戶問題：{user_message}\n\n請回答："
            
            # Generate response
            response = self.gemini_model.generate_content(prompt)
            # Handle both string and object response types
            if hasattr(response, 'text'):
                answer = response.text.strip()
            else:
                answer = str(response).strip()
            logger.info(f"Gemini response generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}", exc_info=True)
            return None
    
    def generate_response(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_language: Optional[str] = None
    ) -> str:
        """
        Generate AI response to user message with automatic fallback.
        Priority: OpenAI -> Gemini
        
        Args:
            user_message: User's message
            conversation_history: List of previous messages [{"role": "user|assistant", "content": "..."}]
            user_language: User's language code (e.g., 'zh', 'zh-CN', 'zh-TW', 'en'). Default: 'zh-CN' (简体中文)
            
        Returns:
            AI generated response
        """
        if not self.is_available():
            # Return message in user's language
            if user_language == "zh-TW":
                return "抱歉，AI 服務暫時不可用，請聯繫人工客服 @wushizhifu_jianglai"
            elif user_language and user_language.startswith("en"):
                return "Sorry, AI service is temporarily unavailable. Please contact customer service @wushizhifu_jianglai"
            else:
                return "抱歉，AI 服务暂时不可用，请联系人工客服 @wushizhifu_jianglai"
        
        answer = None
        used_provider = None
        
        # Normalize user language (default to zh-CN for Simplified Chinese)
        if not user_language:
            user_language = "zh-CN"
        elif user_language.startswith("zh"):
            # zh, zh-CN -> zh-CN (简体中文)
            # zh-TW, zh-HK -> zh-TW (繁体中文)
            if user_language in ["zh-TW", "zh-HK", "zh-Hant"]:
                user_language = "zh-TW"
            else:
                user_language = "zh-CN"
        
        # Try OpenAI first (priority)
        if self.openai_available:
            answer = self._generate_with_openai(user_message, conversation_history, user_language)
            if answer:
                used_provider = "openai"
                self.current_provider = "openai"
        
        # Fallback to Gemini if OpenAI failed or unavailable
        if not answer and self.gemini_available:
            logger.info("OpenAI failed or unavailable, falling back to Gemini")
            answer = self._generate_with_gemini(user_message, conversation_history, user_language)
            if answer:
                used_provider = "gemini"
                self.current_provider = "gemini"
        
        if not answer:
            logger.error("Both OpenAI and Gemini failed to generate response")
            # Return error message in user's language
            if user_language == "zh-TW":
                return "抱歉，處理您的問題時遇到錯誤，請聯繫人工客服 @wushizhifu_jianglai"
            elif user_language and user_language.startswith("en"):
                return "Sorry, an error occurred while processing your request. Please contact customer service @wushizhifu_jianglai"
            else:
                return "抱歉，处理您的问题时遇到错误，请联系人工客服 @wushizhifu_jianglai"
        
        # Check if response indicates need for human support
        if self._should_escalate_to_human(answer):
            # Add escalation message in user's language
            if user_language == "zh-TW":
                return answer + "\n\n如果以上信息無法解決您的問題，請點擊下方按鈕聯繫人工客服。"
            elif user_language and user_language.startswith("en"):
                return answer + "\n\nIf the above information cannot solve your problem, please click the button below to contact customer service."
            else:
                return answer + "\n\n如果以上信息无法解决您的问题，请点击下方按钮联系人工客服。"
        
        return answer
    
    def _should_escalate_to_human(self, response: str) -> bool:
        """
        Check if response indicates need for human support.
        
        Args:
            response: AI generated response
            
        Returns:
            True if should escalate to human
        """
        # Keywords that suggest need for human support
        escalation_keywords = [
            "不清楚", "不知道", "無法確定", "無法回答",
            "建議聯繫", "請聯繫客服", "無法解決",
            "需要人工", "轉人工"
        ]
        
        response_lower = response.lower()
        return any(keyword in response_lower for keyword in escalation_keywords)


# Global AI service instance
_ai_service = None


def get_ai_service() -> AIService:
    """Get global AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
