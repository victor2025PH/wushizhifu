# 准备上传到 GitHub

## ✅ 已完成的更改

1. ✅ 更新了 Bot A 的 `config.py` - 从根目录读取 `.env`
2. ✅ 更新了 Bot B 的 `config.py` - 从根目录读取 `.env`
3. ✅ 创建了 GitHub Actions 工作流
4. ✅ 创建了项目结构文档
5. ✅ 创建了迁移说明

## 📋 执行步骤

### 1. 重命名目录（本地）

#### 方法 A: 使用脚本
```powershell
.\重命名目录脚本.bat
```

#### 方法 B: 手动重命名
- 将 `wushizhifu-bot` 重命名为 `botA`
- 将 `wushizhifu-otc-bot` 重命名为 `botB`

### 2. 确认 .env 文件位置

确保 `.env` 文件在项目根目录 (`D:\wushizhifu\.env`)，包含：

```env
BOT_TOKEN=your_bot_a_token_here
BOT_TOKEN_B=your_bot_b_token_here
```

### 3. 更新 .gitignore

确认 `.gitignore` 包含 `.env`（不会被上传到 GitHub）

### 4. 提交到 GitHub

```bash
cd D:\wushizhifu

# 检查状态
git status

# 添加所有更改
git add .

# 提交
git commit -m "重构：分离 botA 和 botB，添加 GitHub Actions 自动部署"

# 推送到 GitHub
git push origin main
```

### 5. 配置 GitHub Secrets

在 GitHub 仓库页面：

1. 进入 `Settings` -> `Secrets and variables` -> `Actions`
2. 点击 `New repository secret`
3. 添加以下 secrets：

| Name | Value | 说明 |
|------|-------|------|
| `SERVER_HOST` | `165.154.203.182` | 服务器 IP |
| `SERVER_USER` | `ubuntu` | SSH 用户名 |
| `SSH_PRIVATE_KEY` | `你的SSH私钥内容` | SSH 私钥 |
| `SSH_PORT` | `22` | SSH 端口（可选） |

**获取 SSH 私钥：**
- 在本地机器上：`cat ~/.ssh/id_rsa`（Windows: `type C:\Users\YourUser\.ssh\id_rsa`）
- 或者在服务器上生成新的密钥对

### 6. 在服务器上初始化

```bash
# SSH 连接到服务器
ssh ubuntu@165.154.203.182

# 进入项目目录（如果不存在，创建）
mkdir -p /home/ubuntu/wushizhifu
cd /home/ubuntu/wushizhifu

# 如果是新部署，克隆仓库
git clone https://github.com/victor2025PH/wushizhifu.git .

# 如果是更新现有部署，拉取代码
# git pull origin main

# 创建 .env 文件（重要：不会从 Git 克隆，需要手动创建）
nano .env
# 添加内容：
# BOT_TOKEN=your_bot_a_token
# BOT_TOKEN_B=your_bot_b_token

# 设置目录权限
chmod 600 .env
```

### 7. 创建 systemd 服务

参考 `迁移说明.md` 创建 `botA.service` 和 `botB.service`

### 8. 测试 GitHub Actions

1. 修改任意 `botA/` 或 `botB/` 下的文件
2. 提交并推送：
```bash
git add .
git commit -m "测试部署"
git push origin main
```
3. 在 GitHub 仓库页面查看 `Actions` 标签页
4. 应该看到自动部署工作流运行

## 🔍 验证清单

- [ ] `botA/` 目录存在
- [ ] `botB/` 目录存在
- [ ] `.env` 文件在根目录
- [ ] `.github/workflows/` 目录存在
- [ ] GitHub Secrets 已配置
- [ ] 服务器上已克隆/更新代码
- [ ] systemd 服务已创建并启用
- [ ] 测试推送触发部署

## ⚠️ 注意事项

1. **`.env` 文件不会被上传** - 必须在服务器上手动创建
2. **SSH 密钥权限** - 确保 GitHub Actions 可以 SSH 到服务器
3. **服务重启** - Actions 会尝试重启服务，如果服务不存在会跳过
4. **首次部署** - 可能需要手动在服务器上运行 `pip install -r requirements.txt`

## 🐛 故障排除

### GitHub Actions 失败

1. 检查 Secrets 是否正确配置
2. 检查 SSH 密钥是否有权限
3. 查看 Actions 日志获取详细错误信息

### 服务无法启动

```bash
# 检查服务状态
sudo systemctl status botA.service
sudo systemctl status botB.service

# 查看日志
sudo journalctl -u botA.service -n 50
sudo journalctl -u botB.service -n 50
```

### 配置文件找不到 .env

确认 `.env` 文件在 `/home/ubuntu/wushizhifu/.env`，并且权限正确：
```bash
ls -la /home/ubuntu/wushizhifu/.env
chmod 600 /home/ubuntu/wushizhifu/.env
```

