#!/bin/bash
# 一键修复 500 错误 - 自动部署前端并修复配置

set -e

echo "=========================================="
echo "🚀 一键修复 500 Internal Server Error"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 下载部署前端脚本
echo -e "${YELLOW}📥 步骤 1: 下载部署脚本...${NC}"
cd ~
if [ ! -f "部署前端项目.sh" ]; then
    wget -q https://raw.githubusercontent.com/victor2025PH/wushizhifu/main/deploy/部署前端项目.sh
    chmod +x 部署前端项目.sh
fi
echo -e "${GREEN}✅ 脚本已准备${NC}"

# 运行部署脚本
echo ""
echo -e "${YELLOW}🚀 步骤 2: 部署前端项目...${NC}"
sudo ./部署前端项目.sh

# 下载修复脚本
echo ""
echo -e "${YELLOW}📥 步骤 3: 下载修复脚本...${NC}"
if [ ! -f "修复500错误.sh" ]; then
    wget -q https://raw.githubusercontent.com/victor2025PH/wushizhifu/main/deploy/修复500错误.sh
    chmod +x 修复500错误.sh
fi
echo -e "${GREEN}✅ 脚本已准备${NC}"

# 运行修复脚本
echo ""
echo -e "${YELLOW}🔧 步骤 4: 修复配置...${NC}"
sudo ./修复500错误.sh

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 一键修复完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}🌐 访问网站: https://50zf.usdt2026.cc${NC}"

