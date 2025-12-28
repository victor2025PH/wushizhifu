#!/bin/bash
# 检查并清理多个 Bot 服务，只保留 wushizhifu-bot

echo "========================================="
echo "检查 Bot 服务状态"
echo "========================================="

# 1. 检查所有 Bot 相关的服务
echo ""
echo "1. 检查所有 Bot 相关的 systemd 服务："
echo "----------------------------------------"
systemctl list-units --all --type=service | grep -E "(bot|Bot)" || echo "未找到 Bot 服务"

# 2. 检查 wushipay-bot 服务
echo ""
echo "2. 检查 wushipay-bot 服务："
echo "----------------------------------------"
if systemctl list-units --all | grep -q "wushipay-bot.service"; then
    echo "⚠️  发现 wushipay-bot.service"
    systemctl status wushipay-bot.service --no-pager -l | head -15
else
    echo "✅ wushipay-bot.service 不存在"
fi

# 3. 检查 wushizhifu-bot 服务
echo ""
echo "3. 检查 wushizhifu-bot 服务："
echo "----------------------------------------"
if systemctl list-units --all | grep -q "wushizhifu-bot.service"; then
    echo "✅ 发现 wushizhifu-bot.service"
    systemctl status wushizhifu-bot.service --no-pager -l | head -15
else
    echo "❌ wushizhifu-bot.service 不存在"
fi

# 4. 检查运行的 Bot 进程
echo ""
echo "4. 检查运行的 Bot 进程："
echo "----------------------------------------"
ps aux | grep -E "bot.py|python.*bot" | grep -v grep || echo "未找到 Bot 进程"

# 5. 检查服务文件
echo ""
echo "5. 检查服务文件："
echo "----------------------------------------"
echo "wushipay-bot.service:"
if [ -f /etc/systemd/system/wushipay-bot.service ]; then
    echo "  ✅ 存在: /etc/systemd/system/wushipay-bot.service"
    ls -lh /etc/systemd/system/wushipay-bot.service
else
    echo "  ❌ 不存在"
fi

echo ""
echo "wushizhifu-bot.service:"
if [ -f /etc/systemd/system/wushizhifu-bot.service ]; then
    echo "  ✅ 存在: /etc/systemd/system/wushizhifu-bot.service"
    ls -lh /etc/systemd/system/wushizhifu-bot.service
else
    echo "  ❌ 不存在"
fi

echo ""
echo "========================================="
echo "开始清理旧服务"
echo "========================================="

# 6. 停止并禁用 wushipay-bot
if systemctl is-active --quiet wushipay-bot.service 2>/dev/null; then
    echo ""
    echo "6. 停止 wushipay-bot 服务..."
    sudo systemctl stop wushipay-bot.service
    echo "✅ 已停止"
fi

if systemctl is-enabled --quiet wushipay-bot.service 2>/dev/null; then
    echo ""
    echo "7. 禁用 wushipay-bot 服务（开机不自启）..."
    sudo systemctl disable wushipay-bot.service
    echo "✅ 已禁用"
fi

# 7. 强制停止所有 Bot 相关进程
echo ""
echo "8. 强制停止所有 bot.py 进程..."
pkill -9 -f "bot.py" 2>/dev/null && echo "✅ 已停止所有 bot.py 进程" || echo "⚠️  没有运行的 bot.py 进程"

# 8. 确保 wushizhifu-bot 正在运行
echo ""
echo "9. 启动正确的 Bot 服务 (wushizhifu-bot)..."
sudo systemctl enable wushizhifu-bot.service
sudo systemctl restart wushizhifu-bot.service
sleep 3

# 9. 最终状态检查
echo ""
echo "========================================="
echo "最终状态检查"
echo "========================================="

echo ""
echo "10. 检查 wushizhifu-bot 状态："
sudo systemctl status wushizhifu-bot.service --no-pager -l | head -20

echo ""
echo "11. 检查运行的 Bot 进程："
ps aux | grep -E "bot.py|python.*bot" | grep -v grep || echo "未找到 Bot 进程"

echo ""
echo "12. 查看最新日志："
sudo journalctl -u wushizhifu-bot.service -n 30 --no-pager | tail -20

echo ""
echo "========================================="
echo "清理完成！"
echo "========================================="
echo ""
echo "现在只有 wushizhifu-bot 服务在运行。"
echo "请在 Telegram 中测试 Bot 功能。"

