#!/bin/bash
# 手动部署 Miniapp - 在服务器上执行

set -e

echo "=========================================="
echo "🚀 手动部署 Miniapp (50zf.usdt2026.cc)"
echo "=========================================="
echo ""

PROJECT_DIR="$HOME/wushizhifu"
FRONTEND_DIR="$PROJECT_DIR/frontend"
REPO_DIR="$PROJECT_DIR/repo"

# 1. 拉取最新代码
echo "1. 拉取最新代码..."
cd "$PROJECT_DIR"
git stash || true
git pull origin main || {
    echo "⚠️  git pull 失败，如果目录不是 Git 仓库，将克隆..."
    if [ ! -d ".git" ]; then
        git clone https://github.com/victor2025PH/wushizhifu.git "$PROJECT_DIR/repo" || {
            echo "❌ Git 克隆失败"
            exit 1
        }
    fi
}

# 2. 确定源代码目录
echo ""
echo "2. 确定源代码目录..."
if [ -d "wushizhifu-full" ]; then
    SOURCE_DIR="wushizhifu-full"
elif [ -d "repo/wushizhifu-full" ]; then
    SOURCE_DIR="repo/wushizhifu-full"
else
    echo "❌ 错误: 找不到 wushizhifu-full 目录"
    echo "当前目录: $(pwd)"
    echo "目录内容:"
    ls -la | head -20
    exit 1
fi

echo "✅ 找到源代码目录: $SOURCE_DIR"
cd "$SOURCE_DIR"

# 3. 安装依赖
echo ""
echo "3. 安装依赖..."
npm install --production=false || {
    echo "⚠️  npm install 失败，尝试清理后重试..."
    rm -rf node_modules package-lock.json
    npm install --production=false
}

# 4. 构建项目
echo ""
echo "4. 构建项目..."
export NODE_OPTIONS="--max-old-space-size=3072"
npm run build || {
    echo "❌ 构建失败"
    exit 1
}

# 5. 检查构建结果
if [ ! -d "dist" ]; then
    echo "❌ dist 目录不存在"
    exit 1
fi

echo "✅ 构建完成"

# 6. 复制构建结果到部署目录
echo ""
echo "5. 复制构建结果到部署目录..."
TARGET_DIR="$FRONTEND_DIR/dist"

# 备份现有目录
if [ -d "$TARGET_DIR" ]; then
    echo "📦 备份现有目录..."
    BACKUP_DIR="${TARGET_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    mv "$TARGET_DIR" "$BACKUP_DIR" || rm -rf "$TARGET_DIR"
    echo "✅ 已备份到: $BACKUP_DIR"
fi

# 复制新构建的文件
echo "📋 复制构建结果..."
echo "源目录: $(pwd)/dist"
echo "目标目录: $TARGET_DIR"
mkdir -p "$(dirname "$TARGET_DIR")"
cp -r dist "$TARGET_DIR"
echo "✅ 文件复制完成"

# 7. 设置文件权限
echo ""
echo "6. 设置文件权限..."
sudo chown -R www-data:www-data "$TARGET_DIR" || sudo chown -R ubuntu:ubuntu "$TARGET_DIR"
sudo chmod -R 755 "$TARGET_DIR"
echo "✅ 权限设置完成"

# 8. 更新 Nginx 配置
echo ""
echo "7. 更新 Nginx 配置..."
NGINX_CONFIG="/etc/nginx/sites-available/50zf.usdt2026.cc"
if [ ! -f "$NGINX_CONFIG" ]; then
    NGINX_CONFIG="/etc/nginx/sites-available/wushizhifu"
fi

if [ -f "$NGINX_CONFIG" ]; then
    echo "找到 Nginx 配置: $NGINX_CONFIG"
    
    # 更新 root 路径
    CURRENT_ROOT=$(grep -E "^\s*root\s+" "$NGINX_CONFIG" | head -1 | sed 's/.*root\s*//;s/;.*//' | tr -d ';' | xargs)
    echo "当前 root: $CURRENT_ROOT"
    echo "目标 root: $TARGET_DIR"
    
    if [ "$CURRENT_ROOT" != "$TARGET_DIR" ]; then
        echo "🔧 更新 Nginx 配置中的 root 路径..."
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
    echo "⚠️  Nginx 配置文件不存在: $NGINX_CONFIG"
    echo "   请手动创建或检查配置文件位置"
fi

# 9. 验证部署
echo ""
echo "8. 验证部署..."
if [ -f "$TARGET_DIR/index.html" ]; then
    echo "✅ index.html 存在"
    ls -lh "$TARGET_DIR/index.html"
    
    # 检查文件内容（验证是否包含新代码）
    if grep -q "开通帐户" "$TARGET_DIR/index.html" 2>/dev/null || grep -q "openAccount" "$TARGET_DIR/index.html" 2>/dev/null; then
        echo "✅ 新代码已部署（找到'开通帐户'相关代码）"
    else
        echo "⚠️  警告: 可能未找到新代码标记，但文件已更新"
    fi
else
    echo "❌ 错误: index.html 不存在"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📋 部署信息:"
echo "  源代码目录: $SOURCE_DIR"
echo "  构建输出: $SOURCE_DIR/dist"
echo "  部署目录: $TARGET_DIR"
echo "  Nginx root: $TARGET_DIR"
echo ""
echo "🌐 访问: https://50zf.usdt2026.cc"
echo ""
echo "如果仍有问题，请检查:"
echo "  sudo tail -50 /var/log/nginx/error.log"
echo "  ls -la $TARGET_DIR/ | head -10"

