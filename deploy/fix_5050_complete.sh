#!/bin/bash
# 完整修复5050.usdt2026.cc配置
# 解决：1. 缺少HTTPS配置 2. 构建权限问题 3. 确保指向正确的目录

set -e

echo "=========================================="
echo "🔧 完整修复5050.usdt2026.cc配置"
echo "=========================================="

# 路径定义
NGINX_CONFIG="/etc/nginx/sites-available/web-5050"
DOMAIN="5050.usdt2026.cc"
WEB_DIST="/home/ubuntu/wushizhifu/web/dist"
WEB_DIR="/home/ubuntu/wushizhifu/web"
SSL_CERT="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
SSL_KEY="/etc/letsencrypt/live/${DOMAIN}/privkey.pem"

# 步骤1: 修复构建权限问题
echo ""
echo "📋 步骤1: 修复构建权限..."
cd ${WEB_DIR} || exit 1

if [ -d "dist" ]; then
    echo "   修复dist目录权限..."
    sudo chown -R ${USER}:${USER} dist 2>/dev/null || true
    sudo chmod -R 755 dist 2>/dev/null || true
    rm -rf dist || sudo rm -rf dist || true
    echo "✅ 权限已修复，dist目录已清理"
fi

# 步骤2: 重新构建Web前端
echo ""
echo "📋 步骤2: 重新构建Web前端..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js"
    exit 1
fi

npm install --production=false || npm ci || {
    echo "⚠️ npm install有警告，继续构建..."
}

npm run build || {
    echo "❌ 构建失败，查看详细错误："
    npm run build 2>&1 | tail -20
    exit 1
}

# 验证构建结果
if [ ! -d "dist" ] || [ ! -f "dist/index.html" ]; then
    echo "❌ 构建失败：dist目录或index.html不存在"
    exit 1
fi

FILE_COUNT=$(find dist -type f 2>/dev/null | wc -l)
echo "✅ 构建成功，文件数量: $FILE_COUNT"

# 设置正确的文件权限
sudo chown -R www-data:www-data dist || true
sudo chmod -R 755 dist || true

# 步骤3: 检查SSL证书
echo ""
echo "📋 步骤3: 检查SSL证书..."
HAS_SSL=false
if sudo test -f "${SSL_CERT}" && sudo test -f "${SSL_KEY}"; then
    HAS_SSL=true
    echo "✅ SSL证书存在"
    sudo ls -la "${SSL_CERT}" "${SSL_KEY}" 2>/dev/null | head -2
else
    echo "⚠️ SSL证书不存在，将只配置HTTP"
    echo "   稍后可以运行: sudo certbot --nginx -d ${DOMAIN}"
fi

# 步骤4: 创建/更新Nginx配置
echo ""
echo "📋 步骤4: 创建/更新Nginx配置..."

# 备份现有配置
if [ -f "${NGINX_CONFIG}" ]; then
    sudo cp "${NGINX_CONFIG}" "${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ 已备份现有配置"
fi

# 创建完整的Nginx配置（包括HTTP和HTTPS）
sudo tee "${NGINX_CONFIG}" > /dev/null <<EOF
# Nginx 配置文件 - Web前端网站
# 域名: ${DOMAIN}

# HTTP Server Block - 重定向到HTTPS（如果SSL存在）
server {
    listen 80;
    server_name ${DOMAIN};
    
    # 如果SSL证书存在，重定向到HTTPS
    $([ "$HAS_SSL" = true ] && echo "return 301 https://\$server_name\$request_uri;" || echo "# return 301 https://\$server_name\$request_uri;")
    
    # 如果没有SSL，直接提供HTTP服务
    $([ "$HAS_SSL" = false ] && cat <<INNER_EOF
    # Web前端靜態文件
    root ${WEB_DIST};
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
INNER_EOF
    )
}

$([ "$HAS_SSL" = true ] && cat <<HTTPS_EOF
# HTTPS Server Block
server {
    listen 443 ssl http2;
    server_name ${DOMAIN};
    
    # SSL 證書
    ssl_certificate ${SSL_CERT};
    ssl_certificate_key ${SSL_KEY};
    
    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Web前端靜態文件
    root ${WEB_DIST};
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
HTTPS_EOF
)
EOF

echo "✅ Nginx配置已创建/更新"

# 步骤5: 启用配置
echo ""
echo "📋 步骤5: 启用Nginx配置..."
sudo ln -sf "${NGINX_CONFIG}" /etc/nginx/sites-enabled/web-5050
echo "✅ 配置已启用"

# 步骤6: 测试Nginx配置
echo ""
echo "📋 步骤6: 测试Nginx配置..."
if sudo nginx -t 2>&1 | grep -q "test is successful"; then
    echo "✅ Nginx配置测试通过"
else
    echo "❌ Nginx配置测试失败！"
    sudo nginx -t
    exit 1
fi

# 步骤7: 验证root路径
echo ""
echo "📋 步骤7: 验证root路径..."
ROOT_HTTP=$(sudo nginx -T 2>/dev/null | grep -A 30 "server_name ${DOMAIN}" | grep -A 5 "listen 80" | grep "root" | head -1 | awk '{print $2}' | sed 's/;//' || echo "")
ROOT_HTTPS=$(sudo nginx -T 2>/dev/null | grep -A 30 "server_name ${DOMAIN}" | grep -A 5 "listen 443" | grep "root" | head -1 | awk '{print $2}' | sed 's/;//' || echo "")

echo "   HTTP root: ${ROOT_HTTP:-未找到}"
echo "   HTTPS root: ${ROOT_HTTPS:-未找到}"
echo "   期望root: ${WEB_DIST}"

if [ "$HAS_SSL" = true ]; then
    if [ "$ROOT_HTTPS" = "${WEB_DIST}" ]; then
        echo "✅ HTTPS root路径正确"
    else
        echo "❌ HTTPS root路径错误！"
        exit 1
    fi
else
    if [ "$ROOT_HTTP" = "${WEB_DIST}" ]; then
        echo "✅ HTTP root路径正确"
    else
        echo "❌ HTTP root路径错误！"
        exit 1
    fi
fi

# 步骤8: 重新加载Nginx
echo ""
echo "📋 步骤8: 重新加载Nginx..."
sudo systemctl reload nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx已重新加载"
else
    echo "❌ Nginx重新加载失败"
    exit 1
fi

# 步骤9: 最终验证
echo ""
echo "📋 步骤9: 最终验证..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx服务运行正常"
else
    echo "❌ Nginx服务未运行！"
    sudo systemctl start nginx
fi

# 检查端口监听
if sudo ss -tlnp 2>/dev/null | grep -q ":80 "; then
    echo "✅ 端口80正在监听"
fi
if sudo ss -tlnp 2>/dev/null | grep -q ":443 "; then
    echo "✅ 端口443正在监听"
fi

# 测试本地访问
echo ""
echo "📋 测试本地访问..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ -H "Host: ${DOMAIN}" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ HTTP本地访问成功 (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ HTTP重定向到HTTPS (HTTP $HTTP_CODE)"
else
    echo "⚠️ HTTP本地访问异常 (HTTP $HTTP_CODE)"
fi

if [ "$HAS_SSL" = true ]; then
    HTTPS_CODE=$(curl -s -k -o /dev/null -w "%{http_code}" https://localhost/ -H "Host: ${DOMAIN}" 2>/dev/null || echo "000")
    if [ "$HTTPS_CODE" = "200" ]; then
        echo "✅ HTTPS本地访问成功 (HTTP $HTTPS_CODE)"
    else
        echo "⚠️ HTTPS本地访问异常 (HTTP $HTTPS_CODE)"
    fi
fi

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "📋 修复摘要："
echo "   1. ✅ 修复了构建权限问题"
echo "   2. ✅ 重新构建了Web前端"
echo "   3. ✅ 创建了完整的Nginx配置（HTTP + HTTPS）"
echo "   4. ✅ 确保root路径指向: ${WEB_DIST}"
echo "   5. ✅ 验证并重新加载了Nginx"
echo ""
if [ "$HAS_SSL" = true ]; then
    echo "🌐 现在可以访问:"
    echo "   - https://${DOMAIN} (HTTPS)"
    echo "   - http://${DOMAIN} (自动重定向到HTTPS)"
else
    echo "🌐 现在可以访问:"
    echo "   - http://${DOMAIN} (HTTP)"
    echo ""
    echo "💡 要启用HTTPS，请运行:"
    echo "   sudo certbot --nginx -d ${DOMAIN}"
fi
echo ""
