# Web部署检查清单

## 🔍 问题诊断

访问 `http://5050.usdt2026.cc` 出现 404 错误，需要进行以下检查：

### 1. 检查GitHub Actions部署状态

1. 访问 GitHub Actions 页面
2. 查看最新的 `Deploy Web Frontend` 工作流运行状态
3. 确认是否成功完成

### 2. 检查服务器上的文件

在服务器上执行以下命令：

```bash
# 检查web目录是否存在
ls -la /home/ubuntu/wushizhifu/web/

# 检查dist目录是否存在
ls -la /home/ubuntu/wushizhifu/web/dist/

# 检查dist目录中是否有文件
ls -la /home/ubuntu/wushizhifu/web/dist/ | head -20
```

### 3. 检查Nginx配置

```bash
# 检查Nginx配置文件是否存在
sudo cat /etc/nginx/sites-available/web-5050

# 检查是否已启用
ls -la /etc/nginx/sites-enabled/ | grep web-5050

# 检查Nginx配置语法
sudo nginx -t

# 查看Nginx错误日志
sudo tail -50 /var/log/nginx/error.log
```

### 4. 检查文件权限

```bash
# 检查文件所有者
ls -la /home/ubuntu/wushizhifu/web/dist/

# 如果权限不正确，修复权限
sudo chown -R www-data:www-data /home/ubuntu/wushizhifu/web/dist
sudo chmod -R 755 /home/ubuntu/wushizhifu/web/dist
```

### 5. 手动触发部署（如果需要）

如果GitHub Actions部署失败或未运行，可以手动执行：

```bash
cd /home/ubuntu/wushizhifu
git pull origin main

cd web
npm install
npm run build

# 检查构建是否成功
ls -la dist/

# 设置权限
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist

# 检查并重载Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 6. 检查Nginx配置路径

确认Nginx配置中的 `root` 路径是否正确：

```bash
# 查看配置中的root路径
sudo grep "root" /etc/nginx/sites-available/web-5050

# 应该显示类似：root /home/ubuntu/wushizhifu/web/dist;
```

### 7. 测试访问

```bash
# 在服务器上测试本地访问
curl -I http://localhost/
curl -I https://localhost/  # 如果SSL已配置

# 检查是否有index.html
ls -la /home/ubuntu/wushizhifu/web/dist/index.html
```

## 🚀 快速修复步骤

如果文件不存在，执行完整部署：

```bash
# 1. 进入web目录
cd /home/ubuntu/wushizhifu/web

# 2. 确保Node.js已安装
node --version  # 应该是v18或更高
npm --version

# 3. 安装依赖
npm install

# 4. 构建项目
npm run build

# 5. 检查构建结果
ls -la dist/

# 6. 设置权限
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist

# 7. 检查Nginx配置
sudo nginx -t

# 8. 重载Nginx
sudo systemctl reload nginx

# 9. 测试访问
curl -I http://5050.usdt2026.cc
```

## ⚠️ 常见问题

### 问题1: dist目录不存在
**原因**: 构建失败或未执行
**解决**: 运行 `npm run build`

### 问题2: 权限错误
**原因**: 文件所有者不是www-data
**解决**: `sudo chown -R www-data:www-data dist`

### 问题3: Nginx配置路径错误
**原因**: root路径配置不正确
**解决**: 检查并更新 `/etc/nginx/sites-available/web-5050` 中的root路径

### 问题4: 配置文件未启用
**原因**: 配置文件未链接到sites-enabled
**解决**: `sudo ln -sf /etc/nginx/sites-available/web-5050 /etc/nginx/sites-enabled/`

## 📝 下一步

1. 首先检查GitHub Actions是否成功运行
2. 如果失败，查看日志找出原因
3. 如果成功但文件不存在，检查服务器上的实际路径
4. 如果文件存在但404，检查Nginx配置和权限
5. 手动执行部署步骤进行修复
