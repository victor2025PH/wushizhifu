#!/bin/bash
# 全面检查所有可能的 Bot 启动方式

echo "🔍 全面检查 Bot 启动项和运行实例..."
echo "=========================================="
echo ""

# 1. 检查当前运行的 Bot 进程
echo "1️⃣ 检查当前运行的 Bot 进程："
echo "----------------------------------------"
ps aux | grep -E "bot\.py|python.*wushizhifu.*bot|python.*bot" | grep -v grep
PROCESS_COUNT=$(ps aux | grep -E "bot\.py|python.*wushizhifu.*bot|python.*bot" | grep -v grep | wc -l)
echo ""
echo "   总计: $PROCESS_COUNT 个进程"
if [ "$PROCESS_COUNT" -gt 1 ]; then
    echo "   ⚠️ 警告：发现多个 Bot 进程！"
    echo "   详细信息："
    ps aux | grep -E "bot\.py|python.*wushizhifu.*bot|python.*bot" | grep -v grep | awk '{print "   PID:", $2, "| 启动命令:", $11, $12, $13, $14}'
else
    echo "   ✅ Bot 进程数量正常"
fi
echo ""

# 2. 检查 systemd 服务
echo "2️⃣ 检查 systemd 服务状态："
echo "----------------------------------------"
sudo systemctl status wushizhifu-bot --no-pager -l | head -15
echo ""
echo "   检查服务是否启用（开机自启）："
if systemctl is-enabled wushizhifu-bot > /dev/null 2>&1; then
    echo "   ✅ 服务已启用（开机自启）"
else
    echo "   ⚠️ 服务未启用（不会开机自启）"
fi
echo ""

# 3. 检查 systemd 服务文件
echo "3️⃣ 检查 systemd 服务文件："
echo "----------------------------------------"
if [ -f "/etc/systemd/system/wushizhifu-bot.service" ]; then
    echo "   ✅ 服务文件存在: /etc/systemd/system/wushizhifu-bot.service"
    echo "   文件内容："
    cat /etc/systemd/system/wushizhifu-bot.service | sed 's/^/   /'
else
    echo "   ❌ 服务文件不存在"
fi
echo ""

# 4. 检查是否有其他 systemd 服务
echo "4️⃣ 检查是否有其他 Bot 相关服务："
echo "----------------------------------------"
systemctl list-units --all --type=service | grep -i bot
echo ""

# 5. 检查 cron 任务
echo "5️⃣ 检查 cron 任务（可能定时启动 Bot）："
echo "----------------------------------------"
echo "   root 用户的 cron:"
sudo crontab -l 2>/dev/null | grep -i bot || echo "   (无)"
echo ""
echo "   ubuntu 用户的 cron:"
crontab -l 2>/dev/null | grep -i bot || echo "   (无)"
echo ""

# 6. 检查 /etc/cron.* 目录
echo "6️⃣ 检查系统 cron 任务："
echo "----------------------------------------"
for cron_dir in /etc/cron.daily /etc/cron.hourly /etc/cron.weekly /etc/cron.monthly /etc/cron.d; do
    if [ -d "$cron_dir" ]; then
        echo "   检查 $cron_dir:"
        grep -r -i bot "$cron_dir" 2>/dev/null | sed 's/^/      /' || echo "      (无)"
    fi
done
echo ""

# 7. 检查 screen 会话
echo "7️⃣ 检查 screen 会话（可能后台运行 Bot）："
echo "----------------------------------------"
SCREEN_COUNT=$(screen -ls 2>/dev/null | grep -c "bot\|wushizhifu" || echo "0")
if [ "$SCREEN_COUNT" -gt 0 ]; then
    echo "   ⚠️ 发现 screen 会话："
    screen -ls 2>/dev/null | grep -E "bot|wushizhifu" | sed 's/^/      /'
else
    echo "   ✅ 没有发现 screen 会话"
fi
echo ""

# 8. 检查 tmux 会话
echo "8️⃣ 检查 tmux 会话（可能后台运行 Bot）："
echo "----------------------------------------"
TMUX_COUNT=$(tmux ls 2>/dev/null | grep -c "bot\|wushizhifu" || echo "0")
if [ "$TMUX_COUNT" -gt 0 ]; then
    echo "   ⚠️ 发现 tmux 会话："
    tmux ls 2>/dev/null | grep -E "bot|wushizhifu" | sed 's/^/      /'
else
    echo "   ✅ 没有发现 tmux 会话"
fi
echo ""

# 9. 检查是否有其他用户运行 Bot
echo "9️⃣ 检查所有用户的 Bot 进程："
echo "----------------------------------------"
ps aux | grep -E "bot\.py|python.*wushizhifu.*bot|python.*bot" | grep -v grep | awk '{print "   用户:", $1, "| PID:", $2, "| 命令:", $11, $12, $13}'
echo ""

# 10. 检查启动脚本
echo "🔟 检查可能的启动脚本："
echo "----------------------------------------"
for script in ~/start_bot.sh ~/bot.sh ~/wushizhifu/start.sh ~/wushizhifu/bot/start.sh /home/ubuntu/*.sh; do
    if [ -f "$script" ] && grep -q "bot.py\|python.*bot" "$script" 2>/dev/null; then
        echo "   ⚠️ 发现启动脚本: $script"
        echo "   内容："
        head -20 "$script" | sed 's/^/      /'
    fi
done
echo ""

# 11. 检查 .bashrc, .profile 等启动文件
echo "1️⃣1️⃣ 检查 shell 启动文件："
echo "----------------------------------------"
for rc_file in ~/.bashrc ~/.bash_profile ~/.profile ~/.zshrc; do
    if [ -f "$rc_file" ] && grep -q -i "bot\|python.*wushizhifu" "$rc_file" 2>/dev/null; then
        echo "   ⚠️ 在 $rc_file 中发现 Bot 相关命令："
        grep -i "bot\|python.*wushizhifu" "$rc_file" | sed 's/^/      /'
    fi
done
echo ""

# 12. 检查是否有守护进程管理工具
echo "1️⃣2️⃣ 检查是否有 supervisord 或其他守护进程："
echo "----------------------------------------"
if command -v supervisorctl > /dev/null 2>&1; then
    echo "   ⚠️ 发现 supervisord："
    sudo supervisorctl status 2>/dev/null | grep -i bot || echo "      (无 Bot 配置)"
else
    echo "   ✅ 没有安装 supervisord"
fi
echo ""

# 13. 检查网络连接（查看是否有多个 Bot 连接到 Telegram）
echo "1️⃣3️⃣ 检查网络连接（Bot 到 Telegram API）："
echo "----------------------------------------"
echo "   连接到 api.telegram.org 的连接数："
netstat -an 2>/dev/null | grep -c "api.telegram.org.*ESTABLISHED" || ss -an 2>/dev/null | grep -c "api.telegram.org.*ESTAB"
echo ""

# 14. 检查代码版本
echo "1️⃣4️⃣ 检查代码版本（确认是否已更新）："
echo "----------------------------------------"
cd /home/ubuntu/wushizhifu/bot 2>/dev/null || exit 1
echo "   当前 git commit:"
git log -1 --oneline 2>/dev/null || echo "   (不是 git 仓库)"
echo ""
echo "   检查 keyboards/main_kb.py 中的 get_main_keyboard 函数签名："
if grep -q "def get_main_keyboard(user_id" keyboards/main_kb.py 2>/dev/null; then
    echo "   ✅ 函数签名已更新（包含 user_id 参数）"
    grep "def get_main_keyboard" keyboards/main_kb.py | sed 's/^/      /'
else
    echo "   ❌ 函数签名未更新（缺少 user_id 参数）"
    echo "   当前定义："
    grep "def get_main_keyboard" keyboards/main_kb.py | sed 's/^/      /'
fi
echo ""

# 15. 检查是否有备份或旧版本
echo "1️⃣5️⃣ 检查是否有多个 Bot 目录："
echo "----------------------------------------"
find /home/ubuntu -type d -name "*bot*" -o -name "*wushizhifu*" 2>/dev/null | head -10
echo ""

# 总结
echo "=========================================="
echo "📊 检查总结："
echo "=========================================="
echo ""
echo "当前运行的 Bot 进程数: $PROCESS_COUNT"
if [ "$PROCESS_COUNT" -gt 1 ]; then
    echo "❌ 发现多个 Bot 实例，这是导致 TelegramConflictError 的原因！"
    echo ""
    echo "建议操作："
    echo "1. 停止所有 Bot 进程："
    echo "   sudo systemctl stop wushizhifu-bot"
    echo "   sudo pkill -9 -f bot.py"
    echo "   sudo pkill -9 -f 'python.*wushizhifu.*bot'"
    echo ""
    echo "2. 检查并关闭 screen/tmux 会话："
    echo "   screen -ls"
    echo "   tmux ls"
    echo ""
    echo "3. 确保代码已更新到最新版本"
    echo "4. 重新启动服务："
    echo "   sudo systemctl daemon-reload"
    echo "   sudo systemctl start wushizhifu-bot"
else
    echo "✅ Bot 进程数量正常"
fi
echo ""

