"""
验证 Bot A 是否能访问频道并接收消息
使用方法：直接运行，不需要停止 Bot A 服务
"""
import asyncio
import logging
from aiogram import Bot
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 当前配置的频道 ID
VIDEO_CHANNEL_ID = -1003390475622


async def verify_channel_access():
    """验证频道访问权限"""
    bot = Bot(token=Config.BOT_TOKEN)
    
    print("=" * 60)
    print("🔍 验证 Bot A 频道访问权限")
    print("=" * 60)
    print()
    
    try:
        # 1. 测试获取频道信息
        print("1️⃣  测试获取频道信息...")
        try:
            chat = await bot.get_chat(VIDEO_CHANNEL_ID)
            print(f"   ✅ 成功获取频道信息")
            print(f"   频道名称: {chat.title}")
            print(f"   频道类型: {chat.type}")
            if hasattr(chat, 'username') and chat.username:
                print(f"   用户名: @{chat.username}")
            print()
        except Exception as e:
            print(f"   ❌ 无法获取频道信息: {e}")
            print("   可能原因：")
            print("   - Bot 未添加到频道")
            print("   - Bot 不是管理员")
            print("   - 频道 ID 不正确")
            print()
            await bot.session.close()
            return
        
        # 2. 检查 Bot 是否是频道成员
        print("2️⃣  检查 Bot 成员状态...")
        try:
            member = await bot.get_chat_member(VIDEO_CHANNEL_ID, bot.id)
            print(f"   ✅ Bot 是频道成员")
            print(f"   状态: {member.status}")
            if member.status in ['administrator', 'creator']:
                print(f"   ✅ Bot 是管理员")
            else:
                print(f"   ⚠️  Bot 不是管理员（需要管理员权限才能接收频道消息）")
            print()
        except Exception as e:
            print(f"   ❌ 无法获取成员信息: {e}")
            print()
        
        # 3. 检查频道消息权限
        print("3️⃣  检查频道消息权限...")
        try:
            # 尝试获取频道的最新消息（如果有权限）
            # 注意：这可能需要 Bot 有读取消息历史权限
            print("   ℹ️  频道消息权限检查需要手动验证")
            print("   请确认：")
            print("   - Bot 在频道设置中是否有'查看消息'权限")
            print("   - Bot 是否有'读取消息历史'权限")
            print()
        except Exception as e:
            print(f"   ⚠️  {e}")
            print()
        
        # 4. 总结和建议
        print("=" * 60)
        print("📋 验证总结")
        print("=" * 60)
        print()
        print("✅ 频道 ID 配置正确")
        print(f"✅ 频道名称: {chat.title}")
        print()
        print("🔍 下一步检查：")
        print("1. 确认 Bot A 服务正在运行：")
        print("   sudo systemctl status wushizhifu-bot")
        print()
        print("2. 查看 Bot A 日志，确认是否收到频道消息：")
        print("   sudo journalctl -u wushizhifu-bot -f")
        print()
        print("3. 在频道中上传一个新视频，观察日志输出")
        print()
        print("4. 如果日志中没有'检测到频道视频'，可能原因：")
        print("   - Bot 没有'查看消息'权限")
        print("   - Bot 没有'读取消息历史'权限")
        print("   - channel_video_handler 未正确注册")
        print()
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"验证过程出错: {e}", exc_info=True)
        print(f"\n❌ 验证失败: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        exit(1)
    
    asyncio.run(verify_channel_access())

