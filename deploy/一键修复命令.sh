#!/bin/bash
# 一键修复 MiniApp 403 错误 - 直接在服务器上执行

PROJECT_DIR="/home/ubuntu/wushizhifu"
MINIAPP_DIR="${PROJECT_DIR}/wushizhifu-full"
DIST_DIR="${MINIAPP_DIR}/dist"

echo "=========================================="
echo "🔧 修复 MiniApp 403 错误"
echo "=========================================="

# 方案 1: 检查是否有已构建的文件
if [ -d "${PROJECT_DIR}/frontend/dist" ] && [ -f "${PROJECT_DIR}/frontend/dist/index.html" ]; then
    echo "✅ 找到已构建的文件，正在复制..."
    sudo rm -rf "$DIST_DIR"
    sudo mkdir -p "$DIST_DIR"
    sudo cp -r "${PROJECT_DIR}/frontend/dist/"* "$DIST_DIR/"
    sudo chown -R www-data:www-data "$DIST_DIR"
    sudo chmod -R 755 "$DIST_DIR"
    sudo systemctl reload nginx
    echo "✅ 修复完成！"
    ls -la "$DIST_DIR/" | head -5
    exit 0
fi

# 方案 2: 重新构建
echo "📦 未找到已构建文件，开始重新构建..."
cd "$MINIAPP_DIR" || exit 1

if [ ! -f "package.json" ]; then
    echo "❌ 错误: 找不到 package.json"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    echo "📥 安装依赖..."
    npm install
fi

echo "🔨 构建项目..."
rm -rf dist
npm run build

if [ ! -f "dist/index.html" ]; then
    echo "❌ 构建失败"
    exit 1
fi

sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist
sudo nginx -t && sudo systemctl reload nginx

echo "✅ 修复完成！"
echo "文件数量: $(find dist -type f | wc -l)"
