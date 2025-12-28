#!/bin/bash
# 创建 API 服务器的 systemd 服务

set -e

echo "=========================================="
echo "⚙️  创建 API 服务器 Systemd 服务"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 查找项目位置
echo -e "${YELLOW}🔍 查找项目位置...${NC}"

POSSIBLE_DIRS=(
    "/home/ubuntu/wushizhifu"
    "/opt/wushizhifu"
)

PROJECT_DIR=""
for dir in "${POSSIBLE_DIRS[@]}"; do
    if [ -f "$dir/api_server.py" ]; then
        PROJECT_DIR="$dir"
        echo -e "${GREEN}✅ 找到项目: ${PROJECT_DIR}${NC}"
        break
    fi
done

if [ -z "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ 错误: 找不到项目目录${NC}"
    exit 1
fi

# 获取当前用户
CURRENT_USER=$(whoami)

# 2. 创建 systemd 服务文件
echo ""
echo -e "${YELLOW}📝 创建 systemd 服务文件...${NC}"

SERVICE_NAME="wushipay-api"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=WuShiPay API Server
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${PROJECT_DIR}/venv/bin"
ExecStart=${PROJECT_DIR}/venv/bin/python ${PROJECT_DIR}/api_service.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ 服务文件已创建: ${SERVICE_FILE}${NC}"

# 3. 重新加载 systemd
echo ""
echo -e "${YELLOW}🔄 重新加载 systemd...${NC}"
sudo systemctl daemon-reload
echo -e "${GREEN}✅ systemd 已重新加载${NC}"

# 4. 启用并启动服务
echo ""
echo -e "${YELLOW}🚀 启用并启动服务...${NC}"
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl start "${SERVICE_NAME}.service"
echo -e "${GREEN}✅ 服务已启动${NC}"

# 5. 检查服务状态
echo ""
echo -e "${YELLOW}📊 检查服务状态...${NC}"
sleep 2
sudo systemctl status "${SERVICE_NAME}.service" --no-pager -l | head -20

echo ""
echo -e "${GREEN}=========================================="
echo "✅ API 服务配置完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}服务名称: ${SERVICE_NAME}.service${NC}"
echo -e "${BLUE}管理命令:${NC}"
echo "  查看状态: sudo systemctl status ${SERVICE_NAME}"
echo "  查看日志: sudo journalctl -u ${SERVICE_NAME} -f"
echo "  重启服务: sudo systemctl restart ${SERVICE_NAME}"
echo "  停止服务: sudo systemctl stop ${SERVICE_NAME}"

