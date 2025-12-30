#!/bin/bash
# 排查部署问题脚本

set -e

echo "=========================================="
echo "🔍 排查 Miniapp 部署问题"
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

echo -e "${BLUE}=========================================="
echo "1. 检查源代码目录构建结果"
echo "==========================================${NC}"
if [ -d "$SOURCE_DIR/dist" ]; then
    echo -e "${GREEN}✅ 源代码 dist 目录存在${NC}"
    echo "文件列表："
    ls -lh "$SOURCE_DIR/dist" | head -10
    echo ""
    if [ -f "$SOURCE_DIR/dist/index.html" ]; then
        echo -e "${GREEN}✅ index.html 存在${NC}"
        echo "修改时间: $(stat -c %y "$SOURCE_DIR/dist/index.html")"
        echo ""
        # 检查 JS 文件名
        JS_FILES=$(find "$SOURCE_DIR/dist/assets" -name "index-*.js" 2>/dev/null | head -1)
        if [ -n "$JS_FILES" ]; then
            echo -e "${GREEN}✅ 找到 JS 文件: $(basename "$JS_FILES")${NC}"
            echo "修改时间: $(stat -c %y "$JS_FILES")"
            # 检查文件内容中是否包含新代码
            if grep -q "openAccount\|开通帐户" "$JS_FILES" 2>/dev/null; then
                echo -e "${GREEN}✅ JS 文件包含新代码（openAccount）${NC}"
            else
                echo -e "${YELLOW}⚠️  JS 文件可能不包含新代码${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ index.html 不存在${NC}"
    fi
else
    echo -e "${RED}❌ 源代码 dist 目录不存在${NC}"
fi
echo ""

echo -e "${BLUE}=========================================="
echo "2. 检查部署目标目录"
echo "==========================================${NC}"
if [ -d "$TARGET_DIR" ]; then
    echo -e "${GREEN}✅ 目标目录存在: $TARGET_DIR${NC}"
    echo "文件权限："
    ls -ld "$TARGET_DIR"
    echo ""
    echo "文件列表："
    ls -lh "$TARGET_DIR" | head -10
    echo ""
    if [ -f "$TARGET_DIR/index.html" ]; then
        echo -e "${GREEN}✅ index.html 存在${NC}"
        echo "修改时间: $(stat -c %y "$TARGET_DIR/index.html")"
        echo "文件大小: $(stat -c %s "$TARGET_DIR/index.html") bytes"
        echo ""
        # 检查 JS 文件名
        if [ -d "$TARGET_DIR/assets" ]; then
            JS_FILES=$(find "$TARGET_DIR/assets" -name "index-*.js" 2>/dev/null | head -1)
            if [ -n "$JS_FILES" ]; then
                echo -e "${GREEN}✅ 找到 JS 文件: $(basename "$JS_FILES")${NC}"
                echo "修改时间: $(stat -c %y "$JS_FILES")"
                echo "文件大小: $(stat -c %s "$JS_FILES") bytes"
                # 检查文件内容
                if grep -q "openAccount\|开通帐户" "$JS_FILES" 2>/dev/null; then
                    echo -e "${GREEN}✅ JS 文件包含新代码（openAccount）${NC}"
                else
                    echo -e "${RED}❌ JS 文件不包含新代码${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  未找到 JS 文件${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ index.html 不存在${NC}"
    fi
else
    echo -e "${RED}❌ 目标目录不存在${NC}"
fi
echo ""

echo -e "${BLUE}=========================================="
echo "3. 比较源代码和部署目录的文件"
echo "==========================================${NC}"
if [ -f "$SOURCE_DIR/dist/index.html" ] && [ -f "$TARGET_DIR/index.html" ]; then
    SOURCE_SIZE=$(stat -c %s "$SOURCE_DIR/dist/index.html")
    TARGET_SIZE=$(stat -c %s "$TARGET_DIR/index.html")
    SOURCE_TIME=$(stat -c %Y "$SOURCE_DIR/dist/index.html")
    TARGET_TIME=$(stat -c %Y "$TARGET_DIR/index.html")
    
    if [ "$SOURCE_SIZE" -eq "$TARGET_SIZE" ] && [ "$SOURCE_TIME" -eq "$TARGET_TIME" ]; then
        echo -e "${GREEN}✅ index.html 文件一致${NC}"
    else
        echo -e "${RED}❌ index.html 文件不一致${NC}"
        echo "  源代码大小: $SOURCE_SIZE bytes"
        echo "  部署文件大小: $TARGET_SIZE bytes"
        echo "  源代码时间: $(stat -c %y "$SOURCE_DIR/dist/index.html")"
        echo "  部署文件时间: $(stat -c %y "$TARGET_DIR/index.html")"
    fi
fi
echo ""

echo -e "${BLUE}=========================================="
echo "4. 检查 Nginx 配置"
echo "==========================================${NC}"
if [ ! -f "$NGINX_CONFIG" ]; then
    NGINX_CONFIG="/etc/nginx/sites-available/wushizhifu"
fi

if [ -f "$NGINX_CONFIG" ]; then
    echo -e "${GREEN}✅ Nginx 配置文件存在: $NGINX_CONFIG${NC}"
    echo ""
    echo "当前 root 配置："
    grep -E "^\s*root\s+" "$NGINX_CONFIG" || echo "未找到 root 配置"
    echo ""
    echo "完整配置："
    cat "$NGINX_CONFIG"
else
    echo -e "${RED}❌ Nginx 配置文件不存在${NC}"
fi
echo ""

echo -e "${BLUE}=========================================="
echo "5. 检查文件权限"
echo "==========================================${NC}"
if [ -d "$TARGET_DIR" ]; then
    echo "目录权限："
    ls -ld "$TARGET_DIR"
    echo ""
    echo "文件所有者："
    stat -c "%n: %U:%G (%a)" "$TARGET_DIR" 2>/dev/null || true
    if [ -f "$TARGET_DIR/index.html" ]; then
        stat -c "%n: %U:%G (%a)" "$TARGET_DIR/index.html" 2>/dev/null || true
    fi
fi
echo ""

echo -e "${BLUE}=========================================="
echo "6. 测试 Nginx 配置"
echo "==========================================${NC}"
if sudo nginx -t 2>&1; then
    echo -e "${GREEN}✅ Nginx 配置测试通过${NC}"
else
    echo -e "${RED}❌ Nginx 配置测试失败${NC}"
fi
echo ""

echo -e "${BLUE}=========================================="
echo "7. 检查 Nginx 服务状态"
echo "==========================================${NC}"
sudo systemctl status nginx --no-pager -l | head -20
echo ""

echo -e "${BLUE}=========================================="
echo "排查完成"
echo "==========================================${NC}"
echo ""
echo "根据以上信息，可以确定问题所在。"
echo "如果文件不一致，需要执行修复脚本。"
