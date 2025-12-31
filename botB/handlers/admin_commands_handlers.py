"""
Admin commands help handler
Shows administrator command reference
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_admin_commands_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin commands help display"""
    try:
        # Handle both message and callback query updates
        message_target = None
        query = None
        
        # Enhanced validation
        if not update:
            logger.error("handle_admin_commands_help: update is None")
            return
        
        if update.message:
            message_target = update.message
            logger.debug(f"Using update.message for admin commands help (user: {update.effective_user.id if update.effective_user else 'unknown'})")
        elif update.callback_query and update.callback_query.message:
            message_target = update.callback_query.message
            query = update.callback_query
            logger.debug(f"Using callback_query.message for admin commands help (user: {update.effective_user.id if update.effective_user else 'unknown'})")
        else:
            logger.error(f"handle_admin_commands_help: No message target found. update.message={update.message}, update.callback_query={update.callback_query}")
            return
        
        chat = update.effective_chat
        is_group = chat.type in ['group', 'supergroup']
        
        help_message = (
            "⚡ <b>管理员快捷指令完整教程</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📋 <b>基础指令（w0-w9）</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        if is_group:
            help_message += (
                "<b>🔹 群组管理指令：</b>\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                
                "<b>w0 / SZ</b> - 查看群组设置\n"
                "功能：查看当前群组的加价、地址等配置信息\n"
                "示例：<code>w0</code> 或 <code>SZ</code>\n\n"
                
                "<b>w1 / HL</b> - 查看价格详情\n"
                "功能：查看 Binance P2P 实时汇率、加价、最终价格\n"
                "示例：<code>w1</code> 或 <code>HL</code>\n\n"
                
                "<b>w2 [数字] / SJJ [数字]</b> - 设置群组加价\n"
                "功能：为当前群组设置独立的加价值（可以是正数或负数）\n"
                "示例：<code>w2 0.5</code>（加价 0.5）或 <code>w2 -0.2</code>（降价 0.2）\n"
                "说明：设置后，该群组的所有结算都会使用此加价\n\n"
                
                "<b>w3 [地址] / SDZ [地址]</b> - 设置群组地址\n"
                "功能：为当前群组设置独立的 USDT 收款地址\n"
                "示例：<code>w3 TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t</code>\n"
                "说明：设置后，该群组的结算账单会显示此地址\n\n"
                
                "<b>w8 / CZSZ</b> - 重置群组设置\n"
                "功能：将群组的加价和地址重置为全局默认值\n"
                "示例：<code>w8</code> 或 <code>CZSZ</code>\n"
                "说明：重置后，群组将使用全局默认设置\n\n"
                
                "<b>w9 / SCSZ</b> - 删除群组配置\n"
                "功能：完全删除群组的独立配置，恢复使用全局默认\n"
                "示例：<code>w9</code> 或 <code>SCSZ</code>\n"
                "说明：删除后，群组配置将从数据库中移除\n\n"
            )
        else:
            help_message += (
                "<b>🔹 全局管理指令：</b>\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                
                "<b>w1 / HL</b> - 查看价格详情\n"
                "功能：查看 Binance P2P 实时汇率、全局加价、最终价格\n"
                "示例：<code>w1</code> 或 <code>HL</code>\n\n"
                
                "<b>w4 / CKQJ</b> - 查看全局设置\n"
                "功能：查看全局默认加价、全局默认地址等配置\n"
                "示例：<code>w4</code> 或 <code>CKQJ</code>\n"
                "说明：全局设置会影响所有未配置独立设置的群组\n\n"
                
                
                "<b>w7 / CKQL</b> - 查看所有群组列表\n"
                "功能：查看所有已配置的群组及其设置信息\n"
                "示例：<code>w7</code> 或 <code>CKQL</code>\n"
                "说明：显示所有群组的加价、地址、交易统计等信息\n\n"
            )
        
        help_message += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔤 <b>拼音快捷指令</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "支持拼音首字母，不区分大小写：\n\n"
        )
        
        if is_group:
            help_message += (
                "• <code>HL</code> / <code>hl</code> → w1（查看汇率）\n"
                "• <code>SZ</code> / <code>sz</code> → w0（查看设置）\n"
                "• <code>SJJ</code> / <code>sjj</code> → w2（设置加价）\n"
                "• <code>SDZ</code> / <code>sdz</code> → w3（设置地址）\n"
                "• <code>CZSZ</code> / <code>czsz</code> → w8（重置设置）\n"
                "• <code>SCSZ</code> / <code>scsz</code> → w9（删除配置）\n\n"
            )
        else:
            help_message += (
                "• <code>HL</code> / <code>hl</code> → w1（查看汇率）\n"
                "• <code>CKQJ</code> / <code>ckqj</code> → w4（查看全局）\n"
                "• <code>CKQL</code> / <code>ckql</code> → w7（查看群组列表）\n\n"
            )
        
        help_message += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🌐 <b>Telegram 命令</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "在输入框使用 / 开头的命令：\n\n"
            "• <code>/price</code> - 查看实时汇率\n"
            "• <code>/settlement</code> - 结算计算\n"
            "• <code>/today</code> - 查看今日账单（群组）\n"
            "• <code>/history</code> - 查看历史账单（群组）\n"
            "• <code>/address</code> - 查看USDT地址\n"
            "• <code>/support</code> - 联系客服\n"
            "• <code>/mybills</code> - 我的账单（私聊）\n"
            "• <code>/alerts</code> - 价格预警（私聊）\n"
            "• <code>/settings</code> - 查看设置\n"
            "• <code>/help</code> - 查看详细帮助\n\n"
        )
        
        help_message += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔘 <b>快捷按钮</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "使用聊天框底部的快捷按钮：\n\n"
        )
        
        if is_group:
            help_message += (
                "• <b>💱 汇率</b> - 查看实时汇率和商户报价\n"
                "• <b>📊 今日</b> - 查看今日账单统计\n"
                "• <b>📜 历史</b> - 查看历史账单列表\n"
                "• <b>💰 结算</b> - 结算计算菜单\n"
                "• <b>🔗 地址</b> - 查看收款地址\n"
                "• <b>📞 客服</b> - 联系人工客服\n"
                "• <b>⚙️ 设置</b> - 群组设置菜单（管理员）\n"
                "• <b>📈 统计</b> - 群组统计数据（管理员）\n\n"
            )
        else:
            help_message += (
                "• <b>💱 汇率</b> - 查看实时汇率和商户报价\n"
                "• <b>💰 结算</b> - 结算计算菜单\n"
                "• <b>📜 我的账单</b> - 查看个人账单\n"
                "• <b>🔔 预警</b> - 价格预警管理\n"
                "• <b>🔗 地址</b> - 查看收款地址\n"
                "• <b>📞 客服</b> - 联系人工客服\n"
                "• <b>⚙️ 管理</b> - 全局管理菜单（管理员）\n"
                "• <b>📊 数据</b> - 全局数据统计（管理员）\n\n"
            )
        
        help_message += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💡 <b>使用提示</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "• 所有指令支持多种输入方式，选择最方便的即可\n"
            "• 拼音指令不区分大小写，输入更快\n"
            "• 点击按钮时会显示功能介绍和使用教程\n"
            "• 群组和私聊的部分功能有所不同\n"
            "• 使用 <code>w2 -0.5</code> 可以实现降价效果\n\n"
        )
        
        # Add inline keyboard
        from keyboards.inline_keyboard import get_admin_commands_help_keyboard
        reply_markup = get_admin_commands_help_keyboard(is_group)
        
        if update.callback_query:
            await query.edit_message_text(help_message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
        else:
            await message_target.reply_text(help_message, parse_mode="HTML", reply_markup=reply_markup)
        
        logger.info(f"Admin {update.effective_user.id} viewed commands help")
        
    except Exception as e:
        logger.error(f"Error in handle_admin_commands_help: {e}", exc_info=True)
        try:
            if update.message:
                await update.message.reply_text(f"❌ 错误: {str(e)}")
            elif update.callback_query:
                await update.callback_query.answer(f"❌ 错误: {str(e)}", show_alert=True)
        except:
            pass

