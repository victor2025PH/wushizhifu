#!/bin/bash
# Bot B 更新部署腳本
# 用於從 GitHub 拉取最新代碼並重啟服務

set -e

echo "=========================================="
echo "🔄 Bot B 更新部署"
echo "=========================================="

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置變數
BOT_DIR="/home/ubuntu/wushizhifu/botB"
SERVICE_NAME="otc-bot.service"

echo -e "${BLUE}📁 Bot 目錄: ${BOT_DIR}${NC}"
echo -e "${BLUE}🔧 服務名稱: ${SERVICE_NAME}${NC}"
echo ""

# 檢查目錄是否存在
if [ ! -d "$BOT_DIR" ]; then
    echo -e "${RED}❌ 錯誤: Bot 目錄不存在: ${BOT_DIR}${NC}"
    echo -e "${YELLOW}💡 提示: 請先克隆倉庫或創建目錄${NC}"
    exit 1
fi

cd "$BOT_DIR"

# 1. 停止服務
echo -e "${YELLOW}⏹️  步驟 1: 停止服務...${NC}"
if systemctl is-active --quiet "$SERVICE_NAME"; then
    sudo systemctl stop "$SERVICE_NAME"
    echo -e "${GREEN}✅ 服務已停止${NC}"
else
    echo -e "${YELLOW}⚠️  服務未運行${NC}"
fi

# 2. 拉取最新代碼
echo -e "${YELLOW}📥 步驟 2: 拉取最新代碼...${NC}"
if [ -d ".git" ]; then
    git pull origin main
    echo -e "${GREEN}✅ 代碼已更新${NC}"
else
    echo -e "${YELLOW}⚠️  不是 Git 倉庫，跳過拉取${NC}"
    echo -e "${YELLOW}💡 提示: 如果是首次部署，請先克隆倉庫${NC}"
fi

# 3. 安裝/更新依賴
echo -e "${YELLOW}📦 步驟 3: 檢查依賴...${NC}"
if [ -f "requirements.txt" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
        echo -e "${GREEN}✅ 依賴已更新${NC}"
    else
        echo -e "${YELLOW}⚠️  虛擬環境不存在，創建中...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
        echo -e "${GREEN}✅ 虛擬環境已創建並安裝依賴${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  requirements.txt 不存在，跳過依賴安裝${NC}"
fi

# 4. 檢查服務文件
echo -e "${YELLOW}🔧 步驟 4: 檢查服務配置...${NC}"
if [ -f "$SERVICE_NAME" ]; then
    # 更新服務文件
    sudo cp "$SERVICE_NAME" "/etc/systemd/system/"
    sudo systemctl daemon-reload
    echo -e "${GREEN}✅ 服務配置已更新${NC}"
else
    echo -e "${YELLOW}⚠️  服務文件不存在: ${SERVICE_NAME}${NC}"
fi

# 5. 啟動服務
echo -e "${YELLOW}🚀 步驟 5: 啟動服務...${NC}"
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

# 等待服務啟動
sleep 3

# 6. 檢查服務狀態
echo -e "${YELLOW}📊 步驟 6: 檢查服務狀態...${NC}"
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ 服務運行正常${NC}"
    echo ""
    echo -e "${BLUE}📋 服務資訊:${NC}"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
    echo ""
    echo -e "${GREEN}🎉 部署完成！${NC}"
    echo ""
    echo -e "${BLUE}💡 常用命令:${NC}"
    echo -e "  查看日誌: ${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}"
    echo -e "  重啟服務: ${YELLOW}sudo systemctl restart $SERVICE_NAME${NC}"
    echo -e "  停止服務: ${YELLOW}sudo systemctl stop $SERVICE_NAME${NC}"
else
    echo -e "${RED}❌ 服務啟動失敗${NC}"
    echo ""
    echo -e "${YELLOW}📋 查看錯誤日誌:${NC}"
    sudo journalctl -u "$SERVICE_NAME" --no-pager -n 50
    exit 1
fi
