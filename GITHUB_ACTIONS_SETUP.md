# GitHub Actions 自动部署配置指南

## ✅ 已配置的工作流

### Bot B 自动部署
- **文件**: `.github/workflows/deploy-botB.yml`
- **触发条件**:
  - 推送到 `main` 分支
  - 修改 `botB/**`、`services/**`、`database/**` 目录下的文件
  - 手动触发（workflow_dispatch）

## 🔧 配置 GitHub Secrets

在 GitHub 仓库中配置以下 Secrets（Settings → Secrets and variables → Actions）：

### 必需的 Secrets

1. **SSH_PRIVATE_KEY**
   - 服务器SSH私钥
   - 用于连接服务器进行部署
   - 获取方式：`cat ~/.ssh/id_rsa`（在服务器上）

2. **SERVER_HOST**
   - 服务器地址（IP或域名）
   - 例如：`123.456.789.0` 或 `your-server.com`

3. **SERVER_USER**
   - 服务器用户名
   - 例如：`ubuntu` 或 `root`

4. **SERVER_PATH**
   - 项目在服务器上的路径
   - 例如：`/home/ubuntu/wushizhifu`

## 📝 配置步骤

### 1. 获取SSH私钥

在服务器上执行：
```bash
# 如果还没有SSH密钥，先生成
ssh-keygen -t rsa -b 4096 -C "github-actions"

# 查看私钥（复制全部内容）
cat ~/.ssh/id_rsa

# 将公钥添加到authorized_keys（如果还没有）
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 2. 在GitHub上配置Secrets

1. 进入仓库：`https://github.com/victor2025PH/wushizhifu`
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加以下Secrets：

| Secret名称 | 值 | 说明 |
|-----------|-----|------|
| `SSH_PRIVATE_KEY` | `-----BEGIN RSA PRIVATE KEY-----...` | SSH私钥完整内容 |
| `SERVER_HOST` | `your-server-ip` | 服务器IP或域名 |
| `SERVER_USER` | `ubuntu` | 服务器用户名 |
| `SERVER_PATH` | `/home/ubuntu/wushizhifu` | 项目路径 |

### 3. 测试部署

#### 方法1：手动触发
1. 进入 **Actions** 标签页
2. 选择 **Deploy Bot B** 工作流
3. 点击 **Run workflow**
4. 选择分支（main）
5. 点击 **Run workflow** 按钮

#### 方法2：自动触发
推送代码到 `main` 分支：
```bash
git push origin main
```

## 🔍 查看部署日志

1. 进入 **Actions** 标签页
2. 点击最新的工作流运行
3. 查看 **deploy** job 的日志

## ⚠️ 注意事项

1. **SSH密钥权限**
   - 确保服务器上的SSH密钥有正确的权限
   - 确保用户有sudo权限（用于重启服务）

2. **服务名称**
   - 默认服务名：`otc-bot.service`
   - 如果不同，需要修改 `.github/workflows/deploy-botB.yml` 中的服务名

3. **路径配置**
   - 确保 `SERVER_PATH` 指向正确的项目目录
   - 确保 `botB` 目录存在于该路径下

4. **虚拟环境**
   - 如果虚拟环境不存在，脚本会自动创建
   - 确保服务器上已安装 Python 3.11+

## 🚀 部署流程

当代码推送到 `main` 分支时，GitHub Actions 会自动：

1. ✅ 检出代码
2. ✅ 设置Python环境
3. ✅ 通过SSH连接到服务器
4. ✅ 拉取最新代码
5. ✅ 安装/更新依赖
6. ✅ 重启Bot B服务
7. ✅ 验证服务状态

## 📊 部署状态

部署完成后，可以在Actions页面查看：
- ✅ 绿色：部署成功
- ❌ 红色：部署失败（查看日志排查问题）
- ⏸ 黄色：部署进行中

---

**配置完成后，每次推送代码到main分支都会自动部署！**
