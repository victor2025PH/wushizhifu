#!/bin/bash
# 直接部署前端 - 使用实际找到的路径

set -e

echo "=========================================="
echo "🚀 直接部署前端项目"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查并确定源路径
echo -e "${YELLOW}🔍 检查前端代码位置...${NC}"

POSSIBLE_PATHS=(
    "/home/ubuntu/wushizhifu/wushizhifu-full"
    "/home/ubuntu/wushizhifu/repo/wushizhifu-full"
)

SOURCE_DIR=""
for path in "${POSSIBLE_PATHS[@]}"; do
    echo "检查: $path"
    if [ -d "$path" ]; then
        echo "  目录存在"
        if [ -f "$path/package.json" ]; then
            SOURCE_DIR="$path"
            echo -e "${GREEN}  ✅ 找到 package.json${NC}"
            break
        else
            echo "  但 package.json 不存在"
            echo "  目录内容:"
            ls -la "$path/" | head -5
        fi
    else
        echo "  目录不存在"
    fi
    echo ""
done

# 如果没找到，尝试查找
if [ -z "$SOURCE_DIR" ]; then
    echo -e "${YELLOW}搜索所有可能的 wushizhifu-full 目录...${NC}"
    FOUND_DIRS=$(find /home/ubuntu -type d -name "wushizhifu-full" 2>/dev/null)
    
    for dir in $FOUND_DIRS; do
        echo "检查: $dir"
        if [ -f "$dir/package.json" ]; then
            SOURCE_DIR="$dir"
            echo -e "${GREEN}✅ 找到: $SOURCE_DIR${NC}"
            break
        fi
    done
fi

# 如果还是没找到，从 GitHub 克隆
if [ -z "$SOURCE_DIR" ]; then
    echo -e "${YELLOW}⚠️  未找到现有代码，从 GitHub 克隆...${NC}"
    PROJECT_DIR="$HOME/wushizhifu"
    mkdir -p ${PROJECT_DIR}
    cd ${PROJECT_DIR}
    
    if [ ! -d "repo" ]; then
        git clone https://github.com/victor2025PH/wushizhifu.git repo
    else
        cd repo && git pull && cd ..
    fi
    
    if [ -f "repo/wushizhifu-full/package.json" ]; then
        SOURCE_DIR="$PROJECT_DIR/repo/wushizhifu-full"
        echo -e "${GREEN}✅ 从 GitHub 获取: ${SOURCE_DIR}${NC}"
    else
        echo -e "${RED}❌ 错误: 无法找到前端代码${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}✅ 使用前端代码: ${SOURCE_DIR}${NC}"

# 设置目标目录
TARGET_DIR="$HOME/wushizhifu/frontend"

echo ""
echo -e "${YELLOW}📂 准备部署目录...${NC}"
echo "源: $SOURCE_DIR"
echo "目标: $TARGET_DIR"

# 如果源和目标相同，直接使用
if [ "$(realpath "$SOURCE_DIR" 2>/dev/null || echo "$SOURCE_DIR")" = "$(realpath "$TARGET_DIR" 2>/dev/null || echo "$TARGET_DIR")" ]; then
    echo -e "${GREEN}✅ 源路径和目标路径相同，直接使用${NC}"
    WORK_DIR="$SOURCE_DIR"
else
    # 创建或清理目标目录
    if [ -d "$TARGET_DIR" ]; then
        echo "备份现有目录..."
        mv "$TARGET_DIR" "${TARGET_DIR}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || rm -rf "$TARGET_DIR"
    fi
    
    echo "复制文件..."
    mkdir -p "$TARGET_DIR"
    
    # 复制所有文件
    cd "$SOURCE_DIR"
    cp -r . "$TARGET_DIR"/
    
    # 验证
    if [ ! -f "$TARGET_DIR/package.json" ]; then
        echo -e "${RED}❌ 复制失败: package.json 不存在${NC}"
        exit 1
    fi
    
    WORK_DIR="$TARGET_DIR"
fi

# 验证 package.json
echo ""
echo -e "${YELLOW}✅ 验证文件...${NC}"
if [ ! -f "$WORK_DIR/package.json" ]; then
    echo -e "${RED}❌ 错误: package.json 不存在于 $WORK_DIR${NC}"
    echo "目录内容:"
    ls -la "$WORK_DIR/" | head -10
    exit 1
fi
echo -e "${GREEN}✅ package.json 已找到${NC}"

# 检查 Node.js
echo ""
echo -e "${YELLOW}🔍 检查 Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"

# 安装依赖
echo ""
echo -e "${YELLOW}📦 安装依赖...${NC}"
cd "$WORK_DIR"
npm install
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 构建前端
echo ""
echo -e "${YELLOW}🏗️  构建前端...${NC}"
if [ -d "dist" ]; then
    chown -R $USER:$USER dist 2>/dev/null || true
    rm -rf dist/*
fi

npm run build

# 检查构建结果
if [ ! -f "dist/index.html" ]; then
    echo -e "${RED}❌ 构建失败: dist/index.html 不存在${NC}"
    echo "dist 目录内容:"
    ls -la dist/ 2>/dev/null || echo "dist 目录不存在"
    exit 1
fi
echo -e "${GREEN}✅ 前端构建完成${NC}"

# 设置权限
echo ""
echo -e "${YELLOW}🔐 设置权限...${NC}"
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist
echo -e "${GREEN}✅ 权限设置完成${NC}"

# 显示结果
echo ""
echo -e "${BLUE}📋 构建结果:${NC}"
ls -lh dist/ | head -10

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 前端部署完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}📁 工作目录: ${WORK_DIR}${NC}"
echo -e "${BLUE}📁 构建输出: ${WORK_DIR}/dist${NC}"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo "1. 更新 Nginx 配置:"
echo "   sudo nano /etc/nginx/sites-available/wushizhifu"
echo "   设置 root 为: ${WORK_DIR}/dist"
echo ""
echo "2. 测试并重载 Nginx:"
echo "   sudo nginx -t && sudo systemctl reload nginx"

