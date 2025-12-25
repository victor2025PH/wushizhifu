#!/bin/bash
# 快速部署腳本 - 執行所有自動化步驟

set -e

echo "=========================================="
echo "🚀 WuShiPay 快速部署"
echo "=========================================="

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 獲取當前目錄（Bot 項目根目錄）
BOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
PROJECT_DIR="/opt/wushizhifu"

echo -e "${BLUE}📁 項目目錄: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}🤖 Bot 目錄: ${BOT_DIR}${NC}"
echo ""

# 1. 創建項目目錄結構
echo -e "${YELLOW}📂 步驟 1: 創建項目目錄結構...${NC}"
sudo mkdir -p ${PROJECT_DIR}
sudo chown $USER:$USER ${PROJECT_DIR}
cd ${PROJECT_DIR}

# 2. 克隆前端項目
if [ ! -d "frontend" ]; then
    echo -e "${YELLOW}📥 步驟 2: 克隆前端項目...${NC}"
    git clone https://github.com/victor2025PH/wushizhifu.git frontend
    echo -e "${GREEN}✅ 前端項目已克隆${NC}"
else
    echo -e "${YELLOW}⚠️  前端目錄已存在，跳過克隆${NC}"
fi

# 3. 設置 Bot 目錄
echo -e "${YELLOW}🤖 步驟 3: 設置 Bot 目錄...${NC}"
if [ ! -d "bot" ]; then
    mkdir -p bot
fi

# 複製 Bot 代碼（如果在當前目錄）
if [ -f "${BOT_DIR}/bot.py" ]; then
    echo -e "${YELLOW}📋 複製 Bot 代碼...${NC}"
    cp -r ${BOT_DIR}/* ${PROJECT_DIR}/bot/ 2>/dev/null || true
    # 排除不需要的文件
    rm -rf ${PROJECT_DIR}/bot/frontend 2>/dev/null || true
    rm -rf ${PROJECT_DIR}/bot/.git 2>/dev/null || true
    echo -e "${GREEN}✅ Bot 代碼已複製${NC}"
fi

cd ${PROJECT_DIR}/bot

# 4. 設置 Python 虛擬環境
echo -e "${YELLOW}🐍 步驟 4: 設置 Python 虛擬環境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ 虛擬環境已創建${NC}"
fi

# 5. 安裝依賴
echo -e "${YELLOW}📦 步驟 5: 安裝 Python 依賴...${NC}"
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt
echo -e "${GREEN}✅ 依賴安裝完成${NC}"

# 6. 檢查 .env 文件
echo -e "${YELLOW}🔐 步驟 6: 檢查配置文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}⚠️  .env 文件不存在！${NC}"
    echo "BOT_TOKEN=your_bot_token_here" > .env
    echo -e "${RED}❌ 請編輯 .env 文件並設置正確的 BOT_TOKEN${NC}"
    echo -e "${YELLOW}執行: nano .env${NC}"
    exit 1
fi

# 檢查 BOT_TOKEN 是否已設置
if grep -q "your_bot_token_here" .env 2>/dev/null || ! grep -q "BOT_TOKEN=" .env 2>/dev/null; then
    echo -e "${RED}⚠️  請確保 .env 文件中的 BOT_TOKEN 已正確設置${NC}"
    echo -e "${YELLOW}執行: nano .env${NC}"
    read -p "按 Enter 繼續（確保已設置 BOT_TOKEN）..."
fi

# 7. 初始化數據庫
echo -e "${YELLOW}💾 步驟 7: 初始化數據庫...${NC}"
python3 -c "from database.models import init_database; init_database()" 2>/dev/null || {
    echo -e "${YELLOW}嘗試使用 venv 中的 Python...${NC}"
    venv/bin/python -c "from database.models import init_database; init_database()"
}
echo -e "${GREEN}✅ 數據庫初始化完成${NC}"

# 8. 創建 systemd 服務文件
echo -e "${YELLOW}⚙️  步驟 8: 創建 systemd 服務配置...${NC}"
cat > wushipay-bot.service << EOF
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

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ systemd 服務文件已創建${NC}"

# 9. 測試運行（可選）
echo ""
echo -e "${BLUE}=========================================="
echo "✅ 自動化部署完成！"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}下一步操作：${NC}"
echo ""
echo "1. 確保 .env 文件中的 BOT_TOKEN 已正確設置："
echo "   ${BLUE}cd ${PROJECT_DIR}/bot${NC}"
echo "   ${BLUE}nano .env${NC}"
echo ""
echo "2. 測試運行 Bot（可選）："
echo "   ${BLUE}cd ${PROJECT_DIR}/bot${NC}"
echo "   ${BLUE}source venv/bin/activate${NC}"
echo "   ${BLUE}python bot.py${NC}"
echo ""
echo "3. 設置為系統服務："
echo "   ${BLUE}sudo cp ${PROJECT_DIR}/bot/wushipay-bot.service /etc/systemd/system/${NC}"
echo "   ${BLUE}sudo systemctl daemon-reload${NC}"
echo "   ${BLUE}sudo systemctl enable wushipay-bot${NC}"
echo "   ${BLUE}sudo systemctl start wushipay-bot${NC}"
echo "   ${BLUE}sudo systemctl status wushipay-bot${NC}"
echo ""
echo "4. 查看日誌："
echo "   ${BLUE}sudo journalctl -u wushipay-bot -f${NC}"
echo ""

