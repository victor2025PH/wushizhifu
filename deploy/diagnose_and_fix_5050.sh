#!/bin/bash

# 诊断和修复5050.usdt2026.cc连接问题

echo "🔍 开始诊断5050.usdt2026.cc连接问题..."
echo ""

# 1. 检查Nginx服务状态
echo "📋 步骤1: 检查Nginx服务状态..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx服务正在运行"
else
    echo "❌ Nginx服务未运行！"
    echo "   正在启动Nginx..."
    sudo systemctl start nginx
    sleep 2
    if systemctl is-active --quiet nginx; then
        echo "✅ Nginx已启动"
    else
        echo "❌ Nginx启动失败，查看错误："
        sudo systemctl status nginx --no-pager -l | head -20
        exit 1
    fi
fi

# 2. 检查Nginx配置语法
echo ""
echo "📋 步骤2: 检查Nginx配置语法..."
if sudo nginx -t 2>&1 | grep -q "syntax is ok"; then
    echo "✅ Nginx配置语法正确"
else
    echo "❌ Nginx配置语法错误！"
    sudo nginx -t
    exit 1
fi

# 3. 检查5050配置是否存在
echo ""
echo "📋 步骤3: 检查5050配置..."
NGINX_CONFIG="/etc/nginx/sites-available/web-5050"
if [ -f "$NGINX_CONFIG" ]; then
    echo "✅ 配置文件存在: $NGINX_CONFIG"
else
    echo "❌ 配置文件不存在: $NGINX_CONFIG"
    echo "   正在创建配置..."
    
    # 创建基本配置
    sudo tee "$NGINX_CONFIG" > /dev/null <<EOF
# Nginx配置文件 - Web前端网站
# 域名: 5050.usdt2026.cc

server {
    listen 80;
    server_name 5050.usdt2026.cc;
    
    root /home/ubuntu/wushizhifu/web/dist;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
EOF
    echo "✅ 配置已创建"
fi

# 4. 检查配置是否已启用
echo ""
echo "📋 步骤4: 检查配置是否已启用..."
if [ -L "/etc/nginx/sites-enabled/web-5050" ]; then
    echo "✅ 配置已启用"
else
    echo "⚠️ 配置未启用，正在启用..."
    sudo ln -sf "$NGINX_CONFIG" /etc/nginx/sites-enabled/web-5050
    echo "✅ 配置已启用"
fi

# 5. 验证root路径
echo ""
echo "📋 步骤5: 验证root路径..."
ROOT_5050=$(sudo nginx -T 2>/dev/null | grep -A 10 "server_name 5050.usdt2026.cc" | grep "root" | head -1 | awk '{print $2}' | sed 's/;//')
EXPECTED_ROOT="/home/ubuntu/wushizhifu/web/dist"

if [ -z "$ROOT_5050" ]; then
    echo "❌ 无法找到5050的root配置"
    exit 1
fi

echo "  当前root: $ROOT_5050"
echo "  期望root: $EXPECTED_ROOT"

if [ "$ROOT_5050" != "$EXPECTED_ROOT" ]; then
    echo "⚠️ root路径不正确，正在修复..."
    sudo sed -i "s|root .*;|root $EXPECTED_ROOT;|g" "$NGINX_CONFIG"
    echo "✅ root路径已修复"
fi

# 6. 检查目录是否存在
echo ""
echo "📋 步骤6: 检查目录是否存在..."
if [ -d "$EXPECTED_ROOT" ]; then
    echo "✅ 目录存在: $EXPECTED_ROOT"
    FILE_COUNT=$(find "$EXPECTED_ROOT" -type f | wc -l)
    echo "  文件数量: $FILE_COUNT"
    if [ "$FILE_COUNT" -eq 0 ]; then
        echo "⚠️ 目录为空！需要重新构建Web前端"
    fi
else
    echo "❌ 目录不存在: $EXPECTED_ROOT"
    echo "   正在创建目录..."
    sudo mkdir -p "$EXPECTED_ROOT"
    echo "✅ 目录已创建（但需要构建Web前端）"
fi

# 7. 检查端口监听
echo ""
echo "📋 步骤7: 检查端口监听..."
if sudo netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    echo "✅ 端口80正在监听"
    sudo netstat -tlnp 2>/dev/null | grep ":80 "
elif sudo ss -tlnp 2>/dev/null | grep -q ":80 "; then
    echo "✅ 端口80正在监听"
    sudo ss -tlnp 2>/dev/null | grep ":80 "
else
    echo "❌ 端口80未监听！"
    echo "   这可能是连接被拒绝的原因"
fi

# 8. 检查防火墙
echo ""
echo "📋 步骤8: 检查防火墙..."
if command -v ufw > /dev/null 2>&1; then
    if sudo ufw status | grep -q "Status: active"; then
        echo "⚠️ UFW防火墙已启用"
        if sudo ufw status | grep -q "80/tcp"; then
            echo "✅ 端口80已允许"
        else
            echo "⚠️ 端口80可能被阻止"
            echo "   运行: sudo ufw allow 80/tcp"
        fi
        if sudo ufw status | grep -q "443/tcp"; then
            echo "✅ 端口443已允许"
        else
            echo "⚠️ 端口443可能被阻止"
            echo "   运行: sudo ufw allow 443/tcp"
        fi
    else
        echo "✅ UFW防火墙未启用"
    fi
fi

# 9. 重载Nginx
echo ""
echo "📋 步骤9: 重载Nginx..."
if sudo nginx -t; then
    sudo systemctl reload nginx
    echo "✅ Nginx已重载"
else
    echo "❌ Nginx配置测试失败"
    exit 1
fi

# 10. 测试本地连接
echo ""
echo "📋 步骤10: 测试本地连接..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ -H "Host: 5050.usdt2026.cc" | grep -q "200\|301\|302"; then
    echo "✅ 本地连接测试成功"
else
    echo "⚠️ 本地连接测试失败"
    echo "   响应码: $(curl -s -o /dev/null -w "%{http_code}" http://localhost/ -H "Host: 5050.usdt2026.cc")"
fi

# 11. 检查DNS解析
echo ""
echo "📋 步骤11: 检查DNS解析..."
DNS_IP=$(dig +short 5050.usdt2026.cc @8.8.8.8 2>/dev/null | tail -1)
if [ -n "$DNS_IP" ]; then
    echo "✅ DNS解析成功: 5050.usdt2026.cc -> $DNS_IP"
    SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip)
    echo "   服务器IP: $SERVER_IP"
    if [ "$DNS_IP" = "$SERVER_IP" ]; then
        echo "✅ DNS指向正确的服务器"
    else
        echo "⚠️ DNS可能指向错误的IP"
    fi
else
    echo "⚠️ DNS解析失败"
fi

echo ""
echo "✅ 诊断完成！"
echo ""
echo "📋 总结："
echo "   - Nginx服务: $(systemctl is-active nginx && echo '运行中' || echo '未运行')"
echo "   - 配置文件: $([ -f "$NGINX_CONFIG" ] && echo '存在' || echo '不存在')"
echo "   - 配置启用: $([ -L "/etc/nginx/sites-enabled/web-5050" ] && echo '已启用' || echo '未启用')"
echo "   - Root路径: $ROOT_5050"
echo "   - 目录存在: $([ -d "$EXPECTED_ROOT" ] && echo '是' || echo '否')"
echo ""
echo "💡 如果问题仍然存在，请检查："
echo "   1. 云服务商的安全组/防火墙设置"
echo "   2. DNS解析是否正确"
echo "   3. Web前端是否已构建（运行: cd /home/ubuntu/wushizhifu/web && npm run build）"
