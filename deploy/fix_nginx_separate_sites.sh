#!/bin/bash
# 彻底修复Nginx配置 - 确保50zf和5050指向不同的目录

echo "=========================================="
echo "🔧 修复Nginx配置 - 分离MiniApp和Web网站"
echo "=========================================="
echo ""

# 目录定义
MINIAPP_DIR="/home/ubuntu/wushizhifu/wushizhifu-full/dist"
WEB_DIR="/home/ubuntu/wushizhifu/web/dist"

# 配置文件
CONFIG_50ZF="/etc/nginx/sites-available/50zf.usdt2026.cc"
CONFIG_5050="/etc/nginx/sites-available/web-5050"
CONFIG_WUSHIZHIFU="/etc/nginx/sites-available/wushizhifu"

echo "1. 检查目录..."
if [ ! -d "$MINIAPP_DIR" ]; then
    echo "  ❌ MiniApp目录不存在: $MINIAPP_DIR"
    exit 1
fi
echo "  ✅ MiniApp目录: $MINIAPP_DIR"

if [ ! -d "$WEB_DIR" ]; then
    echo "  ❌ Web目录不存在: $WEB_DIR"
    exit 1
fi
echo "  ✅ Web目录: $WEB_DIR"

echo ""
echo "2. 检查现有配置..."

# 查找50zf的配置
FOUND_50ZF=""
if [ -f "$CONFIG_50ZF" ]; then
    FOUND_50ZF="$CONFIG_50ZF"
    echo "  ✅ 找到: $CONFIG_50ZF"
fi
if [ -f "$CONFIG_WUSHIZHIFU" ] && grep -q "50zf.usdt2026.cc" "$CONFIG_WUSHIZHIFU" 2>/dev/null; then
    FOUND_50ZF="$CONFIG_WUSHIZHIFU"
    echo "  ✅ 找到: $CONFIG_WUSHIZHIFU (包含50zf配置)"
fi

# 查找5050的配置
FOUND_5050=""
if [ -f "$CONFIG_5050" ]; then
    FOUND_5050="$CONFIG_5050"
    echo "  ✅ 找到: $CONFIG_5050"
fi

echo ""
echo "3. 创建/修复50zf.usdt2026.cc配置 (MiniApp)..."

# 创建50zf专用配置
sudo tee "$CONFIG_50ZF" > /dev/null <<EOF
# Nginx 配置文件 - MiniApp
# 域名: 50zf.usdt2026.cc

server {
    listen 80;
    server_name 50zf.usdt2026.cc;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 50zf.usdt2026.cc;
    
    # SSL证书（如果已配置）
    ssl_certificate /etc/letsencrypt/live/50zf.usdt2026.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/50zf.usdt2026.cc/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # MiniApp静态文件
    root $MINIAPP_DIR;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # API代理到Bot B的API服务器
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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

echo "  ✅ 已创建/更新: $CONFIG_50ZF"

echo ""
echo "4. 创建/修复5050.usdt2026.cc配置 (Web网站)..."

# 创建5050专用配置
sudo tee "$CONFIG_5050" > /dev/null <<EOF
# Nginx 配置文件 - Web前端网站
# 域名: 5050.usdt2026.cc

server {
    listen 80;
    server_name 5050.usdt2026.cc;
    
    # 如果SSL证书已配置，取消下面这行的注释以启用HTTPS重定向
    # return 301 https://\$server_name\$request_uri;
    
    # Web前端静态文件
    root $WEB_DIR;
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

# HTTPS配置（如果SSL证书已配置）
server {
    listen 443 ssl http2;
    server_name 5050.usdt2026.cc;
    
    # SSL证书（如果已配置）
    ssl_certificate /etc/letsencrypt/live/5050.usdt2026.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/5050.usdt2026.cc/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Web前端静态文件
    root $WEB_DIR;
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

echo "  ✅ 已创建/更新: $CONFIG_5050"

echo ""
echo "5. 启用站点..."

# 启用50zf
sudo ln -sf "$CONFIG_50ZF" /etc/nginx/sites-enabled/50zf.usdt2026.cc
echo "  ✅ 已启用: 50zf.usdt2026.cc"

# 启用5050
sudo ln -sf "$CONFIG_5050" /etc/nginx/sites-enabled/web-5050
echo "  ✅ 已启用: web-5050"

# 如果wushizhifu配置存在且包含50zf，可能需要禁用或重命名
if [ -f "$CONFIG_WUSHIZHIFU" ] && grep -q "50zf.usdt2026.cc" "$CONFIG_WUSHIZHIFU" 2>/dev/null; then
    echo ""
    echo "  ⚠️  发现旧的wushizhifu配置包含50zf，建议禁用："
    echo "     sudo rm /etc/nginx/sites-enabled/wushizhifu"
    echo "     或重命名配置文件以避免冲突"
fi

echo ""
echo "6. 测试Nginx配置..."
if sudo nginx -t; then
    echo "  ✅ Nginx配置测试通过"
    echo ""
    echo "7. 重载Nginx..."
    sudo systemctl reload nginx
    echo "  ✅ Nginx已重载"
else
    echo "  ❌ Nginx配置测试失败"
    echo "  请检查配置文件并修复错误"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 修复完成"
echo "=========================================="
echo ""
echo "📋 当前配置:"
echo "  50zf.usdt2026.cc (MiniApp): $MINIAPP_DIR"
echo "  5050.usdt2026.cc (Web): $WEB_DIR"
echo ""
echo "🧪 验证:"
echo "  访问 https://50zf.usdt2026.cc - 应该显示MiniApp"
echo "  访问 https://5050.usdt2026.cc - 应该显示Web网站"
echo ""
echo "📝 如果还有问题，检查："
echo "  sudo nginx -T | grep -A 5 'server_name 50zf'"
echo "  sudo nginx -T | grep -A 5 'server_name 5050'"
