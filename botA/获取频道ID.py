"""
获取 Telegram 频道的正确 ID
使用方法：
1. 将 Bot A 添加到频道作为管理员
2. 运行此脚本
3. 在频道中发送任意消息
4. 脚本会显示频道 ID
"""
import asyncio
import logging
from aiogram import Bot
from aiogram.types import Update
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_channel_updates():
    """获取频道更新以获取频道 ID"""
    bot = Bot(token=Config.BOT_TOKEN)
    
    print("=" * 50)
    print("🔍 获取频道 ID 工具")
    print("=" * 50)
    print("\n📋 使用说明：")
    print("1. 确保 Bot A 已添加到频道作为管理员")
    print("2. 在频道中发送任意消息（视频、文本等）")
    print("3. 脚本会显示频道信息\n")
    print("正在监听频道更新...")
    print("（按 Ctrl+C 停止）\n")
    print("=" * 50)
    
    try:
        updates = await bot.get_updates(limit=10, timeout=30)
        
        channel_updates = []
        for update in updates:
            if update.channel_post:
                channel_id = update.channel_post.chat.id
                channel_title = update.channel_post.chat.title or "未知频道"
                channel_username = getattr(update.channel_post.chat, 'username', None)
                
                channel_info = {
                    'id': channel_id,
                    'title': channel_title,
                    'username': channel_username,
                    'type': update.channel_post.chat.type
                }
                
                # 避免重复
                if not any(c['id'] == channel_id for c in channel_updates):
                    channel_updates.append(channel_info)
        
        if channel_updates:
            print("\n✅ 找到以下频道：\n")
            for i, ch in enumerate(channel_updates, 1):
                print(f"{i}. 频道名称: {ch['title']}")
                print(f"   频道 ID: {ch['id']}")
                if ch['username']:
                    print(f"   用户名: @{ch['username']}")
                print(f"   类型: {ch['type']}")
                print()
            
            # 查找包含"素材"或"视频"的频道
            target = None
            for ch in channel_updates:
                if '素材' in ch['title'] or '视频' in ch['title'] or '伍拾' in ch['title']:
                    target = ch
                    break
            
            if target:
                print(f"\n🎯 推荐的频道 ID: {target['id']}")
                print(f"   频道名称: {target['title']}")
                print(f"\n请在 botA/handlers/channel_video_handler.py 中更新：")
                print(f"VIDEO_CHANNEL_ID = {target['id']}")
            else:
                print(f"\n💡 请从上面的列表中选择正确的频道 ID")
        else:
            print("\n⚠️  未检测到频道更新")
            print("\n可能的原因：")
            print("1. Bot 未添加到频道")
            print("2. Bot 不是管理员")
            print("3. 频道中还没有消息")
            print("4. 频道 ID 已被清理（需要新消息）")
            print("\n解决方法：")
            print("1. 确保 Bot A 已添加到频道作为管理员")
            print("2. 在频道中发送一条新消息")
            print("3. 重新运行此脚本")
    
    except Exception as e:
        logger.error(f"错误: {e}", exc_info=True)
    finally:
        await bot.session.close()


async def test_current_channel():
    """测试当前配置的频道 ID"""
    bot = Bot(token=Config.BOT_TOKEN)
    channel_id = -1003390475622  # 当前配置的 ID
    
    try:
        chat = await bot.get_chat(channel_id)
        print(f"\n✅ 当前配置的频道 ID ({channel_id}) 有效")
        print(f"频道名称: {chat.title}")
        print(f"频道类型: {chat.type}")
        if hasattr(chat, 'username'):
            print(f"用户名: @{chat.username}")
    except Exception as e:
        print(f"\n❌ 当前配置的频道 ID ({channel_id}) 无效或 Bot 无权限访问")
        print(f"错误: {e}")
        print("\n请使用上面的方法获取正确的频道 ID")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        exit(1)
    
    # 先测试当前配置
    asyncio.run(test_current_channel())
    
    # 然后获取更新
    asyncio.run(get_channel_updates())

