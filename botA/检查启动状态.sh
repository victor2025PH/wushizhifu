#!/bin/bash
# 检查 Bot 启动状态和功能初始化

echo "🔍 检查 Bot 启动状态..."
echo ""

# 1. 检查服务状态
echo "1️⃣ 检查服务状态:"
sudo systemctl status wushizhifu-bot --no-pager -l | head -15
echo ""

# 2. 检查是否有冲突错误
echo "2️⃣ 检查是否有冲突错误:"
if sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -q "TelegramConflictError"; then
    echo "   ❌ 仍然有冲突错误"
else
    echo "   ✅ 没有冲突错误"
fi
echo ""

# 3. 检查数据库初始化
echo "3️⃣ 检查数据库初始化:"
if sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -q "Database tables initialized successfully"; then
    echo "   ✅ 数据库初始化成功"
else
    echo "   ⚠️ 数据库初始化消息未找到"
fi
echo ""

# 4. 检查 Bot 命令设置
echo "4️⃣ 检查 Bot 命令设置:"
if sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -q "Bot commands set successfully"; then
    echo "   ✅ Bot 命令设置成功"
else
    echo "   ⚠️ Bot 命令设置消息未找到（可能仍在初始化中）"
fi
echo ""

# 5. 检查菜单按钮设置
echo "5️⃣ 检查菜单按钮设置:"
if sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -q "Menu button set"; then
    echo "   ✅ 菜单按钮设置成功"
    sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep "Menu button set"
else
    echo "   ⚠️ 菜单按钮设置消息未找到（可能仍在初始化中）"
fi
echo ""

# 6. 检查 Bot 描述设置
echo "6️⃣ 检查 Bot 描述设置:"
if sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -q "Bot description set successfully"; then
    echo "   ✅ Bot 描述设置成功"
else
    echo "   ⚠️ Bot 描述设置消息未找到（可能仍在初始化中或需要 BotFather 手动设置）"
fi
echo ""

# 7. 检查 Bot 启动完成消息
echo "7️⃣ 检查 Bot 启动完成:"
if sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -q "WuShiPay System Initialized Successfully"; then
    echo "   ✅ Bot 启动完成"
else
    echo "   ⚠️ Bot 启动完成消息未找到"
fi
echo ""

# 8. 显示最新日志（最后30行）
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 最新日志（最后30行）:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo journalctl -u wushizhifu-bot -n 30 --no-pager
echo ""

# 9. 检查是否有错误
echo "9️⃣ 检查最近的错误:"
ERRORS=$(sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -i "error\|failed\|exception" | tail -5)
if [ -z "$ERRORS" ]; then
    echo "   ✅ 没有发现错误"
else
    echo "   ⚠️ 发现以下错误:"
    echo "$ERRORS"
fi
echo ""

# 10. 检查进程
echo "🔟 检查运行中的进程:"
BOT_PROCESSES=$(ps aux | grep bot.py | grep -v grep)
if [ -z "$BOT_PROCESSES" ]; then
    echo "   ❌ 没有发现 bot.py 进程"
else
    echo "   ✅ 发现 bot.py 进程:"
    echo "$BOT_PROCESSES" | awk '{print "      PID:", $2, "| CPU:", $3"%", "| MEM:", $4"%"}'
fi

