#!/bin/bash
# 诊断并重新设置 Bot 启动项

echo "🔍 诊断 Bot 启动问题..."
echo "=========================================="
echo ""

# 1. 检查所有 systemd 服务文件
echo "1️⃣ 检查所有 Bot 相关的 systemd 服务文件："
echo "----------------------------------------"
sudo find /etc/systemd/system -name "*bot*" -o -name "*wushizhifu*" 2>/dev/null
echo ""

# 2. 检查所有服务
echo "2️⃣ 检查所有 Bot 相关的 systemd 服务："
echo "----------------------------------------"
systemctl list-units --all --type=service | grep -iE "bot|wushizhifu"
echo ""

# 3. 检查当前服务配置
echo "3️⃣ 检查当前服务配置："
echo "----------------------------------------"
if [ -f "/etc/systemd/system/wushizhifu-bot.service" ]; then
    echo "服务文件存在："
    cat /etc/systemd/system/wushizhifu-bot.service
else
    echo "❌ 服务文件不存在"
fi
echo ""

# 4. 检查是否有其他服务文件
echo "4️⃣ 检查是否有其他服务文件："
echo "----------------------------------------"
for service_file in /etc/systemd/system/*bot*.service /etc/systemd/system/*wushizhifu*.service; do
    if [ -f "$service_file" ]; then
        echo "发现服务文件: $service_file"
        cat "$service_file"
        echo ""
    fi
done

# 5. 检查是否有多个服务启动 Bot
echo "5️⃣ 检查是否有多个服务在运行："
echo "----------------------------------------"
systemctl list-units --type=service --state=running | grep -iE "bot|wushizhifu"
echo ""

# 6. 检查服务状态
echo "6️⃣ 检查 wushizhifu-bot 服务状态："
echo "----------------------------------------"
sudo systemctl status wushizhifu-bot --no-pager -l | head -30
echo ""

# 7. 检查进程树
echo "7️⃣ 检查进程树（查看进程父子关系）："
echo "----------------------------------------"
ps auxf | grep -E "bot\.py|python.*wushizhifu.*bot" | grep -v grep
echo ""

# 8. 检查是否有自动重启导致的问题
echo "8️⃣ 检查服务重启策略："
echo "----------------------------------------"
if [ -f "/etc/systemd/system/wushizhifu-bot.service" ]; then
    grep -E "Restart=|RestartSec=" /etc/systemd/system/wushizhifu-bot.service || echo "未找到重启策略配置"
fi
echo ""

echo "=========================================="
echo "📋 诊断完成"
echo "=========================================="

