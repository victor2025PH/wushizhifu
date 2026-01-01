# 修复部署问题指南

## 🔍 问题总结

### 问题1: MiniApp被Web网站覆盖
**现象**: 访问 `https://50zf.usdt2026.cc` 显示的是Web网站的内容，而不是MiniApp

**原因**: Nginx配置中，两个域名可能指向了同一个目录

**解决方法**:
1. 检查当前Nginx配置
2. 确保 50zf.usdt2026.cc 指向 MiniApp 的 dist 目录
3. 确保 5050.usdt2026.cc 指向 Web 的 dist 目录

### 问题2: 客服分配使用占位符
**现象**: 点击"立即开户"或"客服支持"按钮，分配到了 `wushizhifu_jianglai` 而不是10个客服账号之一

**原因**: 
- MiniApp代码中仍有硬编码的fallback逻辑
- 可能API调用失败，导致使用fallback
- 数据库中可能还没有添加10个客服账号

**解决方法**:
1. 运行批量添加客服账号脚本
2. 确保API服务器正常运行
3. 检查API调用是否成功

## 🔧 修复步骤

### 步骤1: 检查Nginx配置

在服务器上执行：

```bash
# 检查当前Nginx配置
sudo nginx -T | grep -A 30 "server_name 50zf.usdt2026.cc"
sudo nginx -T | grep -A 30 "server_name 5050.usdt2026.cc"

# 检查实际的目录结构
ls -la /home/ubuntu/wushizhifu/wushizhifu-full/dist/
ls -la /home/ubuntu/wushizhifu/web/dist/
```

### 步骤2: 修复Nginx配置（如果需要）

#### 修复50zf.usdt2026.cc (MiniApp)

```bash
sudo nano /etc/nginx/sites-available/50zf.usdt2026.cc
# 或
sudo nano /etc/nginx/sites-available/wushizhifu
```

确保配置如下：

```nginx
server {
    listen 443 ssl http2;
    server_name 50zf.usdt2026.cc;
    
    ssl_certificate /etc/letsencrypt/live/50zf.usdt2026.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/50zf.usdt2026.cc/privkey.pem;
    
    # MiniApp静态文件 - 根据实际目录选择
    root /home/ubuntu/wushizhifu/wushizhifu-full/dist;
    # 或者如果是 /opt/wushizhifu/frontend/dist/
    # root /opt/wushizhifu/frontend/dist;
    
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

#### 修复5050.usdt2026.cc (Web网站)

```bash
sudo nano /etc/nginx/sites-available/web-5050
```

确保配置如下：

```nginx
server {
    listen 80;
    server_name 5050.usdt2026.cc;
    
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

然后测试并重载：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 步骤3: 添加10个客服账号

```bash
cd /home/ubuntu/wushizhifu/botB
python3 add_customer_service_accounts.py
```

### 步骤4: 检查API服务器

```bash
# 检查API服务器状态
sudo systemctl status api-server
# 或
sudo systemctl status wushipay-api

# 查看日志
sudo journalctl -u api-server -f
# 或
sudo journalctl -u wushipay-api -f

# 测试API端点
curl -X POST http://localhost:8000/api/customer-service/assign \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123456, "username": "testuser"}'
```

### 步骤5: 验证修复

1. **验证网站访问**:
   - 访问 `https://50zf.usdt2026.cc` - 应该显示MiniApp
   - 访问 `https://5050.usdt2026.cc` - 应该显示Web网站

2. **验证客服分配**:
   - 在MiniApp中点击"立即开户"按钮
   - 在MiniApp中点击"客服支持"按钮
   - 在Web网站中点击"Telegram"客服按钮
   - 都应该分配到10个客服账号之一（不是 wushizhifu_jianglai）

3. **检查数据库**:
   ```bash
   sqlite3 /home/ubuntu/wushizhifu/wushipay.db
   SELECT username, is_active FROM customer_service_accounts;
   SELECT value FROM settings WHERE key = 'customer_service_strategy';
   .quit
   ```

## 📝 注意事项

1. **目录路径**: 根据实际部署情况，MiniApp的dist目录可能在：
   - `/home/ubuntu/wushizhifu/wushizhifu-full/dist/`
   - `/opt/wushizhifu/frontend/dist/`
   - 需要确认实际路径

2. **API URL**: MiniApp和Web网站都需要能访问API服务器
   - MiniApp通过 `/api/` 路径（Nginx代理）
   - Web网站可能需要配置API_BASE_URL环境变量或直接使用完整URL

3. **客服账号**: 确保10个客服账号都已添加并且 `is_active = 1`
