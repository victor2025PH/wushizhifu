# 服务器部署结构说明

## 📋 四个服务的逻辑关系

服务器上共有4个服务/项目：

### 1. Bot A
- **类型**: Telegram Bot (Python/Aiogram)
- **位置**: `/home/ubuntu/wushizhifu/botA/` 或 `/opt/wushizhifu/botA/`
- **功能**: 群组管理、敏感词过滤等（已迁移到Bot B，但代码保留）
- **状态**: 已静默（群组中不响应start命令）

### 2. Bot B
- **类型**: Telegram Bot (Python/python-telegram-bot)
- **位置**: `/home/ubuntu/wushizhifu/botB/` 或 `/opt/wushizhifu/botB/`
- **功能**: 
  - 完整的交易管理功能
  - 用户管理、群组管理（从Bot A迁移）
  - 管理员面板
  - 客服分配管理
- **数据库**: `/home/ubuntu/wushizhifu/wushipay.db`
- **API服务器**: `api_server.py` 运行在端口 8000

### 3. MiniApp (wushizhifu-full)
- **类型**: Telegram MiniApp (React/TypeScript)
- **源代码位置**: `/home/ubuntu/wushizhifu/wushizhifu-full/`
- **构建输出**: `/home/ubuntu/wushizhifu/wushizhifu-full/dist/` 或 `/opt/wushizhifu/frontend/dist/`
- **域名**: `https://50zf.usdt2026.cc`
- **Nginx配置**: `/etc/nginx/sites-available/50zf.usdt2026.cc` 或 `/etc/nginx/sites-available/wushizhifu`
- **Nginx root**: 应指向 MiniApp 的 dist 目录
- **API代理**: `/api/` → `http://127.0.0.1:8000` (Bot B的API服务器)
- **功能**: 
  - 支付网关界面
  - 用户仪表板
  - 交易管理
  - 客服支持（调用API分配客服）

### 4. Web网站 (web)
- **类型**: 营销/展示网站 (React/TypeScript/Vite)
- **源代码位置**: `/home/ubuntu/wushizhifu/web/`
- **构建输出**: `/home/ubuntu/wushizhifu/web/dist/`
- **域名**: `https://5050.usdt2026.cc`
- **Nginx配置**: `/etc/nginx/sites-available/web-5050`
- **Nginx root**: `/home/ubuntu/wushizhifu/web/dist/`
- **功能**:
  - 产品展示
  - 营销页面
  - 客服支持（调用API分配客服）
  - 引导用户使用MiniApp或Bot

## 🔧 Nginx配置要求

### 1. MiniApp (50zf.usdt2026.cc)

配置文件: `/etc/nginx/sites-available/50zf.usdt2026.cc` 或 `/etc/nginx/sites-available/wushizhifu`

```nginx
server {
    listen 80;
    server_name 50zf.usdt2026.cc;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 50zf.usdt2026.cc;
    
    ssl_certificate /etc/letsencrypt/live/50zf.usdt2026.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/50zf.usdt2026.cc/privkey.pem;
    
    # MiniApp静态文件
    # 如果使用 /home/ubuntu/wushizhifu/wushizhifu-full/dist/
    root /home/ubuntu/wushizhifu/wushizhifu-full/dist;
    # 或者如果使用 /opt/wushizhifu/frontend/dist/
    # root /opt/wushizhifu/frontend/dist;
    
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API代理到Bot B的API服务器
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态资源缓存
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

### 2. Web网站 (5050.usdt2026.cc)

配置文件: `/etc/nginx/sites-available/web-5050`

```nginx
server {
    listen 80;
    server_name 5050.usdt2026.cc;
    # return 301 https://$server_name$request_uri;  # SSL配置后取消注释
    
    # Web网站静态文件
    root /home/ubuntu/wushizhifu/web/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 静态资源缓存
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

## 🔗 客服分配逻辑

所有客服分配都应通过Bot B的API服务器进行：

1. **API端点**: `POST /api/customer-service/assign`
2. **分配策略**: 从数据库设置中读取（默认: round_robin）
3. **客服账号**: 从数据库 `customer_service_accounts` 表中读取
4. **Fallback**: 如果分配失败，使用数据库中的第一个可用账号（不是硬编码的 wushizhifu_jianglai）

### 需要调用API的地方：

1. ✅ **Bot B 群组中的"客服"按钮** - 已实现，使用数据库分配
2. ✅ **Web网站的"Telegram"客服按钮** - 已实现，调用API
3. ❌ **MiniApp的"立即开户"按钮** - 需要修复，当前使用硬编码
4. ❌ **MiniApp的"客服支持"按钮** - 需要修复，当前使用硬编码

## 📝 当前问题

### 问题1: MiniApp被Web网站覆盖
- **原因**: Nginx配置中，50zf.usdt2026.cc 可能指向了错误的目录
- **解决**: 检查并修复 Nginx 配置，确保：
  - 50zf.usdt2026.cc → wushizhifu-full/dist 或 frontend/dist
  - 5050.usdt2026.cc → web/dist

### 问题2: 客服分配使用占位符
- **原因**: 
  - MiniApp (wushizhifu-full) 中仍有硬编码的 `wushizhifu_jianglai`
  - Dashboard.tsx 和 ProfileView.tsx 直接调用 `openSupportChat('wushizhifu_jianglai')`
- **解决**: 
  - 移除硬编码，改为调用 `assignCustomerService()` API
  - 修改 Dashboard.tsx 和 ProfileView.tsx 使用API分配

## ✅ 修复步骤

1. 检查并修复Nginx配置
2. 修复MiniApp中的客服分配逻辑
3. 运行批量添加客服账号脚本
4. 验证两个网站都能正常访问
