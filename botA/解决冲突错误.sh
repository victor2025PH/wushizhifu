#!/bin/bash
# 解决 TelegramConflictError - 查找并停止冲突的 Bot 进程

set -e

echo "=========================================="
echo "🔍 解决 TelegramConflictError"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

BOT_DIR="/home/ubuntu/wushizhifu/botA"
SERVICE_NAME="wushizhifu-bot"

echo -e "${BLUE}查找所有正在运行的 Bot 进程...${NC}"
echo ""

# 1. 查找所有运行 bot.py 的进程
echo -e "${YELLOW}1️⃣  查找 bot.py 进程...${NC}"
BOT_PROCESSES=$(ps aux | grep -E "[b]ot.py|[p]ython.*bot.py" | grep -v grep || true)

if [ -z "$BOT_PROCESSES" ]; then
    echo -e "${GREEN}✅ 没有找到运行中的 bot.py 进程${NC}"
else
    echo -e "${YELLOW}⚠️  找到以下 bot.py 进程：${NC}"
    echo "$BOT_PROCESSES"
    echo ""
    
    # 提取 PID
    PIDS=$(echo "$BOT_PROCESSES" | awk '{print $2}')
    for pid in $PIDS; do
        # 检查是否是 systemd 服务进程
        if systemctl is-active --quiet ${SERVICE_NAME} 2>/dev/null; then
            SERVICE_PID=$(systemctl show -p MainPID ${SERVICE_NAME} --value)
            if [ "$pid" = "$SERVICE_PID" ]; then
                echo -e "${GREEN}✅ PID $pid 是 systemd 服务进程（保留）${NC}"
                continue
            fi
        fi
        
        echo -e "${YELLOW}⚠️  发现非服务进程 PID: $pid${NC}"
        echo "进程详情："
        ps -fp $pid 2>/dev/null || echo "进程已结束"
        echo ""
    done
fi

# 2. 查找所有 Python 进程
echo -e "${YELLOW}2️⃣  查找所有 Python 进程...${NC}"
PYTHON_PROCESSES=$(ps aux | grep -E "[p]ython.*wushizhifu|[p]ython.*botA" | grep -v grep || true)

if [ -z "$PYTHON_PROCESSES" ]; then
    echo -e "${GREEN}✅ 没有找到相关的 Python 进程${NC}"
else
    echo -e "${YELLOW}⚠️  找到以下相关 Python 进程：${NC}"
    echo "$PYTHON_PROCESSES"
    echo ""
fi

# 3. 检查 systemd 服务状态
echo -e "${YELLOW}3️⃣  检查 systemd 服务状态...${NC}"
if systemctl is-active --quiet ${SERVICE_NAME}; then
    SERVICE_PID=$(systemctl show -p MainPID ${SERVICE_NAME} --value)
    echo -e "${GREEN}✅ ${SERVICE_NAME} 正在运行${NC}"
    echo "  服务 PID: $SERVICE_PID"
    ps -fp $SERVICE_PID 2>/dev/null | tail -1 || true
else
    echo -e "${RED}❌ ${SERVICE_NAME} 未运行${NC}"
fi

# 4. 查找其他可能的 systemd 服务
echo ""
echo -e "${YELLOW}4️⃣  查找其他 Bot 相关的 systemd 服务...${NC}"
OTHER_SERVICES=$(systemctl list-units --all | grep -E "bot|wushi" | grep -v ${SERVICE_NAME} || true)

if [ -z "$OTHER_SERVICES" ]; then
    echo -e "${GREEN}✅ 没有找到其他相关服务${NC}"
else
    echo -e "${YELLOW}⚠️  找到其他相关服务：${NC}"
    echo "$OTHER_SERVICES"
fi

# 5. 停止所有非服务进程
echo ""
echo -e "${YELLOW}5️⃣  停止冲突进程...${NC}"

# 停止所有 bot.py 进程（除了服务进程）
if [ ! -z "$BOT_PROCESSES" ]; then
    SERVICE_PID=""
    if systemctl is-active --quiet ${SERVICE_NAME} 2>/dev/null; then
        SERVICE_PID=$(systemctl show -p MainPID ${SERVICE_NAME} --value)
    fi
    
    PIDS=$(echo "$BOT_PROCESSES" | awk '{print $2}')
    STOPPED=0
    for pid in $PIDS; do
        if [ "$pid" != "$SERVICE_PID" ] && [ ! -z "$pid" ]; then
            echo "停止进程 PID: $pid"
            kill $pid 2>/dev/null || true
            STOPPED=1
        fi
    done
    
    if [ $STOPPED -eq 1 ]; then
        sleep 2
        echo -e "${GREEN}✅ 冲突进程已停止${NC}"
    else
        echo -e "${GREEN}✅ 没有需要停止的冲突进程${NC}"
    fi
else
    echo -e "${GREEN}✅ 没有冲突进程需要停止${NC}"
fi

# 6. 停止可能的其他 Python 进程
if [ ! -z "$PYTHON_PROCESSES" ]; then
    SERVICE_PID=""
    if systemctl is-active --quiet ${SERVICE_NAME} 2>/dev/null; then
        SERVICE_PID=$(systemctl show -p MainPID ${SERVICE_NAME} --value)
    fi
    
    PIDS=$(echo "$PYTHON_PROCESSES" | awk '{print $2}')
    for pid in $PIDS; do
        if [ "$pid" != "$SERVICE_PID" ] && [ ! -z "$pid" ]; then
            # 检查进程是否还在运行
            if ps -p $pid > /dev/null 2>&1; then
                echo "检查进程 PID: $pid"
                ps -fp $pid | grep -q bot.py && {
                    echo "停止可能的冲突进程 PID: $pid"
                    kill $pid 2>/dev/null || true
                }
            fi
        fi
    done
fi

# 7. 重启服务（确保使用正确的进程）
echo ""
echo -e "${YELLOW}6️⃣  重启 Bot A 服务...${NC}"
sudo systemctl restart ${SERVICE_NAME}
sleep 3

# 8. 检查服务状态
echo ""
echo -e "${YELLOW}7️⃣  检查服务状态...${NC}"
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✅ 服务运行正常${NC}"
    systemctl status ${SERVICE_NAME} --no-pager -l | head -15
else
    echo -e "${RED}❌ 服务未运行${NC}"
    sudo journalctl -u ${SERVICE_NAME} -n 20 --no-pager
fi

# 9. 等待几秒后检查日志
echo ""
echo -e "${YELLOW}8️⃣  检查冲突错误是否解决...${NC}"
sleep 5
ERRORS=$(sudo journalctl -u ${SERVICE_NAME} --since "10 seconds ago" --no-pager | grep -i "Conflict\|TelegramConflictError" || true)

if [ -z "$ERRORS" ]; then
    echo -e "${GREEN}✅ 没有发现冲突错误${NC}"
    echo ""
    echo "查看最新日志："
    sudo journalctl -u ${SERVICE_NAME} -n 10 --no-pager
else
    echo -e "${YELLOW}⚠️  仍然存在冲突错误${NC}"
    echo "$ERRORS"
    echo ""
    echo "可能的原因："
    echo "1. 有另一个服务器或实例在使用同一个 Bot Token"
    echo "2. 有其他进程在后台运行"
    echo ""
    echo "请运行以下命令查找："
    echo "  ps aux | grep bot.py"
    echo "  ps aux | grep python | grep wushizhifu"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 冲突处理完成"
echo "==========================================${NC}"

