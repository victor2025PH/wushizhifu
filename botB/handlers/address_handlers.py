"""
Address management handlers for Bot B
Handles multiple USDT address management with confirmation and QR code support
"""
import logging
from typing import Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from database import db
from admin_checker import is_admin

logger = logging.getLogger(__name__)


async def handle_address_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle address list display"""
    try:
        query = update.callback_query if hasattr(update, 'callback_query') and update.callback_query else None
        user = (query.from_user if query else update.effective_user)
        user_id = user.id
        
        if not is_admin(user_id):
            if query:
                await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            else:
                await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        chat = update.effective_chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        
        # Get group_id from context if in private chat
        if not group_id and 'selected_group_id' in context.user_data:
            group_id = context.user_data['selected_group_id']
        
        if not group_id:
            if query:
                await query.answer("❌ 请在群组中使用此功能，或从私聊中选择群组", show_alert=True)
            else:
                await update.message.reply_text("❌ 请在群组中使用此功能，或从私聊中选择群组")
            return
        
        addresses = db.get_usdt_addresses(group_id=group_id, active_only=False)
        
        if not addresses:
            message = (
                f"📍 <b>群组地址管理</b>\n\n"
                f"群组ID: <code>{group_id}</code>\n"
                f"暂无配置的地址。\n\n"
                f"点击「➕ 添加地址」开始添加"
            )
        else:
            active_count = sum(1 for a in addresses if a['is_active'] and not a['pending_confirmation'])
            pending_count = sum(1 for a in addresses if a['pending_confirmation'])
            
            message = (
                f"📍 <b>群组地址管理</b>\n\n"
                f"群组ID: <code>{group_id}</code>\n"
                f"共 {len(addresses)} 个地址（{active_count} 个可用，{pending_count} 个待确认）\n"
                f"────────────────────────\n\n"
            )
            
            for idx, addr in enumerate(addresses, 1):
                if addr['pending_confirmation']:
                    status_icon = "⏳"
                    status_text = "待确认"
                elif addr['is_active']:
                    status_icon = "✅"
                    status_text = "已启用"
                else:
                    status_icon = "❌"
                    status_text = "已禁用"
                
                default_icon = "⭐" if addr['is_default'] else ""
                addr_display = addr['address'][:15] + "..." + addr['address'][-15:] if len(addr['address']) > 30 else addr['address']
                
                message += (
                    f"{idx}. {status_icon} {default_icon} <b>{addr['label'] or '未命名'}</b>\n"
                    f"   状态: {status_text}\n"
                    f"   地址: <code>{addr_display}</code>\n"
                    f"   使用次数: {addr['usage_count']}\n"
                )
                if addr['last_used_at']:
                    message += f"   最后使用: {addr['last_used_at'][:16]}\n"
                if addr['confirmed_at']:
                    message += f"   确认时间: {addr['confirmed_at'][:16]}\n"
                message += "\n"
        
        keyboard = []
        for idx, addr in enumerate(addresses[:10], 1):  # Max 10 addresses per page
            keyboard.append([
                InlineKeyboardButton(
                    f"{idx}. {addr['label'] or '未命名'[:10]}",
                    callback_data=f"address_detail_{addr['id']}"
                )
            ])
        
        keyboard.append([
                InlineKeyboardButton("➕ 添加地址", callback_data="address_add"),
                InlineKeyboardButton("🔄 刷新", callback_data="address_list")
        ])
        
        # Add back button based on context
        if 'selected_group_id' in context.user_data:
            keyboard.append([
                InlineKeyboardButton("🔙 返回群组管理", callback_data="global_groups_list")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🔙 返回", callback_data="group_settings_menu")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            try:
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
            except BadRequest as e:
                if "not modified" in str(e).lower():
                    await query.answer("✅ 内容未更改")
                else:
                    raise
        else:
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_address_list: {e}", exc_info=True)
        try:
            if query:
                await query.answer("❌ 错误: " + str(e), show_alert=True)
            else:
                await update.message.reply_text("❌ 错误: " + str(e))
        except Exception as inner_e:
            logger.error(f"Error sending error message: {inner_e}", exc_info=True)


async def handle_address_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle address detail view"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        # Extract address_id from callback_data
        callback_data = query.data
        if not callback_data.startswith("address_detail_"):
            await query.answer("❌ 无效的地址ID", show_alert=True)
            return
        
        address_id = int(callback_data.split("_")[-1])
        address = db.get_address_by_id(address_id)
        
        if not address:
            await query.answer("❌ 地址不存在", show_alert=True)
            return
        
        # Build detail message
        status_icon = "⏳" if address['pending_confirmation'] else ("✅" if address['is_active'] else "❌")
        status_text = "待确认" if address['pending_confirmation'] else ("已启用" if address['is_active'] else "已禁用")
        
        message = (
            f"📍 <b>地址详情</b>\n"
            f"────────────────────────\n\n"
            f"<b>标签：</b>{address['label'] or '未命名'}\n"
            f"<b>状态：</b>{status_icon} {status_text}\n"
            f"<b>地址：</b>\n<code>{address['address']}</code>\n\n"
        )
        
        if address['is_default']:
            message += "⭐ <b>默认地址</b>\n\n"
        
        if address['qr_code_file_id']:
            message += "📷 <b>已上传二维码</b>\n\n"
        
        message += (
            f"<b>使用次数：</b>{address['usage_count']}\n"
        )
        
        if address['last_used_at']:
            message += f"<b>最后使用：</b>{address['last_used_at'][:16]}\n"
        
        if address['pending_confirmation']:
            message += "\n⚠️ <b>此地址等待群组成员确认</b>\n"
        elif address['confirmed_at']:
            message += f"<b>确认时间：</b>{address['confirmed_at'][:16]}\n"
        
        message += f"\n<b>创建时间：</b>{address['created_at'][:16]}\n"
        
        keyboard = []
        
        # Show QR code button if exists
        if address['qr_code_file_id']:
            keyboard.append([
                InlineKeyboardButton("📷 显示二维码", callback_data=f"address_show_qr_{address_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("✏️ 编辑", callback_data=f"address_edit_{address_id}"),
            InlineKeyboardButton("🗑️ 删除", callback_data=f"address_delete_{address_id}")
        ])
        
        if not address['is_default']:
            keyboard.append([
                InlineKeyboardButton("⭐ 设为默认", callback_data=f"address_set_default_{address_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔄 启用/禁用", callback_data=f"address_toggle_{address_id}")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 返回列表", callback_data="address_list")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
        except BadRequest as e:
            if "not modified" in str(e).lower():
                await query.answer("✅ 内容未更改")
            else:
                raise
        
    except Exception as e:
        logger.error(f"Error in handle_address_detail: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_show_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle showing QR code for address"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        callback_data = query.data
        address_id = int(callback_data.split("_")[-1])
        address = db.get_address_by_id(address_id)
        
        if not address or not address['qr_code_file_id']:
            await query.answer("❌ 此地址没有二维码", show_alert=True)
            return
        
        # Send QR code photo with address text
        message = (
            f"📍 <b>收款地址</b>\n\n"
            f"<b>标签：</b>{address['label'] or '未命名'}\n"
            f"<b>地址：</b>\n<code>{address['address']}</code>\n\n"
            f"💡 请扫描上方二维码或复制地址进行转账"
        )
        
        try:
            await query.message.reply_photo(
                photo=address['qr_code_file_id'],
                caption=message,
                parse_mode="HTML"
            )
            await query.answer("✅ 二维码已发送")
        except Exception as e:
            logger.error(f"Error sending QR code: {e}", exc_info=True)
            await query.answer("❌ 发送二维码失败", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in handle_address_show_qr: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_add_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle address add prompt"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        chat = query.message.chat
        group_id = chat.id if chat.type in ['group', 'supergroup'] else None
        
        # Get group_id from context if in private chat
        if not group_id and 'selected_group_id' in context.user_data:
            group_id = context.user_data['selected_group_id']
        
        if not group_id:
            await query.answer("❌ 请在群组中使用此功能，或从私聊中选择群组", show_alert=True)
            return
        
        message = (
            f"➕ <b>添加群组地址</b>\n\n"
            f"群组ID: <code>{group_id}</code>\n\n"
            f"请按以下步骤操作：\n"
            f"1️⃣ 输入 USDT 地址\n"
            f"2️⃣ （可选）发送二维码图片\n\n"
            f"💡 <i>提示：地址格式应为有效的 USDT 钱包地址（26-60个字符）</i>\n"
            f"💡 <i>添加后需要群组成员确认才能使用</i>"
        )
        
        try:
        await query.edit_message_text(message, parse_mode="HTML")
        except BadRequest as e:
            if "not modified" in str(e).lower():
                await query.answer("✅ 内容未更改")
            else:
                raise
        
        context.user_data['adding_address'] = True
        context.user_data['address_group_id'] = group_id
        context.user_data['address_step'] = 'address'  # address -> qr_code (optional)
        
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error in handle_address_add_prompt: {e}", exc_info=True)
        try:
            if update.callback_query:
        await update.callback_query.answer("❌ 错误", show_alert=True)
        except Exception as inner_e:
            logger.error(f"Error sending error message: {inner_e}", exc_info=True)


async def handle_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE, address_text: str):
    """Handle address input"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if 'adding_address' not in context.user_data or context.user_data.get('address_step') != 'address':
            return
        
        group_id = context.user_data.get('address_group_id')
        if not group_id:
            await update.message.reply_text("❌ 群组ID无效，请重新开始")
            del context.user_data['adding_address']
            return
        
        address = address_text.strip()
        
        # Basic validation
        if len(address) < 26 or len(address) > 60:
            await update.message.reply_text("❌ 地址格式无效，USDT 地址应为 26-60 个字符")
            return
        
        # Check if address already exists in this group
        existing = db.get_usdt_addresses(group_id=group_id, active_only=False)
        if any(a['address'] == address for a in existing):
            await update.message.reply_text("❌ 该地址已存在于此群组")
            return
        
        # Store address in context, wait for optional QR code
        context.user_data['new_address'] = address
        context.user_data['address_step'] = 'qr_code'
        
        message = (
            f"✅ <b>地址已接收</b>\n\n"
            f"地址: <code>{address[:20]}...</code>\n\n"
            f"📷 现在可以发送二维码图片（可选）\n"
            f"或点击「跳过」直接添加地址"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("⏭️ 跳过，直接添加", callback_data="address_add_skip_qr"),
                InlineKeyboardButton("❌ 取消", callback_data="address_add_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in handle_address_input: {e}", exc_info=True)
        await update.message.reply_text("❌ 错误: " + str(e))


async def handle_address_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle QR code photo upload"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            return
        
        if 'adding_address' not in context.user_data or context.user_data.get('address_step') != 'qr_code':
            return
        
        if 'new_address' not in context.user_data:
            return
        
        group_id = context.user_data.get('address_group_id')
        if not group_id:
            return
        
        # Get the largest photo (best quality)
        photo = update.message.photo[-1] if update.message.photo else None
        if not photo:
            await update.message.reply_text("❌ 未检测到图片，请重新发送")
            return
        
        file_id = photo.file_id
        address = context.user_data['new_address']
        
        # Add address with QR code
        address_id = db.add_usdt_address(
            group_id=group_id,
            address=address,
            label="群组地址",
            qr_code_file_id=file_id,
            needs_confirmation=True,
            created_by=user_id
        )
        
        if address_id:
            # Send confirmation message to group
            await send_address_confirmation_message(update, context, address_id, group_id)
            
            message = (
                f"✅ <b>地址已添加</b>\n\n"
                f"地址: <code>{address[:20]}...</code>\n"
                f"二维码: ✅ 已上传\n\n"
                f"⏳ 等待群组成员确认后即可使用"
            )
            await update.message.reply_text(message, parse_mode="HTML")
            
            # Clean up context
            del context.user_data['adding_address']
            del context.user_data['address_group_id']
            del context.user_data['new_address']
            del context.user_data['address_step']
            
            logger.info(f"Admin {user_id} added address {address_id} with QR code (group_id: {group_id})")
        else:
            await update.message.reply_text("❌ 添加地址失败，请重试")
        
    except Exception as e:
        logger.error(f"Error in handle_address_photo: {e}", exc_info=True)
        await update.message.reply_text("❌ 错误: " + str(e))


async def handle_address_add_skip_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle skip QR code and add address"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        if 'new_address' not in context.user_data:
            await query.answer("❌ 未找到地址信息", show_alert=True)
            return
        
        group_id = context.user_data.get('address_group_id')
        address = context.user_data['new_address']
        
        if not group_id:
            await query.answer("❌ 群组ID无效", show_alert=True)
            return
        
        # Add address without QR code
        address_id = db.add_usdt_address(
            group_id=group_id,
            address=address,
            label="群组地址",
            needs_confirmation=True,
            created_by=user_id
        )
        
        if address_id:
            # Send confirmation message to group
            await send_address_confirmation_message(update, context, address_id, group_id)
            
            message = (
                f"✅ <b>地址已添加</b>\n\n"
                f"地址: <code>{address[:20]}...</code>\n\n"
                f"⏳ 等待群组成员确认后即可使用"
            )
            
            try:
                await query.edit_message_text(message, parse_mode="HTML")
            except BadRequest:
                await query.message.reply_text(message, parse_mode="HTML")
            
            await query.answer("✅ 地址已添加")
            
            # Clean up context
            del context.user_data['adding_address']
            del context.user_data['address_group_id']
            del context.user_data['new_address']
            del context.user_data['address_step']
            
            logger.info(f"Admin {user_id} added address {address_id} without QR code (group_id: {group_id})")
        else:
            await query.answer("❌ 添加地址失败", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in handle_address_add_skip_qr: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel adding address"""
    try:
        query = update.callback_query
        
        # Clean up context
        if 'adding_address' in context.user_data:
            del context.user_data['adding_address']
        if 'address_group_id' in context.user_data:
            del context.user_data['address_group_id']
        if 'new_address' in context.user_data:
            del context.user_data['new_address']
        if 'address_step' in context.user_data:
            del context.user_data['address_step']
        
        await query.answer("❌ 已取消")
        await query.edit_message_text("❌ 已取消添加地址")
        
    except Exception as e:
        logger.error(f"Error in handle_address_add_cancel: {e}", exc_info=True)
        await query.answer("❌ 错误", show_alert=True)


async def send_address_confirmation_message(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                           address_id: int, group_id: int):
    """Send address confirmation message to group"""
    try:
        address = db.get_address_by_id(address_id)
        if not address:
            return
        
        admin = update.effective_user
        admin_name = admin.first_name or admin.username or "管理员"
        
        message = (
            f"📍 <b>新地址待确认</b>\n"
            f"────────────────────────\n\n"
            f"管理员 <b>{admin_name}</b> 添加了新地址：\n\n"
            f"<b>标签：</b>{address['label'] or '未命名'}\n"
            f"<b>地址：</b>\n<code>{address['address']}</code>\n\n"
            f"⚠️ 请确认此地址是否正确\n\n"
            f"💡 只有群组成员可以确认地址"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ 确认地址正确", callback_data=f"address_confirm_{address_id}"),
                InlineKeyboardButton("❌ 地址有误", callback_data=f"address_reject_{address_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send to group
        from telegram import Bot
        bot = context.bot
        await bot.send_message(
            chat_id=group_id,
            text=message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error sending confirmation message: {e}", exc_info=True)


async def handle_address_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle address confirmation by group member"""
    try:
        query = update.callback_query
        user = query.from_user
        user_id = user.id
        
        # Only non-admin users can confirm (to prevent self-confirmation)
        if is_admin(user_id):
            await query.answer("❌ 管理员不能确认自己添加的地址，请等待其他群组成员确认", show_alert=True)
            return
        
        callback_data = query.data
        address_id = int(callback_data.split("_")[-1])
        address = db.get_address_by_id(address_id)
        
        if not address:
            await query.answer("❌ 地址不存在", show_alert=True)
            return
        
        if not address['pending_confirmation']:
            await query.answer("✅ 此地址已确认", show_alert=True)
            return
        
        # Confirm address
        if db.confirm_address(address_id, user_id):
            # 如果地址没有二维码，自动生成并保存
            if not address.get('qr_code_file_id'):
                try:
                    from utils.qr_generator import generate_qr_code_bytes, QRCODE_AVAILABLE
                    if QRCODE_AVAILABLE:
                        bot = context.bot
                        # 生成二维码
                        qr_bytes = generate_qr_code_bytes(address['address'])
                        if qr_bytes:
                            # 发送到群组并获取file_id（静默发送，caption为空）
                            sent_message = await bot.send_photo(
                                chat_id=address['group_id'],
                                photo=qr_bytes,
                                caption="",  # 静默发送，不显示caption
                                parse_mode=None
                            )
                            if sent_message.photo:
                                file_id = sent_message.photo[-1].file_id
                                # 保存二维码file_id到数据库
                                db.update_address_qr_code(address_id, file_id)
                                logger.info(f"Auto-generated and saved QR code for confirmed address {address_id}")
                            else:
                                logger.warning(f"Failed to get file_id from sent QR code for address {address_id}")
                except Exception as qr_error:
                    logger.warning(f"Failed to auto-generate QR code for address {address_id}: {qr_error}")
            
            message = (
                f"✅ <b>地址已确认</b>\n\n"
                f"<b>标签：</b>{address['label'] or '未命名'}\n"
                f"<b>地址：</b><code>{address['address']}</code>\n\n"
                f"确认者：{user.first_name or user.username or '群组成员'}\n"
                f"确认时间：{address['confirmed_at'][:16] if address.get('confirmed_at') else '刚刚'}\n\n"
                f"✅ 此地址现在可以用于结算"
            )
            
            try:
                await query.edit_message_text(message, parse_mode="HTML")
            except BadRequest:
                await query.message.reply_text(message, parse_mode="HTML")
            
            await query.answer("✅ 地址已确认")
            logger.info(f"Address {address_id} confirmed by user {user_id}")
        else:
            await query.answer("❌ 确认失败，请重试", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in handle_address_confirm: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle address rejection"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        callback_data = query.data
        address_id = int(callback_data.split("_")[-1])
        
        # Delete the rejected address
        if db.delete_usdt_address(address_id):
            message = "❌ 地址已被拒绝并删除"
            try:
                await query.edit_message_text(message)
            except BadRequest:
                await query.message.reply_text(message)
            await query.answer("✅ 地址已删除")
            logger.info(f"Address {address_id} rejected and deleted by user {user_id}")
        else:
            await query.answer("❌ 删除失败", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in handle_address_reject: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle address deletion"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        callback_data = query.data
        address_id = int(callback_data.split("_")[-1])
        address = db.get_address_by_id(address_id)
        
        if not address:
            await query.answer("❌ 地址不存在", show_alert=True)
            return
        
        # Confirm deletion
        message = (
            f"🗑️ <b>确认删除地址</b>\n\n"
            f"<b>标签：</b>{address['label'] or '未命名'}\n"
            f"<b>地址：</b><code>{address['address'][:30]}...</code>\n\n"
            f"⚠️ 此操作不可恢复！"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ 确认删除", callback_data=f"address_delete_confirm_{address_id}"),
                InlineKeyboardButton("❌ 取消", callback_data=f"address_detail_{address_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
        except BadRequest as e:
            if "not modified" in str(e).lower():
                await query.answer("✅ 内容未更改")
            else:
                raise
        
    except Exception as e:
        logger.error(f"Error in handle_address_delete: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmed address deletion"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        callback_data = query.data
        
        logger.info(f"handle_address_delete_confirm called: callback_data={callback_data}, user_id={user_id}")
        
        if not is_admin(user_id):
            logger.warning(f"User {user_id} attempted to delete address but is not admin")
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        try:
            address_id = int(callback_data.split("_")[-1])
            logger.info(f"Parsed address_id: {address_id}")
        except (ValueError, IndexError) as e:
            logger.error(f"Invalid address_id format: {callback_data}, error: {e}")
            await query.answer("❌ 无效的地址ID", show_alert=True)
            return
        
        # Get address info before deletion for logging
        address = db.get_address_by_id(address_id)
        if not address:
            logger.warning(f"Address {address_id} not found")
            await query.answer("❌ 地址不存在", show_alert=True)
            return
        
        logger.info(f"Attempting to delete address {address_id} (label: {address.get('label', 'N/A')}, group_id: {address.get('group_id', 'N/A')})")
        
        # Delete address
        if db.delete_usdt_address(address_id):
            logger.info(f"Successfully deleted address {address_id} by admin {user_id}")
            message = "✅ 地址已删除"
            try:
                await query.edit_message_text(message)
            except BadRequest as e:
                logger.warning(f"Failed to edit message, trying reply: {e}")
                try:
                    await query.message.reply_text(message)
                except Exception as reply_error:
                    logger.error(f"Failed to send reply message: {reply_error}")
            await query.answer("✅ 已删除")
        else:
            logger.error(f"delete_usdt_address returned False for address_id: {address_id}")
            await query.answer("❌ 删除失败，请重试", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in handle_address_delete_confirm: {e}", exc_info=True)
        try:
            await query.answer("❌ 错误: " + str(e), show_alert=True)
        except Exception as answer_error:
            logger.error(f"Error sending answer: {answer_error}", exc_info=True)


async def handle_address_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle address edit prompt"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        callback_data = query.data
        address_id = int(callback_data.split("_")[-1])
        address = db.get_address_by_id(address_id)
        
        if not address:
            await query.answer("❌ 地址不存在", show_alert=True)
            return
        
        message = (
            f"✏️ <b>编辑地址</b>\n\n"
            f"<b>当前标签：</b>{address['label'] or '未命名'}\n"
            f"<b>当前地址：</b><code>{address['address']}</code>\n\n"
            f"请选择要编辑的内容："
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✏️ 编辑标签", callback_data=f"address_edit_label_{address_id}"),
                InlineKeyboardButton("✏️ 编辑地址", callback_data=f"address_edit_addr_{address_id}")
            ],
            [
                InlineKeyboardButton("📷 上传/更新二维码", callback_data=f"address_edit_qr_{address_id}")
            ],
            [
                InlineKeyboardButton("🔙 返回详情", callback_data=f"address_detail_{address_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(message, parse_mode="HTML", reply_markup=reply_markup)
            await query.answer()
        except BadRequest as e:
            if "not modified" in str(e).lower():
                await query.answer("✅ 内容未更改")
            else:
                raise
        
    except Exception as e:
        logger.error(f"Error in handle_address_edit: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_set_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle setting address as default"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        callback_data = query.data
        address_id = int(callback_data.split("_")[-1])
        
        if db.update_usdt_address(address_id, is_default=True):
            await query.answer("✅ 已设为默认地址")
            # Refresh detail view
            await handle_address_detail(update, context)
        else:
            await query.answer("❌ 设置失败", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in handle_address_set_default: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle toggling address active status"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        callback_data = query.data
        address_id = int(callback_data.split("_")[-1])
        address = db.get_address_by_id(address_id)
        
        if not address:
            await query.answer("❌ 地址不存在", show_alert=True)
            return
        
        new_status = not address['is_active']
        if db.update_usdt_address(address_id, is_active=new_status):
            status_text = "已启用" if new_status else "已禁用"
            await query.answer(f"✅ {status_text}")
            # Refresh detail view
            await handle_address_detail(update, context)
        else:
            await query.answer("❌ 操作失败", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in handle_address_toggle: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_edit_label(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle editing address label"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        callback_data = query.data
        address_id = int(callback_data.split("_")[-1])
        address = db.get_address_by_id(address_id)
        
        if not address:
            await query.answer("❌ 地址不存在", show_alert=True)
            return
        
        message = (
            f"✏️ <b>编辑标签</b>\n\n"
            f"当前标签：{address['label'] or '未命名'}\n\n"
            f"请输入新标签："
        )
        
        try:
            await query.edit_message_text(message, parse_mode="HTML")
        except BadRequest:
            await query.message.reply_text(message, parse_mode="HTML")
        
        context.user_data['editing_address_label'] = address_id
        await query.answer("💡 请输入新标签")
        
    except Exception as e:
        logger.error(f"Error in handle_address_edit_label: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_edit_addr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle editing address"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        callback_data = query.data
        address_id = int(callback_data.split("_")[-1])
        address = db.get_address_by_id(address_id)
        
        if not address:
            await query.answer("❌ 地址不存在", show_alert=True)
            return
        
        message = (
            f"✏️ <b>编辑地址</b>\n\n"
            f"当前地址：\n<code>{address['address']}</code>\n\n"
            f"请输入新地址：\n\n"
            f"💡 <i>提示：地址格式应为有效的 USDT 钱包地址（26-60个字符）</i>\n"
            f"⚠️ <i>修改地址后需要重新确认</i>"
        )
        
        try:
            await query.edit_message_text(message, parse_mode="HTML")
        except BadRequest:
            await query.message.reply_text(message, parse_mode="HTML")
        
        context.user_data['editing_address'] = address_id
        await query.answer("💡 请输入新地址")
        
    except Exception as e:
        logger.error(f"Error in handle_address_edit_addr: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_edit_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle editing QR code"""
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not is_admin(user_id):
            await query.answer("❌ 此功能仅限管理员使用", show_alert=True)
            return
        
        callback_data = query.data
        address_id = int(callback_data.split("_")[-1])
        address = db.get_address_by_id(address_id)
        
        if not address:
            await query.answer("❌ 地址不存在", show_alert=True)
            return
        
        message = (
            f"📷 <b>上传/更新二维码</b>\n\n"
            f"地址：<code>{address['address'][:30]}...</code>\n\n"
            f"请发送二维码图片："
        )
        
        try:
            await query.edit_message_text(message, parse_mode="HTML")
        except BadRequest:
            await query.message.reply_text(message, parse_mode="HTML")
        
        context.user_data['editing_address_qr'] = address_id
        await query.answer("💡 请发送二维码图片")
        
    except Exception as e:
        logger.error(f"Error in handle_address_edit_qr: {e}", exc_info=True)
        await query.answer("❌ 错误: " + str(e), show_alert=True)


async def handle_address_label_input(update: Update, context: ContextTypes.DEFAULT_TYPE, label_text: str):
    """Handle address label input"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if 'editing_address_label' not in context.user_data:
            return
        
        address_id = context.user_data['editing_address_label']
        label = label_text.strip()
        
        if not label:
            await update.message.reply_text("❌ 标签不能为空")
            return
        
        if len(label) > 50:
            await update.message.reply_text("❌ 标签长度不能超过50个字符")
            return
        
        if db.update_usdt_address(address_id, label=label):
            message = f"✅ 标签已更新为：{label}"
            await update.message.reply_text(message)
            
            del context.user_data['editing_address_label']
            logger.info(f"Admin {user_id} updated label for address {address_id}")
        else:
            await update.message.reply_text("❌ 更新失败，请重试")
        
    except Exception as e:
        logger.error(f"Error in handle_address_label_input: {e}", exc_info=True)
        await update.message.reply_text("❌ 错误: " + str(e))


async def handle_address_addr_input(update: Update, context: ContextTypes.DEFAULT_TYPE, address_text: str):
    """Handle address input for editing"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ 此功能仅限管理员使用")
            return
        
        if 'editing_address' not in context.user_data:
            return
        
        address_id = context.user_data['editing_address']
        address = db.get_address_by_id(address_id)
        
        if not address:
            await update.message.reply_text("❌ 地址不存在")
            del context.user_data['editing_address']
            return
        
        new_address = address_text.strip()
        
        # Basic validation
        if len(new_address) < 26 or len(new_address) > 60:
            await update.message.reply_text("❌ 地址格式无效，USDT 地址应为 26-60 个字符")
            return
        
        # Check if address already exists in the same group
        existing = db.get_usdt_addresses(group_id=address['group_id'], active_only=False)
        if any(a['address'] == new_address and a['id'] != address_id for a in existing):
            await update.message.reply_text("❌ 该地址已存在于此群组")
            return
        
        # Update address and set needs confirmation
        if db.update_usdt_address(address_id, address=new_address, needs_confirmation=True):
            # Send confirmation message to group
            await send_address_confirmation_message(update, context, address_id, address['group_id'])
            
            message = (
                f"✅ <b>地址已更新</b>\n\n"
                f"新地址: <code>{new_address[:20]}...</code>\n\n"
                f"⏳ 等待群组成员确认后即可使用"
            )
            await update.message.reply_text(message, parse_mode="HTML")
            
            del context.user_data['editing_address']
            logger.info(f"Admin {user_id} updated address {address_id}")
        else:
            await update.message.reply_text("❌ 更新失败，请重试")
        
    except Exception as e:
        logger.error(f"Error in handle_address_addr_input: {e}", exc_info=True)
        await update.message.reply_text("❌ 错误: " + str(e))


async def handle_address_qr_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle QR code photo upload for editing"""
    try:
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            return
        
        if 'editing_address_qr' not in context.user_data:
            return
        
        address_id = context.user_data['editing_address_qr']
        address = db.get_address_by_id(address_id)
        
        if not address:
            await update.message.reply_text("❌ 地址不存在")
            del context.user_data['editing_address_qr']
            return
        
        # Get the largest photo (best quality)
        photo = update.message.photo[-1] if update.message.photo else None
        if not photo:
            await update.message.reply_text("❌ 未检测到图片，请重新发送")
            return
        
        file_id = photo.file_id
        
        # Update QR code
        if db.update_address_qr_code(address_id, file_id):
            message = (
                f"✅ <b>二维码已更新</b>\n\n"
                f"地址: <code>{address['address'][:20]}...</code>\n"
                f"二维码: ✅ 已更新"
            )
            await update.message.reply_text(message, parse_mode="HTML")
            
            del context.user_data['editing_address_qr']
            logger.info(f"Admin {user_id} updated QR code for address {address_id}")
        else:
            await update.message.reply_text("❌ 更新失败，请重试")
        
    except Exception as e:
        logger.error(f"Error in handle_address_qr_photo: {e}", exc_info=True)
        await update.message.reply_text("❌ 错误: " + str(e))
