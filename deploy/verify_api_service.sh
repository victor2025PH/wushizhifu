#!/bin/bash

# 验证API服务器和Nginx配置

echo "🔍 验证API服务器和Nginx配置..."
echo ""

# 1. 检查API服务器状态
echo "📋 步骤1: 检查API服务器状态..."
if systemctl is-active --quiet wushipay-api; then
    echo "✅ API服务正在运行"
    sudo systemctl status wushipay-api --no-pager -l | head -10
else
    echo "❌ API服务未运行！"
    echo "   正在启动..."
    sudo systemctl start wushipay-api
    sleep 2
    if systemctl is-active --quiet wushipay-api; then
        echo "✅ API服务已启动"
    else
        echo "❌ API服务启动失败"
        echo "   查看日志："
        sudo journalctl -u wushipay-api -n 20 --no-pager
    fi
fi

# 2. 检查端口8000监听
echo ""
echo "📋 步骤2: 检查端口8000监听..."
if sudo ss -tlnp | grep -q ":8000 "; then
    echo "✅ 端口8000正在监听"
    sudo ss -tlnp | grep ":8000 "
else
    echo "❌ 端口8000未监听"
fi

# 3. 测试API端点
echo ""
echo "📋 步骤3: 测试API端点..."
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null || echo "000")
if [ "$API_RESPONSE" = "200" ] || [ "$API_RESPONSE" = "404" ]; then
    echo "✅ API服务器响应正常 (HTTP $API_RESPONSE)"
else
    echo "⚠️ API服务器响应异常 (HTTP $API_RESPONSE)"
fi

# 4. 测试客服分配API
echo ""
echo "📋 步骤4: 测试客服分配API..."
CS_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/customer-service/assign \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123456, "username": "test_user"}' \
  -w "\nHTTP状态码: %{http_code}\n" 2>/dev/null || echo "请求失败")

if echo "$CS_RESPONSE" | grep -q "service_account"; then
    echo "✅ 客服分配API响应正常"
    echo "$CS_RESPONSE" | head -5
else
    echo "⚠️ 客服分配API响应异常"
    echo "$CS_RESPONSE"
fi

# 5. 检查Nginx配置
echo ""
echo "📋 步骤5: 检查Nginx配置..."
NGINX_CONFIG="/etc/nginx/sites-available/wushizhifu"
if [ -f "$NGINX_CONFIG" ]; then
    echo "✅ Nginx配置文件存在"
    
    # 检查是否有/api/ location
    if grep -q "location /api/" "$NGINX_CONFIG"; then
        echo "✅ /api/ location配置存在"
        echo "  配置内容:"
        grep -A 10 "location /api/" "$NGINX_CONFIG" | head -12
    else
        echo "❌ /api/ location配置不存在！"
        echo "   需要添加API代理配置"
    fi
else
    echo "❌ Nginx配置文件不存在: $NGINX_CONFIG"
fi

# 6. 测试通过Nginx访问API
echo ""
echo "📋 步骤6: 测试通过Nginx访问API..."
NGINX_API_RESPONSE=$(curl -s -X POST http://localhost/api/customer-service/assign \
  -H "Host: 50zf.usdt2026.cc" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123456, "username": "test_user"}' \
  -w "\nHTTP状态码: %{http_code}\n" 2>/dev/null || echo "请求失败")

if echo "$NGINX_API_RESPONSE" | grep -q "service_account"; then
    echo "✅ 通过Nginx访问API正常"
    echo "$NGINX_API_RESPONSE" | head -5
else
    echo "⚠️ 通过Nginx访问API异常"
    echo "$NGINX_API_RESPONSE"
fi

# 7. 检查Nginx错误日志
echo ""
echo "📋 步骤7: 检查最近的Nginx错误日志..."
if [ -f "/var/log/nginx/error.log" ]; then
    echo "最近的错误（如果有）:"
    sudo tail -10 /var/log/nginx/error.log | grep -i "error\|warn" || echo "  无错误"
else
    echo "⚠️ Nginx错误日志文件不存在"
fi

echo ""
echo "✅ 验证完成！"
