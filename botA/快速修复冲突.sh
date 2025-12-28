#!/bin/bash
# 快速修复 Bot 多个实例冲突问题

set -e

echo "🔧 修复 Bot 多个实例冲突问题..."
echo ""

# 1. 停止 systemd 服务
echo "1️⃣ 停止 systemd 服务..."
sudo systemctl stop wushizhifu-bot || true
sleep 1

# 2. 查找并停止所有 bot.py 进程
echo "2️⃣ 查找所有 bot.py 进程..."
BOT_PIDS=$(pgrep -f "bot.py" || true)

if [ -n "$BOT_PIDS" ]; then
    echo "   发现进程: $BOT_PIDS"
    echo "   正在停止..."
    sudo pkill -f "bot.py" || true
    sleep 2
else
    echo "   ✅ 没有发现运行中的 bot.py 进程"
fi

# 3. 再次确认
echo "3️⃣ 确认所有进程已停止..."
REMAINING=$(pgrep -f "bot.py" || true)
if [ -n "$REMAINING" ]; then
    echo "   ⚠️ 仍有进程运行，强制停止..."
    sudo killall -9 python3 2>/dev/null || true
    sleep 1
else
    echo "   ✅ 确认所有进程已停止"
fi

# 4. 检查 screen/tmux 会话（可选）
echo "4️⃣ 检查是否有 screen/tmux 会话..."
SCREEN_SESSIONS=$(screen -ls 2>/dev/null | grep -i bot || true)
if [ -n "$SCREEN_SESSIONS" ]; then
    echo "   ⚠️ 发现 screen 会话，请手动处理"
    screen -ls
fi

# 5. 进入 Bot 目录
cd /home/ubuntu/wushizhifu/bot || {
    echo "❌ 无法进入 Bot 目录"
    exit 1
}

# 6. 检查服务配置
echo "5️⃣ 检查 systemd 服务配置..."
if [ ! -f "/etc/systemd/system/wushizhifu-bot.service" ]; then
    echo "   ⚠️ 服务文件不存在，正在创建..."
    
    sudo tee /etc/systemd/system/wushizhifu-bot.service > /dev/null << EOF
[Unit]
Description=WuShiPay Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/wushizhifu/bot
Environment="PATH=/home/ubuntu/wushizhifu/bot/venv/bin"
ExecStart=/home/ubuntu/wushizhifu/bot/venv/bin/python /home/ubuntu/wushizhifu/bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable wushizhifu-bot
    echo "   ✅ 服务文件已创建"
else
    echo "   ✅ 服务文件存在"
fi

# 7. 重新启动服务
echo "6️⃣ 重新启动 Bot 服务..."
sudo systemctl start wushizhifu-bot
sleep 3

# 8. 检查服务状态
echo "7️⃣ 检查服务状态..."
sudo systemctl status wushizhifu-bot --no-pager -l | head -20

# 9. 查看最新日志
echo ""
echo "8️⃣ 查看最新日志..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo journalctl -u wushizhifu-bot -n 30 --no-pager

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 10. 验证是否成功
echo "9️⃣ 验证启动状态..."
if sudo systemctl is-active --quiet wushizhifu-bot; then
    echo "   ✅ 服务正在运行"
    
    # 检查日志中是否有错误
    if sudo journalctl -u wushizhifu-bot -n 50 --no-pager | grep -q "TelegramConflictError"; then
        echo "   ⚠️ 仍然有冲突错误，请检查是否有其他实例"
    else
        echo "   ✅ 没有发现冲突错误"
    fi
    
    # 检查是否有成功消息
    if sudo journalctl -u wushizhifu-bot -n 50 --no-pager | grep -q "Bot commands set successfully"; then
        echo "   ✅ Bot 初始化成功"
    else
        echo "   ⚠️ Bot 初始化消息未找到（可能仍在启动中）"
    fi
else
    echo "   ❌ 服务未运行"
    echo "   查看详细日志: sudo journalctl -u wushizhifu-bot -n 100 --no-pager"
fi

echo ""
echo "✨ 修复完成！"
echo ""
echo "常用命令："
echo "  查看状态: sudo systemctl status wushizhifu-bot"
echo "  查看日志: sudo journalctl -u wushizhifu-bot -f"
echo "  重启服务: sudo systemctl restart wushizhifu-bot"

