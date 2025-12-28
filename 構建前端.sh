#!/bin/bash
# 前端構建腳本（自動處理權限）

set -e

echo "🔨 開始構建前端..."
cd ~/wushizhifu/frontend

# 步驟 1: 改變所有權為 ubuntu（讓構建可以刪除舊文件）
echo "📁 改變 dist 目錄所有權為 ubuntu..."
sudo chown -R ubuntu:ubuntu dist

# 步驟 2: 執行構建
echo ""
echo "🏗️  執行構建..."
npm run build

# 步驟 3: 恢復權限給 www-data
echo ""
echo "🔐 恢復權限給 www-data..."
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist

# 步驟 4: 重載 Nginx
echo ""
echo "🔄 重載 Nginx..."
sudo systemctl reload nginx

echo ""
echo "✅ 構建完成！"
echo "📋 構建文件列表："
ls -lh dist/ | head -10

