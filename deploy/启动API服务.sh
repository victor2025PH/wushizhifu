#!/bin/bash
# 启动 API 服务脚本

set -e

echo "=========================================="
echo "🚀 启动 WuShiPay API 服务"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$HOME/wushizhifu"
API_FILE="$PROJECT_ROOT/api_server.py"
SERVICE_NAME="wushipay-api"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo -e "${BLUE}步骤 1: 检查 API 文件${NC}"
if [ ! -f "$API_FILE" ]; then
    echo -e "${RED}❌ API 文件不存在: $API_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✅ API 文件存在${NC}"
echo ""

echo -e "${BLUE}步骤 2: 检查 Python 环境${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi
PYTHON_PATH=$(which python3)
echo -e "${GREEN}✅ Python3 路径: $PYTHON_PATH${NC}"

# 检查是否有虚拟环境
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${GREEN}✅ 找到虚拟环境${NC}"
    VENV_PYTHON="$PROJECT_ROOT/venv/bin/python3"
    if [ -f "$VENV_PYTHON" ]; then
        PYTHON_PATH="$VENV_PYTHON"
        echo "使用虚拟环境: $PYTHON_PATH"
    fi
else
    echo -e "${YELLOW}⚠️  未找到虚拟环境，使用系统 Python${NC}"
fi
echo ""

echo -e "${BLUE}步骤 3: 检查 Python 依赖${NC}"
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "检查依赖..."
    if $PYTHON_PATH -c "import fastapi, uvicorn" 2>/dev/null; then
        echo -e "${GREEN}✅ 依赖已安装${NC}"
    else
        echo -e "${YELLOW}⚠️  依赖未安装，正在安装...${NC}"
        if [ -d "$PROJECT_ROOT/venv" ]; then
            $PROJECT_ROOT/venv/bin/pip install -r "$PROJECT_ROOT/requirements.txt" || \
            $PYTHON_PATH -m pip install fastapi uvicorn python-multipart httpx requests
        else
            $PYTHON_PATH -m pip install --user fastapi uvicorn python-multipart httpx requests || \
            sudo $PYTHON_PATH -m pip install fastapi uvicorn python-multipart httpx requests
        fi
    fi
else
    echo -e "${YELLOW}⚠️  requirements.txt 不存在，安装基础依赖...${NC}"
    if [ -d "$PROJECT_ROOT/venv" ]; then
        $PROJECT_ROOT/venv/bin/pip install fastapi uvicorn python-multipart httpx requests
    else
        $PYTHON_PATH -m pip install --user fastapi uvicorn python-multipart httpx requests || \
        sudo $PYTHON_PATH -m pip install fastapi uvicorn python-multipart httpx requests
    fi
fi
echo ""

echo -e "${BLUE}步骤 4: 创建 Systemd 服务${NC}"
if [ -f "$SERVICE_FILE" ]; then
    echo -e "${GREEN}✅ Systemd 服务文件已存在${NC}"
else
    echo "创建 Systemd 服务文件..."
    
    # 确定 uvicorn 路径
    if [ -f "$PROJECT_ROOT/venv/bin/uvicorn" ]; then
        UVICORN_CMD="$PROJECT_ROOT/venv/bin/uvicorn"
    else
        UVICORN_CMD="$PYTHON_PATH -m uvicorn"
    fi
    
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=WuShiPay API Service (FastAPI)
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=$PROJECT_ROOT/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONPATH=$PROJECT_ROOT"
EnvironmentFile=-$PROJECT_ROOT/.env

ExecStart=$UVICORN_CMD api_server:app --host 127.0.0.1 --port 8000

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=wushipay-api

NoNewPrivileges=true
PrivateTmp=true
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
    
    echo -e "${GREEN}✅ Systemd 服务文件已创建${NC}"
    sudo systemctl daemon-reload
    echo -e "${GREEN}✅ Systemd 配置已重载${NC}"
fi
echo ""

echo -e "${BLUE}步骤 5: 停止占用端口的进程${NC}"
if lsof -i:8000 > /dev/null 2>&1; then
    echo "发现端口 8000 被占用，正在停止..."
    sudo kill -9 $(lsof -t -i:8000) 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}✅ 端口已释放${NC}"
else
    echo -e "${GREEN}✅ 端口 8000 空闲${NC}"
fi
echo ""

echo -e "${BLUE}步骤 6: 启动服务${NC}"
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

sleep 3

if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ 服务已启动${NC}"
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo "查看日志："
    sudo journalctl -u "$SERVICE_NAME" -n 30 --no-pager
    exit 1
fi
echo ""

echo -e "${BLUE}步骤 7: 验证服务${NC}"
sleep 2
if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API 服务正在响应${NC}"
    echo "测试端点："
    curl -s http://127.0.0.1:8000/ | head -3
else
    echo -e "${RED}❌ API 服务无响应${NC}"
    echo "查看日志："
    sudo journalctl -u "$SERVICE_NAME" -n 30 --no-pager
    exit 1
fi
echo ""

echo -e "${GREEN}=========================================="
echo "✅ API 服务启动完成！"
echo "==========================================${NC}"
echo ""
echo "服务信息："
echo "  服务名称: $SERVICE_NAME"
echo "  服务状态: $(sudo systemctl is-active $SERVICE_NAME)"
echo "  访问地址: http://127.0.0.1:8000"
echo ""
echo "常用命令："
echo "  查看状态: sudo systemctl status $SERVICE_NAME"
echo "  查看日志: sudo journalctl -u $SERVICE_NAME -f"
echo "  重启服务: sudo systemctl restart $SERVICE_NAME"
echo "  停止服务: sudo systemctl stop $SERVICE_NAME"
