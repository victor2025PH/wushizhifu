#!/bin/bash
# 诊断并修复 API 服务启动问题

set -e

echo "=========================================="
echo "🔍 诊断并修复 API 服务"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/home/ubuntu/wushizhifu"
SERVICE_NAME="wushipay-api"

echo -e "${BLUE}项目目录: ${PROJECT_DIR}${NC}"
echo ""

# 1. 检查虚拟环境
echo -e "${YELLOW}🔍 步骤 1: 检查虚拟环境...${NC}"
if [ -f "${PROJECT_DIR}/venv/bin/python" ]; then
    echo -e "${GREEN}✅ Python 路径存在: ${PROJECT_DIR}/venv/bin/python${NC}"
    ${PROJECT_DIR}/venv/bin/python --version
else
    echo -e "${RED}❌ 虚拟环境不存在${NC}"
    echo "创建虚拟环境..."
    cd "${PROJECT_DIR}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip --quiet
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    echo -e "${GREEN}✅ 虚拟环境已创建${NC}"
fi

# 2. 检查 api_service.py
echo ""
echo -e "${YELLOW}🔍 步骤 2: 检查 api_service.py...${NC}"
if [ -f "${PROJECT_DIR}/api_service.py" ]; then
    echo -e "${GREEN}✅ api_service.py 存在${NC}"
else
    echo -e "${RED}❌ api_service.py 不存在${NC}"
    exit 1
fi

# 3. 测试直接运行
echo ""
echo -e "${YELLOW}🔍 步骤 3: 测试直接运行...${NC}"
cd "${PROJECT_DIR}"
source venv/bin/activate

# 检查依赖
echo "检查关键依赖..."
python3 -c "import fastapi; import uvicorn; import httpx; print('✅ 所有依赖已安装')" || {
    echo -e "${YELLOW}⚠️  缺少依赖，正在安装...${NC}"
    pip install -r requirements.txt
}

# 4. 检查并修复服务文件
echo ""
echo -e "${YELLOW}🔧 步骤 4: 修复服务文件...${NC}"

# 获取实际的 Python 路径
PYTHON_PATH="${PROJECT_DIR}/venv/bin/python"
if [ ! -f "$PYTHON_PATH" ]; then
    PYTHON_PATH=$(which python3)
    echo -e "${YELLOW}⚠️  使用系统 Python: ${PYTHON_PATH}${NC}"
fi

# 更新服务文件
CURRENT_USER=$(whoami)
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=WuShiPay API Server
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${PROJECT_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${PYTHON_PATH} ${PROJECT_DIR}/api_service.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ 服务文件已更新${NC}"

# 5. 重新加载并重启服务
echo ""
echo -e "${YELLOW}🔄 步骤 5: 重新加载并重启服务...${NC}"
sudo systemctl daemon-reload
sudo systemctl stop ${SERVICE_NAME} 2>/dev/null || true
sleep 1
sudo systemctl start ${SERVICE_NAME}
sleep 3

# 6. 检查服务状态
echo ""
echo -e "${YELLOW}📊 步骤 6: 检查服务状态...${NC}"
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✅ 服务正在运行${NC}"
else
    echo -e "${RED}❌ 服务未运行${NC}"
    echo "查看日志:"
    sudo journalctl -u ${SERVICE_NAME} -n 20 --no-pager
    exit 1
fi

# 7. 验证 API
echo ""
echo -e "${YELLOW}✅ 步骤 7: 验证 API 端点...${NC}"
sleep 2

echo "测试根路径..."
if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo -e "${GREEN}✅ API 根路径正常${NC}"
    curl -s http://127.0.0.1:8000/ | head -c 100
    echo ""
else
    echo -e "${YELLOW}⚠️  API 根路径无响应（可能还在启动）${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ API 服务诊断和修复完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}服务信息:${NC}"
echo "  服务名称: ${SERVICE_NAME}.service"
echo "  项目目录: ${PROJECT_DIR}"
echo "  Python 路径: ${PYTHON_PATH}"
echo ""
echo -e "${BLUE}管理命令:${NC}"
echo "  查看状态: sudo systemctl status ${SERVICE_NAME}"
echo "  查看日志: sudo journalctl -u ${SERVICE_NAME} -f"
echo "  重启服务: sudo systemctl restart ${SERVICE_NAME}"
echo ""
echo -e "${BLUE}测试命令:${NC}"
echo "  测试 API: curl http://127.0.0.1:8000/"
echo "  测试视频端点: curl http://127.0.0.1:8000/api/videos/alipay"

