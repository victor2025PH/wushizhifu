"""
Onboarding service for Bot B
Handles new user onboarding and feature discovery
"""
import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_new_user_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle new user onboarding flow.
    
    Shows step-by-step guide for first-time users.
    """
    try:
        from database import db
        from keyboards.inline_keyboard import get_onboarding_keyboard
        
        user = update.effective_user
        user_id = user.id
        
        # Check if onboarding already completed
        if db.is_onboarding_completed(user_id):
            return False  # Skip onboarding
        
        # Step 1: Welcome and introduction
        welcome_message = (
            f"👋 <b>欢迎使用 OTC 群组管理 Bot！</b>\n\n"
            f"你好，{user.first_name}！\n\n"
            f"这是一个专业的 OTC（场外交易）群组管理机器人。\n\n"
            f"让我们快速了解如何使用："
        )
        
        keyboard = get_onboarding_keyboard(step=1)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        return True  # Onboarding started
        
    except Exception as e:
        logger.error(f"Error in handle_new_user_onboarding: {e}", exc_info=True)
        return False


async def show_onboarding_step(update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
    """
    Show specific onboarding step.
    
    Args:
        step: Step number (1-4)
    """
    try:
        from database import db
        from keyboards.inline_keyboard import get_onboarding_keyboard
        
        query = update.callback_query
        user = query.from_user
        user_id = user.id
        
        if step == 1:
            message = (
                "📖 <b>第一步：了解功能</b>\n\n"
                "本 Bot 提供以下核心功能：\n\n"
                "• 💱 <b>实时汇率查询</b>\n"
                "  使用 Binance P2P 数据源，实时获取 USDT/CNY 汇率\n\n"
                "• 🧮 <b>自动结算计算</b>\n"
                "  输入人民币金额，自动计算应结算的 USDT 数量\n\n"
                "• 📜 <b>交易记录管理</b>\n"
                "  查看历史账单、统计信息\n\n"
                "• ⚙️ <b>群组独立配置</b>\n"
                "  不同群组可以设置不同的加价和收款地址\n\n"
                "点击「下一步」继续 →"
            )
        
        elif step == 2:
            message = (
                "💡 <b>第二步：如何使用</b>\n\n"
                "<b>方式一：快捷按钮</b>\n"
                "使用聊天框底部的快捷按钮快速操作\n\n"
                "<b>方式二：直接输入</b>\n"
                "• 发送人民币金额（如：<code>20000</code>）\n"
                "• 发送算式（如：<code>20000-200</code>）\n"
                "• <b>批量结算</b>：用逗号或换行分隔多个金额\n\n"
                "<b>方式三：命令</b>\n"
                "• <code>/start</code> - 显示帮助\n"
                "• <code>/help</code> - 查看详细帮助\n"
                "• <code>/price</code> - 查询汇率\n\n"
                "点击「下一步」继续 →"
            )
        
        elif step == 3:
            message = (
                "🎯 <b>第三步：实际操作</b>\n\n"
                "让我们来试试结算计算：\n\n"
                "<b>示例：</b>\n"
                "假设您要结算 1000 元人民币，只需：\n\n"
                "1. 输入：<code>1000</code>\n"
                "2. Bot 会自动计算应结算的 USDT\n"
                "3. 显示结算单，包含汇率和地址\n\n"
                "💡 <i>提示：您可以点击「已支付」按钮标记交易状态</i>\n\n"
                "点击「下一步」查看高级功能 →"
            )
        
        elif step == 4:
            message = (
                "✨ <b>第四步：高级功能</b>\n\n"
                "本 Bot 还提供以下高级功能：\n\n"
                "• 🔍 <b>高级搜索筛选</b>\n"
                "  支持按金额、日期、状态筛选交易\n\n"
                "• 📥 <b>数据导出</b>\n"
                "  导出账单为 CSV/Excel 格式\n\n"
                "• 📊 <b>统计分析</b>\n"
                "  查看群组和个人的交易统计\n\n"
                "• ⚙️ <b>群组管理</b>\n"
                "  管理员可以设置群组独立的加价和地址\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "🎉 <b>完成引导！</b>\n\n"
                "现在您可以开始使用 Bot 了。\n\n"
                "💡 <i>提示：如有问题，请发送 /help 查看帮助</i>"
            )
        
        keyboard = get_onboarding_keyboard(step=step)
        
        await query.edit_message_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in show_onboarding_step: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误，请重试", show_alert=True)


async def complete_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Complete onboarding and mark as done.
    """
    try:
        from database import db
        
        query = update.callback_query
        user_id = query.from_user.id
        
        # Mark onboarding as completed
        db.mark_onboarding_completed(user_id)
        
        message = (
            "✅ <b>引导完成！</b>\n\n"
            "现在您可以开始使用 Bot 了。\n\n"
            "💡 <i>提示：发送 /help 可以随时查看帮助文档</i>"
        )
        
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=None)
        await query.answer("🎉 欢迎使用！")
        
        logger.info(f"User {user_id} completed onboarding")
        
    except Exception as e:
        logger.error(f"Error completing onboarding: {e}", exc_info=True)
        await update.callback_query.answer("❌ 错误，请重试", show_alert=True)


async def check_feature_usage_and_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, feature: str):
    """
    Check if user has used a feature, and prompt if not.
    
    Args:
        feature: Feature name (e.g., 'batch_settlement', 'search', 'export')
    """
    try:
        from database import db
        
        user_id = update.effective_user.id
        
        # Check if user has used this feature
        setting = db.get_user_setting(user_id)
        if setting:
            prefs = setting.get('preferences', {})
            feature_key = f'feature_used_{feature}'
            
            if prefs.get(feature_key):
                return  # Feature already used, no prompt needed
        
        # Show feature discovery prompt based on feature
        if feature == 'batch_settlement':
            # Check if user has done many single settlements
            from database import db
            user_txs = db.get_transactions_by_user(user_id, limit=10)
            
            if len(user_txs) >= 3:
                message = (
                    "💡 <b>发现新功能：批量结算</b>\n\n"
                    "您已经完成多笔结算，可以尝试批量结算功能：\n\n"
                    "• 用逗号分隔：<code>1000,2000,3000</code>\n"
                    "• 用换行分隔：<code>1000\n2000\n3000</code>\n\n"
                    "批量结算可以提高效率！✨"
                )
                
                await update.message.reply_text(message, parse_mode="HTML")
                
                # Mark as prompted
                db.set_user_preference(user_id, f'feature_prompted_{feature}', True)
        
        elif feature == 'search':
            message = (
                "💡 <b>发现新功能：高级搜索</b>\n\n"
                "您可以在历史账单中使用高级搜索功能：\n\n"
                "• 按金额筛选\n"
                "• 按日期筛选\n"
                "• 按状态筛选\n\n"
                "点击「🔍 高级筛选」按钮试试吧！"
            )
            
            await update.message.reply_text(message, parse_mode="HTML")
            db.set_user_preference(user_id, f'feature_prompted_{feature}', True)
        
    except Exception as e:
        logger.error(f"Error in check_feature_usage_and_prompt: {e}", exc_info=True)

