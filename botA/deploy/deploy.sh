#!/bin/bash
# WuShiPay Bot 部署腳本

set -e  # Exit on error

echo "=========================================="
echo "🚀 WuShiPay Bot 部署開始"
echo "=========================================="

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 檢查是否在正確的目錄
if [ ! -f "bot.py" ]; then
    echo -e "${RED}❌ 錯誤：請在項目根目錄執行此腳本${NC}"
    exit 1
fi

# 1. 檢查 Python 版本
echo -e "${YELLOW}📋 檢查 Python 版本...${NC}"
python3 --version || { echo -e "${RED}❌ Python 3 未安裝${NC}"; exit 1; }

# 2. 創建虛擬環境（如果不存在）
echo -e "${YELLOW}📦 設置虛擬環境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ 虛擬環境已創建${NC}"
fi

# 3. 激活虛擬環境並安裝依賴
echo -e "${YELLOW}📥 安裝 Python 依賴...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Python 依賴安裝完成${NC}"

# 4. 檢查 .env 文件
echo -e "${YELLOW}🔐 檢查配置文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在，請創建並設置 BOT_TOKEN${NC}"
    echo "BOT_TOKEN=your_bot_token_here" > .env
    echo -e "${RED}❌ 請編輯 .env 文件並設置正確的 BOT_TOKEN 後重新運行${NC}"
    exit 1
fi

# 5. 初始化數據庫
echo -e "${YELLOW}💾 初始化數據庫...${NC}"
python3 -c "from database.models import init_database; init_database()"
echo -e "${GREEN}✅ 數據庫初始化完成${NC}"

# 6. 創建 systemd 服務文件（可選）
echo -e "${YELLOW}⚙️  創建 systemd 服務配置...${NC}"
cat > wushipay-bot.service << EOF
[Unit]
Description=WuShiPay Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/python $(pwd)/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ systemd 服務文件已創建: wushipay-bot.service${NC}"
echo -e "${YELLOW}💡 要啟用服務，請運行：${NC}"
echo "   sudo cp wushipay-bot.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable wushipay-bot"
echo "   sudo systemctl start wushipay-bot"

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 部署腳本執行完成！"
echo "==========================================${NC}"
echo ""
echo "下一步："
echo "1. 確保 .env 文件中的 BOT_TOKEN 正確設置"
echo "2. 測試運行: source venv/bin/activate && python bot.py"
echo "3. 或使用 systemd 服務: sudo systemctl start wushipay-bot"

