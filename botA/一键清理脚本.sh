#!/bin/bash
# 一键清理多个 Bot 服务，只保留 wushizhifu-bot

set -e

echo "========================================="
echo "开始清理多个 Bot 服务"
echo "========================================="

# 1. 停止旧服务
echo ""
echo "1. 停止 wushipay-bot 服务..."
sudo systemctl stop wushipay-bot.service 2>/dev/null && echo "✅ 已停止 wushipay-bot" || echo "ℹ️  wushipay-bot 未运行"

# 2. 禁用旧服务
echo ""
echo "2. 禁用 wushipay-bot 服务..."
sudo systemctl disable wushipay-bot.service 2>/dev/null && echo "✅ 已禁用 wushipay-bot" || echo "ℹ️  wushipay-bot 未配置"

# 3. 强制停止所有 Bot 进程
echo ""
echo "3. 强制停止所有 bot.py 进程..."
sudo pkill -9 -f "bot.py" 2>/dev/null && sleep 1 && echo "✅ 已停止所有 bot.py 进程" || echo "ℹ️  没有运行的 bot.py 进程"

# 4. 重新加载 systemd
echo ""
echo "4. 重新加载 systemd..."
sudo systemctl daemon-reload
echo "✅ systemd 已重新加载"

# 5. 启用并启动正确服务
echo ""
echo "5. 启用并启动 wushizhifu-bot 服务..."
sudo systemctl enable wushizhifu-bot.service
sudo systemctl restart wushizhifu-bot.service
sleep 3
echo "✅ 服务已启动"

# 6. 检查状态
echo ""
echo "========================================="
echo "状态检查"
echo "========================================="

echo ""
echo "6. wushizhifu-bot 服务状态："
sudo systemctl status wushizhifu-bot.service --no-pager | head -15

echo ""
echo "7. 运行的 Bot 进程："
BOT_PROCS=$(ps aux | grep "bot.py" | grep -v grep | wc -l)
if [ "$BOT_PROCS" -eq "0" ]; then
    echo "❌ 警告：没有 Bot 进程在运行！"
elif [ "$BOT_PROCS" -eq "1" ]; then
    echo "✅ 只有 1 个 Bot 进程在运行（正确）"
    ps aux | grep "bot.py" | grep -v grep
else
    echo "⚠️  警告：有 $BOT_PROCS 个 Bot 进程在运行！可能有冲突"
    ps aux | grep "bot.py" | grep -v grep
fi

echo ""
echo "8. 最新日志（关键信息）："
sudo journalctl -u wushizhifu-bot.service -n 30 --no-pager | grep -E "(Menu button|Bot description|Initialized|ERROR|Error|Conflict)" | tail -10

echo ""
echo "========================================="
echo "清理完成！"
echo "========================================="
echo ""
echo "✅ 现在只有 wushizhifu-bot 服务在运行"
echo ""
echo "📱 请在 Telegram 中验证："
echo "   1. 发送 /start 命令"
echo "   2. 检查按钮功能是否正常"
echo "   3. 检查信息面板的「打开应用」按钮"

