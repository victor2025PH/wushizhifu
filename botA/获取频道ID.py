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
    """获取频道更新以获取频道 ID（不轮询，避免冲突）"""
    bot = Bot(token=Config.BOT_TOKEN)
    
    print("=" * 50)
    print("🔍 获取频道 ID 工具")
    print("=" * 50)
    print("\n📋 注意：")
    print("由于 Bot A 服务正在运行，无法直接轮询更新")
    print("将使用其他方法获取频道信息\n")
    print("=" * 50)
    
    try:
        # 不轮询，直接测试已知频道 ID
        # 或者让用户手动提供频道用户名
        print("\n方法 1: 测试当前配置的频道 ID")
        print("-" * 50)
        
        # 方法 2: 通过频道用户名获取（如果知道用户名）
        print("\n方法 2: 通过频道用户名获取（可选）")
        print("-" * 50)
        print("如果知道频道用户名（如 @wszfsc），可以运行：")
        print("  python3 -c \"")
        print("import asyncio")
        print("from aiogram import Bot")
        print("from config import Config")
        print("async def get():")
        print("    bot = Bot(token=Config.BOT_TOKEN)")
        print("    chat = await bot.get_chat('@wszfsc')")
        print("    print(f'频道ID: {chat.id}')")
        print("    print(f'频道名称: {chat.title}')")
        print("    await bot.session.close()")
        print("asyncio.run(get())\"")
    
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

