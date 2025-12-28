#!/bin/bash
# 修復權限以便使用 WinSCP 替換 Logo

set -e

echo "🔧 修復權限以便使用 WinSCP 替換 Logo..."
cd ~/wushizhifu/frontend

# 改變所有權為 ubuntu（以便 WinSCP 操作）
echo "📁 改變 dist 和 public 目錄的所有權為 ubuntu..."
sudo chown -R ubuntu:ubuntu dist public

echo ""
echo "✅ 權限已修復！"
echo ""
echo "現在您可以使用 WinSCP："
echo "1. 連接到服務器"
echo "2. 導航到: /home/ubuntu/wushizhifu/frontend/public/"
echo "3. 上傳新的 logo_300.png 文件（覆蓋現有文件）"
echo ""
echo "上傳完成後，請執行："
echo "  cd ~/wushizhifu/frontend"
echo "  npm run build"
echo "  sudo chown -R www-data:www-data dist"
echo "  sudo chmod -R 755 dist"
echo "  sudo systemctl reload nginx"
echo ""
echo "或者執行: bash 修復權限並替換Logo_完成.sh"

