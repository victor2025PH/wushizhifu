#!/bin/bash
# 检查并启动 API 服务脚本

set -e

echo "=========================================="
echo "🔍 检查并启动 API 服务"
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

echo -e "${BLUE}=========================================="
echo "1. 检查 API 服务文件"
echo "==========================================${NC}"
if [ -f "$API_FILE" ]; then
    echo -e "${GREEN}✅ API 文件存在: $API_FILE${NC}"
else
    echo -e "${RED}❌ API 文件不存在: $API_FILE${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}=========================================="
echo "2. 检查端口 8000 占用情况"
echo "==========================================${NC}"
if lsof -i:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  端口 8000 已被占用${NC}"
    echo "占用进程："
    lsof -i:8000
    echo ""
    read -p "是否要停止占用端口的进程？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "停止占用端口的进程..."
        sudo kill -9 $(lsof -t -i:8000) 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✅ 进程已停止${NC}"
    fi
else
    echo -e "${GREEN}✅ 端口 8000 空闲${NC}"
fi
echo ""

echo -e "${BLUE}=========================================="
echo "3. 检查 Systemd 服务状态"
echo "==========================================${NC}"
if systemctl list-units --type=service | grep -q "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ Systemd 服务存在: $SERVICE_NAME${NC}"
    echo "服务状态："
    sudo systemctl status "$SERVICE_NAME" --no-pager -l | head -20 || true
    echo ""
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ 服务正在运行${NC}"
    else
        echo -e "${YELLOW}⚠️  服务未运行，正在启动...${NC}"
        sudo systemctl start "$SERVICE_NAME"
        sleep 2
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            echo -e "${GREEN}✅ 服务已启动${NC}"
        else
            echo -e "${RED}❌ 服务启动失败${NC}"
            echo "查看日志："
            sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Systemd 服务不存在，检查是否需要创建${NC}"
    
    # 检查 Python 环境
    if command -v python3 &> /dev/null; then
        PYTHON_PATH=$(which python3)
        echo "Python 路径: $PYTHON_PATH"
        
        # 检查是否有虚拟环境
        if [ -d "$PROJECT_ROOT/venv" ]; then
            PYTHON_PATH="$PROJECT_ROOT/venv/bin/python3"
            echo "使用虚拟环境: $PYTHON_PATH"
        fi
        
        echo ""
        echo "创建 Systemd 服务..."
        sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=WuShiPay API Server
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=$PROJECT_ROOT/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PYTHON_PATH -m uvicorn api_server:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable "$SERVICE_NAME"
        sudo systemctl start "$SERVICE_NAME"
        
        sleep 2
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            echo -e "${GREEN}✅ 服务已创建并启动${NC}"
        else
            echo -e "${RED}❌ 服务启动失败${NC}"
            sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
        fi
    else
        echo -e "${RED}❌ Python3 未安装${NC}"
        exit 1
    fi
fi
echo ""

echo -e "${BLUE}=========================================="
echo "4. 检查 API 服务是否响应"
echo "==========================================${NC}"
sleep 2
if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API 服务正在响应${NC}"
    echo "测试健康检查端点："
    curl -s http://127.0.0.1:8000/ | head -5 || echo "无响应"
else
    echo -e "${RED}❌ API 服务无响应${NC}"
    echo "检查服务日志："
    sudo journalctl -u "$SERVICE_NAME" -n 30 --no-pager
fi
echo ""

echo -e "${BLUE}=========================================="
echo "5. 检查 Nginx 配置"
echo "==========================================${NC}"
NGINX_CONFIG="/etc/nginx/sites-available/wushizhifu"
if [ -f "$NGINX_CONFIG" ]; then
    echo "检查 API 代理配置："
    if grep -q "location /api/" "$NGINX_CONFIG"; then
        echo -e "${GREEN}✅ Nginx API 代理配置存在${NC}"
        echo "代理配置："
        grep -A 5 "location /api/" "$NGINX_CONFIG" | head -10
    else
        echo -e "${YELLOW}⚠️  Nginx API 代理配置不存在${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Nginx 配置文件不存在${NC}"
fi
echo ""

echo -e "${GREEN}=========================================="
echo "✅ 检查完成"
echo "==========================================${NC}"
echo ""
echo "如果服务未运行，请检查："
echo "  1. sudo journalctl -u $SERVICE_NAME -n 50 --no-pager"
echo "  2. sudo systemctl status $SERVICE_NAME"
echo "  3. 检查 Python 依赖是否安装: pip install -r requirements.txt"
