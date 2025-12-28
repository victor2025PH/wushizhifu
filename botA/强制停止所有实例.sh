#!/bin/bash
# 强制停止所有 Bot 实例

echo "🛑 强制停止所有 Bot 实例..."
echo ""

# 1. 停止 systemd 服务
echo "1. 停止 systemd 服务..."
sudo systemctl stop wushizhifu-bot 2>/dev/null
sleep 2

# 2. 列出所有 Bot 进程
echo "2. 列出所有 Bot 进程："
ps aux | grep -E "bot\.py|python.*wushizhifu.*bot|python.*bot" | grep -v grep

# 3. 强制终止所有相关进程
echo ""
echo "3. 强制终止所有 Bot 进程..."
sudo pkill -9 -f bot.py
sudo pkill -9 -f "python.*wushizhifu.*bot"
sudo pkill -9 -f "python.*bot"
sleep 3

# 4. 按 PID 逐个终止（更彻底）
for pid in $(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | awk '{print $2}'); do
    echo "   终止进程 PID: $pid"
    sudo kill -9 $pid 2>/dev/null
done
sleep 2

# 5. 终止 screen 会话中的 Bot
echo ""
echo "4. 检查并终止 screen 会话..."
for session in $(screen -ls 2>/dev/null | grep -E "bot|wushizhifu" | awk '{print $1}'); do
    echo "   终止 screen 会话: $session"
    screen -S "$session" -X quit 2>/dev/null
done

# 6. 终止 tmux 会话中的 Bot
echo ""
echo "5. 检查并终止 tmux 会话..."
for session in $(tmux ls 2>/dev/null | grep -E "bot|wushizhifu" | cut -d: -f1); do
    echo "   终止 tmux 会话: $session"
    tmux kill-session -t "$session" 2>/dev/null
done

# 7. 最终确认
echo ""
echo "6. 最终确认..."
REMAINING=$(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo "   ✅ 所有 Bot 实例已停止"
else
    echo "   ⚠️ 仍有 $REMAINING 个进程在运行："
    ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep
    echo ""
    echo "   强制终止剩余进程..."
    for pid in $(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep | awk '{print $2}'); do
        sudo kill -9 $pid 2>/dev/null
    done
    sleep 2
fi

echo ""
echo "✅ 停止操作完成"

