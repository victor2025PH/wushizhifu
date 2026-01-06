#!/bin/bash
# 修复 MiniApp 403 错误 - 重新构建并部署

echo "=========================================="
echo "🔧 修复 MiniApp 403 错误"
echo "=========================================="
echo ""

# 项目目录
PROJECT_DIR="/home/ubuntu/wushizhifu"
MINIAPP_DIR="${PROJECT_DIR}/wushizhifu-full"
DIST_DIR="${MINIAPP_DIR}/dist"

echo "1. 检查项目目录..."
if [ ! -d "$MINIAPP_DIR" ]; then
    echo "❌ 错误: 找不到项目目录 $MINIAPP_DIR"
    exit 1
fi
echo "✅ 项目目录存在: $MINIAPP_DIR"

echo ""
echo "2. 检查是否有已构建的 dist 目录..."
if [ -d "${PROJECT_DIR}/frontend/dist" ] && [ -f "${PROJECT_DIR}/frontend/dist/index.html" ]; then
    echo "✅ 找到已构建的 dist: ${PROJECT_DIR}/frontend/dist"
    echo "   是否使用此目录? (y/n)"
    read -r USE_EXISTING
    if [ "$USE_EXISTING" = "y" ] || [ "$USE_EXISTING" = "Y" ]; then
        echo "   复制文件到目标目录..."
        sudo rm -rf "$DIST_DIR"
        sudo mkdir -p "$DIST_DIR"
        sudo cp -r "${PROJECT_DIR}/frontend/dist/"* "$DIST_DIR/"
        echo "✅ 文件已复制"
        sudo chown -R www-data:www-data "$DIST_DIR"
        sudo chmod -R 755 "$DIST_DIR"
        echo "✅ 权限已设置"
        echo ""
        echo "=========================================="
        echo "✅ 修复完成！"
        echo "=========================================="
        echo ""
        echo "请测试访问: https://50zf.usdt2026.cc"
        exit 0
    fi
fi

echo ""
echo "3. 进入项目目录并检查依赖..."
cd "$MINIAPP_DIR" || exit 1

if [ ! -f "package.json" ]; then
    echo "❌ 错误: 找不到 package.json"
    exit 1
fi

echo "✅ 找到 package.json"

echo ""
echo "4. 检查 Node.js 和 npm..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    echo "   安装 Node.js: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs"
    exit 1
fi

NODE_VERSION=$(node -v)
NPM_VERSION=$(npm -v)
echo "✅ Node.js: $NODE_VERSION"
echo "✅ npm: $NPM_VERSION"

echo ""
echo "5. 安装依赖（如果需要）..."
if [ ! -d "node_modules" ]; then
    echo "   正在安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ node_modules 已存在，跳过安装"
fi

echo ""
echo "6. 清理旧的构建文件..."
if [ -d "$DIST_DIR" ]; then
    sudo rm -rf "$DIST_DIR"
    echo "✅ 已清理旧文件"
fi

echo ""
echo "7. 构建项目..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi

echo ""
echo "8. 检查构建结果..."
if [ ! -d "$DIST_DIR" ]; then
    echo "❌ 错误: dist 目录未创建"
    exit 1
fi

if [ ! -f "$DIST_DIR/index.html" ]; then
    echo "❌ 错误: index.html 不存在"
    exit 1
fi

echo "✅ 构建成功"
echo "   文件数量: $(find "$DIST_DIR" -type f | wc -l)"
echo "   目录大小: $(du -sh "$DIST_DIR" | cut -f1)"

echo ""
echo "9. 设置文件权限..."
sudo chown -R www-data:www-data "$DIST_DIR"
sudo chmod -R 755 "$DIST_DIR"
echo "✅ 权限已设置"

echo ""
echo "10. 验证 Nginx 配置..."
if sudo nginx -t; then
    echo "✅ Nginx 配置正确"
else
    echo "❌ Nginx 配置有错误"
    exit 1
fi

echo ""
echo "11. 重载 Nginx..."
sudo systemctl reload nginx
echo "✅ Nginx 已重载"

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "📝 验证步骤:"
echo "  1. 访问 https://50zf.usdt2026.cc"
echo "  2. 应该能看到 MiniApp 界面"
echo ""
echo "📋 构建信息:"
echo "  项目目录: $MINIAPP_DIR"
echo "  构建目录: $DIST_DIR"
echo "  文件数量: $(find "$DIST_DIR" -type f | wc -l)"
echo "  目录大小: $(du -sh "$DIST_DIR" | cut -f1)"
