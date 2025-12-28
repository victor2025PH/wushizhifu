#!/bin/bash
# 诊断 Bot 错误和状态

echo "========================================="
echo "Bot 诊断工具"
echo "========================================="

# 1. 检查服务状态
echo ""
echo "1. 检查 wushizhifu-bot 服务状态："
echo "----------------------------------------"
sudo systemctl status wushizhifu-bot.service --no-pager -l | head -20

# 2. 检查进程
echo ""
echo "2. 检查 Bot 进程："
echo "----------------------------------------"
BOT_PROCS=$(ps aux | grep "wushizhifu/bot/bot.py" | grep -v grep)
if [ -z "$BOT_PROCS" ]; then
    echo "❌ 没有找到 Bot 进程！"
    echo "   检查所有 bot.py 进程："
    ps aux | grep "bot.py" | grep -v grep || echo "   无进程"
else
    echo "✅ 找到 Bot 进程："
    echo "$BOT_PROCS"
fi

# 3. 检查服务文件
echo ""
echo "3. 检查服务文件："
echo "----------------------------------------"
if [ -f /etc/systemd/system/wushizhifu-bot.service ]; then
    echo "✅ 服务文件存在"
    echo "   路径：/etc/systemd/system/wushizhifu-bot.service"
    echo "   内容预览："
    head -15 /etc/systemd/system/wushizhifu-bot.service
else
    echo "❌ 服务文件不存在！"
fi

# 4. 检查代码目录
echo ""
echo "4. 检查代码目录："
echo "----------------------------------------"
if [ -d /home/ubuntu/wushizhifu/bot ]; then
    echo "✅ 代码目录存在"
    echo "   路径：/home/ubuntu/wushizhifu/bot"
    echo "   bot.py 文件："
    ls -lh /home/ubuntu/wushizhifu/bot/bot.py 2>/dev/null || echo "   ❌ bot.py 不存在"
else
    echo "❌ 代码目录不存在！"
fi

# 5. 查看最近错误日志
echo ""
echo "5. 查看最近错误日志（最近 50 条）："
echo "----------------------------------------"
sudo journalctl -u wushizhifu-bot.service -n 50 --no-pager | grep -E "(ERROR|Error|Exception|Traceback|Failed|失败)" | tail -20

# 6. 查看启动日志
echo ""
echo "6. 查看启动日志（最近 30 条）："
echo "----------------------------------------"
sudo journalctl -u wushizhifu-bot.service -n 30 --no-pager | tail -20

# 7. 检查数据库文件
echo ""
echo "7. 检查数据库文件："
echo "----------------------------------------"
if [ -f /home/ubuntu/wushizhifu/bot/data/bot.db ]; then
    echo "✅ 数据库文件存在"
    ls -lh /home/ubuntu/wushizhifu/bot/data/bot.db
else
    echo "⚠️  数据库文件不存在（首次运行会创建）"
fi

# 8. 检查环境变量
echo ""
echo "8. 检查环境变量文件："
echo "----------------------------------------"
if [ -f /home/ubuntu/wushizhifu/bot/.env ]; then
    echo "✅ .env 文件存在"
    echo "   BOT_TOKEN 是否设置："
    grep -q "BOT_TOKEN" /home/ubuntu/wushizhifu/bot/.env && echo "   ✅ 已设置" || echo "   ❌ 未设置"
else
    echo "❌ .env 文件不存在！"
fi

# 9. 检查 Python 环境
echo ""
echo "9. 检查 Python 环境："
echo "----------------------------------------"
if [ -d /home/ubuntu/wushizhifu/bot/venv ]; then
    echo "✅ venv 目录存在"
    echo "   Python 版本："
    /home/ubuntu/wushizhifu/bot/venv/bin/python --version 2>/dev/null || echo "   ❌ 无法获取版本"
else
    echo "⚠️  venv 目录不存在"
fi

# 10. 尝试手动运行（测试）
echo ""
echo "========================================="
echo "建议的修复步骤"
echo "========================================="

if ! systemctl is-active --quiet wushizhifu-bot.service; then
    echo ""
    echo "⚠️  服务未运行，尝试启动："
    echo "   sudo systemctl start wushizhifu-bot.service"
    echo "   sudo systemctl status wushizhifu-bot.service"
fi

if [ -z "$BOT_PROCS" ]; then
    echo ""
    echo "⚠️  没有 Bot 进程，检查服务："
    echo "   sudo systemctl restart wushizhifu-bot.service"
    echo "   sudo journalctl -u wushizhifu-bot.service -f"
fi

echo ""
echo "========================================="
echo "诊断完成"
echo "========================================="

