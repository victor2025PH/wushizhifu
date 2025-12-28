#!/bin/bash
# 立即修复错误并查看正确日志

echo "========================================="
echo "修复错误并查看日志"
echo "========================================="

# 1. 确保使用正确的服务名
SERVICE_NAME="wushizhifu-bot.service"

echo ""
echo "1. 检查服务状态："
echo "----------------------------------------"
sudo systemctl status $SERVICE_NAME --no-pager | head -15

# 2. 查看实时日志（正确命令）
echo ""
echo "2. 查看实时日志（按 Ctrl+C 退出）："
echo "----------------------------------------"
echo "命令：sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "或者查看最近 50 条日志："
echo "命令：sudo journalctl -u $SERVICE_NAME -n 50 --no-pager"
echo ""

# 3. 查看错误日志
echo ""
echo "3. 查看错误日志："
echo "----------------------------------------"
sudo journalctl -u $SERVICE_NAME -n 100 --no-pager | grep -E "(ERROR|Error|Exception|Traceback|Failed|失败)" | tail -20

# 4. 查看最近完整日志
echo ""
echo "4. 查看最近 30 条完整日志："
echo "----------------------------------------"
sudo journalctl -u $SERVICE_NAME -n 30 --no-pager

echo ""
echo "========================================="
echo "正确的日志查看命令"
echo "========================================="
echo ""
echo "1. 实时查看日志（跟随最新）："
echo "   sudo journalctl -u wushizhifu-bot.service -f"
echo ""
echo "2. 查看最近 50 条："
echo "   sudo journalctl -u wushizhifu-bot.service -n 50 --no-pager"
echo ""
echo "3. 查看错误日志："
echo "   sudo journalctl -u wushizhifu-bot.service -n 100 --no-pager | grep -i error"
echo ""
echo "4. 查看今天的日志："
echo "   sudo journalctl -u wushizhifu-bot.service --since today --no-pager"
echo ""
echo "⚠️  注意：服务名是 'wushizhifu-bot'（不是 wushipay-bot）"

