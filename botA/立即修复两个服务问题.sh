#!/bin/bash
# 立即修复两个服务同时运行的问题

echo "🔧 修复两个服务冲突问题..."
echo "=========================================="
echo ""

# 1. 停止所有服务
echo "1️⃣ 停止所有 Bot 服务..."
echo "----------------------------------------"
sudo systemctl stop wushipay-bot 2>/dev/null
sudo systemctl stop wushizhifu-bot 2>/dev/null
echo "✅ 所有服务已停止"
echo ""

# 2. 强制终止所有进程
echo "2️⃣ 强制终止所有 Bot 进程..."
echo "----------------------------------------"
sudo pkill -9 -f bot.py
sudo pkill -9 -f "python.*wushizhifu.*bot"
sleep 3

# 确认没有进程
REMAINING=$(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | wc -l)
if [ "$REMAINING" -gt 0 ]; then
    echo "⚠️ 仍有 $REMAINING 个进程，强制终止..."
    for pid in $(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | awk '{print $2}'); do
        sudo kill -9 $pid 2>/dev/null
    done
    sleep 2
fi
echo "✅ 所有进程已停止"
echo ""

# 3. 禁用旧服务 (wushipay-bot)
echo "3️⃣ 禁用旧服务 wushipay-bot..."
echo "----------------------------------------"
sudo systemctl disable wushipay-bot 2>/dev/null
sudo systemctl mask wushipay-bot 2>/dev/null  # 阻止被意外启动
echo "✅ wushipay-bot 已禁用并屏蔽"
echo ""

# 4. 删除旧的服务文件
echo "4️⃣ 删除旧的服务文件..."
echo "----------------------------------------"
if [ -f "/etc/systemd/system/wushipay-bot.service" ]; then
    echo "删除: /etc/systemd/system/wushipay-bot.service"
    sudo rm -f /etc/systemd/system/wushipay-bot.service
    echo "✅ 旧服务文件已删除"
else
    echo "✅ 旧服务文件不存在"
fi
echo ""

# 5. 更新 wushizhifu-bot 服务配置
echo "5️⃣ 更新 wushizhifu-bot 服务配置..."
echo "----------------------------------------"
sudo tee /etc/systemd/system/wushizhifu-bot.service > /dev/null << 'EOF'
[Unit]
Description=WuShiPay Telegram Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/wushizhifu/bot
Environment="PATH=/home/ubuntu/wushizhifu/bot/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ubuntu/wushizhifu/bot/venv/bin/python /home/ubuntu/wushizhifu/bot/bot.py
ExecReload=/bin/kill -HUP $MAINPID

# 重启策略：改为 on-failure
Restart=on-failure
RestartSec=10
StartLimitInterval=300
StartLimitBurst=5

# 日志
StandardOutput=journal
StandardError=journal
SyslogIdentifier=wushizhifu-bot

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
echo "✅ 服务配置已更新"
echo ""

# 6. 重新加载 systemd
echo "6️⃣ 重新加载 systemd..."
echo "----------------------------------------"
sudo systemctl daemon-reload
echo "✅ systemd 已重新加载"
echo ""

# 7. 启用服务
echo "7️⃣ 启用 wushizhifu-bot 服务..."
echo "----------------------------------------"
sudo systemctl enable wushizhifu-bot
echo "✅ 服务已启用"
echo ""

# 8. 确认没有进程
echo "8️⃣ 确认没有进程在运行..."
echo "----------------------------------------"
COUNT=$(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | wc -l)
if [ "$COUNT" -eq 0 ]; then
    echo "✅ 确认：没有 Bot 进程在运行"
else
    echo "⚠️ 仍有 $COUNT 个进程在运行："
    ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep
fi
echo ""

echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "现在可以启动服务："
echo "  sudo systemctl start wushizhifu-bot"
echo ""
echo "然后验证："
echo "  ps aux | grep bot.py | grep -v grep | wc -l"
echo "  应该输出: 1"

