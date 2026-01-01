#!/bin/bash

# 修复API 502错误

echo "🔍 诊断和修复API 502错误..."
echo ""

# 1. 检查API服务器状态
echo "📋 步骤1: 检查API服务器状态..."
if systemctl is-active --quiet wushipay-api; then
    echo "✅ API服务正在运行"
    sudo systemctl status wushipay-api --no-pager -l | head -15
else
    echo "❌ API服务未运行！"
    echo "   正在启动..."
    sudo systemctl start wushipay-api
    sleep 3
    if systemctl is-active --quiet wushipay-api; then
        echo "✅ API服务已启动"
    else
        echo "❌ API服务启动失败"
        echo "   查看日志："
        sudo journalctl -u wushipay-api -n 30 --no-pager
        exit 1
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
    echo "   API服务器可能未正确启动"
    exit 1
fi

# 3. 测试API本地访问
echo ""
echo "📋 步骤3: 测试API本地访问..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
    echo "✅ API本地访问正常 (HTTP $HTTP_CODE)"
else
    echo "❌ API本地访问失败 (HTTP $HTTP_CODE)"
    echo "   查看API日志："
    sudo journalctl -u wushipay-api -n 20 --no-pager
    exit 1
fi

# 4. 检查Nginx配置
echo ""
echo "📋 步骤4: 检查Nginx配置..."
NGINX_CONFIG="/etc/nginx/sites-available/wushizhifu"
if [ -f "$NGINX_CONFIG" ]; then
    echo "✅ Nginx配置文件存在"
    
    # 检查是否有/api/ location
    if grep -q "location /api/" "$NGINX_CONFIG"; then
        echo "✅ /api/ location配置存在"
        echo "   配置内容:"
        grep -A 10 "location /api/" "$NGINX_CONFIG" | head -12
    else
        echo "❌ /api/ location配置不存在！"
        echo "   正在添加..."
        
        # 在location /之前添加/api/ location
        sudo sed -i '/location \/ {/i\    # API代理\n    location /api/ {\n        proxy_pass http://127.0.0.1:8000;\n        proxy_http_version 1.1;\n        proxy_set_header Upgrade $http_upgrade;\n        proxy_set_header Connection '\''upgrade'\'';\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n        proxy_cache_bypass $http_upgrade;\n    }\n' "$NGINX_CONFIG"
        
        echo "✅ /api/ location已添加"
    fi
else
    echo "❌ Nginx配置文件不存在: $NGINX_CONFIG"
    exit 1
fi

# 5. 测试Nginx配置
echo ""
echo "📋 步骤5: 测试Nginx配置..."
if sudo nginx -t; then
    echo "✅ Nginx配置正确"
else
    echo "❌ Nginx配置错误"
    exit 1
fi

# 6. 重载Nginx
echo ""
echo "📋 步骤6: 重载Nginx..."
sudo systemctl reload nginx
sleep 2

# 7. 测试通过Nginx访问API
echo ""
echo "📋 步骤7: 测试通过Nginx访问API..."
NGINX_API_RESPONSE=$(curl -s -X POST http://localhost/api/customer-service/assign \
  -H "Host: 50zf.usdt2026.cc" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123456, "username": "test_user"}' \
  -w "\nHTTP状态码: %{http_code}\n" 2>/dev/null || echo "请求失败")

HTTP_CODE_NGINX=$(echo "$NGINX_API_RESPONSE" | tail -1 | grep -o "[0-9]\{3\}" || echo "000")

if [ "$HTTP_CODE_NGINX" = "200" ]; then
    echo "✅ 通过Nginx访问API正常 (HTTP 200)"
    echo "$NGINX_API_RESPONSE" | head -5
elif [ "$HTTP_CODE_NGINX" = "500" ]; then
    echo "⚠️ API返回500错误（可能是业务逻辑问题）"
    echo "$NGINX_API_RESPONSE"
elif [ "$HTTP_CODE_NGINX" = "502" ]; then
    echo "❌ 仍然返回502错误"
    echo "   检查Nginx错误日志："
    sudo tail -20 /var/log/nginx/error.log
    echo ""
    echo "   检查API服务器日志："
    sudo journalctl -u wushipay-api -n 30 --no-pager
else
    echo "⚠️ 通过Nginx访问API异常 (HTTP $HTTP_CODE_NGINX)"
    echo "$NGINX_API_RESPONSE"
fi

# 8. 检查Nginx错误日志
echo ""
echo "📋 步骤8: 检查Nginx错误日志..."
if [ -f "/var/log/nginx/error.log" ]; then
    echo "最近的错误（如果有）:"
    sudo tail -20 /var/log/nginx/error.log | grep -i "error\|502\|upstream" || echo "  无相关错误"
else
    echo "⚠️ Nginx错误日志文件不存在"
fi

echo ""
echo "✅ 诊断完成！"
