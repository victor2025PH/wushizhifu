# 快速修复Nginx配置（服务器上执行）

## 问题
Nginx配置文件中启用了 `listen 443 ssl`，但SSL证书配置被注释掉了，导致Nginx无法启动。

## 立即修复步骤

在服务器上执行以下命令：

### 方法1: 使用更新后的模板文件（推荐）

```bash
cd /home/ubuntu/wushizhifu

# 拉取最新代码
git pull origin main

# 使用新的模板文件覆盖当前配置
sudo cp deploy/nginx-web.conf /etc/nginx/sites-available/web-5050

# 测试配置
sudo nginx -t

# 如果测试通过，重载Nginx
sudo systemctl reload nginx
```

### 方法2: 手动修复当前配置

```bash
# 编辑配置文件
sudo nano /etc/nginx/sites-available/web-5050
```

将整个 HTTPS server 块（从 `server {` 到对应的 `}`）注释掉，或者直接删除。

或者使用sed命令快速修复：

```bash
# 备份当前配置
sudo cp /etc/nginx/sites-available/web-5050 /etc/nginx/sites-available/web-5050.backup

# 注释掉HTTPS server块（从第12行开始的server块）
sudo sed -i '12,44s/^/#/' /etc/nginx/sites-available/web-5050

# 同时注释掉HTTP块中的HTTPS重定向
sudo sed -i 's/return 301 https/# return 301 https/' /etc/nginx/sites-available/web-5050

# 测试配置
sudo nginx -t

# 如果测试通过，重载Nginx
sudo systemctl reload nginx
```

### 方法3: 创建最简单的HTTP配置

```bash
# 创建新的配置文件（只有HTTP）
sudo tee /etc/nginx/sites-available/web-5050 > /dev/null <<'EOF'
# Nginx 配置文件 - Web前端网站
# 域名: 5050.usdt2026.cc

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
EOF

# 测试配置
sudo nginx -t

# 如果测试通过，重载Nginx
sudo systemctl reload nginx
```

## 验证修复

```bash
# 检查Nginx状态
sudo systemctl status nginx

# 测试访问
curl -I http://5050.usdt2026.cc

# 或者在浏览器中访问
# http://5050.usdt2026.cc
```

## 修复后申请SSL证书

修复Nginx配置后，可以申请SSL证书：

```bash
sudo certbot --nginx -d 5050.usdt2026.cc
```

Certbot会自动：
- 申请SSL证书
- 更新Nginx配置，添加HTTPS server块
- 配置HTTP到HTTPS的重定向
