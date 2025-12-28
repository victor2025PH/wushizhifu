#!/bin/bash
# 彻底部署前端 - 清理并重新部署

set -e

echo "=========================================="
echo "🚀 彻底部署前端项目"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="$HOME/wushizhifu"
TARGET_DIR="$PROJECT_DIR/frontend"
REPO_DIR="$PROJECT_DIR/repo"
SOURCE_DIR="$REPO_DIR/wushizhifu-full"

echo -e "${BLUE}项目目录: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}目标目录: ${TARGET_DIR}${NC}"
echo ""

# 1. 清理旧的空目录
echo -e "${YELLOW}🧹 步骤 1: 清理旧目录...${NC}"
if [ -d "$PROJECT_DIR/wushizhifu-full" ]; then
    # 检查是否为空目录
    if [ -z "$(ls -A $PROJECT_DIR/wushizhifu-full 2>/dev/null)" ]; then
        echo "删除空目录: $PROJECT_DIR/wushizhifu-full"
        rmdir "$PROJECT_DIR/wushizhifu-full" 2>/dev/null || rm -rf "$PROJECT_DIR/wushizhifu-full"
    fi
fi

if [ -d "$SOURCE_DIR" ]; then
    # 检查是否为空目录
    if [ -z "$(ls -A $SOURCE_DIR 2>/dev/null)" ]; then
        echo "删除空目录: $SOURCE_DIR"
        rmdir "$SOURCE_DIR" 2>/dev/null || rm -rf "$SOURCE_DIR"
    fi
fi
echo -e "${GREEN}✅ 清理完成${NC}"

# 2. 确保项目目录存在
echo ""
echo -e "${YELLOW}📂 步骤 2: 准备项目目录...${NC}"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
echo -e "${GREEN}✅ 目录准备完成${NC}"

# 3. 克隆或更新仓库
echo ""
echo -e "${YELLOW}📥 步骤 3: 获取源代码...${NC}"
if [ ! -d "$REPO_DIR" ]; then
    echo "克隆仓库..."
    git clone https://github.com/victor2025PH/wushizhifu.git repo
    echo -e "${GREEN}✅ 仓库已克隆${NC}"
else
    echo "更新仓库..."
    cd "$REPO_DIR"
    git pull
    cd "$PROJECT_DIR"
    echo -e "${GREEN}✅ 仓库已更新${NC}"
fi

# 4. 验证源目录
echo ""
echo -e "${YELLOW}🔍 步骤 4: 验证源代码...${NC}"
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ 错误: $SOURCE_DIR 不存在${NC}"
    echo "repo 目录内容:"
    ls -la "$REPO_DIR/" | head -20
    exit 1
fi

echo "检查源目录内容..."
ls -la "$SOURCE_DIR/" | head -10

if [ ! -f "$SOURCE_DIR/package.json" ]; then
    echo -e "${RED}❌ 错误: $SOURCE_DIR/package.json 不存在${NC}"
    echo "尝试查找 package.json..."
    find "$REPO_DIR" -name "package.json" -type f 2>/dev/null | head -5
    exit 1
fi

echo -e "${GREEN}✅ 源代码验证通过${NC}"
echo "package.json 内容（前几行）:"
head -5 "$SOURCE_DIR/package.json"

# 5. 准备目标目录
echo ""
echo -e "${YELLOW}📋 步骤 5: 准备目标目录...${NC}"
if [ -d "$TARGET_DIR" ]; then
    echo "备份现有目录..."
    mv "$TARGET_DIR" "${TARGET_DIR}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || rm -rf "$TARGET_DIR"
fi

echo "创建目标目录..."
mkdir -p "$TARGET_DIR"

# 6. 复制文件
echo ""
echo -e "${YELLOW}📋 步骤 6: 复制文件...${NC}"
echo "从 $SOURCE_DIR 复制到 $TARGET_DIR"

cd "$SOURCE_DIR"
# 使用 cp -r 复制所有文件（包括隐藏文件）
cp -r . "$TARGET_DIR"/

# 验证复制结果
echo "验证复制结果..."
if [ ! -f "$TARGET_DIR/package.json" ]; then
    echo -e "${RED}❌ 复制失败: package.json 不存在${NC}"
    echo "目标目录内容:"
    ls -la "$TARGET_DIR/" | head -10
    exit 1
fi

echo -e "${GREEN}✅ 文件复制完成${NC}"
echo "目标目录内容:"
ls -la "$TARGET_DIR/" | head -10

# 7. 检查 Node.js
echo ""
echo -e "${YELLOW}🔍 步骤 7: 检查 Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"
echo -e "${GREEN}✅ npm: $(npm --version)${NC}"

# 8. 安装依赖
echo ""
echo -e "${YELLOW}📦 步骤 8: 安装依赖...${NC}"
cd "$TARGET_DIR"
npm install
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 9. 构建前端
echo ""
echo -e "${YELLOW}🏗️  步骤 9: 构建前端...${NC}"
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
echo "构建结果:"
ls -lh dist/ | head -10

# 10. 设置权限
echo ""
echo -e "${YELLOW}🔐 步骤 10: 设置权限...${NC}"
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist
echo -e "${GREEN}✅ 权限设置完成${NC}"

# 完成
echo ""
echo -e "${GREEN}=========================================="
echo "✅ 前端部署完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}📁 前端目录: ${TARGET_DIR}${NC}"
echo -e "${BLUE}📁 构建输出: ${TARGET_DIR}/dist${NC}"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo "1. 更新 Nginx 配置:"
echo "   sudo nano /etc/nginx/sites-available/wushizhifu"
echo "   设置 root 为: ${TARGET_DIR}/dist"
echo ""
echo "2. 测试并重载 Nginx:"
echo "   sudo nginx -t && sudo systemctl reload nginx"
echo ""
echo "3. 验证:"
echo "   curl -I https://50zf.usdt2026.cc"

