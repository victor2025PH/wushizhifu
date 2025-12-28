# 配置 Git 远程仓库

## 🔍 检查当前远程仓库配置

```bash
git remote -v
```

如果输出为空或没有 `origin`，需要添加远程仓库。

## 🔧 添加远程仓库

根据您的 GitHub 仓库地址 `https://github.com/victor2025PH/wushizhifu`，执行：

### 方法 1: 添加新的远程仓库

```bash
git remote add origin https://github.com/victor2025PH/wushizhifu.git
```

### 方法 2: 如果 origin 已存在但 URL 错误

```bash
# 查看当前配置
git remote -v

# 更新 URL
git remote set-url origin https://github.com/victor2025PH/wushizhifu.git
```

### 方法 3: 使用 SSH（如果已配置 SSH 密钥）

```bash
git remote add origin git@github.com:victor2025PH/wushizhifu.git
```

## 📤 推送到 GitHub

```bash
# 推送并设置上游分支
git push -u origin main
```

## ⚠️ 注意：关于 botA 子模块问题

从提交信息看，`botA` 显示为 `mode 160000`，这表示它仍然被视为子模块。需要修复：

```bash
# 1. 从 Git 索引中移除 botA
git rm --cached botA

# 2. 确认 botA/.git 已被删除
# (如果还存在，需要手动删除)

# 3. 重新添加 botA 作为普通目录
git add botA/

# 4. 提交更改
git commit -m "修复：将 botA 从子模块改为普通目录"

# 5. 推送
git push -u origin main
```

## 🔍 完整检查清单

```bash
# 1. 检查远程仓库
git remote -v

# 2. 如果没有 origin，添加它
git remote add origin https://github.com/victor2025PH/wushizhifu.git

# 3. 检查 botA/.git 是否存在
# Windows PowerShell:
Test-Path .\botA\.git
# 如果返回 True，需要删除：
Remove-Item -Recurse -Force .\botA\.git

# 4. 修复 botA 子模块问题
git rm --cached botA
git add botA/

# 5. 提交并推送
git commit -m "修复：将 botA 从子模块改为普通目录"
git push -u origin main
```

