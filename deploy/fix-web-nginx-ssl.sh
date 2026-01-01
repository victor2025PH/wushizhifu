#!/bin/bash
# 修复Web Nginx配置 - 如果SSL证书不存在，禁用HTTPS配置

DOMAIN="5050.usdt2026.cc"
NGINX_CONFIG="/etc/nginx/sites-available/web-5050"
SSL_CERT="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
SSL_KEY="/etc/letsencrypt/live/${DOMAIN}/privkey.pem"

echo "🔍 检查SSL证书..."

if [ ! -f "$SSL_CERT" ] || [ ! -f "$SSL_KEY" ]; then
  echo "⚠️ SSL证书不存在，修复Nginx配置（禁用HTTPS块）..."
  
  # 创建临时配置文件（只包含HTTP块）
  sudo tee ${NGINX_CONFIG} > /dev/null <<'HTTP_CONFIG'
# Nginx 配置文件 - Web前端网站
# 域名: 5050.usdt2026.cc
# 注意: SSL证书未配置，只启用HTTP

server {
    listen 80;
    server_name 5050.usdt2026.cc;
    
    # Web前端靜態文件
    root /home/ubuntu/wushizhifu/web/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
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

# HTTPS配置已禁用 - 运行以下命令申请SSL证书后，certbot会自动配置HTTPS
# sudo certbot --nginx -d 5050.usdt2026.cc
HTTP_CONFIG
  
  echo "✅ 已创建仅HTTP的Nginx配置"
else
  echo "✅ SSL证书存在，保持当前配置"
fi

# 测试配置
echo "🧪 测试Nginx配置..."
if sudo nginx -t; then
  echo "✅ Nginx配置测试通过"
  sudo systemctl reload nginx
  echo "✅ Nginx已重载"
else
  echo "❌ Nginx配置测试失败"
  exit 1
fi
