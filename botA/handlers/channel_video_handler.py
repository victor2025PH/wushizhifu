"""
Channel video handler for automatic video updates
监听频道视频并询问管理员是微信还是支付宝视频
"""
import logging
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.video_repository import VideoRepository
from database.admin_repository import AdminRepository
from config import Config

router = Router()
logger = logging.getLogger(__name__)

# 频道 ID
# 如果频道 ID 不正确，请：
# 1. 运行 botA/获取频道ID.py 获取正确的频道 ID
# 2. 更新下面的值
# 3. 重启 Bot A 服务
VIDEO_CHANNEL_ID = -1003390475622  # TODO: 请确认这是正确的频道 ID

# 临时存储待确认的视频信息 (message_id -> video_info)
pending_videos: dict[int, dict] = {}


@router.channel_post(F.chat.id == VIDEO_CHANNEL_ID, F.video)
async def handle_channel_video(message: Message, bot: Bot):
    """
    处理频道中的视频消息
    """
    try:
        # 检查是否有视频
        if not message.video:
            return
        
        video = message.video
        channel_id = message.chat.id
        message_id = message.message_id
        
        logger.info(f"检测到频道视频: channel_id={channel_id}, message_id={message_id}, file_id={video.file_id}")
        
        # 保存待确认的视频信息
        video_info = {
            'channel_id': channel_id,
            'message_id': message_id,
            'file_id': video.file_id,
            'file_unique_id': video.file_unique_id,
            'file_size': video.file_size,
            'duration': video.duration,
            'thumbnail': video.thumbnail.file_id if video.thumbnail else None
        }
        pending_videos[message_id] = video_info
        
        # 获取所有管理员
        admins = AdminRepository.get_all_admins()
        
        if not admins:
            logger.warning("没有找到管理员，无法询问视频类型")
            return
        
        # 创建询问键盘
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="微信视频", callback_data=f"video_type:wechat:{message_id}"),
                InlineKeyboardButton(text="支付宝视频", callback_data=f"video_type:alipay:{message_id}")
            ],
            [
                InlineKeyboardButton(text="取消", callback_data=f"video_type:cancel:{message_id}")
            ]
        ])
        
        # 向所有管理员发送询问消息
        question_text = (
            f"📹 检测到频道新视频\n\n"
            f"消息 ID: {message_id}\n"
            f"文件大小: {video.file_size / 1024 / 1024:.2f} MB\n"
            f"时长: {video.duration} 秒\n\n"
            f"请选择视频类型："
        )
        
        for admin in admins:
            try:
                admin_id = admin['user_id']
                await bot.send_message(
                    chat_id=admin_id,
                    text=question_text,
                    reply_markup=keyboard
                )
                logger.info(f"已向管理员 {admin_id} 发送视频类型询问")
            except Exception as e:
                logger.error(f"向管理员 {admin_id} 发送消息失败: {e}")
        
    except Exception as e:
        logger.error(f"处理频道视频错误: {e}", exc_info=True)


@router.callback_query(F.data.startswith("video_type:"))
async def handle_video_type_selection(callback: CallbackQuery, bot: Bot):
    """
    处理视频类型选择
    """
    try:
        # 解析 callback_data: video_type:wechat:123 或 video_type:alipay:123
        parts = callback.data.split(":")
        if len(parts) != 3:
            await callback.answer("❌ 无效的请求", show_alert=True)
            return
        
        action, video_type, message_id_str = parts
        message_id = int(message_id_str)
        
        # 检查是否是管理员
        user_id = callback.from_user.id
        if not AdminRepository.is_admin(user_id):
            await callback.answer("❌ 您不是管理员，无权操作", show_alert=True)
            return
        
        # 如果是取消操作
        if video_type == "cancel":
            if message_id in pending_videos:
                del pending_videos[message_id]
            await callback.message.edit_text("❌ 已取消视频配置")
            await callback.answer("已取消")
            return
        
        # 验证视频类型
        if video_type not in ["wechat", "alipay"]:
            await callback.answer("❌ 无效的视频类型", show_alert=True)
            return
        
        # 获取待确认的视频信息
        if message_id not in pending_videos:
            await callback.answer("❌ 视频信息已过期，请重新上传", show_alert=True)
            return
        
        video_info = pending_videos[message_id]
        
        # 保存视频配置
        success = VideoRepository.save_video_config(
            video_type=video_type,
            channel_id=video_info['channel_id'],
            message_id=video_info['message_id'],
            file_id=video_info['file_id'],
            file_unique_id=video_info.get('file_unique_id'),
            file_size=video_info.get('file_size'),
            duration=video_info.get('duration'),
            thumbnail_file_id=video_info.get('thumbnail'),
            updated_by=user_id
        )
        
        if success:
            # 删除待确认信息
            del pending_videos[message_id]
            
            video_type_name = "微信" if video_type == "wechat" else "支付宝"
            await callback.message.edit_text(
                f"✅ {video_type_name}视频配置已更新！\n\n"
                f"消息 ID: {message_id}\n"
                f"文件 ID: {video_info['file_id'][:20]}...\n"
                f"更新时间: {callback.message.date.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await callback.answer(f"{video_type_name}视频已保存")
            logger.info(f"视频配置已更新: {video_type}, message_id={message_id}, updated_by={user_id}")
        else:
            await callback.answer("❌ 保存失败，请稍后重试", show_alert=True)
            logger.error(f"保存视频配置失败: {video_type}, message_id={message_id}")
        
    except ValueError as e:
        logger.error(f"解析 callback_data 错误: {e}")
        await callback.answer("❌ 请求格式错误", show_alert=True)
    except Exception as e:
        logger.error(f"处理视频类型选择错误: {e}", exc_info=True)
        await callback.answer("❌ 系统错误，请稍后重试", show_alert=True)

