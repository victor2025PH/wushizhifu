"""
AI chat handlers for user messages
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from keyboards.main_kb import get_main_keyboard
from services.ai_service import get_ai_service, AIService
from database.admin_repository import AdminRepository
from config import Config
from utils.text_utils import escape_markdown_v2

router = Router()
logger = logging.getLogger(__name__)

# In-memory conversation history storage (simple implementation)
# In production, you might want to store this in database
_conversation_history: dict[int, list[dict[str, str]]] = {}


def get_conversation_history(user_id: int) -> list[dict[str, str]]:
    """Get conversation history for user"""
    return _conversation_history.get(user_id, [])


def add_to_history(user_id: int, role: str, content: str):
    """Add message to conversation history"""
    if user_id not in _conversation_history:
        _conversation_history[user_id] = []
    
    _conversation_history[user_id].append({"role": role, "content": content})
    
    # Keep only last 10 messages
    if len(_conversation_history[user_id]) > 10:
        _conversation_history[user_id] = _conversation_history[user_id][-10:]


@router.callback_query(F.data == "ai_chat")
async def callback_ai_chat(callback: CallbackQuery):
    """Handle AI chat button callback"""
    try:
        user_id = callback.from_user.id
        is_admin = AdminRepository.is_admin(user_id)
        
        # Clear conversation history when starting new AI chat session
        _conversation_history[user_id] = []
        
        text = (
            "*🤖 AI 智能助手*\n\n"
            "您好！我是伍拾支付的智能客服助手，有什么可以帮助您的吗？\n"
            "您可以随时提问关于公司业务、产品功能、常见问题等。\n\n"
            "输入 `/exit` 退出 AI 模式。"
        )
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="转人工客服", url=Config.SUPPORT_URL)],
            [InlineKeyboardButton(text="🔙 返回主菜单", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )
        await callback.answer()
        
        logger.info(f"User {user_id} entered AI chat mode")
        
    except Exception as e:
        logger.error(f"Error in callback_ai_chat: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后再试", show_alert=True)


@router.message(F.text)
async def handle_ai_message(message: Message):
    """
    Handle user messages for AI chat.
    Only processes text messages that are not commands.
    """
    try:
        # Skip if message is in a group (only handle private messages)
        if message.chat.type != "private":
            return
        
        user_id = message.from_user.id
        user_text = message.text
        
        if not user_text:
            return  # Skip non-text messages
        
        # Get user's language code (default to zh-CN for Simplified Chinese)
        user_language = getattr(message.from_user, "language_code", None) or "zh-CN"
        
        # Handle /exit command to exit AI mode
        if user_text.lower() == '/exit':
            # Clear conversation history
            _conversation_history.pop(user_id, None)
            is_admin = AdminRepository.is_admin(user_id)
            await message.answer(
                "*🤖 AI 模式已退出*\n\n"
                "您已退出 AI 智能助手模式。如有其他需要，请随时点击按钮。",
                parse_mode="MarkdownV2",
                reply_markup=get_main_keyboard(user_id=user_id, is_admin=is_admin)
            )
            logger.info(f"User {user_id} exited AI chat mode")
            return
        
        # Skip other commands (messages starting with '/')
        if user_text.startswith('/'):
            return
        
        # Get AI service
        ai_service = get_ai_service()
        
        if not ai_service.is_available():
            await message.answer(
                "抱歉，AI 服务暂时不可用。请点击下方按钮联系人工客服。",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="💬 聯繫客服",
                        url=Config.SUPPORT_URL
                    )]
                ])
            )
            return
        
        # Get conversation history
        history = get_conversation_history(user_id)
        
        # Add user message to history
        add_to_history(user_id, "user", user_text)
        
        # Show typing indicator (if supported)
        try:
            await message.bot.send_chat_action(message.chat.id, "typing")
        except:
            pass
        
        # Generate AI response with user's language
        ai_response = ai_service.generate_response(user_text, history, user_language)
        
        # Add AI response to history
        add_to_history(user_id, "assistant", ai_response)
        
        # Check if should show support button
        should_show_support = ai_service._should_escalate_to_human(ai_response) or \
                              "联系客服" in ai_response or \
                              "人工客服" in ai_response
        
        # Escape MarkdownV2
        escaped_response = escape_markdown_v2(ai_response)
        
        # Create reply markup
        reply_markup = None
        if should_show_support:
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🤝 轉人工客服",
                    url=Config.SUPPORT_URL
                )],
                [InlineKeyboardButton(
                    text="🔙 返回主菜單",
                    callback_data="main_menu"
                )]
            ])
        else:
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🔙 返回主菜單",
                    callback_data="main_menu"
                )]
            ])
        
        # Send AI response
        await message.answer(
            escaped_response,
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )
        
        logger.info(f"User {user_id} received AI response")
        
    except Exception as e:
        logger.error(f"Error in handle_ai_message: {e}", exc_info=True)
        await message.answer(
            "抱歉，处理您的消息时遇到错误。请联系客服 @wushizhifu_jianglai",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="💬 聯繫客服",
                    url=Config.SUPPORT_URL
                )]
            ])
        )

