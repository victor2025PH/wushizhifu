# 修复Nginx配置混淆问题

## 🔍 问题描述

两个域名指向了错误的目录：
- `50zf.usdt2026.cc` 应该显示 MiniApp，但可能显示了 Web 网站
- `5050.usdt2026.cc` 应该显示 Web 网站，但可能显示了 MiniApp

## 🔧 快速修复方法

### 方法1: 使用自动修复脚本（推荐）

```bash
cd /home/ubuntu/wushizhifu
chmod +x deploy/fix_nginx_separate_sites.sh
./deploy/fix_nginx_separate_sites.sh
```

### 方法2: 手动检查和修复

#### 步骤1: 检查当前配置

```bash
# 查看所有Nginx配置
sudo nginx -T | grep -B 5 -A 15 "server_name 50zf.usdt2026.cc"
sudo nginx -T | grep -B 5 -A 15 "server_name 5050.usdt2026.cc"

# 查看启用的站点
ls -la /etc/nginx/sites-enabled/
```

#### 步骤2: 检查目录

```bash
# 确认MiniApp目录存在
ls -la /home/ubuntu/wushizhifu/wushizhifu-full/dist/

# 确认Web目录存在
ls -la /home/ubuntu/wushizhifu/web/dist/
```

#### 步骤3: 创建/修复50zf.usdt2026.cc配置

```bash
sudo nano /etc/nginx/sites-available/50zf.usdt2026.cc
```

确保配置如下：

```nginx
server {
    listen 443 ssl http2;
    server_name 50zf.usdt2026.cc;
    
    ssl_certificate /etc/letsencrypt/live/50zf.usdt2026.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/50zf.usdt2026.cc/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # MiniApp静态文件 - 重要：指向wushizhifu-full
    root /home/ubuntu/wushizhifu/wushizhifu-full/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
```

#### 步骤4: 创建/修复5050.usdt2026.cc配置

```bash
sudo nano /etc/nginx/sites-available/web-5050
```

确保配置如下：

```nginx
server {
    listen 80;
    server_name 5050.usdt2026.cc;
    
    # Web前端静态文件 - 重要：指向web
    root /home/ubuntu/wushizhifu/web/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}

# HTTPS配置（如果SSL证书已配置）
server {
    listen 443 ssl http2;
    server_name 5050.usdt2026.cc;
    
    ssl_certificate /etc/letsencrypt/live/5050.usdt2026.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/5050.usdt2026.cc/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Web前端静态文件 - 重要：指向web
    root /home/ubuntu/wushizhifu/web/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
```

#### 步骤5: 启用站点并禁用冲突配置

```bash
# 启用50zf配置
sudo ln -sf /etc/nginx/sites-available/50zf.usdt2026.cc /etc/nginx/sites-enabled/50zf.usdt2026.cc

# 启用5050配置
sudo ln -sf /etc/nginx/sites-available/web-5050 /etc/nginx/sites-enabled/web-5050

# 如果wushizhifu配置存在且包含50zf，禁用它以避免冲突
if [ -f "/etc/nginx/sites-enabled/wushizhifu" ]; then
    echo "发现wushizhifu配置，检查是否包含50zf..."
    if grep -q "50zf.usdt2026.cc" /etc/nginx/sites-available/wushizhifu 2>/dev/null; then
        echo "禁用旧的wushizhifu配置以避免冲突"
        sudo rm /etc/nginx/sites-enabled/wushizhifu
    fi
fi

# 测试配置
sudo nginx -t

# 重载Nginx
sudo systemctl reload nginx
```

## ✅ 验证修复

### 1. 检查配置

```bash
# 检查50zf配置
sudo nginx -T | grep -A 10 "server_name 50zf.usdt2026.cc" | grep "root"

# 检查5050配置
sudo nginx -T | grep -A 10 "server_name 5050.usdt2026.cc" | grep "root"
```

应该看到：
- `50zf.usdt2026.cc` 的 `root` 是 `/home/ubuntu/wushizhifu/wushizhifu-full/dist`
- `5050.usdt2026.cc` 的 `root` 是 `/home/ubuntu/wushizhifu/web/dist`

### 2. 访问网站验证

- 访问 `https://50zf.usdt2026.cc` - 应该显示MiniApp（有底部导航栏：首页、钱包、记录、我的）
- 访问 `https://5050.usdt2026.cc` - 应该显示Web网站（营销页面，有"启动机器人"和"打开WebApp"按钮）

### 3. 检查是否有配置冲突

```bash
# 查看所有启用的站点
ls -la /etc/nginx/sites-enabled/

# 检查是否有重复的server_name
sudo nginx -T | grep "server_name" | sort | uniq -d
```

如果有重复的 `server_name`，需要禁用其中一个配置。

## 🔍 常见问题

### 问题1: 两个域名显示相同内容

**原因**: 两个配置文件的 `root` 指向了同一个目录

**解决**: 确保：
- `50zf.usdt2026.cc` → `/home/ubuntu/wushizhifu/wushizhifu-full/dist`
- `5050.usdt2026.cc` → `/home/ubuntu/wushizhifu/web/dist`

### 问题2: 配置修改后没有生效

**原因**: Nginx配置没有重载，或者有配置冲突

**解决**:
```bash
# 检查配置语法
sudo nginx -t

# 重载配置
sudo systemctl reload nginx

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### 问题3: 旧的wushizhifu配置干扰

**原因**: `/etc/nginx/sites-available/wushizhifu` 可能包含50zf的配置，导致冲突

**解决**:
```bash
# 检查wushizhifu配置
sudo cat /etc/nginx/sites-available/wushizhifu | grep -A 5 "server_name"

# 如果包含50zf，禁用这个配置
sudo rm /etc/nginx/sites-enabled/wushizhifu
sudo nginx -t && sudo systemctl reload nginx
```
