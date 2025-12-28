"""
检查视频处理 Handler 是否正确注册
"""
import sys
import importlib.util
from pathlib import Path

print("=" * 60)
print("🔍 检查视频 Handler 注册")
print("=" * 60)
print()

# 检查 bot.py 是否包含 channel_video_handler
bot_py_path = Path(__file__).parent / "bot.py"
if not bot_py_path.exists():
    print("❌ 找不到 bot.py")
    sys.exit(1)

print("1️⃣  检查 bot.py 中的导入...")
with open(bot_py_path, 'r', encoding='utf-8') as f:
    bot_content = f.read()
    
    if "channel_video_handler" in bot_content:
        print("   ✅ 找到 channel_video_handler 导入")
        if "from handlers.channel_video_handler import" in bot_content:
            print("   ✅ 导入语句正确")
        if "channel_video_router" in bot_content:
            print("   ✅ 找到 channel_video_router")
        if "dp.include_router(channel_video_router)" in bot_content:
            print("   ✅ Handler 已注册到 dispatcher")
        else:
            print("   ⚠️  Handler 可能未注册到 dispatcher")
            print("   请检查 bot.py 中是否有：")
            print("   dp.include_router(channel_video_router)")
    else:
        print("   ❌ 未找到 channel_video_handler")
        print("   需要添加：")
        print("   from handlers.channel_video_handler import router as channel_video_router")
        print("   dp.include_router(channel_video_router)")

print()

# 检查 channel_video_handler.py
handler_path = Path(__file__).parent / "handlers" / "channel_video_handler.py"
print("2️⃣  检查 channel_video_handler.py...")
if handler_path.exists():
    print("   ✅ 文件存在")
    with open(handler_path, 'r', encoding='utf-8') as f:
        handler_content = f.read()
        if "@router.channel_post" in handler_content:
            print("   ✅ 找到 channel_post 处理器")
        if "VIDEO_CHANNEL_ID" in handler_content:
            # 提取频道 ID
            import re
            match = re.search(r'VIDEO_CHANNEL_ID\s*=\s*(-?\d+)', handler_content)
            if match:
                channel_id = match.group(1)
                print(f"   ✅ 频道 ID: {channel_id}")
        if "handle_channel_video" in handler_content:
            print("   ✅ 找到 handle_channel_video 函数")
else:
    print("   ❌ 文件不存在")

print()
print("=" * 60)
print("📋 检查完成")
print("=" * 60)
print()
print("如果所有检查都通过，但 Bot 仍不响应频道视频：")
print("1. 确认 Bot A 服务已重启（在修改代码后）")
print("2. 查看日志确认是否有错误")
print("3. 确认 Bot 在频道中的权限设置")

