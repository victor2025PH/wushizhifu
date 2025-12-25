"""
Message service for generating professional messages
"""
from datetime import datetime
from utils.text_utils import escape_markdown_v2, get_user_display_name
from services.user_service import UserService


class MessageService:
    """Service for generating professional bot messages"""
    
    @staticmethod
    def generate_welcome_message(user, is_new_user: bool = False) -> str:
        """
        Generate professional welcome message.
        
        Args:
            user: Telegram User object
            is_new_user: Whether this is user's first interaction
            
        Returns:
            Formatted welcome message in MarkdownV2
        """
        user_display_name = get_user_display_name(user)
        
        # Get current time for greeting
        current_hour = datetime.utcnow().hour
        if 5 <= current_hour < 12:
            time_greeting = "早上好"
        elif 12 <= current_hour < 18:
            time_greeting = "下午好"
        elif 18 <= current_hour < 22:
            time_greeting = "晚上好"
        else:
            time_greeting = "您好"
        
        # New user vs returning user greeting
        if is_new_user:
            welcome_line = f"👋 *{time_greeting}，{user_display_name}！歡迎加入伍拾支付生態系統*"
            status_note = "*首次登錄成功，您的專屬賬戶已激活*"
        else:
            welcome_line = f"👋 *{time_greeting}，{user_display_name}！歡迎回來*"
            user_data = UserService.get_user(user.id)
            if user_data:
                status_note = f"*賬戶狀態：正常 \\| 消息數：{user_data.get('message_count', 0)}*"
            else:
                status_note = "*賬戶狀態：正常*"
        
        # User info section
        user_info_parts = []
        if user.username:
            user_info_parts.append(f"👤 *Telegram*: `@{escape_markdown_v2(user.username)}`")
        if user.id:
            user_info_parts.append(f"🆔 *UID*: `{user.id}`")
        if getattr(user, "is_premium", False):
            user_info_parts.append("⭐ *Premium 會員*")
        
        user_info_text = ""
        if user_info_parts:
            user_info_text = "\n".join(user_info_parts) + "\n\n"
        
        # System status with timestamp
        current_time = datetime.utcnow().strftime("%Y\\-%m\\-%d %H:%M UTC")
        
        # Professional welcome message
        welcome_text = (
            "╔═══════════════════════════════╗\n"
            "║  *伍拾支付 \\| WUSHI PAY*     ║\n"
            "║  *Enterprise Payment Gateway* ║\n"
            "╚═══════════════════════════════╝\n\n"
            f"{welcome_line}\n"
            f"{status_note}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*系統狀態實時監控*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 *服務狀態*: 在線 \\(100\\%\\)\n"
            "🔒 *安全通道*: TLS 1\\.3 已建立\n"
            "⚡ *響應時間*: < 50ms\n"
            "🛡️  *風控系統*: 實時監控中\n"
            f"📅 *當前時間*: `{current_time}`\n"
            f"{user_info_text}"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"尊敬的 {user_display_name}，\n\n"
            "歡迎訪問 *伍拾支付* 企業級自動化結算中心。\n\n"
            "我們為您提供：\n"
            "• *7×24小時* 不間斷服務\n"
            "• *企業級* 代收代付解決方案\n"
            "• *銀行級* 資金安全保障\n"
            "• *毫秒級* 交易處理速度\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*今日匯率概覽*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🇺🇸 `USDT/CNY`: *7\\.42* \\(實時鎖定\\)\n"
            "⚡ *平均到賬時效*: *3\\.2秒*\n"
            "💱 *24H 交易量*: *$12\\.8M*\n\n"
            "👇 *請選擇您的操作終端：*"
        )
        
        return welcome_text
    
    @staticmethod
    def generate_rates_message() -> str:
        """
        Generate professional rates information message.
        
        Returns:
            Formatted rates message in MarkdownV2
        """
        rates_text = (
            "╔═══════════════════════════════╗\n"
            "║  *費率標準與服務條款*         ║\n"
            "╚═══════════════════════════════╝\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*支付通道費率*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💳 *支付寶通道*\n"
            "   標準費率: *0\\.6\\%*\n"
            "   到賬時間: *即時到賬*\n"
            "   單筆限額: ¥1\\-500,000\n\n"
            "🍀 *微信支付通道*\n"
            "   標準費率: *0\\.6\\%*\n"
            "   到賬時間: *即時到賬*\n"
            "   單筆限額: ¥1\\-500,000\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*VIP 費率優惠*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⭐ *VIP1*: 月交易量 > ¥100萬 → *0\\.55\\%*\n"
            "⭐ *VIP2*: 月交易量 > ¥500萬 → *0\\.50\\%*\n"
            "⭐ *VIP3*: 月交易量 > ¥1000萬 → *0\\.45\\%*\n\n"
            "💼 企業客戶可聯繫商務合作獲取專屬費率\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "*服務條款*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• 所有費率均為實時報價\n"
            "• 結算週期: T\\+0 \\(當日到賬\\)\n"
            "• 支持退款與售後服務\n"
            "• 7×24小時技術支持\n\n"
            "📞 詳情請聯繫專屬客服"
        )
        
        return rates_text

