#!/bin/bash
# 正确部署前端 - 处理实际路径情况

set -e

echo "=========================================="
echo "🚀 正确部署前端项目"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 查找前端代码位置
echo -e "${YELLOW}🔍 步骤 1: 查找前端代码...${NC}"

# 可能的源路径
SOURCE_PATHS=(
    "/home/ubuntu/wushizhifu/wushizhifu-full"
    "/home/ubuntu/wushizhifu/repo/wushizhifu-full"
    "/opt/wushizhifu/wushizhifu-full"
)

SOURCE_DIR=""
for path in "${SOURCE_PATHS[@]}"; do
    if [ -f "$path/package.json" ]; then
        SOURCE_DIR="$path"
        echo -e "${GREEN}✅ 找到前端代码: ${SOURCE_DIR}${NC}"
        break
    fi
done

# 如果没找到，尝试从 GitHub 克隆
if [ -z "$SOURCE_DIR" ]; then
    echo -e "${YELLOW}⚠️  未找到现有代码，从 GitHub 克隆...${NC}"
    PROJECT_DIR="$HOME/wushizhifu"
    mkdir -p ${PROJECT_DIR}
    cd ${PROJECT_DIR}
    
    if [ ! -d "repo" ]; then
        git clone https://github.com/victor2025PH/wushizhifu.git repo
    fi
    
    if [ -f "repo/wushizhifu-full/package.json" ]; then
        SOURCE_DIR="repo/wushizhifu-full"
        echo -e "${GREEN}✅ 从 GitHub 获取代码: ${PROJECT_DIR}/${SOURCE_DIR}${NC}"
    else
        echo -e "${RED}❌ 错误: 无法找到前端代码${NC}"
        exit 1
    fi
fi

# 2. 确定目标路径
echo ""
echo -e "${YELLOW}📂 步骤 2: 确定部署路径...${NC}"
TARGET_DIR="$HOME/wushizhifu/frontend"

echo -e "${BLUE}源路径: ${SOURCE_DIR}${NC}"
echo -e "${BLUE}目标路径: ${TARGET_DIR}${NC}"

# 3. 复制或移动文件
echo ""
echo -e "${YELLOW}📋 步骤 3: 准备前端目录...${NC}"

# 如果目标目录已存在，备份
if [ -d "$TARGET_DIR" ]; then
    if [ "$(realpath "$SOURCE_DIR")" != "$(realpath "$TARGET_DIR")" ]; then
        echo "备份现有目录..."
        mv "$TARGET_DIR" "${TARGET_DIR}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || rm -rf "$TARGET_DIR"
    else
        echo -e "${GREEN}✅ 源路径和目标路径相同，无需复制${NC}"
    fi
fi

# 如果源和目标不同，需要复制
if [ "$(realpath "$SOURCE_DIR" 2>/dev/null || echo "$SOURCE_DIR")" != "$(realpath "$TARGET_DIR" 2>/dev/null || echo "$TARGET_DIR")" ]; then
    echo "复制文件..."
    
    # 获取源目录的绝对路径
    cd "$(dirname "$SOURCE_DIR")"
    ABS_SOURCE=$(pwd)/$(basename "$SOURCE_DIR")
    
    # 创建目标目录的父目录
    mkdir -p "$(dirname "$TARGET_DIR")"
    
    # 复制文件（使用 * 确保复制内容而不是目录本身）
    if [ -d "$ABS_SOURCE" ]; then
        cp -r "$ABS_SOURCE"/* "$TARGET_DIR" 2>/dev/null || {
            # 如果上面失败，尝试先创建目录再复制
            mkdir -p "$TARGET_DIR"
            cp -r "$ABS_SOURCE"/* "$TARGET_DIR"
        }
    else
        echo -e "${RED}❌ 错误: 源目录不存在${NC}"
        exit 1
    fi
fi

# 4. 验证复制结果
echo ""
echo -e "${YELLOW}✅ 步骤 4: 验证文件...${NC}"
if [ ! -f "$TARGET_DIR/package.json" ]; then
    echo -e "${RED}❌ 错误: package.json 不存在${NC}"
    echo "目录内容:"
    ls -la "$TARGET_DIR/" | head -10
    exit 1
fi
echo -e "${GREEN}✅ package.json 已找到${NC}"

# 5. 检查 Node.js
echo ""
echo -e "${YELLOW}🔍 步骤 5: 检查 Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js 版本: $(node --version)${NC}"

# 6. 安装依赖
echo ""
echo -e "${YELLOW}📦 步骤 6: 安装依赖...${NC}"
cd "$TARGET_DIR"
if [ ! -d "node_modules" ]; then
    npm install
else
    npm install
fi
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 7. 构建前端
echo ""
echo -e "${YELLOW}🏗️  步骤 7: 构建前端...${NC}"
# 设置 dist 目录权限
if [ -d "dist" ]; then
    chown -R $USER:$USER dist 2>/dev/null || true
fi

npm run build

# 检查构建结果
if [ ! -f "dist/index.html" ]; then
    echo -e "${RED}❌ 构建失败: dist/index.html 不存在${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 前端构建完成${NC}"

# 8. 设置权限
echo ""
echo -e "${YELLOW}🔐 步骤 8: 设置权限...${NC}"
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist
echo -e "${GREEN}✅ 权限设置完成${NC}"

# 9. 显示结果
echo ""
echo -e "${GREEN}=========================================="
echo "✅ 前端部署完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}📁 前端目录: ${TARGET_DIR}${NC}"
echo -e "${BLUE}📁 构建输出: ${TARGET_DIR}/dist${NC}"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo "更新 Nginx 配置中的 root 路径为: ${TARGET_DIR}/dist"

