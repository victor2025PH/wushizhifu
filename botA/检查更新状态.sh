#!/bin/bash
# 检查本地和服务器文件更新状态

echo "🔍 检查文件更新状态..."
echo ""

# 1. 检查本地 message_service.py 是否有顶部边框
echo "1️⃣ 检查本地 message_service.py（顶部边框）:"
if grep -q "╔═" services/message_service.py 2>/dev/null; then
    echo "   ❌ 发现顶部边框代码（未更新）"
    grep -n "╔═" services/message_service.py
else
    echo "   ✅ 没有顶部边框代码（已更新）"
fi
echo ""

# 2. 检查本地是否有繁体中文
echo "2️⃣ 检查本地 message_service.py（繁体中文）:"
if grep -q "歡迎加入\|歡迎訪問\|為您提供\|生態系統\|專屬賬戶" services/message_service.py 2>/dev/null; then
    echo "   ❌ 发现繁体中文（未更新）"
    grep -n "歡迎加入\|歡迎訪問\|為您提供\|生態系統\|專屬賬戶" services/message_service.py | head -5
else
    echo "   ✅ 没有繁体中文（已更新）"
fi
echo ""

# 3. 检查本地是否有简体中文
echo "3️⃣ 检查本地 message_service.py（简体中文）:"
if grep -q "欢迎加入\|欢迎访问\|为您提供\|生态系统\|专属账户" services/message_service.py 2>/dev/null; then
    echo "   ✅ 发现简体中文（已更新）"
    grep -n "欢迎加入\|欢迎访问\|为您提供" services/message_service.py | head -3
else
    echo "   ❌ 没有简体中文（未更新）"
fi
echo ""

# 4. 显示关键代码段
echo "4️⃣ 显示欢迎消息代码段（第65-95行）:"
sed -n '65,95p' services/message_service.py
echo ""

# 5. 检查 Git 状态
echo "5️⃣ 检查 Git 状态:"
git status --short services/message_service.py
echo ""

# 6. 检查最近的提交
echo "6️⃣ 检查最近的提交（message_service.py）:"
git log --oneline -5 -- services/message_service.py
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 检查完成！"
echo ""
echo "如果本地文件已更新但服务器没有更新，请在服务器上执行："
echo "  cd /home/ubuntu/wushizhifu/bot"
echo "  git pull origin main"
echo "  grep -n '╔═' services/message_service.py  # 应该没有输出"
echo "  grep -n '欢迎加入' services/message_service.py  # 应该有输出"
echo "  sudo systemctl restart wushizhifu-bot"

