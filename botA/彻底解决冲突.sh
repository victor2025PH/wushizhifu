#!/bin/bash
# 彻底解决 TelegramConflictError

set -e

echo "=========================================="
echo "🔍 彻底解决 TelegramConflictError"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE_NAME="wushizhifu-bot"
BOT_DIR="/home/ubuntu/wushizhifu/botA"

echo -e "${RED}⚠️  注意：此脚本将停止所有可能的 Bot 进程${NC}"
echo ""

# 1. 停止 systemd 服务
echo -e "${YELLOW}1️⃣  停止 systemd 服务...${NC}"
sudo systemctl stop ${SERVICE_NAME} 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ 服务已停止${NC}"

# 2. 查找并停止所有 bot.py 相关进程
echo ""
echo -e "${YELLOW}2️⃣  查找所有 bot.py 进程...${NC}"
BOT_PIDS=$(ps aux | grep -E "[b]ot.py|[p]ython.*bot\.py" | awk '{print $2}' || true)

if [ ! -z "$BOT_PIDS" ]; then
    echo "找到以下进程："
    ps aux | grep -E "[b]ot.py|[p]ython.*bot\.py" | grep -v grep || true
    echo ""
    for pid in $BOT_PIDS; do
        echo "停止进程 PID: $pid"
        kill -9 $pid 2>/dev/null || true
    done
    sleep 2
    echo -e "${GREEN}✅ 所有 bot.py 进程已停止${NC}"
else
    echo -e "${GREEN}✅ 没有找到 bot.py 进程${NC}"
fi

# 3. 查找并停止所有相关的 Python 进程
echo ""
echo -e "${YELLOW}3️⃣  查找所有相关 Python 进程...${NC}"
PYTHON_PIDS=$(ps aux | grep -E "[p]ython.*wushizhifu|[p]ython.*botA" | awk '{print $2}' || true)

if [ ! -z "$PYTHON_PIDS" ]; then
    echo "找到以下进程："
    ps aux | grep -E "[p]ython.*wushizhifu|[p]ython.*botA" | grep -v grep || true
    echo ""
    for pid in $PYTHON_PIDS; do
        echo "停止进程 PID: $pid"
        kill -9 $pid 2>/dev/null || true
    done
    sleep 2
    echo -e "${GREEN}✅ 相关 Python 进程已停止${NC}"
else
    echo -e "${GREEN}✅ 没有找到相关 Python 进程${NC}"
fi

# 4. 使用 pkill 强制停止（更彻底）
echo ""
echo -e "${YELLOW}4️⃣  使用 pkill 强制停止...${NC}"
pkill -9 -f "bot.py" 2>/dev/null || true
pkill -9 -f "botA/bot.py" 2>/dev/null || true
pkill -9 -f "wushizhifu.*bot" 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ pkill 执行完成${NC}"

# 5. 检查所有 systemd 服务
echo ""
echo -e "${YELLOW}5️⃣  检查所有 Bot 相关的 systemd 服务...${NC}"
ALL_SERVICES=$(systemctl list-units --all --type=service | grep -E "bot|wushi" | awk '{print $1}' || true)

if [ ! -z "$ALL_SERVICES" ]; then
    echo "找到以下服务："
    for service in $ALL_SERVICES; do
        echo "  - $service"
        if [ "$service" != "${SERVICE_NAME}.service" ]; then
            echo "    停止服务: $service"
            sudo systemctl stop "$service" 2>/dev/null || true
            sudo systemctl disable "$service" 2>/dev/null || true
        fi
    done
    echo -e "${GREEN}✅ 其他服务已停止${NC}"
else
    echo -e "${GREEN}✅ 没有找到其他相关服务${NC}"
fi

# 6. 最终验证 - 确保没有进程在运行
echo ""
echo -e "${YELLOW}6️⃣  最终验证 - 确保没有进程在运行...${NC}"
sleep 3

REMAINING=$(ps aux | grep -E "[b]ot.py|[p]ython.*bot\.py" | grep -v grep || true)
if [ -z "$REMAINING" ]; then
    echo -e "${GREEN}✅ 确认：没有 Bot 进程在运行${NC}"
else
    echo -e "${RED}❌ 仍有进程在运行：${NC}"
    echo "$REMAINING"
    echo ""
    echo "强制停止剩余进程..."
    for pid in $(echo "$REMAINING" | awk '{print $2}'); do
        kill -9 $pid 2>/dev/null || true
    done
    sleep 2
fi

# 7. 等待 Telegram API 清理（重要！）
echo ""
echo -e "${YELLOW}7️⃣  等待 Telegram API 清理连接（30秒）...${NC}"
echo "这是关键步骤：Telegram 服务器需要时间释放之前的连接"
echo "倒计时："
for i in {30..1}; do
    echo -ne "\r等待 $i 秒..."
    sleep 1
done
echo -e "\r${GREEN}✅ 等待完成${NC}"

# 8. 重新启动服务
echo ""
echo -e "${YELLOW}8️⃣  重新启动 Bot A 服务...${NC}"
sudo systemctl daemon-reload
sudo systemctl start ${SERVICE_NAME}
sleep 5

# 9. 检查服务状态
echo ""
echo -e "${YELLOW}9️⃣  检查服务状态...${NC}"
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✅ 服务运行正常${NC}"
    systemctl status ${SERVICE_NAME} --no-pager -l | head -15
else
    echo -e "${RED}❌ 服务未运行${NC}"
    sudo journalctl -u ${SERVICE_NAME} -n 20 --no-pager
    exit 1
fi

# 10. 等待并检查冲突错误
echo ""
echo -e "${YELLOW}🔟 等待并检查冲突错误（15秒）...${NC}"
sleep 15

CONFLICTS=$(sudo journalctl -u ${SERVICE_NAME} --since "20 seconds ago" --no-pager | grep -i "Conflict\|TelegramConflictError" || true)

if [ -z "$CONFLICTS" ]; then
    echo -e "${GREEN}✅ 没有发现冲突错误！${NC}"
    echo ""
    echo "查看最新日志："
    sudo journalctl -u ${SERVICE_NAME} -n 15 --no-pager | tail -10
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✅ 冲突已彻底解决！"
    echo "==========================================${NC}"
else
    echo -e "${RED}❌ 仍然存在冲突错误${NC}"
    echo "$CONFLICTS"
    echo ""
    echo -e "${YELLOW}可能的原因：${NC}"
    echo "1. 有另一个服务器或实例在使用同一个 Bot Token"
    echo "2. 有本地开发环境在运行"
    echo "3. 有其他进程在后台运行"
    echo ""
    echo -e "${YELLOW}请检查：${NC}"
    echo "1. 是否有其他服务器在使用这个 Bot Token？"
    echo "2. 本地是否有开发环境在运行？"
    echo "3. 运行以下命令查找："
    echo "   ps aux | grep bot.py"
    echo "   ps aux | grep python | grep wushizhifu"
    echo ""
    echo -e "${YELLOW}如果确认没有其他实例，可能需要：${NC}"
    echo "1. 在 Telegram Bot 设置中重置 Webhook（如果有）"
    echo "2. 联系 Telegram 支持（如果问题持续）"
fi

echo ""
echo -e "${BLUE}服务管理命令：${NC}"
echo "  查看状态: sudo systemctl status ${SERVICE_NAME}"
echo "  查看日志: sudo journalctl -u ${SERVICE_NAME} -f"
echo "  重启服务: sudo systemctl restart ${SERVICE_NAME}"
