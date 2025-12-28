#!/bin/bash
# 更新 API 服务器：安装依赖、初始化数据库、重启服务

set -e

echo "=========================================="
echo "🔄 更新 API 服务器"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 查找项目位置
echo -e "${YELLOW}🔍 步骤 1: 查找项目位置...${NC}"

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
    echo -e "${RED}❌ 错误: 找不到项目目录（包含 api_server.py）${NC}"
    echo "检查的路径:"
    for dir in "${POSSIBLE_DIRS[@]}"; do
        echo "  - $dir"
        ls -la "$dir/api_server.py" 2>/dev/null || echo "    不存在"
    done
    exit 1
fi

cd "$PROJECT_DIR"
echo -e "${BLUE}当前目录: $(pwd)${NC}"

# 2. 更新代码
echo ""
echo -e "${YELLOW}📥 步骤 2: 更新代码...${NC}"
if [ -d ".git" ]; then
    git pull
    echo -e "${GREEN}✅ 代码已更新${NC}"
else
    echo -e "${YELLOW}⚠️  当前目录不是 Git 仓库，跳过更新${NC}"
fi

# 3. 检查并创建虚拟环境
echo ""
echo -e "${YELLOW}🐍 步骤 3: 设置虚拟环境...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ 虚拟环境已存在${NC}"
else
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo -e "${GREEN}✅ 虚拟环境已创建${NC}"
fi

# 4. 激活虚拟环境并安装依赖
echo ""
echo -e "${YELLOW}📦 步骤 4: 安装/更新依赖...${NC}"
source venv/bin/activate

# 升级 pip
pip install --upgrade pip --quiet

# 安装依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
else
    echo -e "${RED}❌ 错误: requirements.txt 不存在${NC}"
    exit 1
fi

# 5. 初始化数据库
echo ""
echo -e "${YELLOW}🗄️  步骤 5: 初始化数据库...${NC}"
python3 -c "from database.models import init_database; init_database()"
echo -e "${GREEN}✅ 数据库初始化完成${NC}"

# 6. 检查 API 服务
echo ""
echo -e "${YELLOW}🔍 步骤 6: 检查 API 服务...${NC}"

# 检查是否作为 systemd 服务运行
API_SERVICE_NAMES=(
    "wushipay-api"
    "api-server"
    "wushizhifu-api"
)

SERVICE_FOUND=false
for service_name in "${API_SERVICE_NAMES[@]}"; do
    if systemctl list-units --all | grep -q "$service_name.service"; then
        echo -e "${GREEN}✅ 找到服务: ${service_name}.service${NC}"
        echo "重启服务..."
        sudo systemctl restart "${service_name}.service"
        sleep 2
        sudo systemctl status "${service_name}.service" --no-pager -l | head -15
        SERVICE_FOUND=true
        break
    fi
done

if [ "$SERVICE_FOUND" = false ]; then
    echo -e "${YELLOW}⚠️  未找到 systemd 服务${NC}"
    echo "检查是否有进程在运行..."
    
    if pgrep -f "api_server" > /dev/null; then
        echo -e "${YELLOW}发现运行中的 API 进程，正在停止...${NC}"
        pkill -f "api_server"
        sleep 1
    fi
    
    echo "手动启动 API 服务器..."
    echo "使用以下命令在后台运行："
    echo "  cd $PROJECT_DIR"
    echo "  source venv/bin/activate"
    echo "  nohup python3 api_service.py > api_server.log 2>&1 &"
    echo ""
    echo "或创建 systemd 服务文件"
fi

# 7. 验证 API 服务
echo ""
echo -e "${YELLOW}✅ 步骤 7: 验证 API 服务...${NC}"
sleep 3

if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo -e "${GREEN}✅ API 服务正在运行${NC}"
    echo "测试视频端点..."
    curl -s http://127.0.0.1:8000/api/videos/alipay | head -c 100
    echo ""
else
    echo -e "${YELLOW}⚠️  API 服务未运行（可能还在启动中）${NC}"
    echo "手动检查: curl http://127.0.0.1:8000/"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ API 服务器更新完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}项目目录: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}虚拟环境: ${PROJECT_DIR}/venv${NC}"

