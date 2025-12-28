# 配置 GitHub Secrets 指南

## ❌ 错误信息

GitHub Actions 部署失败，错误：`Error: missing server host`

这表示 GitHub Secrets 没有配置。

## ✅ 解决步骤

### 1. 进入 GitHub 仓库设置

访问：https://github.com/victor2025PH/wushizhifu/settings/secrets/actions

或者：
1. 打开仓库：https://github.com/victor2025PH/wushizhifu
2. 点击 `Settings`（设置）
3. 左侧菜单选择 `Secrets and variables` → `Actions`
4. 点击 `New repository secret`（新建仓库密钥）

### 2. 添加必需的 Secrets

需要添加以下 4 个 Secrets：

#### Secret 1: SERVER_HOST
- **Name**: `SERVER_HOST`
- **Value**: `165.154.203.182`（您的服务器 IP）

#### Secret 2: SERVER_USER
- **Name**: `SERVER_USER`
- **Value**: `ubuntu`（SSH 用户名）

#### Secret 3: SSH_PRIVATE_KEY
- **Name**: `SSH_PRIVATE_KEY`
- **Value**: 您的 SSH 私钥内容（见下方说明）

#### Secret 4: SSH_PORT（可选）
- **Name**: `SSH_PORT`
- **Value**: `22`（默认 SSH 端口，如果使用默认端口可以省略）

## 🔑 获取 SSH 私钥

### 方法 1: 如果已有 SSH 密钥

**Windows PowerShell:**
```powershell
# 查看公钥（用于验证）
cat ~/.ssh/id_rsa.pub

# 查看私钥（复制内容）
cat ~/.ssh/id_rsa
```

**或者手动查看：**
- 路径：`C:\Users\您的用户名\.ssh\id_rsa`
- 用记事本打开，复制全部内容

### 方法 2: 如果没有 SSH 密钥，生成新的

**在本地机器（Windows PowerShell）上：**

```powershell
# 生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions"

# 按提示操作（可以按 Enter 使用默认路径）
# 设置密码（可选，建议留空直接按 Enter）

# 查看私钥
cat ~/.ssh/id_rsa

# 查看公钥
cat ~/.ssh/id_rsa.pub
```

### 方法 3: 将公钥添加到服务器

```bash
# SSH 到服务器
ssh ubuntu@165.154.203.182

# 添加公钥到 authorized_keys
# 将本地 id_rsa.pub 的内容添加到服务器
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "您的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**或者使用 ssh-copy-id（如果在 Linux/Mac）：**
```bash
ssh-copy-id ubuntu@165.154.203.182
```

## 📝 配置步骤详情

### 步骤 1: 添加 SERVER_HOST

1. 点击 `New repository secret`
2. Name: `SERVER_HOST`
3. Secret: `165.154.203.182`
4. 点击 `Add secret`

### 步骤 2: 添加 SERVER_USER

1. 点击 `New repository secret`
2. Name: `SERVER_USER`
3. Secret: `ubuntu`
4. 点击 `Add secret`

### 步骤 3: 添加 SSH_PRIVATE_KEY

1. 点击 `New repository secret`
2. Name: `SSH_PRIVATE_KEY`
3. Secret: 粘贴您的 SSH 私钥（包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----` 行）
4. 点击 `Add secret`

**私钥格式示例：**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
...（更多行）...
-----END OPENSSH PRIVATE KEY-----
```

### 步骤 4: 添加 SSH_PORT（可选）

1. 点击 `New repository secret`
2. Name: `SSH_PORT`
3. Secret: `22`
4. 点击 `Add secret`

## ✅ 验证配置

配置完成后：

1. 返回仓库 Actions 页面：https://github.com/victor2025PH/wushizhifu/actions
2. 找到失败的 workflow
3. 点击 `Re-run jobs`（重新运行）
4. 或者推送新的更改触发自动部署

## 🔍 测试 SSH 连接

在配置之前，先测试 SSH 连接是否正常：

```bash
# 测试 SSH 连接（使用密码）
ssh ubuntu@165.154.203.182

# 如果连接成功，说明服务器和用户名正确
```

## ⚠️ 常见问题

### 问题 1: 私钥格式错误

**错误**: SSH 连接失败

**解决**: 
- 确保私钥包含完整的 BEGIN 和 END 行
- 确保没有多余的空格或换行
- 如果使用 Windows，确保行尾是 LF 而不是 CRLF

### 问题 2: 权限错误

**错误**: Permission denied

**解决**:
```bash
# 在服务器上
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### 问题 3: 服务器连接超时

**错误**: Connection timeout

**解决**:
- 检查服务器 IP 是否正确
- 检查服务器防火墙是否允许 SSH 连接
- 检查 SSH 端口是否正确

## 🚀 配置完成后

配置完 Secrets 后：

1. 返回 Actions 页面
2. 点击失败的 workflow
3. 点击 `Re-run jobs` → `Re-run failed jobs`
4. 等待部署完成

或者推送一个小更改触发自动部署：
```bash
# 创建一个空提交
git commit --allow-empty -m "触发部署测试"
git push origin main
```

