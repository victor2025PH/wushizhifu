#!/bin/bash

# 完整修复Nginx配置脚本

echo "🔧 开始完整修复Nginx配置..."
echo ""

SERVER_PATH="/home/ubuntu/wushizhifu"
WEB_DIST="${SERVER_PATH}/web/dist"
MINIAPP_DIST="${SERVER_PATH}/wushizhifu-full/dist"

# 1. 检查并创建5050配置
echo "📋 步骤1: 检查并创建5050配置..."
NGINX_5050="/etc/nginx/sites-available/web-5050"

if [ ! -f "$NGINX_5050" ]; then
    echo "   配置文件不存在，正在创建..."
fi

sudo tee "$NGINX_5050" > /dev/null <<EOF
# Nginx配置文件 - Web前端网站
# 域名: 5050.usdt2026.cc

server {
    listen 80;
    server_name 5050.usdt2026.cc;
    
    root ${WEB_DIST};
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

echo "✅ 5050配置已创建/更新"

# 2. 检查并创建50zf配置
echo ""
echo "📋 步骤2: 检查并创建50zf配置..."
NGINX_50ZF="/etc/nginx/sites-available/wushizhifu"

if [ ! -f "$NGINX_50ZF" ]; then
    echo "   配置文件不存在，正在创建..."
fi

sudo tee "$NGINX_50ZF" > /dev/null <<EOF
# Nginx配置文件 - MiniApp
# 域名: 50zf.usdt2026.cc

server {
    listen 80;
    server_name 50zf.usdt2026.cc;
    
    root ${MINIAPP_DIST};
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
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

echo "✅ 50zf配置已创建/更新"

# 3. 启用配置
echo ""
echo "📋 步骤3: 启用配置..."
sudo ln -sf "$NGINX_5050" /etc/nginx/sites-enabled/web-5050
sudo ln -sf "$NGINX_50ZF" /etc/nginx/sites-enabled/wushizhifu
echo "✅ 配置已启用"

# 4. 检查配置语法
echo ""
echo "📋 步骤4: 检查配置语法..."
if sudo nginx -t; then
    echo "✅ 配置语法正确"
else
    echo "❌ 配置语法错误！"
    exit 1
fi

# 5. 验证配置内容
echo ""
echo "📋 步骤5: 验证配置内容..."
echo "检查5050配置:"
ROOT_5050=$(sudo nginx -T 2>/dev/null | grep -A 15 "server_name 5050.usdt2026.cc" | grep "root" | head -1 | awk '{print $2}' | sed 's/;//')
if [ -n "$ROOT_5050" ]; then
    echo "  ✅ 找到root: $ROOT_5050"
else
    echo "  ❌ 未找到root配置"
    echo "  完整配置内容:"
    sudo nginx -T 2>/dev/null | grep -A 20 "server_name 5050.usdt2026.cc"
fi

echo ""
echo "检查50zf配置:"
ROOT_50ZF=$(sudo nginx -T 2>/dev/null | grep -A 15 "server_name 50zf.usdt2026.cc" | grep "root" | head -1 | awk '{print $2}' | sed 's/;//')
if [ -n "$ROOT_50ZF" ]; then
    echo "  ✅ 找到root: $ROOT_50ZF"
else
    echo "  ❌ 未找到root配置"
    echo "  完整配置内容:"
    sudo nginx -T 2>/dev/null | grep -A 20 "server_name 50zf.usdt2026.cc"
fi

# 6. 检查目录
echo ""
echo "📋 步骤6: 检查目录..."
if [ -d "$WEB_DIST" ]; then
    echo "  ✅ Web目录存在: $WEB_DIST"
    FILE_COUNT=$(find "$WEB_DIST" -type f 2>/dev/null | wc -l)
    echo "     文件数量: $FILE_COUNT"
else
    echo "  ⚠️ Web目录不存在: $WEB_DIST"
    sudo mkdir -p "$WEB_DIST"
    echo "     已创建目录（需要构建）"
fi

if [ -d "$MINIAPP_DIST" ]; then
    echo "  ✅ MiniApp目录存在: $MINIAPP_DIST"
    FILE_COUNT=$(find "$MINIAPP_DIST" -type f 2>/dev/null | wc -l)
    echo "     文件数量: $FILE_COUNT"
else
    echo "  ⚠️ MiniApp目录不存在: $MINIAPP_DIST"
    sudo mkdir -p "$MINIAPP_DIST"
    echo "     已创建目录（需要构建）"
fi

# 7. 重载Nginx
echo ""
echo "📋 步骤7: 重载Nginx..."
sudo systemctl reload nginx
sleep 2

# 8. 检查服务状态
echo ""
echo "📋 步骤8: 检查服务状态..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx服务运行正常"
else
    echo "❌ Nginx服务未运行！"
    sudo systemctl start nginx
fi

# 9. 检查端口监听
echo ""
echo "📋 步骤9: 检查端口监听..."
if sudo ss -tlnp | grep -q ":80 "; then
    echo "✅ 端口80正在监听"
    sudo ss -tlnp | grep ":80 "
else
    echo "❌ 端口80未监听！"
fi

# 10. 测试本地连接
echo ""
echo "📋 步骤10: 测试本地连接..."
echo "测试5050:"
HTTP_CODE_5050=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ -H "Host: 5050.usdt2026.cc" 2>/dev/null || echo "000")
if [ "$HTTP_CODE_5050" = "200" ] || [ "$HTTP_CODE_5050" = "301" ] || [ "$HTTP_CODE_5050" = "302" ]; then
    echo "  ✅ 5050本地连接成功 (HTTP $HTTP_CODE_5050)"
else
    echo "  ⚠️ 5050本地连接失败 (HTTP $HTTP_CODE_5050)"
fi

echo "测试50zf:"
HTTP_CODE_50ZF=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ -H "Host: 50zf.usdt2026.cc" 2>/dev/null || echo "000")
if [ "$HTTP_CODE_50ZF" = "200" ] || [ "$HTTP_CODE_50ZF" = "301" ] || [ "$HTTP_CODE_50ZF" = "302" ]; then
    echo "  ✅ 50zf本地连接成功 (HTTP $HTTP_CODE_50ZF)"
else
    echo "  ⚠️ 50zf本地连接失败 (HTTP $HTTP_CODE_50ZF)"
fi

echo ""
echo "✅ 配置修复完成！"
echo ""
echo "📋 总结:"
echo "  - 5050配置: $([ -f "$NGINX_5050" ] && echo '存在' || echo '不存在')"
echo "  - 50zf配置: $([ -f "$NGINX_50ZF" ] && echo '存在' || echo '不存在')"
echo "  - Nginx服务: $(systemctl is-active nginx && echo '运行中' || echo '未运行')"
echo "  - 端口80: $(sudo ss -tlnp | grep -q ':80 ' && echo '监听中' || echo '未监听')"
echo ""
echo "💡 如果外部访问仍然失败，请检查："
echo "  1. 云服务商安全组是否开放80/443端口"
echo "  2. DNS解析是否正确指向服务器IP"
echo "  3. 是否有其他防火墙规则阻止连接"
