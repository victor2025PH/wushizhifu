#!/bin/bash
# 检查并清除可能冲突的 Webhook

set -e

echo "=========================================="
echo "🔍 检查并清除 Webhook"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 从 .env 读取 BOT_TOKEN
ENV_FILE="/home/ubuntu/wushizhifu/.env"
if [ -f "$ENV_FILE" ]; then
    BOT_TOKEN=$(grep "^BOT_TOKEN=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'" || true)
else
    echo -e "${RED}❌ 找不到 .env 文件${NC}"
    exit 1
fi

if [ -z "$BOT_TOKEN" ]; then
    echo -e "${RED}❌ BOT_TOKEN 未设置${NC}"
    exit 1
fi

echo -e "${BLUE}Bot Token: ${BOT_TOKEN:0:10}...${NC}"
echo ""

# 1. 检查当前 Webhook 信息
echo -e "${YELLOW}1️⃣  检查当前 Webhook 信息...${NC}"
WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")
echo "$WEBHOOK_INFO" | python3 -m json.tool 2>/dev/null || echo "$WEBHOOK_INFO"
echo ""

# 检查是否有 Webhook URL
WEBHOOK_URL=$(echo "$WEBHOOK_INFO" | grep -o '"url":"[^"]*"' | cut -d'"' -f4 || true)

if [ ! -z "$WEBHOOK_URL" ] && [ "$WEBHOOK_URL" != "null" ]; then
    echo -e "${YELLOW}⚠️  发现 Webhook URL: ${WEBHOOK_URL}${NC}"
    echo "这可能导致冲突，因为 Webhook 和 Polling 不能同时使用"
    echo ""
    
    # 2. 删除 Webhook
    echo -e "${YELLOW}2️⃣  删除 Webhook...${NC}"
    DELETE_RESULT=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook?drop_pending_updates=true")
    echo "$DELETE_RESULT" | python3 -m json.tool 2>/dev/null || echo "$DELETE_RESULT"
    echo ""
    
    # 验证删除
    sleep 2
    VERIFY_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")
    VERIFY_URL=$(echo "$VERIFY_INFO" | grep -o '"url":"[^"]*"' | cut -d'"' -f4 || true)
    
    if [ -z "$VERIFY_URL" ] || [ "$VERIFY_URL" = "null" ] || [ "$VERIFY_URL" = "" ]; then
        echo -e "${GREEN}✅ Webhook 已成功删除${NC}"
    else
        echo -e "${YELLOW}⚠️  Webhook 可能仍然存在${NC}"
    fi
else
    echo -e "${GREEN}✅ 没有发现 Webhook（这是正常的，使用 Polling 模式）${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Webhook 检查完成"
echo "=========================================="
echo ""
echo -e "${BLUE}下一步：${NC}"
echo "1. 等待 10-15 秒让 Telegram API 完全释放连接"
echo "2. 重启 Bot A 服务："
echo "   sudo systemctl restart wushizhifu-bot"
echo "3. 查看日志确认冲突是否解决："
echo "   sudo journalctl -u wushizhifu-bot -f"

