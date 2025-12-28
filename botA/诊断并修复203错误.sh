#!/bin/bash
# 诊断并修复 status=203/EXEC 错误

set -e

echo "=========================================="
echo "🔍 诊断并修复 203/EXEC 错误"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

BOT_DIR="/home/ubuntu/wushizhifu/botA"
VENV_PATH="${BOT_DIR}/venv"
PYTHON_PATH="${VENV_PATH}/bin/python"
BOT_PY="${BOT_DIR}/bot.py"
SERVICE_NAME="wushizhifu-bot"
CURRENT_USER=$(whoami)

echo -e "${BLUE}检查路径：${NC}"
echo "  项目目录: ${BOT_DIR}"
echo "  虚拟环境: ${VENV_PATH}"
echo "  Python 路径: ${PYTHON_PATH}"
echo "  Bot 脚本: ${BOT_PY}"
echo ""

# 1. 停止服务
echo -e "${YELLOW}1️⃣  停止服务...${NC}"
sudo systemctl stop ${SERVICE_NAME} 2>/dev/null || true
echo -e "${GREEN}✅ 服务已停止${NC}"

# 2. 检查项目目录
echo ""
echo -e "${YELLOW}2️⃣  检查项目目录...${NC}"
if [ ! -d "${BOT_DIR}" ]; then
    echo -e "${RED}❌ 项目目录不存在: ${BOT_DIR}${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 项目目录存在${NC}"

# 3. 检查 bot.py
echo ""
echo -e "${YELLOW}3️⃣  检查 bot.py...${NC}"
if [ ! -f "${BOT_PY}" ]; then
    echo -e "${RED}❌ bot.py 不存在: ${BOT_PY}${NC}"
    exit 1
fi
echo -e "${GREEN}✅ bot.py 存在${NC}"
ls -lh "${BOT_PY}"

# 4. 检查虚拟环境
echo ""
echo -e "${YELLOW}4️⃣  检查虚拟环境...${NC}"
if [ ! -d "${VENV_PATH}" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    cd "${BOT_DIR}"
    python3 -m venv venv
    echo -e "${GREEN}✅ 虚拟环境已创建${NC}"
fi

# 5. 检查 Python 可执行文件
echo ""
echo -e "${YELLOW}5️⃣  检查 Python 可执行文件...${NC}"
if [ ! -f "${PYTHON_PATH}" ]; then
    echo -e "${RED}❌ Python 可执行文件不存在: ${PYTHON_PATH}${NC}"
    echo "重新创建虚拟环境..."
    cd "${BOT_DIR}"
    rm -rf venv
    python3 -m venv venv
    echo -e "${GREEN}✅ 虚拟环境已重新创建${NC}"
fi

# 测试 Python 是否可执行
if [ ! -x "${PYTHON_PATH}" ]; then
    echo -e "${YELLOW}⚠️  Python 文件没有执行权限，正在修复...${NC}"
    chmod +x "${PYTHON_PATH}"
fi

echo -e "${GREEN}✅ Python 可执行文件存在${NC}"
echo "测试执行："
"${PYTHON_PATH}" --version

# 6. 检查并安装依赖
echo ""
echo -e "${YELLOW}6️⃣  检查依赖...${NC}"
cd "${BOT_DIR}"
if [ -f "requirements.txt" ]; then
    source venv/bin/activate
    echo "检查关键依赖..."
    python3 -c "import aiogram; import fastapi; print('✅ 关键依赖已安装')" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  缺少依赖，正在安装...${NC}"
        pip install --upgrade pip --quiet
        pip install -r requirements.txt
    }
    echo -e "${GREEN}✅ 依赖检查完成${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt 不存在${NC}"
fi

# 7. 测试直接运行 bot.py
echo ""
echo -e "${YELLOW}7️⃣  测试直接运行 bot.py...${NC}"
cd "${BOT_DIR}"
timeout 3 "${PYTHON_PATH}" "${BOT_PY}" 2>&1 | head -20 || {
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 124 ]; then
        echo -e "${GREEN}✅ Bot 脚本可以启动（3秒后超时，这是正常的）${NC}"
    else
        echo -e "${YELLOW}⚠️  Bot 启动测试退出码: ${EXIT_CODE}${NC}"
        echo "（这可能是正常的，因为需要配置）"
    fi
}

# 8. 检查文件权限
echo ""
echo -e "${YELLOW}8️⃣  检查文件权限...${NC}"
chmod +x "${BOT_PY}" 2>/dev/null || true
chmod +x "${VENV_PATH}/bin/"* 2>/dev/null || true
echo -e "${GREEN}✅ 权限已设置${NC}"

# 9. 验证路径存在性（再次确认）
echo ""
echo -e "${YELLOW}9️⃣  验证所有路径...${NC}"
ALL_OK=true
for path in "${BOT_DIR}" "${VENV_PATH}" "${PYTHON_PATH}" "${BOT_PY}"; do
    if [ -e "${path}" ]; then
        echo -e "${GREEN}✅ ${path}${NC}"
    else
        echo -e "${RED}❌ ${path}${NC}"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = false ]; then
    echo -e "${RED}❌ 某些路径不存在，无法继续${NC}"
    exit 1
fi

# 10. 更新服务文件（使用绝对路径，确保正确）
echo ""
echo -e "${YELLOW}🔟 更新服务文件...${NC}"
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
Environment="PYTHONUNBUFFERED=1"
ExecStart=${PYTHON_PATH} ${BOT_PY}
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

# 11. 重新加载并启动
echo ""
echo -e "${YELLOW}1️⃣1️⃣  重新加载并启动服务...${NC}"
sudo systemctl daemon-reload
sleep 1
sudo systemctl start ${SERVICE_NAME}
sleep 3

# 12. 检查服务状态
echo ""
echo -e "${YELLOW}1️⃣2️⃣  检查服务状态...${NC}"
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✅ 服务已成功启动${NC}"
    systemctl status ${SERVICE_NAME} --no-pager -l | head -20
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo ""
    echo "查看详细错误："
    sudo journalctl -u ${SERVICE_NAME} -n 20 --no-pager
    echo ""
    echo "检查路径是否正确："
    echo "  cat /etc/systemd/system/${SERVICE_NAME}.service | grep ExecStart"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 诊断和修复完成！"
echo "==========================================${NC}"

