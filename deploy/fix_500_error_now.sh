#!/bin/bash
# 立即修复 500 错误

set -e

echo "=========================================="
echo "🔧 修复 50zf.usdt2026.cc 500 错误"
echo "=========================================="
echo ""

PROJECT_DIR="$HOME/wushizhifu"
FRONTEND_DIR="$PROJECT_DIR/frontend"
TARGET_DIR="$FRONTEND_DIR/dist"

# 1. 检查前端目录是否存在
echo "1. 检查前端目录..."
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ 错误: $TARGET_DIR 不存在"
    echo "正在查找 wushizhifu-full 目录..."
    
    if [ -d "$PROJECT_DIR/repo/wushizhifu-full" ]; then
        SOURCE_DIR="$PROJECT_DIR/repo/wushizhifu-full"
    elif [ -d "$PROJECT_DIR/wushizhifu-full" ]; then
        SOURCE_DIR="$PROJECT_DIR/wushizhifu-full"
    else
        echo "❌ 错误: 找不到 wushizhifu-full 目录"
        exit 1
    fi
    
    echo "找到源代码目录: $SOURCE_DIR"
    
    # 检查是否需要构建
    if [ ! -d "$SOURCE_DIR/dist" ]; then
        echo "📦 构建前端..."
        cd "$SOURCE_DIR"
        npm install --production=false
        export NODE_OPTIONS="--max-old-space-size=3072"
        npm run build
    fi
    
    # 复制到目标目录
    echo "📋 复制构建结果..."
    mkdir -p "$(dirname "$TARGET_DIR")"
    cp -r "$SOURCE_DIR/dist" "$TARGET_DIR"
    echo "✅ 文件已复制到: $TARGET_DIR"
else
    echo "✅ 前端目录存在: $TARGET_DIR"
fi

# 2. 检查文件权限
echo ""
echo "2. 设置文件权限..."
sudo chown -R www-data:www-data "$TARGET_DIR" || sudo chown -R ubuntu:ubuntu "$TARGET_DIR"
sudo chmod -R 755 "$TARGET_DIR"
echo "✅ 权限已设置"

# 3. 检查 Nginx 配置
echo ""
echo "3. 检查 Nginx 配置..."
NGINX_CONFIG="/etc/nginx/sites-available/50zf.usdt2026.cc"
if [ ! -f "$NGINX_CONFIG" ]; then
    NGINX_CONFIG="/etc/nginx/sites-available/wushizhifu"
fi

if [ -f "$NGINX_CONFIG" ]; then
    echo "找到 Nginx 配置文件: $NGINX_CONFIG"
    
    # 检查 root 路径
    CURRENT_ROOT=$(grep -E "^\s*root\s+" "$NGINX_CONFIG" | head -1 | sed 's/.*root\s*//;s/;.*//' | tr -d ';' | xargs)
    echo "当前 root 路径: $CURRENT_ROOT"
    echo "应该设置为: $TARGET_DIR"
    
    if [ "$CURRENT_ROOT" != "$TARGET_DIR" ]; then
        echo "🔧 更新 Nginx 配置..."
        sudo sed -i "s|root /.*/frontend/dist;|root $TARGET_DIR;|g" "$NGINX_CONFIG"
        sudo sed -i "s|root /.*/frontend;|root $TARGET_DIR;|g" "$NGINX_CONFIG"
        echo "✅ Nginx 配置已更新"
    else
        echo "✅ Nginx 配置正确"
    fi
    
    # 测试配置
    echo "测试 Nginx 配置..."
    if sudo nginx -t; then
        echo "✅ Nginx 配置测试通过"
        echo "🔄 重载 Nginx..."
        sudo systemctl reload nginx
        echo "✅ Nginx 已重载"
    else
        echo "❌ Nginx 配置测试失败"
        sudo nginx -t
        exit 1
    fi
else
    echo "❌ 错误: Nginx 配置文件不存在"
    echo "请检查: /etc/nginx/sites-available/50zf.usdt2026.cc 或 /etc/nginx/sites-available/wushizhifu"
    exit 1
fi

# 4. 验证文件
echo ""
echo "4. 验证文件..."
if [ -f "$TARGET_DIR/index.html" ]; then
    echo "✅ index.html 存在"
    ls -lh "$TARGET_DIR/index.html"
else
    echo "❌ 错误: index.html 不存在"
    echo "目录内容:"
    ls -la "$TARGET_DIR/" | head -10
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "📋 检查清单:"
echo "  ✅ 前端文件: $TARGET_DIR"
echo "  ✅ Nginx root: $TARGET_DIR"
echo "  ✅ 文件权限: 已设置"
echo ""
echo "🌐 访问: https://50zf.usdt2026.cc"
echo ""
echo "如果仍有问题，请检查:"
echo "  sudo tail -50 /var/log/nginx/error.log"

