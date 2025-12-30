#!/bin/bash
# 彻底修复部署问题脚本

set -e

echo "=========================================="
echo "🔧 彻底修复 Miniapp 部署问题"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$HOME/wushizhifu"
SOURCE_DIR="$PROJECT_ROOT/wushizhifu-full"
TARGET_DIR="$PROJECT_ROOT/frontend/dist"
NGINX_CONFIG="/etc/nginx/sites-available/50zf.usdt2026.cc"

# 1. 确保在正确的目录
echo -e "${YELLOW}步骤 1: 检查源代码目录...${NC}"
cd "$PROJECT_ROOT"
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ 源代码目录不存在: $SOURCE_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 源代码目录存在${NC}"
echo ""

# 2. 拉取最新代码
echo -e "${YELLOW}步骤 2: 拉取最新代码...${NC}"
git stash || true
git pull origin main
echo -e "${GREEN}✅ 代码已更新${NC}"
echo ""

# 3. 进入源代码目录并构建
echo -e "${YELLOW}步骤 3: 构建前端...${NC}"
cd "$SOURCE_DIR"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "安装 npm 依赖..."
    npm install --production=false
fi

# 构建前端
echo "执行构建..."
export NODE_OPTIONS="--max-old-space-size=3072"
npm run build

# 检查构建结果
if [ ! -d "dist" ]; then
    echo -e "${RED}❌ 构建失败: dist 目录不存在${NC}"
    exit 1
fi

if [ ! -f "dist/index.html" ]; then
    echo -e "${RED}❌ 构建失败: dist/index.html 不存在${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 前端构建完成${NC}"
echo "构建时间: $(stat -c %y dist/index.html)"
echo ""

# 4. 使用 sudo 彻底删除旧文件
echo -e "${YELLOW}步骤 4: 彻底删除旧部署文件...${NC}"
if [ -d "$TARGET_DIR" ]; then
    echo "备份当前文件列表..."
    ls -la "$TARGET_DIR" > /tmp/old_files_list.txt 2>/dev/null || true
    
    echo "使用 sudo 删除旧文件..."
    sudo rm -rf "$TARGET_DIR"/*
    sudo rm -rf "$TARGET_DIR"/.[^.]* 2>/dev/null || true  # 删除隐藏文件（除了 . 和 ..）
    
    # 如果目录还存在，确保是空的
    if [ -d "$TARGET_DIR" ]; then
        REMAINING=$(find "$TARGET_DIR" -mindepth 1 2>/dev/null | wc -l)
        if [ "$REMAINING" -gt 0 ]; then
            echo -e "${YELLOW}⚠️  仍有文件残留，强制删除目录...${NC}"
            sudo rm -rf "$TARGET_DIR"
            sudo mkdir -p "$TARGET_DIR"
        fi
    else
        sudo mkdir -p "$TARGET_DIR"
    fi
    echo -e "${GREEN}✅ 旧文件已删除${NC}"
else
    echo "目标目录不存在，创建..."
    sudo mkdir -p "$TARGET_DIR"
    echo -e "${GREEN}✅ 目录已创建${NC}"
fi
echo ""

# 5. 复制新文件
echo -e "${YELLOW}步骤 5: 复制新构建文件...${NC}"
echo "源目录: $SOURCE_DIR/dist"
echo "目标目录: $TARGET_DIR"

# 使用 sudo 复制以确保权限正确
sudo cp -r "$SOURCE_DIR/dist"/* "$TARGET_DIR"/
sudo cp -r "$SOURCE_DIR/dist"/.[^.]* "$TARGET_DIR"/ 2>/dev/null || true  # 复制隐藏文件

# 验证复制结果
if [ ! -f "$TARGET_DIR/index.html" ]; then
    echo -e "${RED}❌ 复制失败: index.html 不存在${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 文件复制完成${NC}"
echo "文件列表："
ls -lh "$TARGET_DIR" | head -10
echo ""

# 6. 设置文件权限
echo -e "${YELLOW}步骤 6: 设置文件权限...${NC}"
sudo chown -R www-data:www-data "$TARGET_DIR"
sudo chmod -R 755 "$TARGET_DIR"
echo -e "${GREEN}✅ 权限设置完成${NC}"
echo "验证权限："
ls -ld "$TARGET_DIR"
ls -l "$TARGET_DIR/index.html" | head -1
echo ""

# 7. 更新 Nginx 配置
echo -e "${YELLOW}步骤 7: 更新 Nginx 配置...${NC}"
if [ ! -f "$NGINX_CONFIG" ]; then
    NGINX_CONFIG="/etc/nginx/sites-available/wushizhifu"
fi

if [ -f "$NGINX_CONFIG" ]; then
    echo "找到 Nginx 配置: $NGINX_CONFIG"
    
    # 备份配置
    sudo cp "$NGINX_CONFIG" "${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # 获取当前 root 配置
    CURRENT_ROOT=$(grep -E "^\s*root\s+" "$NGINX_CONFIG" | head -1 | sed 's/.*root\s*//;s/;.*//' | tr -d ';' | xargs)
    echo "当前 root: $CURRENT_ROOT"
    echo "目标 root: $TARGET_DIR"
    
    # 更新 root 路径
    if [ "$CURRENT_ROOT" != "$TARGET_DIR" ]; then
        echo "更新 root 路径..."
        sudo sed -i "s|root[[:space:]]*[^;]*;|root $TARGET_DIR;|g" "$NGINX_CONFIG"
        sudo sed -i "s|root[[:space:]]*/.*/frontend/dist;|root $TARGET_DIR;|g" "$NGINX_CONFIG"
        sudo sed -i "s|root[[:space:]]*/.*/frontend;|root $TARGET_DIR;|g" "$NGINX_CONFIG"
        echo -e "${GREEN}✅ Nginx 配置已更新${NC}"
    else
        echo -e "${GREEN}✅ Nginx 配置已正确${NC}"
    fi
    
    # 验证配置
    echo "验证 Nginx 配置..."
    if sudo nginx -t 2>&1; then
        echo -e "${GREEN}✅ Nginx 配置测试通过${NC}"
    else
        echo -e "${RED}❌ Nginx 配置测试失败${NC}"
        echo "恢复备份..."
        sudo cp "${NGINX_CONFIG}.backup."* "$NGINX_CONFIG" 2>/dev/null || true
        exit 1
    fi
else
    echo -e "${RED}❌ Nginx 配置文件不存在${NC}"
    exit 1
fi
echo ""

# 8. 重载 Nginx
echo -e "${YELLOW}步骤 8: 重载 Nginx...${NC}"
sudo systemctl reload nginx
echo -e "${GREEN}✅ Nginx 已重载${NC}"
echo ""

# 9. 验证部署
echo -e "${YELLOW}步骤 9: 验证部署...${NC}"
if [ -f "$TARGET_DIR/index.html" ]; then
    echo -e "${GREEN}✅ index.html 存在${NC}"
    echo "文件信息："
    ls -lh "$TARGET_DIR/index.html"
    echo ""
    
    # 检查 JS 文件
    JS_FILES=$(find "$TARGET_DIR/assets" -name "index-*.js" 2>/dev/null | head -1)
    if [ -n "$JS_FILES" ]; then
        echo -e "${GREEN}✅ 找到 JS 文件: $(basename "$JS_FILES")${NC}"
        # 检查是否包含新代码
        if grep -q "openAccount\|开通帐户" "$JS_FILES" 2>/dev/null; then
            echo -e "${GREEN}✅ JS 文件包含新代码（openAccount）${NC}"
        else
            echo -e "${YELLOW}⚠️  JS 文件可能不包含新代码（这可能是正常的，取决于代码压缩）${NC}"
        fi
    fi
else
    echo -e "${RED}❌ index.html 不存在${NC}"
    exit 1
fi
echo ""

# 完成
echo -e "${GREEN}=========================================="
echo "✅ 部署修复完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}📋 部署信息：${NC}"
echo "  部署目录: $TARGET_DIR"
echo "  Nginx 配置: $NGINX_CONFIG"
echo "  访问地址: https://50zf.usdt2026.cc"
echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo "  1. 如果浏览器仍显示旧内容，请清除浏览器缓存（Ctrl+Shift+R）"
echo "  2. 或在无痕模式下访问网站"
echo "  3. 检查浏览器开发者工具的 Network 标签，确认加载的是新文件"
echo ""
