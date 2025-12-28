#!/bin/bash
# 重新设置 Bot 启动项（彻底清理并重新配置）

echo "🔧 重新设置 Bot 启动项..."
echo "=========================================="
echo ""

cd /home/ubuntu/wushizhifu/bot || exit 1

# 1. 停止所有 Bot 进程
echo "1️⃣ 停止所有 Bot 进程和服务..."
echo "----------------------------------------"
sudo systemctl stop wushizhifu-bot 2>/dev/null
sudo systemctl stop wushipay-bot 2>/dev/null  # 检查是否有旧的名称
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

# 2. 删除所有旧的服务文件
echo "2️⃣ 删除所有旧的服务文件..."
echo "----------------------------------------"
for service_file in /etc/systemd/system/*bot*.service /etc/systemd/system/*wushizhifu*.service; do
    if [ -f "$service_file" ]; then
        echo "删除: $service_file"
        sudo rm -f "$service_file"
    fi
done
echo "✅ 旧服务文件已删除"
echo ""

# 3. 禁用所有旧服务
echo "3️⃣ 禁用所有旧服务..."
echo "----------------------------------------"
sudo systemctl disable wushizhifu-bot 2>/dev/null
sudo systemctl disable wushipay-bot 2>/dev/null
echo "✅ 旧服务已禁用"
echo ""

# 4. 创建新的服务文件
echo "4️⃣ 创建新的服务文件..."
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

# 重启策略：只在失败时重启，限制重启频率
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

echo "✅ 新服务文件已创建"
echo ""

# 5. 重新加载 systemd
echo "5️⃣ 重新加载 systemd..."
echo "----------------------------------------"
sudo systemctl daemon-reload
echo "✅ systemd 已重新加载"
echo ""

# 6. 验证服务文件
echo "6️⃣ 验证服务文件..."
echo "----------------------------------------"
sudo systemctl cat wushizhifu-bot.service
echo ""

# 7. 启用服务（但不立即启动）
echo "7️⃣ 启用服务（开机自启）..."
echo "----------------------------------------"
sudo systemctl enable wushizhifu-bot
echo "✅ 服务已启用"
echo ""

# 8. 确认没有进程
echo "8️⃣ 最终确认没有进程在运行..."
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
echo "✅ 重新设置完成"
echo "=========================================="
echo ""
echo "下一步："
echo "  1. 检查配置是否正确"
echo "  2. 启动服务：sudo systemctl start wushizhifu-bot"
echo "  3. 检查进程数：ps aux | grep bot.py | grep -v grep | wc -l"
echo "  4. 应该只有 1 个进程"
echo ""

