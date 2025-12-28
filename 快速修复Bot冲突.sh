#!/bin/bash

echo "🔧 修复 Bot 冲突问题..."

# 1. 停止所有 Bot 进程
echo "🛑 停止所有 Bot 进程..."
sudo systemctl stop wushipay-bot
pkill -f "bot.py" 2>/dev/null || true
sleep 3

# 2. 强制终止残留进程
BOT_PIDS=$(ps aux | grep "bot.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$BOT_PIDS" ]; then
    echo "⚠️ 发现残留进程，正在终止..."
    echo $BOT_PIDS | xargs sudo kill -9 2>/dev/null || true
    sleep 2
fi

# 3. 再次确保所有进程已停止
sudo pkill -9 -f "bot.py" 2>/dev/null || true
sleep 2

# 4. 验证
REMAINING=$(ps aux | grep "bot.py" | grep -v grep | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo "✅ 所有进程已停止"
else
    echo "⚠️ 仍有 $REMAINING 个进程，继续清理..."
fi

# 5. 删除 Webhook（使用 Polling）
echo "🔗 删除 Webhook（如果存在）..."
cd /home/ubuntu/wushizhifu/bot
source venv/bin/activate 2>/dev/null || true
python3 << 'PYTHON_SCRIPT'
from aiogram import Bot
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('BOT_TOKEN')

async def delete_webhook():
    if not token:
        print("⚠️ 未找到 BOT_TOKEN")
        return
    bot = Bot(token=token)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook 已删除")
    except Exception as e:
        print(f"ℹ️ {e}")
    finally:
        await bot.session.close()

try:
    asyncio.run(delete_webhook())
except Exception as e:
    print(f"⚠️ {e}")
PYTHON_SCRIPT

# 6. 启动服务
echo "🚀 启动 Bot 服务..."
sudo systemctl start wushipay-bot
sleep 3

# 7. 检查状态
echo ""
echo "📊 Bot 服务状态:"
sudo systemctl status wushipay-bot --no-pager -l | head -15

# 8. 检查进程数量
PROCESS_COUNT=$(ps aux | grep "bot.py" | grep -v grep | wc -l)
echo ""
echo "🔍 当前运行的 Bot 进程数: $PROCESS_COUNT"
if [ "$PROCESS_COUNT" -eq 1 ]; then
    echo "✅ 正常：只有一个进程在运行"
elif [ "$PROCESS_COUNT" -eq 0 ]; then
    echo "⚠️ 警告：没有进程在运行"
else
    echo "❌ 错误：有 $PROCESS_COUNT 个进程在运行，需要清理"
fi

echo ""
echo "✅ 修复完成！"
echo "查看实时日志: sudo journalctl -u wushipay-bot -f"

