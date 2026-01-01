# 快速修复网站访问问题

## 🔍 问题诊断

从日志看，部署已成功，但网站无法访问。可能的原因：
1. 访问 `https://` 但SSL证书不存在
2. 云服务商安全组未开放端口
3. Nginx配置强制HTTPS重定向

## 🚀 立即修复步骤

### 步骤1: 拉取最新代码

```bash
cd /home/ubuntu/wushizhifu
git pull origin main
```

### 步骤2: 确保HTTP配置正确（不强制HTTPS）

```bash
# 修复5050配置
sudo sed -i 's|^[[:space:]]*return 301 https://|    # return 301 https://|g' /etc/nginx/sites-available/web-5050

# 修复50zf配置
sudo sed -i 's|^[[:space:]]*return 301 https://|    # return 301 https://|g' /etc/nginx/sites-available/wushizhifu

# 测试并重载
sudo nginx -t && sudo systemctl reload nginx
```

### 步骤3: 测试本地HTTP访问

```bash
# 测试5050
curl -v http://localhost/ -H "Host: 5050.usdt2026.cc"

# 测试50zf
curl -v http://localhost/ -H "Host: 50zf.usdt2026.cc"
```

如果返回HTTP 200，说明本地访问正常。

### 步骤4: 检查端口监听

```bash
sudo ss -tlnp | grep ":80"
```

应该看到 `0.0.0.0:80` 正在监听。

### 步骤5: 获取服务器IP并测试

```bash
# 获取服务器公网IP
SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip)
echo "服务器IP: $SERVER_IP"

# 从外部测试（在另一台机器上运行）
curl -v http://$SERVER_IP -H "Host: 5050.usdt2026.cc"
```

### 步骤6: 检查云服务商安全组

**重要：** 如果本地测试成功但外部无法访问，问题在云服务商安全组。

#### 阿里云/腾讯云/华为云：
1. 登录云服务商控制台
2. 找到「安全组」或「防火墙」设置
3. 添加入站规则：
   - **协议类型**: TCP
   - **端口范围**: 80
   - **源地址**: 0.0.0.0/0
   - **动作**: 允许

4. 同样添加443端口（用于HTTPS）

#### AWS EC2：
1. 找到「Security Groups」
2. 添加入站规则：
   - **Type**: HTTP
   - **Port**: 80
   - **Source**: 0.0.0.0/0

## ✅ 验证

修复后，使用 **HTTP**（不是HTTPS）测试：
- `http://5050.usdt2026.cc`
- `http://50zf.usdt2026.cc`

如果HTTP可以访问，再申请SSL证书：
```bash
sudo certbot --nginx -d 5050.usdt2026.cc
sudo certbot --nginx -d 50zf.usdt2026.cc
```

## 🔍 如果还是无法访问

运行完整诊断脚本（如果已拉取代码）：
```bash
chmod +x deploy/check_and_fix_access.sh
./deploy/check_and_fix_access.sh
```

或者手动检查：
```bash
# 检查Nginx状态
sudo systemctl status nginx

# 检查Nginx配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -50 /var/log/nginx/error.log

# 查看Nginx访问日志
sudo tail -50 /var/log/nginx/access.log
```
