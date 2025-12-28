#!/bin/bash
# 部署修复后的代码到服务器

echo "=========================================="
echo "开始部署修复后的代码"
echo "=========================================="

# 进入项目目录
cd ~/wushizhifu/bot || exit 1

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull 失败"
    exit 1
fi

# 清理 Python 缓存
echo "🧹 清理 Python 缓存..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# 重启 Bot 服务
echo "🔄 重启 Bot 服务..."
sudo systemctl restart wushizhifu-bot

# 等待服务启动
sleep 3

# 检查服务状态
echo "📊 检查服务状态..."
sudo systemctl status wushizhifu-bot --no-pager -l

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "查看实时日志："
echo "sudo journalctl -u wushizhifu-bot -f"
echo ""

