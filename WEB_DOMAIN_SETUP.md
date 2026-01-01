# Web网站域名配置指南

## 📋 域名信息

- **域名**: `5050.usdt2026.cc`
- **协议**: HTTPS (SSL/TLS)
- **Nginx配置**: `/etc/nginx/sites-available/web-5050`
- **网站根目录**: `/home/ubuntu/wushizhifu/web/dist`

## 🔧 配置步骤

### 1. DNS配置

确保域名 `5050.usdt2026.cc` 已正确解析到服务器IP地址：

```bash
# 检查DNS解析
nslookup 5050.usdt2026.cc
# 或
dig 5050.usdt2026.cc
```

### 2. 自动配置（推荐）

GitHub Actions 部署工作流会自动：
- ✅ 创建 Nginx 配置文件
- ✅ 启用站点
- ✅ 测试 Nginx 配置
- ✅ 重载 Nginx

部署完成后，需要手动申请 SSL 证书（首次部署）。

### 3. SSL证书申请

首次部署后，需要在服务器上运行：

```bash
sudo certbot --nginx -d 5050.usdt2026.cc
```

Certbot 会自动：
- ✅ 申请 Let's Encrypt SSL 证书
- ✅ 更新 Nginx 配置启用 HTTPS
- ✅ 配置自动续期

### 4. 验证部署

部署完成后，访问：
- **HTTPS**: https://5050.usdt2026.cc
- **HTTP**: http://5050.usdt2026.cc (会自动重定向到HTTPS)

## 📁 文件位置

- **Nginx配置**: `/etc/nginx/sites-available/web-5050`
- **Nginx启用链接**: `/etc/nginx/sites-enabled/web-5050`
- **网站文件**: `/home/ubuntu/wushizhifu/web/dist/`
- **SSL证书**: `/etc/letsencrypt/live/5050.usdt2026.cc/`

## 🔍 故障排查

### 检查Nginx配置

```bash
# 测试配置
sudo nginx -t

# 查看配置
cat /etc/nginx/sites-available/web-5050

# 检查是否启用
ls -la /etc/nginx/sites-enabled/ | grep web-5050
```

### 检查网站文件

```bash
# 查看构建输出
ls -la /home/ubuntu/wushizhifu/web/dist/

# 检查文件权限
sudo chown -R www-data:www-data /home/ubuntu/wushizhifu/web/dist
sudo chmod -R 755 /home/ubuntu/wushizhifu/web/dist
```

### 检查SSL证书

```bash
# 查看证书
sudo certbot certificates

# 测试续期
sudo certbot renew --dry-run
```

### 重载Nginx

```bash
# 重载配置（不中断服务）
sudo systemctl reload nginx

# 或重启
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx
```

### 查看Nginx日志

```bash
# 访问日志
sudo tail -f /var/log/nginx/access.log

# 错误日志
sudo tail -f /var/log/nginx/error.log

# 特定域名的日志（如果配置了）
sudo tail -f /var/log/nginx/web-5050.access.log
sudo tail -f /var/log/nginx/web-5050.error.log
```

## 🔄 自动部署

当 `web/` 目录有变更并推送到 GitHub 时，GitHub Actions 会自动：

1. 拉取最新代码
2. 构建项目
3. 更新 Nginx 配置（如需要）
4. 重载 Nginx

## 📝 注意事项

1. **DNS解析**: 确保域名已正确解析到服务器IP
2. **防火墙**: 确保80和443端口已开放
3. **SSL证书**: 首次部署需要手动运行 `certbot` 申请证书
4. **文件权限**: 确保 `www-data` 用户有读取权限
5. **自动续期**: Certbot 已配置自动续期，无需手动干预

## 🌐 相关域名

- **MiniApp/API**: `50zf.usdt2026.cc` (其他服务)
- **Web网站**: `5050.usdt2026.cc` (本网站)
