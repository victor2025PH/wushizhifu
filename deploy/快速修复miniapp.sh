#!/bin/bash
# 快速修复 MiniApp 403 错误

echo "=========================================="
echo "🔧 快速修复 MiniApp 403 错误"
echo "=========================================="
echo ""

PROJECT_DIR="/home/ubuntu/wushizhifu"
MINIAPP_DIR="${PROJECT_DIR}/wushizhifu-full"
DIST_DIR="${MINIAPP_DIR}/dist"

# 检查是否有已构建的文件
if [ -d "${PROJECT_DIR}/frontend/dist" ] && [ -f "${PROJECT_DIR}/frontend/dist/index.html" ]; then
    echo "✅ 找到已构建的文件，正在复制..."
    sudo rm -rf "$DIST_DIR"
    sudo mkdir -p "$DIST_DIR"
    sudo cp -r "${PROJECT_DIR}/frontend/dist/"* "$DIST_DIR/" 2>/dev/null
    sudo chown -R www-data:www-data "$DIST_DIR"
    sudo chmod -R 755 "$DIST_DIR"
    echo "✅ 文件已复制并设置权限"
    
    if [ -f "$DIST_DIR/index.html" ]; then
        echo "✅ 修复成功！"
        sudo systemctl reload nginx
        echo "✅ Nginx 已重载"
        echo ""
        echo "请访问: https://50zf.usdt2026.cc"
        exit 0
    fi
fi

# 如果没有已构建的文件，重新构建
echo "📦 未找到已构建文件，开始重新构建..."
cd "$MINIAPP_DIR" || exit 1

if [ ! -f "package.json" ]; then
    echo "❌ 错误: 找不到 package.json"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📥 正在安装依赖..."
    npm install
fi

# 清理并构建
echo "🔨 正在构建..."
rm -rf dist
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi

# 检查构建结果
if [ ! -f "dist/index.html" ]; then
    echo "❌ 错误: index.html 不存在"
    exit 1
fi

# 设置权限
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist

# 重载 Nginx
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo "文件数量: $(find dist -type f | wc -l)"
echo "请访问: https://50zf.usdt2026.cc"
