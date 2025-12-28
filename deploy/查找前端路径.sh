#!/bin/bash
# 查找前端代码的实际路径

echo "=========================================="
echo "🔍 查找前端代码路径"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}正在检查可能的路径...${NC}"
echo ""

# 检查路径列表
PATHS=(
    "/home/ubuntu/wushizhifu/wushizhifu-full"
    "/home/ubuntu/wushizhifu/frontend"
    "/home/ubuntu/wushizhifu/repo/wushizhifu-full"
    "/opt/wushizhifu/wushizhifu-full"
    "/opt/wushizhifu/frontend"
    "/root/wushizhifu/wushizhifu-full"
    "/root/wushizhifu/frontend"
)

FOUND=0

for path in "${PATHS[@]}"; do
    if [ -f "$path/package.json" ]; then
        echo -e "${GREEN}✅ 找到 package.json: $path${NC}"
        echo "   内容:"
        ls -la "$path/" | head -5
        echo ""
        FOUND=1
        
        # 检查 dist 目录
        if [ -d "$path/dist" ]; then
            echo -e "${GREEN}  ✅ dist 目录存在${NC}"
            if [ -f "$path/dist/index.html" ]; then
                echo -e "${GREEN}  ✅ index.html 存在${NC}"
            else
                echo -e "${YELLOW}  ⚠️  index.html 不存在，需要构建${NC}"
            fi
        else
            echo -e "${YELLOW}  ⚠️  dist 目录不存在，需要构建${NC}"
        fi
        echo ""
    fi
done

if [ $FOUND -eq 0 ]; then
    echo -e "${RED}❌ 未找到包含 package.json 的前端目录${NC}"
    echo ""
    echo "检查所有可能的 wushizhifu 目录:"
    find /home/ubuntu -name "wushizhifu-full" -type d 2>/dev/null | head -5
    find /opt -name "wushizhifu-full" -type d 2>/dev/null | head -5
    find /root -name "wushizhifu-full" -type d 2>/dev/null | head -5
fi

echo ""
echo -e "${BLUE}检查 Nginx 配置中的路径...${NC}"
if [ -f "/etc/nginx/sites-available/wushizhifu" ]; then
    ROOT_PATH=$(grep "^\s*root" /etc/nginx/sites-available/wushizhifu | awk '{print $2}' | sed 's/;//')
    echo "Nginx 配置的 root: $ROOT_PATH"
    if [ -d "$ROOT_PATH" ]; then
        if [ -f "$ROOT_PATH/index.html" ]; then
            echo -e "${GREEN}✅ Nginx 路径存在且有 index.html${NC}"
        else
            echo -e "${YELLOW}⚠️  Nginx 路径存在但无 index.html${NC}"
        fi
    else
        echo -e "${RED}❌ Nginx 路径不存在${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Nginx 配置文件不存在${NC}"
fi

