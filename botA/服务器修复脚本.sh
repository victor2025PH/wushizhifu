#!/bin/bash
# 修复 is_premium 错误并解决冲突

echo "🔧 开始修复 Bot 错误..."

# 进入 bot 目录
cd /home/ubuntu/wushizhifu/bot || exit 1

# 1. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 2. 清除 Python 缓存
echo "🧹 清除 Python 缓存..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -r {} + 2>/dev/null || true

# 3. 停止所有 Bot 进程
echo "🛑 停止所有 Bot 进程..."
sudo systemctl stop wushizhifu-bot 2>/dev/null
sudo pkill -9 -f bot.py 2>/dev/null
sleep 2

# 4. 确认没有残留进程
if pgrep -f bot.py > /dev/null; then
    echo "⚠️ 仍有 Bot 进程在运行，强制终止..."
    sudo pkill -9 -f bot.py
    sleep 2
fi

# 5. 重启服务
echo "🚀 重启 Bot 服务..."
sudo systemctl start wushizhifu-bot
sleep 3

# 6. 查看日志
echo "📋 查看最新日志..."
sudo journalctl -u wushizhifu-bot -n 30 --no-pager

# 7. 检查错误
echo ""
echo "🔍 检查错误..."
if sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -q "TypeError.*is_premium"; then
    echo "   ❌ 仍有 is_premium 错误"
else
    echo "   ✅ 没有发现 is_premium 错误"
fi

if sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -q "TelegramConflictError"; then
    echo "   ❌ 仍有冲突错误"
else
    echo "   ✅ 没有发现冲突错误"
fi

echo ""
echo "✅ 修复完成！请在 Telegram 中测试 /start 命令"

