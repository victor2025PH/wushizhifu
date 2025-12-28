#!/bin/bash

echo "🔍 MiniApp 功能实现诊断"
echo "=========================="
echo ""

cd /home/ubuntu/wushizhifu/frontend || exit 1

# 1. 检查代码提交
echo "📋 1. 检查代码提交:"
LATEST_COMMIT=$(git log --oneline -1)
echo "   最新提交: $LATEST_COMMIT"
if echo "$LATEST_COMMIT" | grep -q "优化欢迎弹窗\|微信支付引导弹窗\|向下滑动提示"; then
    echo "   ✅ 包含最新优化提交"
else
    echo "   ⚠️  可能不是最新提交，建议: git pull origin main"
fi
echo ""

# 2. 检查关键文件
echo "📁 2. 检查关键文件:"
[ -f "components/WeChatGuideModal.tsx" ] && echo "   ✅ WeChatGuideModal.tsx" || echo "   ❌ WeChatGuideModal.tsx 不存在"
[ -f "components/Dashboard.tsx" ] && echo "   ✅ Dashboard.tsx" || echo "   ❌ Dashboard.tsx 不存在"
[ -f "components/WelcomeModal.tsx" ] && echo "   ✅ WelcomeModal.tsx" || echo "   ❌ WelcomeModal.tsx 不存在"
echo ""

# 3. 验证代码实现
echo "🔍 3. 验证代码实现:"

echo -n "   欢迎弹窗延时: "
if grep -q "setTimeout.*onClose.*1500" components/WelcomeModal.tsx; then
    echo "✅ 已设置为 1500ms"
else
    echo "❌ 未找到 1500ms 设置"
fi

echo -n "   微信弹窗导入: "
if grep -q "WeChatGuideModal" components/Dashboard.tsx; then
    echo "✅ 已导入"
else
    echo "❌ 未导入"
fi

echo -n "   向下滑动提示: "
if grep -q "showScrollHint\|向下滑动" components/Dashboard.tsx; then
    echo "✅ 已实现"
else
    echo "❌ 未实现"
fi

echo -n "   移除点击特效: "
if grep -q "active:scale" components/WelcomeModal.tsx components/Dashboard.tsx 2>/dev/null; then
    echo "⚠️  仍存在 active:scale（可能有遗漏）"
else
    echo "✅ 已移除"
fi
echo ""

# 4. 检查构建时间
echo "⏰ 4. 检查构建时间:"
if [ -f "dist/index.html" ]; then
    BUILD_TIME=$(stat -c %y dist/index.html 2>/dev/null || stat -f "%Sm" dist/index.html 2>/dev/null)
    echo "   构建时间: $BUILD_TIME"
    NOW=$(date +%s)
    BUILD_TS=$(stat -c %Y dist/index.html 2>/dev/null || stat -f "%m" dist/index.html 2>/dev/null)
    DIFF=$((NOW - BUILD_TS))
    if [ $DIFF -lt 3600 ]; then
        echo "   ✅ 构建时间在1小时内（可能是最新的）"
    else
        echo "   ⚠️  构建时间超过1小时，建议重新构建"
    fi
else
    echo "   ❌ dist/index.html 不存在，需要构建"
fi
echo ""

# 5. 检查文件权限
echo "🔐 5. 检查文件权限:"
if [ -d "dist" ]; then
    OWNER=$(stat -c %U dist/ 2>/dev/null || stat -f "%Su" dist/ 2>/dev/null)
    echo "   dist 目录所有者: $OWNER"
    if [ "$OWNER" = "www-data" ] || [ "$OWNER" = "ubuntu" ]; then
        echo "   ✅ 权限正常"
    else
        echo "   ⚠️  权限可能有问题，建议: sudo chown -R www-data:www-data dist/"
    fi
fi
echo ""

# 6. 检查构建产物中的代码
echo "📦 6. 检查构建产物:"
if [ -d "dist/assets" ]; then
    JS_FILES=$(find dist/assets -name "*.js" | head -1)
    if [ -n "$JS_FILES" ]; then
        if grep -q "WeChatGuideModal" "$JS_FILES" 2>/dev/null; then
            echo "   ✅ 构建产物中包含 WeChatGuideModal"
        else
            echo "   ⚠️  构建产物中未找到 WeChatGuideModal（可能需要重新构建）"
        fi
        
        if grep -q "1500" "$JS_FILES" 2>/dev/null | grep -q "setTimeout"; then
            echo "   ✅ 构建产物中包含 1500ms 延时"
        else
            echo "   ⚠️  构建产物中未找到 1500ms（可能需要重新构建）"
        fi
    else
        echo "   ⚠️  未找到 JS 文件"
    fi
else
    echo "   ❌ dist/assets 目录不存在"
fi
echo ""

# 7. 建议操作
echo "💡 7. 建议操作:"
echo ""
echo "   如果发现问题，执行以下命令重新部署:"
echo "   cd /home/ubuntu/wushizhifu/frontend && \\"
echo "   git pull origin main && \\"
echo "   sudo chown -R ubuntu:ubuntu dist/ && \\"
echo "   rm -rf dist/ && \\"
echo "   npm run build && \\"
echo "   sudo chown -R www-data:www-data dist/ && \\"
echo "   sudo systemctl reload nginx"
echo ""
echo "   然后清除浏览器缓存并强制刷新 (Ctrl+Shift+R)"

