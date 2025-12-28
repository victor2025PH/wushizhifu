#!/bin/bash
# 服务器更新步骤 - 更新 Bot 功能完整化代码

echo "========================================="
echo "开始更新 Bot 功能完整化代码"
echo "========================================="

# 进入 Bot 目录
cd /home/ubuntu/wushizhifu/bot

# 1. 拉取最新代码
echo "1. 拉取最新代码..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ 拉取代码失败！"
    exit 1
fi

echo "✅ 代码拉取成功"

# 2. 清除 Python 缓存
echo ""
echo "2. 清除 Python 缓存..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -r {} + 2>/dev/null || true

echo "✅ 缓存清除完成"

# 3. 检查服务状态
echo ""
echo "3. 检查服务状态..."
sudo systemctl status wushizhifu-bot --no-pager | head -10

# 4. 重启服务
echo ""
echo "4. 重启 Bot 服务..."
sudo systemctl restart wushizhifu-bot

# 等待服务启动
sleep 3

# 5. 检查服务状态和日志
echo ""
echo "5. 检查服务状态..."
sudo systemctl status wushizhifu-bot --no-pager | head -15

echo ""
echo "6. 查看最近日志（查找菜单按钮设置）..."
sudo journalctl -u wushizhifu-bot -n 30 --no-pager | grep -E "(Menu button|Bot description|WuShiPay System Initialized)"

echo ""
echo "========================================="
echo "更新完成！"
echo "========================================="
echo ""
echo "请在 Telegram 中验证："
echo "1. 发送 /start 命令，查看按钮是否更新"
echo "2. 打开 Bot 个人资料页面，查看「打开应用」按钮"
echo "3. 在聊天界面顶部，查看「打开应用」按钮"
echo "4. 点击「支付宝」「微信支付」等按钮，应该是在 Bot 内部工作，不跳转 MiniApp"

