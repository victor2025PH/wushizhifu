# 清空 GitHub 仓库并重新推送

## 🗑️ 方法 1: 使用 Git 命令强制推送（最简单）

这会用本地代码完全替换远程仓库：

```bash
# 1. 确保本地代码已提交
git add .
git commit -m "准备重新推送所有文件"

# 2. 强制推送，覆盖远程仓库
git push -u origin main --force
```

⚠️ **注意**：`--force` 会覆盖远程仓库的所有内容。

## 🗑️ 方法 2: 创建空分支覆盖（推荐用于完全清空）

```bash
# 1. 创建临时空分支
git checkout --orphan temp-branch

# 2. 删除所有文件（从索引中）
git rm -rf .

# 3. 提交空分支
git commit --allow-empty -m "清空仓库"

# 4. 切换到 main 分支
git checkout main

# 5. 删除远程 main 分支
git push origin main --delete

# 6. 推送本地 main 到远程（创建新的 main）
git push -u origin main --force
```

## 🗑️ 方法 3: 在 GitHub 网页上删除（最简单直观）

### 步骤：

1. 打开 GitHub 仓库：https://github.com/victor2025PH/wushizhifu
2. 点击仓库中的文件
3. 点击文件旁边的垃圾桶图标删除文件
4. 或者使用 GitHub 的批量删除功能

### 批量删除（通过命令行更简单）：

```bash
# 直接强制推送覆盖即可
git push -u origin main --force
```

## 📋 完整操作步骤（推荐）

### 步骤 1: 确保本地代码完整

```powershell
# 检查状态
git status

# 如果有未提交的更改
git add .
git commit -m "最终提交：分离 botA 和 botB"
```

### 步骤 2: 检查目录结构

```powershell
# 确认目录名称正确
Get-ChildItem -Directory | Where-Object { $_.Name -like "bot*" }

# 如果有 bota，重命名为 botA
if (Test-Path "bota") {
    Rename-Item -Path "bota" -NewName "botA"
    git add .
    git commit -m "修复：重命名 bota 为 botA"
}
```

### 步骤 3: 强制推送到 GitHub（覆盖远程）

```bash
git push -u origin main --force
```

## ✅ 验证

推送成功后：
1. 访问 https://github.com/victor2025PH/wushizhifu
2. 确认文件结构：
   - `botA/` 目录存在
   - `botB/` 目录存在
   - `.github/workflows/` 存在
   - `README.md` 存在

## 🔍 如果遇到错误

### 错误：权限被拒绝
```bash
# 检查远程 URL
git remote -v

# 如果需要，更新为 HTTPS
git remote set-url origin https://github.com/victor2025PH/wushizhifu.git
```

### 错误：需要身份验证
GitHub 现在要求使用 Personal Access Token：
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 生成新 token（需要 `repo` 权限）
3. 推送时使用 token 作为密码

