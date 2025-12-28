#!/bin/bash
# 替換 Logo 完成後執行此腳本

set -e

echo "🏗️  重新構建前端..."
cd ~/wushizhifu/frontend

# 確認 logo 文件存在
if [ ! -f "public/logo_300.png" ]; then
    echo "❌ 錯誤：public/logo_300.png 不存在！"
    echo "請先使用 WinSCP 上傳文件到 public/ 目錄"
    exit 1
fi

echo "✅ Logo 文件存在: $(ls -lh public/logo_300.png | awk '{print $5, $9}')"

# 重新構建
echo ""
echo "🔨 開始構建..."
npm run build

# 檢查構建結果
echo ""
echo "📋 檢查構建結果..."
if [ -f "dist/logo_300.png" ]; then
    ls -lh dist/logo_300.png
    echo "✅ Logo 文件已構建到 dist 目錄"
else
    echo "⚠️  Logo 文件未自動複製，手動複製..."
    cp public/logo_300.png dist/logo_300.png
    ls -lh dist/logo_300.png
fi

# 恢復權限
echo ""
echo "🔐 恢復權限..."
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist

# 重載 Nginx
echo ""
echo "🔄 重載 Nginx..."
sudo systemctl reload nginx

echo ""
echo "✅ Logo 替換完成！"
echo "請刷新瀏覽器查看效果"

