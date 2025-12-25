#!/bin/bash
# 設置 GitHub 倉庫（將 Bot 代碼上傳到 GitHub）

set -e

PROJECT_DIR="/opt/wushizhifu"
BOT_DIR="${PROJECT_DIR}/bot"

echo "=========================================="
echo "📤 設置 GitHub 倉庫"
echo "=========================================="

cd ${BOT_DIR}

# 檢查是否已經是 Git 倉庫
if [ ! -d ".git" ]; then
    echo "初始化 Git 倉庫..."
    git init
    git branch -M main
    
    # 創建 .gitignore（如果不存在）
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# 環境變數
.env
.env.local

# 數據庫
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 系統文件
.DS_Store
Thumbs.db

# 日誌
*.log
logs/

# 備份文件
*.bak
backups/
*.backup

# 臨時文件
tmp/
temp/
*.tmp
EOF
    fi
    
    echo "✅ Git 倉庫已初始化"
fi

# 添加所有文件（除了 .env）
git add .
git reset .env 2>/dev/null || true

echo ""
echo "📋 當前變更："
git status

echo ""
echo "下一步操作："
echo "1. 在 GitHub 創建新倉庫（例如：wushizhifu-bot）"
echo "2. 添加遠程倉庫："
echo "   git remote add origin https://github.com/YOUR_USERNAME/wushizhifu-bot.git"
echo "3. 提交並推送："
echo "   git commit -m 'Initial commit: WuShiPay Bot'"
echo "   git push -u origin main"
echo ""
echo "或者如果要推送到現有倉庫："
echo "   git remote set-url origin <your-repo-url>"
echo "   git commit -m 'Update bot code'"
echo "   git push -u origin main"

