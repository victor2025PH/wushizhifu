# SSL证书配置指南 - 解决"不安全"警告

## 🔍 问题诊断

浏览器显示"不安全"（Insecure）警告的原因通常有：

1. **SSL证书未申请** - 最可能的原因
2. **SSL证书配置不正确** - Nginx配置中证书路径错误
3. **证书过期或无效**
4. **证书域名不匹配**

## ✅ 解决方案

### 方法1: 使用Certbot申请SSL证书（推荐）

在服务器上执行以下命令：

```bash
# 1. 确保Nginx配置只有HTTP（证书申请前的要求）
sudo cat /etc/nginx/sites-available/web-5050

# 2. 确保Nginx正在运行
sudo systemctl status nginx

# 3. 确保域名解析正确
nslookup 5050.usdt2026.cc
# 应该显示服务器IP地址

# 4. 确保防火墙允许80和443端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 5. 申请SSL证书
sudo certbot --nginx -d 5050.usdt2026.cc

# 按提示操作：
# - 输入邮箱地址
# - 同意服务条款（输入Y）
# - 是否重定向HTTP到HTTPS（推荐选择2：重定向）
```

Certbot会自动：
- ✅ 申请Let's Encrypt SSL证书
- ✅ 配置Nginx启用HTTPS
- ✅ 设置HTTP到HTTPS自动重定向
- ✅ 配置自动续期

### 方法2: 手动配置SSL证书

如果Certbot无法自动配置，可以手动编辑Nginx配置：

```bash
# 1. 申请证书（standalone模式）
sudo certbot certonly --standalone -d 5050.usdt2026.cc

# 2. 编辑Nginx配置
sudo nano /etc/nginx/sites-available/web-5050
```

添加HTTPS配置块：

```nginx
server {
    listen 443 ssl http2;
    server_name 5050.usdt2026.cc;
    
    ssl_certificate /etc/letsencrypt/live/5050.usdt2026.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/5050.usdt2026.cc/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
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

同时修改HTTP块，添加重定向：

```nginx
server {
    listen 80;
    server_name 5050.usdt2026.cc;
    
    return 301 https://$server_name$request_uri;
}
```

然后测试并重载：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 🔍 验证SSL配置

### 1. 检查证书是否存在

```bash
# 检查证书文件
sudo ls -la /etc/letsencrypt/live/5050.usdt2026.cc/

# 应该看到：
# - fullchain.pem
# - privkey.pem
# - cert.pem
# - chain.pem
```

### 2. 检查Nginx配置

```bash
# 查看配置中的证书路径
sudo grep -A 5 "listen 443" /etc/nginx/sites-available/web-5050

# 应该看到：
# ssl_certificate /etc/letsencrypt/live/5050.usdt2026.cc/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/5050.usdt2026.cc/privkey.pem;
```

### 3. 测试SSL连接

```bash
# 在服务器上测试
curl -I https://5050.usdt2026.cc

# 使用openssl测试
openssl s_client -connect 5050.usdt2026.cc:443 -servername 5050.usdt2026.cc
```

### 4. 在线SSL检测工具

访问以下网站检查SSL配置：
- https://www.ssllabs.com/ssltest/analyze.html?d=5050.usdt2026.cc
- https://www.sslshopper.com/ssl-checker.html#hostname=5050.usdt2026.cc

## ⚠️ 常见问题

### 问题1: Certbot申请失败

**原因**：
- 域名未正确解析到服务器IP
- 80端口被占用或防火墙阻止
- 之前申请过证书但配置有问题

**解决**：
```bash
# 检查域名解析
dig 5050.usdt2026.cc

# 检查端口是否开放
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# 清除旧的证书申请记录
sudo certbot delete --cert-name 5050.usdt2026.cc
# 然后重新申请
```

### 问题2: 证书配置后仍然显示不安全

**原因**：
- 浏览器缓存了旧的证书信息
- 混合内容（HTTP和HTTPS资源混用）
- 证书链不完整

**解决**：
```bash
# 检查证书链
sudo openssl x509 -in /etc/letsencrypt/live/5050.usdt2026.cc/fullchain.pem -text -noout

# 确保使用fullchain.pem而不是cert.pem
# 清除浏览器缓存，或使用隐私模式访问
```

### 问题3: 证书自动续期

Certbot默认配置了自动续期，但可以手动测试：

```bash
# 测试续期（不会真的续期）
sudo certbot renew --dry-run

# 查看续期服务状态
sudo systemctl status certbot.timer
```

## 📝 快速检查清单

在服务器上运行以下命令快速诊断：

```bash
echo "=== 检查域名解析 ==="
nslookup 5050.usdt2026.cc

echo "=== 检查证书文件 ==="
sudo ls -la /etc/letsencrypt/live/5050.usdt2026.cc/ 2>/dev/null || echo "证书不存在"

echo "=== 检查Nginx配置 ==="
sudo nginx -t

echo "=== 检查SSL配置 ==="
sudo grep -E "ssl_certificate|listen 443" /etc/nginx/sites-available/web-5050

echo "=== 检查Nginx状态 ==="
sudo systemctl status nginx --no-pager | head -5

echo "=== 测试HTTPS连接 ==="
curl -I https://5050.usdt2026.cc 2>&1 | head -5
```

## 🎯 推荐操作步骤

1. **首先确认证书是否已申请**：
   ```bash
   sudo certbot certificates
   ```

2. **如果没有证书，申请证书**：
   ```bash
   sudo certbot --nginx -d 5050.usdt2026.cc
   ```

3. **如果证书已存在但配置有问题**，检查Nginx配置中的证书路径是否正确

4. **验证配置**：
   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ```

5. **在浏览器中清除缓存后重新访问**
