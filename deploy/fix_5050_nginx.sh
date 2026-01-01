#!/bin/bash
# 修复5050.usdt2026.cc指向错误的目录问题
# 确保5050指向Web网站，而不是MiniApp

set -e

echo "🔍 诊断和修复5050.usdt2026.cc配置..."

# 路径定义
NGINX_CONFIG="/etc/nginx/sites-available/web-5050"
EXPECTED_ROOT="/home/ubuntu/wushizhifu/web/dist"
MINIAPP_ROOT="/home/ubuntu/wushizhifu/wushizhifu-full/dist"
DOMAIN="5050.usdt2026.cc"

# 1. 检查配置文件是否存在
echo "📋 步骤1: 检查Nginx配置..."
if [ ! -f "$NGINX_CONFIG" ]; then
    echo "❌ 配置文件不存在: $NGINX_CONFIG"
    echo "   创建新配置..."
    sudo tee "$NGINX_CONFIG" > /dev/null <<EOF
# Nginx 配置文件 - Web前端网站
# 域名: ${DOMAIN}

server {
    listen 80;
    server_name ${DOMAIN};
    
    # Web前端靜態文件
    root ${EXPECTED_ROOT};
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # API 代理（代理到后端API服务器）
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # 靜態資源緩存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip 壓縮
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
EOF
    echo "✅ 已创建新配置"
else
    echo "✅ 配置文件存在: $NGINX_CONFIG"
fi

# 2. 检查当前root路径
echo ""
echo "📋 步骤2: 检查当前root路径..."
CURRENT_ROOT=$(sudo nginx -T 2>/dev/null | grep -A 20 "server_name ${DOMAIN}" | grep "root" | head -1 | awk '{print $2}' | sed 's/;//' || echo "")

if [ -z "$CURRENT_ROOT" ]; then
    echo "⚠️ 无法从Nginx配置中读取root路径"
    echo "   检查配置文件内容:"
    sudo grep -A 5 "server_name ${DOMAIN}" "$NGINX_CONFIG" | head -10
else
    echo "   当前root: $CURRENT_ROOT"
    echo "   期望root: $EXPECTED_ROOT"
    
    if [ "$CURRENT_ROOT" = "$EXPECTED_ROOT" ]; then
        echo "✅ root路径正确"
    elif [ "$CURRENT_ROOT" = "$MINIAPP_ROOT" ]; then
        echo "❌ root路径错误！指向了MiniApp目录"
        echo "   修复中..."
        sudo sed -i "s|root ${MINIAPP_ROOT};|root ${EXPECTED_ROOT};|g" "$NGINX_CONFIG"
        sudo sed -i "s|root /opt/wushizhifu/frontend/dist;|root ${EXPECTED_ROOT};|g" "$NGINX_CONFIG"
        sudo sed -i "s|root.*wushizhifu-full/dist;|root ${EXPECTED_ROOT};|g" "$NGINX_CONFIG"
        echo "✅ 已修复root路径"
    else
        echo "⚠️ root路径不匹配，修复为正确路径..."
        sudo sed -i "s|root.*;|root ${EXPECTED_ROOT};|g" "$NGINX_CONFIG"
        echo "✅ 已更新root路径"
    fi
fi

# 3. 检查目录是否存在
echo ""
echo "📋 步骤3: 检查目录..."
if [ -d "$EXPECTED_ROOT" ]; then
    echo "✅ Web目录存在: $EXPECTED_ROOT"
    FILE_COUNT=$(find "$EXPECTED_ROOT" -type f 2>/dev/null | wc -l)
    echo "   文件数量: $FILE_COUNT"
    
    if [ "$FILE_COUNT" -lt 5 ]; then
        echo "⚠️ 警告: 文件数量过少，可能未构建"
    fi
    
    if [ ! -f "$EXPECTED_ROOT/index.html" ]; then
        echo "❌ index.html不存在！"
        echo "   需要重新构建Web前端"
    else
        echo "✅ index.html存在"
    fi
else
    echo "❌ Web目录不存在: $EXPECTED_ROOT"
    echo "   需要构建Web前端"
fi

# 4. 确保配置已启用
echo ""
echo "📋 步骤4: 启用配置..."
if [ ! -L "/etc/nginx/sites-enabled/web-5050" ]; then
    echo "   创建符号链接..."
    sudo ln -sf "$NGINX_CONFIG" /etc/nginx/sites-enabled/web-5050
    echo "✅ 配置已启用"
else
    echo "✅ 配置已启用"
fi

# 5. 测试Nginx配置
echo ""
echo "📋 步骤5: 测试Nginx配置..."
if sudo nginx -t 2>&1 | grep -q "test is successful"; then
    echo "✅ Nginx配置测试通过"
else
    echo "❌ Nginx配置测试失败！"
    sudo nginx -t
    exit 1
fi

# 6. 重新加载Nginx
echo ""
echo "📋 步骤6: 重新加载Nginx..."
sudo systemctl reload nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx已重新加载"
else
    echo "❌ Nginx重新加载失败"
    exit 1
fi

# 7. 验证修复结果
echo ""
echo "📋 步骤7: 验证修复结果..."
NEW_ROOT=$(sudo nginx -T 2>/dev/null | grep -A 20 "server_name ${DOMAIN}" | grep "root" | head -1 | awk '{print $2}' | sed 's/;//' || echo "")
if [ "$NEW_ROOT" = "$EXPECTED_ROOT" ]; then
    echo "✅ 修复成功！root路径已正确设置为: $NEW_ROOT"
else
    echo "⚠️ root路径可能仍未正确: $NEW_ROOT"
fi

# 8. 测试本地访问
echo ""
echo "📋 步骤8: 测试本地访问..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ -H "Host: ${DOMAIN}" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 本地访问成功 (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "⚠️ HTTP $HTTP_CODE - 被重定向（可能是HTTPS重定向）"
else
    echo "⚠️ 本地访问异常 (HTTP $HTTP_CODE)"
fi

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo "现在访问 https://${DOMAIN} 应该显示Web网站内容"
echo ""
echo "如果仍有问题，请检查："
echo "1. Web前端是否已构建: ls -la $EXPECTED_ROOT"
echo "2. Nginx配置: sudo nginx -T | grep -A 20 'server_name ${DOMAIN}'"
echo "3. 查看Nginx错误日志: sudo tail -f /var/log/nginx/error.log"
