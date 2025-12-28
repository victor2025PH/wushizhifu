#!/bin/bash
# 更新代码并重新构建前端

set -e

echo "=========================================="
echo "🔄 更新代码并重新构建前端"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="$HOME/wushizhifu"
REPO_DIR="$PROJECT_DIR/repo"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo -e "${BLUE}项目目录: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}前端目录: ${FRONTEND_DIR}${NC}"
echo ""

# 1. 更新仓库
echo -e "${YELLOW}📥 步骤 1: 更新代码...${NC}"
cd "$REPO_DIR"
git pull
echo -e "${GREEN}✅ 代码更新完成${NC}"

# 2. 复制更新的文件
echo ""
echo -e "${YELLOW}📋 步骤 2: 复制更新的文件...${NC}"
if [ ! -f "wushizhifu-full/index.html" ]; then
    echo -e "${RED}❌ 错误: wushizhifu-full/index.html 不存在${NC}"
    echo "当前目录: $(pwd)"
    echo "wushizhifu-full 目录内容:"
    ls -la wushizhifu-full/ 2>/dev/null | head -10 || echo "wushizhifu-full 目录不存在"
    exit 1
fi

echo "从 $(pwd)/wushizhifu-full 复制到 ${FRONTEND_DIR}"
cp -r wushizhifu-full/* "$FRONTEND_DIR"/
echo -e "${GREEN}✅ 文件复制完成${NC}"

# 3. 验证 index.html
echo ""
echo -e "${YELLOW}🔍 步骤 3: 验证 index.html...${NC}"
if grep -q '<script type="module" src="/index.tsx"></script>' "$FRONTEND_DIR/index.html"; then
    echo -e "${GREEN}✅ index.html 包含入口文件引用${NC}"
else
    echo -e "${RED}❌ 警告: index.html 可能缺少入口文件引用${NC}"
fi

# 4. 清理并重新构建
echo ""
echo -e "${YELLOW}🏗️  步骤 4: 清理并重新构建...${NC}"
cd "$FRONTEND_DIR"
sudo chown -R ubuntu:ubuntu dist 2>/dev/null || true
rm -rf dist/*
npm run build

# 5. 检查构建结果
echo ""
echo -e "${YELLOW}✅ 步骤 5: 检查构建结果...${NC}"
if [ ! -f "dist/index.html" ]; then
    echo -e "${RED}❌ 构建失败: dist/index.html 不存在${NC}"
    exit 1
fi

echo "dist 目录内容:"
ls -la dist/

if [ -d "dist/assets" ]; then
    echo ""
    echo "assets 目录内容:"
    ls -la dist/assets/ | head -10
    echo -e "${GREEN}✅ assets 目录存在${NC}"
else
    echo -e "${YELLOW}⚠️  assets 目录不存在${NC}"
fi

echo ""
echo "index.html 中的 script 标签:"
grep -i "script" dist/index.html | head -5

# 6. 设置权限
echo ""
echo -e "${YELLOW}🔐 步骤 6: 设置权限...${NC}"
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist
echo -e "${GREEN}✅ 权限设置完成${NC}"

# 7. 重载 Nginx
echo ""
echo -e "${YELLOW}🔄 步骤 7: 重载 Nginx...${NC}"
sudo systemctl reload nginx
echo -e "${GREEN}✅ Nginx 已重载${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 更新和构建完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}🌐 访问: https://50zf.usdt2026.cc${NC}"

