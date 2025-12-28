#!/bin/bash
# 更新并重启 AI 服务

echo "=========================================="
echo "🚀 更新并重启 AI 服务"
echo "=========================================="

# 进入项目目录
cd ~/wushizhifu/bot || exit 1

# 1. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull 失败"
    exit 1
fi

# 2. 清理 Python 缓存
echo "🧹 清理 Python 缓存..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# 3. 验证 .env 文件
echo "🔐 检查环境变量..."
if grep -q "OPENAI_API_KEY=" .env 2>/dev/null || grep -q "GEMINI_API_KEY=" .env 2>/dev/null; then
    echo "✅ 检测到 API 密钥配置"
else
    echo "⚠️  警告：未检测到 OPENAI_API_KEY 或 GEMINI_API_KEY"
fi

# 4. 重启 Bot 服务
echo "🔄 重启 Bot 服务..."
sudo systemctl restart wushizhifu-bot

# 5. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 6. 检查服务状态
echo "📊 检查服务状态..."
sudo systemctl status wushizhifu-bot --no-pager -l | head -20

echo ""
echo "=========================================="
echo "✅ 更新完成！"
echo "=========================================="
echo ""
echo "查看 AI 服务初始化日志："
echo "sudo journalctl -u wushizhifu-bot -n 50 | grep -i 'ai\|openai\|gemini\|initialized'"
echo ""
echo "查看实时日志："
echo "sudo journalctl -u wushizhifu-bot -f"
echo ""

