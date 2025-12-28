#!/bin/bash
# 修复 Bot A systemd 服务路径

set -e

echo "=========================================="
echo "🔧 修复 Bot A 服务路径"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE_NAME="wushizhifu-bot"
CURRENT_USER=$(whoami)

echo -e "${BLUE}当前用户: ${CURRENT_USER}${NC}"
echo ""

# 1. 检查当前服务状态
echo -e "${YELLOW}1️⃣  检查当前服务状态...${NC}"
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${YELLOW}⚠️  服务正在运行，先停止服务${NC}"
    sudo systemctl stop ${SERVICE_NAME}
    echo -e "${GREEN}✅ 服务已停止${NC}"
fi

# 2. 检查项目目录
echo ""
echo -e "${YELLOW}2️⃣  检查项目目录...${NC}"
BOT_DIR="/home/ubuntu/wushizhifu/botA"
if [ -d "${BOT_DIR}" ] && [ -f "${BOT_DIR}/bot.py" ]; then
    echo -e "${GREEN}✅ 找到 Bot A 目录: ${BOT_DIR}${NC}"
else
    echo -e "${RED}❌ Bot A 目录不存在: ${BOT_DIR}${NC}"
    echo "请确认项目路径"
    exit 1
fi

# 3. 检查虚拟环境
echo ""
echo -e "${YELLOW}3️⃣  检查虚拟环境...${NC}"
VENV_PATH="${BOT_DIR}/venv"
if [ -f "${VENV_PATH}/bin/python" ]; then
    echo -e "${GREEN}✅ 找到虚拟环境: ${VENV_PATH}${NC}"
    ${VENV_PATH}/bin/python --version
else
    echo -e "${YELLOW}⚠️  虚拟环境不存在，将创建${NC}"
    cd "${BOT_DIR}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip --quiet
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    echo -e "${GREEN}✅ 虚拟环境已创建${NC}"
fi

# 4. 创建/更新服务文件
echo ""
echo -e "${YELLOW}4️⃣  更新 systemd 服务文件...${NC}"
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=WuShiPay Telegram Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=${CURRENT_USER}
Group=${CURRENT_USER}
WorkingDirectory=${BOT_DIR}
Environment="PATH=${VENV_PATH}/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${VENV_PATH}/bin/python ${BOT_DIR}/bot.py
ExecReload=/bin/kill -HUP \$MAINPID

# 重启策略
Restart=on-failure
RestartSec=10
StartLimitInterval=300
StartLimitBurst=5

# 日志
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ 服务文件已更新${NC}"

# 5. 重新加载 systemd
echo ""
echo -e "${YELLOW}5️⃣  重新加载 systemd...${NC}"
sudo systemctl daemon-reload
echo -e "${GREEN}✅ systemd 已重新加载${NC}"

# 6. 启用并启动服务
echo ""
echo -e "${YELLOW}6️⃣  启用并启动服务...${NC}"
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}
sleep 3

# 7. 检查服务状态
echo ""
echo -e "${YELLOW}7️⃣  检查服务状态...${NC}"
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✅ 服务已成功启动${NC}"
    systemctl status ${SERVICE_NAME} --no-pager -l | head -15
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo "查看错误日志："
    sudo journalctl -u ${SERVICE_NAME} -n 30 --no-pager
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 服务路径修复完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}服务信息：${NC}"
echo "  服务名称: ${SERVICE_NAME}.service"
echo "  项目目录: ${BOT_DIR}"
echo "  Python 路径: ${VENV_PATH}/bin/python"
echo ""
echo -e "${BLUE}管理命令：${NC}"
echo "  查看状态: sudo systemctl status ${SERVICE_NAME}"
echo "  查看日志: sudo journalctl -u ${SERVICE_NAME} -f"
echo "  重启服务: sudo systemctl restart ${SERVICE_NAME}"

