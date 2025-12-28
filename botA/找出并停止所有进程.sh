#!/bin/bash
# 找出并详细显示所有 Bot 进程，然后停止它们

echo "🔍 找出所有 Bot 进程..."
echo "=========================================="
echo ""

# 1. 详细列出所有 Bot 进程
echo "1️⃣ 当前运行的所有 Bot 进程："
echo "----------------------------------------"
ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep

echo ""
echo "详细进程信息："
ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | while read line; do
    PID=$(echo $line | awk '{print $2}')
    USER=$(echo $line | awk '{print $1}')
    CMD=$(echo $line | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
    START=$(ps -p $PID -o lstart= 2>/dev/null || echo "N/A")
    echo "  PID: $PID | 用户: $USER | 启动时间: $START"
    echo "  命令: $CMD"
    echo ""
done

# 2. 获取所有 PID
PIDS=$(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "✅ 没有发现 Bot 进程"
    exit 0
fi

echo "2️⃣ 发现的进程 PID: $PIDS"
echo ""

# 3. 停止 systemd 服务
echo "3️⃣ 停止 systemd 服务..."
sudo systemctl stop wushizhifu-bot 2>/dev/null
sleep 2

# 4. 强制终止所有进程
echo "4️⃣ 强制终止所有 Bot 进程..."
for pid in $PIDS; do
    echo "  终止进程 PID: $pid"
    sudo kill -9 $pid 2>/dev/null
done

# 5. 更彻底的清理
echo ""
echo "5️⃣ 更彻底的清理..."
sudo pkill -9 -f bot.py
sudo pkill -9 -f "python.*wushizhifu.*bot"
sudo pkill -9 -f "python.*bot"

# 6. 清理 screen/tmux
echo "6️⃣ 清理 screen/tmux 会话..."
screen -ls 2>/dev/null | grep -E "bot|wushizhifu" | awk '{print $1}' | while read session; do
    echo "  终止 screen 会话: $session"
    screen -S "$session" -X quit 2>/dev/null
done

tmux ls 2>/dev/null | grep -E "bot|wushizhifu" | cut -d: -f1 | while read session; do
    echo "  终止 tmux 会话: $session"
    tmux kill-session -t "$session" 2>/dev/null
done

sleep 3

# 7. 最终确认
echo ""
echo "7️⃣ 最终确认..."
REMAINING=$(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo "   ✅ 所有 Bot 进程已停止"
else
    echo "   ⚠️ 仍有 $REMAINING 个进程在运行："
    ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep
    echo ""
    echo "   再次强制终止..."
    for pid in $(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | awk '{print $2}'); do
        echo "     强制终止 PID: $pid"
        sudo kill -9 $pid 2>/dev/null
    done
    sleep 2
fi

echo ""
echo "=========================================="
echo "✅ 清理完成"
echo ""
echo "当前 Bot 进程数: $(ps aux | grep -E 'bot\.py|python.*wushizhifu.*bot' | grep -v grep | wc -l)"

