#!/bin/bash
# 创建并启动 WuShiPay Bot systemd 服务

set -e

echo "🔧 创建 Bot systemd 服务..."

# 进入 Bot 目录
cd /home/ubuntu/wushizhifu/bot

# 获取当前工作目录的绝对路径
BOT_DIR=$(pwd)
VENV_PATH="$BOT_DIR/venv"
BOT_USER=$(whoami)

echo "📁 Bot 目录: $BOT_DIR"
echo "👤 运行用户: $BOT_USER"

# 创建 systemd 服务文件
sudo tee /etc/systemd/system/wushizhifu-bot.service > /dev/null << EOF
[Unit]
Description=WuShiPay Telegram Bot
After=network.target

[Service]
Type=simple
User=$BOT_USER
WorkingDirectory=$BOT_DIR
Environment="PATH=$VENV_PATH/bin"
ExecStart=$VENV_PATH/bin/python $BOT_DIR/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ 服务文件已创建"

# 重新加载 systemd
echo "🔄 重新加载 systemd..."
sudo systemctl daemon-reload

# 启用服务（开机自启）
echo "⚙️ 启用服务..."
sudo systemctl enable wushizhifu-bot.service

# 启动服务
echo "🚀 启动服务..."
sudo systemctl start wushizhifu-bot.service

# 等待几秒
sleep 3

# 检查服务状态
echo "📊 服务状态:"
sudo systemctl status wushizhifu-bot.service --no-pager -l

echo ""
echo "✨ 服务已创建并启动！"
echo ""
echo "常用命令："
echo "  查看状态: sudo systemctl status wushizhifu-bot"
echo "  查看日志: sudo journalctl -u wushizhifu-bot -f"
echo "  重启服务: sudo systemctl restart wushizhifu-bot"
echo "  停止服务: sudo systemctl stop wushizhifu-bot"

