#!/bin/bash
# 快速部署前端 - 不使用 sudo（避免路径问题）

set -e

echo "=========================================="
echo "🚀 快速部署前端项目"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量 - 使用当前用户目录
PROJECT_DIR="$HOME/wushizhifu"
FRONTEND_DIR="$PROJECT_DIR/frontend"
REPO_URL="https://github.com/victor2025PH/wushizhifu.git"

echo -e "${BLUE}📁 项目目录: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}📁 前端目录: ${FRONTEND_DIR}${NC}"
echo ""

# 1. 创建项目目录
echo -e "${YELLOW}📂 步骤 1: 创建项目目录...${NC}"
mkdir -p ${PROJECT_DIR}
cd ${PROJECT_DIR}
echo -e "${GREEN}✅ 目录创建完成${NC}"

# 2. 克隆或更新仓库
echo ""
echo -e "${YELLOW}📥 步骤 2: 获取源代码...${NC}"
if [ ! -d "repo" ]; then
    echo "克隆仓库..."
    git clone ${REPO_URL} repo
    echo -e "${GREEN}✅ 仓库已克隆${NC}"
else
    cd repo
    echo "更新仓库..."
    git pull
    cd ..
    echo -e "${GREEN}✅ 仓库已更新${NC}"
fi

# 3. 检查前端代码是否存在
echo ""
echo -e "${YELLOW}🔍 步骤 3: 检查前端代码...${NC}"
if [ ! -d "repo/wushizhifu-full" ]; then
    echo -e "${RED}❌ 错误: 找不到 wushizhifu-full 目录${NC}"
    echo "仓库结构："
    ls -la repo/ | head -20
    exit 1
fi
echo -e "${GREEN}✅ 找到前端代码目录${NC}"

# 4. 复制前端代码到 frontend 目录
echo ""
echo -e "${YELLOW}📋 步骤 4: 复制前端代码...${NC}"
if [ -d "${FRONTEND_DIR}" ]; then
    echo "备份现有前端目录..."
    mv ${FRONTEND_DIR} ${FRONTEND_DIR}.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || rm -rf ${FRONTEND_DIR}
fi

echo "复制前端代码..."
cp -r repo/wushizhifu-full ${FRONTEND_DIR}

# 验证复制结果
if [ ! -f "${FRONTEND_DIR}/package.json" ]; then
    echo -e "${RED}❌ 错误: package.json 未找到${NC}"
    echo "前端目录内容:"
    ls -la ${FRONTEND_DIR}/ | head -10
    exit 1
fi
echo -e "${GREEN}✅ 前端代码已复制（package.json 验证通过）${NC}"

# 5. 检查 Node.js
echo ""
echo -e "${YELLOW}🔍 步骤 5: 检查 Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    echo "请先安装 Node.js:"
    echo "  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "  sudo apt install -y nodejs"
    exit 1
fi

echo -e "${GREEN}✅ Node.js 版本: $(node --version)${NC}"
echo -e "${GREEN}✅ npm 版本: $(npm --version)${NC}"

# 6. 安装依赖
echo ""
echo -e "${YELLOW}📦 步骤 6: 安装依赖...${NC}"
cd ${FRONTEND_DIR}
if [ ! -d "node_modules" ]; then
    echo "安装 npm 依赖..."
    npm install
else
    echo "更新 npm 依赖..."
    npm install
fi
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 7. 设置 dist 目录权限
echo ""
echo -e "${YELLOW}🔐 步骤 7: 设置权限...${NC}"
if [ -d "dist" ]; then
    chown -R $USER:$USER dist 2>/dev/null || true
fi
echo -e "${GREEN}✅ 权限设置完成${NC}"

# 8. 构建前端
echo ""
echo -e "${YELLOW}🏗️  步骤 8: 构建前端...${NC}"
npm run build

# 检查构建结果
if [ ! -f "dist/index.html" ]; then
    echo -e "${RED}❌ 构建失败: dist/index.html 不存在${NC}"
    echo "dist 目录内容:"
    ls -la dist/ 2>/dev/null || echo "dist 目录不存在"
    exit 1
fi
echo -e "${GREEN}✅ 前端构建完成${NC}"

# 9. 设置构建文件权限（需要 sudo）
echo ""
echo -e "${YELLOW}🔐 步骤 9: 设置构建文件权限（需要 sudo）...${NC}"
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist
echo -e "${GREEN}✅ 权限设置完成${NC}"

# 10. 显示构建结果
echo ""
echo -e "${BLUE}📋 构建结果:${NC}"
ls -lh dist/ | head -10

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 前端项目部署完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}📁 前端目录: ${FRONTEND_DIR}${NC}"
echo -e "${BLUE}📁 构建输出: ${FRONTEND_DIR}/dist${NC}"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo "运行修复脚本更新 Nginx 配置:"
echo "  wget https://raw.githubusercontent.com/victor2025PH/wushizhifu/main/deploy/修复500错误.sh"
echo "  chmod +x 修复500错误.sh"
echo "  sudo ./修复500错误.sh"

