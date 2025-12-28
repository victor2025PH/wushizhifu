#!/bin/bash
# 推送 Bot 代碼到 GitHub 的腳本

set -e

echo "=========================================="
echo "📤 推送代碼到 GitHub"
echo "=========================================="

# 檢查是否在 Git 倉庫中
if [ ! -d ".git" ]; then
    echo "初始化 Git 倉庫..."
    git init
    git branch -M main
    echo "✅ Git 倉庫已初始化"
fi

# 檢查 .gitignore 是否存在
if [ ! -f ".gitignore" ]; then
    echo "⚠️  未找到 .gitignore 文件"
fi

# 添加所有文件（.gitignore 會自動排除不應提交的文件）
echo "添加文件到 Git..."
git add .

# 顯示狀態
echo ""
echo "📋 準備提交的文件："
git status

echo ""
read -p "確認提交這些文件？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 1
fi

# 提交
echo "提交更改..."
git commit -m "Initial commit: WuShiPay Telegram Bot with full features" || {
    echo "⚠️  沒有新文件需要提交，或已提交"
}

# 檢查遠程倉庫
if git remote | grep -q "origin"; then
    REMOTE_URL=$(git remote get-url origin)
    echo "當前遠程倉庫: $REMOTE_URL"
    read -p "是否要推送到此倉庫？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "推送到 GitHub..."
        git push -u origin main
    else
        echo "請手動設置遠程倉庫："
        echo "  git remote set-url origin <your-repo-url>"
        echo "  git push -u origin main"
    fi
else
    echo "未設置遠程倉庫"
    echo ""
    echo "請執行以下命令設置遠程倉庫："
    echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "  git push -u origin main"
fi

echo ""
echo "✅ 完成！"

