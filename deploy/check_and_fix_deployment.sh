#!/bin/bash
# 检查和修复部署问题

echo "=========================================="
echo "🔍 检查部署配置"
echo "=========================================="
echo ""

# 检查Nginx配置
echo "1. 检查Nginx配置..."
echo ""

echo "📋 50zf.usdt2026.cc (MiniApp) 配置:"
sudo nginx -T 2>/dev/null | grep -A 20 "server_name 50zf.usdt2026.cc" | grep -E "(server_name|root|proxy_pass)" || echo "  未找到配置"

echo ""
echo "📋 5050.usdt2026.cc (Web网站) 配置:"
sudo nginx -T 2>/dev/null | grep -A 20 "server_name 5050.usdt2026.cc" | grep -E "(server_name|root)" || echo "  未找到配置"

echo ""
echo "2. 检查目录结构..."
echo ""

# 检查MiniApp目录
echo "📁 MiniApp (wushizhifu-full) 目录:"
if [ -d "/home/ubuntu/wushizhifu/wushizhifu-full/dist" ]; then
    echo "  ✅ /home/ubuntu/wushizhifu/wushizhifu-full/dist 存在"
    ls -lh /home/ubuntu/wushizhifu/wushizhifu-full/dist/ | head -5
elif [ -d "/opt/wushizhifu/frontend/dist" ]; then
    echo "  ✅ /opt/wushizhifu/frontend/dist 存在"
    ls -lh /opt/wushizhifu/frontend/dist/ | head -5
else
    echo "  ❌ 未找到MiniApp的dist目录"
fi

echo ""
# 检查Web目录
echo "📁 Web网站 (web) 目录:"
if [ -d "/home/ubuntu/wushizhifu/web/dist" ]; then
    echo "  ✅ /home/ubuntu/wushizhifu/web/dist 存在"
    ls -lh /home/ubuntu/wushizhifu/web/dist/ | head -5
else
    echo "  ❌ 未找到Web网站的dist目录"
fi

echo ""
echo "3. 检查客服账号..."
echo ""

DB_PATH="/home/ubuntu/wushizhifu/wushipay.db"
if [ -f "$DB_PATH" ]; then
    echo "📊 数据库中的客服账号:"
    sqlite3 "$DB_PATH" "SELECT id, username, display_name, is_active, status FROM customer_service_accounts ORDER BY id;" 2>/dev/null || echo "  无法读取数据库"
    
    echo ""
    echo "📊 当前分配策略:"
    sqlite3 "$DB_PATH" "SELECT value FROM settings WHERE key = 'customer_service_strategy';" 2>/dev/null || echo "  未设置（将使用默认值）"
else
    echo "  ❌ 数据库文件不存在: $DB_PATH"
fi

echo ""
echo "4. 检查API服务器..."
echo ""

if systemctl is-active --quiet api-server 2>/dev/null || systemctl is-active --quiet wushipay-api 2>/dev/null; then
    echo "  ✅ API服务器正在运行"
    
    # 测试API
    echo ""
    echo "🧪 测试客服分配API:"
    API_RESPONSE=$(curl -s -X POST http://localhost:8000/api/customer-service/assign \
      -H "Content-Type: application/json" \
      -d '{"user_id": 999999, "username": "test_user"}')
    
    if [ $? -eq 0 ]; then
        echo "  ✅ API响应: $API_RESPONSE"
    else
        echo "  ❌ API调用失败"
    fi
else
    echo "  ⚠️  API服务器未运行"
    echo "  启动命令: sudo systemctl start api-server 或 sudo systemctl start wushipay-api"
fi

echo ""
echo "=========================================="
echo "✅ 检查完成"
echo "=========================================="
echo ""
echo "📝 如果发现问题，请参考 FIX_DEPLOYMENT_ISSUES.md 进行修复"
