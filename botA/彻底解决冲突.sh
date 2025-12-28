#!/bin/bash
# 彻底解决 TelegramConflictError - 确保只有一个 Bot 实例运行

echo "🔧 彻底解决 Bot 冲突问题..."
echo ""

# 进入 bot 目录
cd /home/ubuntu/wushizhifu/bot || exit 1

# 1. 显示当前运行的 Bot 进程
echo "📋 检查当前运行的 Bot 进程："
ps aux | grep -E "bot\.py|python.*bot" | grep -v grep
echo ""

# 2. 停止 systemd 服务
echo "🛑 停止 systemd 服务..."
sudo systemctl stop wushizhifu-bot 2>/dev/null
sleep 2

# 3. 强制终止所有 Python Bot 进程
echo "🔪 强制终止所有 Bot 相关进程..."
sudo pkill -9 -f "bot.py"
sudo pkill -9 -f "python.*bot"
# 更彻底：查找所有可能包含 bot 的 Python 进程
for pid in $(ps aux | grep -E "python.*wushizhifu.*bot" | grep -v grep | awk '{print $2}'); do
    echo "   终止进程 PID: $pid"
    sudo kill -9 $pid 2>/dev/null
done
sleep 3

# 4. 再次确认没有残留进程
echo "🔍 再次检查是否有残留进程..."
REMAINING=$(ps aux | grep -E "bot\.py|python.*bot" | grep -v grep | wc -l)
if [ "$REMAINING" -gt 0 ]; then
    echo "   ⚠️ 仍有 $REMAINING 个进程在运行："
    ps aux | grep -E "bot\.py|python.*bot" | grep -v grep
    echo "   继续强制终止..."
    sudo pkill -9 -f bot
    sleep 2
else
    echo "   ✅ 确认没有 Bot 进程在运行"
fi
echo ""

# 5. 重新加载 systemd 配置
echo "🔄 重新加载 systemd 配置..."
sudo systemctl daemon-reload
sleep 1

# 6. 拉取最新代码（如果需要）
echo "📥 检查代码更新..."
git pull origin main
echo ""

# 7. 清除 Python 缓存
echo "🧹 清除 Python 缓存..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -r {} + 2>/dev/null || true
echo "   ✅ 缓存已清除"
echo ""

# 8. 启动 systemd 服务
echo "🚀 启动 Bot 服务..."
sudo systemctl start wushizhifu-bot
sleep 4

# 9. 查看服务状态
echo "📊 检查服务状态："
sudo systemctl status wushizhifu-bot --no-pager -l | head -20
echo ""

# 10. 查看最新日志
echo "📋 查看最新日志（最后 30 行）："
sudo journalctl -u wushizhifu-bot -n 30 --no-pager
echo ""

# 11. 检查错误
echo "🔍 检查错误："
ERROR_COUNT=0

if sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -q "TypeError.*is_premium"; then
    echo "   ❌ 发现 is_premium TypeError 错误"
    ERROR_COUNT=$((ERROR_COUNT + 1))
else
    echo "   ✅ 没有 is_premium TypeError 错误"
fi

if sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -q "TelegramConflictError"; then
    echo "   ❌ 发现 TelegramConflictError（可能有其他实例）"
    ERROR_COUNT=$((ERROR_COUNT + 1))
else
    echo "   ✅ 没有 TelegramConflictError"
fi

# 12. 检查进程数量
PROCESS_COUNT=$(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | wc -l)
echo "   📊 当前 Bot 进程数量: $PROCESS_COUNT"
if [ "$PROCESS_COUNT" -eq 0 ]; then
    echo "   ⚠️ 警告：没有 Bot 进程在运行！"
    ERROR_COUNT=$((ERROR_COUNT + 1))
elif [ "$PROCESS_COUNT" -gt 1 ]; then
    echo "   ⚠️ 警告：有 $PROCESS_COUNT 个 Bot 进程在运行（应该只有 1 个）"
    ERROR_COUNT=$((ERROR_COUNT + 1))
else
    echo "   ✅ Bot 进程数量正常（1 个）"
fi

echo ""
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "✅ 所有检查通过！Bot 应该正常运行"
    echo ""
    echo "📱 请在 Telegram 中测试："
    echo "   1. 发送 /start 命令"
    echo "   2. 应该收到欢迎消息"
else
    echo "⚠️ 发现 $ERROR_COUNT 个问题，请检查上面的输出"
fi

