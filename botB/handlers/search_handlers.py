"""
Search and filter handlers for Bot B
Handles advanced search and filtering UI
"""
import logging
from typing import Optional
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from admin_checker import is_admin
from services.search_service import parse_search_query, parse_amount_range, parse_date_range, parse_status_filter

logger = logging.getLogger(__name__)


async def handle_search_filter_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show search filter menu.
    """
    try:
        query = update.callback_query
        chat = query.message.chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        
        if not group_id:
            await query.answer("❌ 此功能仅在群组中可用", show_alert=True)
            return
        
        message = (
            "🔍 <b>高级搜索和筛选</b>\n\n"
            "请选择筛选条件类型：\n\n"
            "💡 <i>提示：您也可以直接输入搜索关键词</i>"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("💰 金额筛选", callback_data=f"filter_amount_{group_id}"),
                InlineKeyboardButton("📅 日期筛选", callback_data=f"filter_date_{group_id}")
            ],
            [
                InlineKeyboardButton("📊 状态筛选", callback_data=f"filter_status_{group_id}"),
                InlineKeyboardButton("👤 用户筛选", callback_data=f"filter_user_{group_id}")
            ],
            [
                InlineKeyboardButton("🔍 综合搜索", callback_data=f"filter_search_{group_id}"),
                InlineKeyboardButton("🔄 清除筛选", callback_data=f"filter_clear_{group_id}")
            ],
            [
                InlineKeyboardButton("🔙 返回", callback_data=f"bills_page_{group_id}_1")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query.message.text.startswith("🔍"):
            try:
                await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            except BadRequest as e:
                if "not modified" in str(e).lower():
                    await query.answer("✅ 内容未更改")
                    return
                else:
                    raise
        else:
            await query.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_search_filter_menu: {e}", exc_info=True)
        try:
            if update.callback_query:
                await update.callback_query.answer(f"❌ 错误: {str(e)}", show_alert=True)
            else:
                await update.message.reply_text(f"❌ 错误: {str(e)}")
        except Exception as inner_e:
            logger.error(f"Error sending error message: {inner_e}", exc_info=True)


async def handle_amount_filter(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int):
    """Handle amount filter input"""
    query = update.callback_query
    await query.edit_message_text(
        "💰 <b>金额筛选</b>\n\n"
        "请输入金额范围：\n\n"
        "<b>格式示例：</b>\n"
        "• <code>1000-5000</code> - 金额范围\n"
        "• <code>>1000</code> - 大于 1000\n"
        "• <code><5000</code> - 小于 5000\n"
        "• <code>2000</code> - 等于 2000\n\n"
        "请输入金额条件：",
        parse_mode="HTML"
    )
    
    context.user_data['awaiting_filter'] = 'amount'
    context.user_data['filter_group_id'] = group_id
    await query.answer()


async def handle_date_filter(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int):
    """Handle date filter input"""
    query = update.callback_query
    await query.edit_message_text(
        "📅 <b>日期筛选</b>\n\n"
        "请输入日期范围：\n\n"
        "<b>格式示例：</b>\n"
        "• <code>2025-01-01 2025-01-31</code> - 日期范围\n"
        "• <code>2025-01-15</code> - 单日\n"
        "• <code>今天</code> - 今天\n"
        "• <code>本周</code> - 本周\n"
        "• <code>本月</code> - 本月\n"
        "• <code>最近7天</code> - 最近7天\n"
        "• <code>最近30天</code> - 最近30天\n\n"
        "请输入日期条件：",
        parse_mode="HTML"
    )
    
    context.user_data['awaiting_filter'] = 'date'
    context.user_data['filter_group_id'] = group_id
    await query.answer()


async def handle_status_filter(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int):
    """Handle status filter selection"""
    query = update.callback_query
    
    keyboard = [
        [
            InlineKeyboardButton("⏳ 待支付", callback_data=f"status_filter_{group_id}_pending"),
            InlineKeyboardButton("✅ 已支付", callback_data=f"status_filter_{group_id}_paid")
        ],
        [
            InlineKeyboardButton("✅ 已确认", callback_data=f"status_filter_{group_id}_confirmed"),
            InlineKeyboardButton("❌ 已取消", callback_data=f"status_filter_{group_id}_cancelled")
        ],
        [
            InlineKeyboardButton("🔙 返回", callback_data=f"filter_menu_{group_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📊 <b>状态筛选</b>\n\n"
        "请选择交易状态：",
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    await query.answer()


async def handle_user_filter(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int):
    """Handle user filter input"""
    query = update.callback_query
    await query.edit_message_text(
        "👤 <b>用户筛选</b>\n\n"
        "请输入用户ID：\n\n"
        "<b>格式示例：</b>\n"
        "• <code>123456789</code> - 用户ID\n\n"
        "请输入用户ID：",
        parse_mode="HTML"
    )
    
    context.user_data['awaiting_filter'] = 'user'
    context.user_data['filter_group_id'] = group_id
    await query.answer()


async def handle_comprehensive_search(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int):
    """Handle comprehensive search input"""
    query = update.callback_query
    await query.edit_message_text(
        "🔍 <b>综合搜索</b>\n\n"
        "请输入搜索关键词：\n\n"
        "<b>格式示例：</b>\n"
        "• <code>金额:1000-5000 日期:2025-01-01 状态:已支付</code>\n"
        "• <code>>1000 本周 已确认</code>\n"
        "• <code>用户:123456 本月</code>\n"
        "• <code>T202501281430001234</code> - 交易编号\n\n"
        "请输入搜索关键词：",
        parse_mode="HTML"
    )
    
    context.user_data['awaiting_filter'] = 'search'
    context.user_data['filter_group_id'] = group_id
    await query.answer()


async def apply_filters_and_show_results(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                        group_id: int, filters: dict, page: int = 1):
    """Apply filters and show filtered results"""
    from handlers.bills_handlers import handle_history_bills
    
    await handle_history_bills(
        update, context,
        page=page,
        start_date=filters.get('start_date'),
        end_date=filters.get('end_date'),
        status=filters.get('status'),
        min_amount=filters.get('min_amount'),
        max_amount=filters.get('max_amount'),
        user_id=filters.get('user_id'),
        edit_message=True
    )

