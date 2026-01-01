# GitHub Actions 部署故障排查指南

## 🔍 当前问题

GitHub Actions 部署失败，错误代码：`exit code 1`

## 📋 可能的原因

### 1. 目录不存在
- `$SERVER_PATH` 目录在服务器上不存在
- `botB` 子目录不存在

### 2. Git 仓库问题
- 目录不是 Git 仓库
- Git 仓库配置不正确（remote、branch 等）

### 3. 权限问题
- 用户没有权限访问目录
- 用户没有 sudo 权限重启服务

### 4. 网络问题
- SSH 连接失败
- 无法访问 GitHub 拉取代码

### 5. 依赖安装问题
- Python 版本不匹配
- requirements.txt 中的依赖安装失败
- 虚拟环境创建失败

### 6. 服务配置问题
- systemd 服务文件不存在
- 服务名称不正确（`otc-bot.service`）

## 🔧 排查步骤

### 步骤 1: 查看详细日志

在 GitHub Actions 页面：
1. 点击失败的 workflow run
2. 展开 "Deploy to server" 步骤
3. 查看完整的错误输出

### 步骤 2: 检查服务器配置

在服务器上手动检查：

```bash
# 检查目录是否存在
echo $SERVER_PATH  # 或在 GitHub Secrets 中查看 SERVER_PATH
ls -la /home/ubuntu/wushizhifu

# 检查 botB 目录
ls -la /home/ubuntu/wushizhifu/botB

# 检查是否是 Git 仓库
cd /home/ubuntu/wushizhifu
git status

# 检查服务配置
sudo systemctl status otc-bot.service
ls -la /etc/systemd/system/otc-bot.service
```

### 步骤 3: 手动执行部署脚本

在服务器上手动执行部署步骤：

```bash
cd /home/ubuntu/wushizhifu

# 如果是 Git 仓库，拉取代码
git pull origin main

# 进入 botB 目录
cd botB

# 创建/激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 重启服务
sudo systemctl restart otc-bot.service
sudo systemctl status otc-bot.service
```

### 步骤 4: 检查 GitHub Secrets

确保以下 Secrets 已正确配置：
- `SSH_PRIVATE_KEY`: SSH 私钥
- `SERVER_HOST`: 服务器地址
- `SERVER_USER`: SSH 用户名（通常是 `ubuntu`）
- `SERVER_PATH`: 项目路径（通常是 `/home/ubuntu/wushizhifu`）

## 🛠️ 临时解决方案

如果无法立即解决问题，可以：

1. **使用手动部署脚本**：
   ```bash
   cd /home/ubuntu/wushizhifu/botB
   bash deploy_update.sh
   ```

2. **直接 SSH 到服务器手动部署**：
   ```bash
   ssh user@server
   cd /home/ubuntu/wushizhifu/botB
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt
   sudo systemctl restart otc-bot.service
   ```

## 📝 改进建议

### 建议 1: 使用 appleboy/ssh-action

参考 Bot A 的部署方式，使用 `appleboy/ssh-action` 可能更可靠：

```yaml
- name: Deploy to server
  uses: appleboy/ssh-action@v1.0.0
  with:
    host: ${{ secrets.SERVER_HOST }}
    username: ${{ secrets.SERVER_USER }}
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    script: |
      cd /home/ubuntu/wushizhifu
      git pull origin main || true
      cd botB
      source venv/bin/activate || python3 -m venv venv && source venv/bin/activate
      pip install -r requirements.txt
      sudo systemctl restart otc-bot.service
```

### 建议 2: 分离步骤

将部署分为多个步骤，便于定位问题：
- Step 1: Pull Code
- Step 2: Install Dependencies
- Step 3: Restart Service

### 建议 3: 添加更多日志

在脚本中添加更多调试信息：
- 显示当前用户
- 显示当前目录
- 显示环境变量
- 显示命令执行结果

## ✅ 验证修复

修复后，验证步骤：
1. 推送代码到 GitHub
2. 观察 GitHub Actions 运行
3. 检查部署日志
4. 在服务器上验证服务状态
5. 测试 Bot 功能

---

**请查看 GitHub Actions 的详细日志以确定具体错误原因。**
