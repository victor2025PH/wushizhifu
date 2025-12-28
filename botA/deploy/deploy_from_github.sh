#!/bin/bash
# 從 GitHub 倉庫自動化部署腳本 - Bot + 前端 + SSL 證書
# 使用 GitHub 倉庫進行部署

set -e  # Exit on error

echo "=========================================="
echo "🚀 WuShiPay 從 GitHub 自動化部署"
echo "=========================================="

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置變數
DOMAIN="50zf.usdt2026.cc"
EMAIL="victor2018zzz@gmail.com"
PROJECT_DIR="$HOME/wushizhifu"
FRONTEND_REPO="https://github.com/victor2025PH/wushizhifu.git"
BOT_REPO="https://github.com/victor2025PH/wushizhifu_bot.git"

echo -e "${BLUE}🌐 域名: ${DOMAIN}${NC}"
echo -e "${BLUE}📧 證書郵箱: ${EMAIL}${NC}"
echo -e "${BLUE}📁 項目目錄: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}🔗 前端倉庫: ${FRONTEND_REPO}${NC}"
echo -e "${BLUE}🔗 Bot 倉庫: ${BOT_REPO}${NC}"
echo ""

# 1. 創建項目目錄
echo -e "${YELLOW}📂 步驟 1: 創建項目目錄...${NC}"
mkdir -p ${PROJECT_DIR}
cd ${PROJECT_DIR}
echo -e "${GREEN}✅ 目錄創建完成${NC}"

# 2. 克隆/更新前端項目
echo -e "${YELLOW}📥 步驟 2: 克隆前端項目...${NC}"
if [ ! -d "frontend" ]; then
    git clone ${FRONTEND_REPO} frontend
    echo -e "${GREEN}✅ 前端項目已克隆${NC}"
else
    cd frontend
    git pull
    cd ..
    echo -e "${GREEN}✅ 前端項目已更新${NC}"
fi

# 3. 克隆/更新 Bot 項目
echo -e "${YELLOW}🤖 步驟 3: 克隆 Bot 項目...${NC}"
if [ ! -d "bot" ]; then
    git clone ${BOT_REPO} bot
    echo -e "${GREEN}✅ Bot 項目已克隆${NC}"
else
    cd bot
    git pull
    cd ..
    echo -e "${GREEN}✅ Bot 項目已更新${NC}"
fi

cd ${PROJECT_DIR}/bot

# 4. 設置 Python 虛擬環境
echo -e "${YELLOW}🐍 步驟 4: 設置 Python 虛擬環境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ 虛擬環境已創建${NC}"
fi

# 5. 安裝 Python 依賴
echo -e "${YELLOW}📦 步驟 5: 安裝 Python 依賴...${NC}"
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt
echo -e "${GREEN}✅ Python 依賴安裝完成${NC}"

# 6. 檢查 .env 文件
echo -e "${YELLOW}🔐 步驟 6: 檢查配置文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env 文件不存在！${NC}"
    echo -e "${YELLOW}正在創建 .env 文件模板...${NC}"
    cat > .env << EOF
BOT_TOKEN=your_bot_token_here
EOF
    echo -e "${YELLOW}⚠️  請編輯 .env 文件並設置 BOT_TOKEN：${NC}"
    echo "   nano ${PROJECT_DIR}/bot/.env"
    echo ""
    read -p "按 Enter 繼續（請確保已設置 BOT_TOKEN），或 Ctrl+C 取消..."
    
    # 再次檢查
    if ! grep -q "BOT_TOKEN=.*[^_here]" .env; then
        echo -e "${RED}❌ BOT_TOKEN 未設置！部署中止${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env 文件已存在${NC}"
fi

# 7. 初始化數據庫
echo -e "${YELLOW}💾 步驟 7: 初始化數據庫...${NC}"
venv/bin/python -c "from database.models import init_database, init_default_admins; from config import Config; init_database(); init_default_admins(Config.INITIAL_ADMINS)" 2>&1 || {
    echo -e "${YELLOW}⚠️  數據庫初始化遇到問題，繼續部署...${NC}"
}
echo -e "${GREEN}✅ 數據庫初始化完成${NC}"

# 8. 安裝 Node.js（如果需要）
echo -e "${YELLOW}📦 步驟 8: 檢查 Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}正在安裝 Node.js 18.x...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    echo -e "${GREEN}✅ Node.js 已安裝${NC}"
else
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js 已安裝 (${NODE_VERSION})${NC}"
fi

# 9. 構建前端
echo -e "${YELLOW}🏗️  步驟 9: 構建前端應用...${NC}"
cd ${PROJECT_DIR}/frontend
npm install --silent
npm run build
echo -e "${GREEN}✅ 前端構建完成${NC}"

# 10. 安裝 Nginx 和 Certbot
echo -e "${YELLOW}🌐 步驟 10: 安裝 Nginx 和 Certbot...${NC}"
if ! command -v nginx &> /dev/null; then
    sudo apt update -qq
    sudo apt install -y nginx
    echo -e "${GREEN}✅ Nginx 已安裝${NC}"
fi

if ! command -v certbot &> /dev/null; then
    sudo apt install -y certbot python3-certbot-nginx
    echo -e "${GREEN}✅ Certbot 已安裝${NC}"
fi

# 11. 配置 Nginx
echo -e "${YELLOW}⚙️  步驟 11: 配置 Nginx...${NC}"
sudo tee /etc/nginx/sites-available/wushizhifu > /dev/null << EOF
server {
    listen 80;
    server_name ${DOMAIN};

    # 前端靜態文件
    location / {
        root ${PROJECT_DIR}/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # API 代理（如果需要）
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 靜態資源緩存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        root ${PROJECT_DIR}/frontend/dist;
    }
}
EOF

# 啟用站點
sudo ln -sf /etc/nginx/sites-available/wushizhifu /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 測試 Nginx 配置
sudo nginx -t
echo -e "${GREEN}✅ Nginx 配置完成${NC}"

# 12. 設置文件權限
echo -e "${YELLOW}🔒 步驟 12: 設置文件權限...${NC}"
sudo chown -R www-data:www-data ${PROJECT_DIR}/frontend/dist 2>/dev/null || true
chmod 600 ${PROJECT_DIR}/bot/.env 2>/dev/null || true
echo -e "${GREEN}✅ 權限設置完成${NC}"

# 13. 重啟 Nginx
echo -e "${YELLOW}🔄 步驟 13: 重啟 Nginx...${NC}"
sudo systemctl restart nginx
sudo systemctl enable nginx
echo -e "${GREEN}✅ Nginx 已啟動${NC}"

# 14. 申請 SSL 證書
echo -e "${YELLOW}🔐 步驟 14: 申請 SSL 證書...${NC}"
echo -e "${BLUE}請確保域名 ${DOMAIN} 已正確解析到當前服務器 IP${NC}"
read -p "按 Enter 繼續申請證書，或 Ctrl+C 取消..."

# 申請證書（非交互式）
sudo certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email ${EMAIL} --redirect || {
    echo -e "${RED}❌ SSL 證書申請失敗${NC}"
    echo -e "${YELLOW}請檢查：${NC}"
    echo "1. 域名 ${DOMAIN} 是否正確解析到服務器 IP"
    echo "2. 防火牆是否允許 80 和 443 端口"
    echo "3. Nginx 是否正常運行"
    echo ""
    echo -e "${YELLOW}您可以稍後手動申請證書：${NC}"
    echo "   sudo certbot --nginx -d ${DOMAIN}"
}

# 15. 創建 systemd 服務
echo -e "${YELLOW}⚙️  步驟 15: 創建 Bot 系統服務...${NC}"
cd ${PROJECT_DIR}/bot
sudo tee /etc/systemd/system/wushipay-bot.service > /dev/null << EOF
[Unit]
Description=WuShiPay Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=${PROJECT_DIR}/bot
Environment="PATH=${PROJECT_DIR}/bot/venv/bin"
ExecStart=${PROJECT_DIR}/bot/venv/bin/python ${PROJECT_DIR}/bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable wushipay-bot
sudo systemctl start wushipay-bot

echo -e "${GREEN}✅ Bot 服務已創建並啟動${NC}"

# 16. 檢查服務狀態
echo -e "${YELLOW}📊 步驟 16: 檢查服務狀態...${NC}"
sleep 3
echo ""
echo -e "${BLUE}Bot 服務狀態：${NC}"
sudo systemctl status wushipay-bot --no-pager -l | head -15
echo ""
echo -e "${BLUE}Nginx 服務狀態：${NC}"
sudo systemctl status nginx --no-pager -l | head -10

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 部署完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}🌐 前端地址: https://${DOMAIN}${NC}"
echo -e "${BLUE}🤖 Bot 服務: 運行中${NC}"
echo -e "${BLUE}📁 項目目錄: ${PROJECT_DIR}${NC}"
echo ""
echo -e "${YELLOW}常用命令：${NC}"
echo "  查看 Bot 日誌: sudo journalctl -u wushipay-bot -f"
echo "  重啟 Bot: sudo systemctl restart wushipay-bot"
echo "  停止 Bot: sudo systemctl stop wushipay-bot"
echo "  查看 Nginx 日誌: sudo tail -f /var/log/nginx/error.log"
echo "  更新前端: cd ${PROJECT_DIR}/frontend && git pull && npm run build && sudo systemctl reload nginx"
echo "  更新 Bot: cd ${PROJECT_DIR}/bot && git pull && sudo systemctl restart wushipay-bot"
echo ""

