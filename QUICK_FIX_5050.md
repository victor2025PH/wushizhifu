# 快速修复5050.usdt2026.cc配置

## 🔍 问题

`5050.usdt2026.cc` 显示的是MiniApp内容，应该显示Web网站内容。

## 🔧 立即修复步骤

### 步骤1: 拉取最新代码

```bash
cd /home/ubuntu/wushizhifu
git pull origin main
```

### 步骤2: 检查当前5050配置

```bash
# 查看5050的root配置
sudo nginx -T | grep -A 10 "server_name 5050.usdt2026.cc" | grep "root"
```

### 步骤3: 修复5050配置

```bash
sudo nano /etc/nginx/sites-available/web-5050
```

**找到 `root` 行，确保是：**
```nginx
root /home/ubuntu/wushizhifu/web/dist;
```

**如果不是，改为上面的路径。**

### 步骤4: 检查是否有其他配置冲突

```bash
# 查看所有启用的站点
ls -la /etc/nginx/sites-enabled/

# 检查是否有多个配置包含5050
sudo grep -r "5050.usdt2026.cc" /etc/nginx/sites-available/
```

### 步骤5: 确保5050配置已启用

```bash
# 启用5050配置
sudo ln -sf /etc/nginx/sites-available/web-5050 /etc/nginx/sites-enabled/web-5050

# 测试配置
sudo nginx -t

# 重载Nginx
sudo systemctl reload nginx
```

### 步骤6: 验证修复

```bash
# 再次检查root配置
sudo nginx -T | grep -A 5 "server_name 5050.usdt2026.cc" | grep "root"
```

应该显示：
```
root /home/ubuntu/wushizhifu/web/dist;
```

然后访问 `https://5050.usdt2026.cc`，应该显示Web网站（营销页面），而不是MiniApp。

## 🔍 如果还是不对

### 检查目录内容

```bash
# 检查Web网站目录内容
ls -la /home/ubuntu/wushizhifu/web/dist/
cat /home/ubuntu/wushizhifu/web/dist/index.html | head -20

# 检查MiniApp目录内容（对比）
ls -la /home/ubuntu/wushizhifu/wushizhifu-full/dist/
cat /home/ubuntu/wushizhifu/wushizhifu-full/dist/index.html | head -20
```

### 检查Nginx实际使用的配置

```bash
# 查看完整的5050配置
sudo nginx -T | grep -B 5 -A 20 "server_name 5050.usdt2026.cc"
```

### 清除浏览器缓存

如果配置已修复但浏览器还是显示旧内容，清除浏览器缓存或使用隐私模式访问。
