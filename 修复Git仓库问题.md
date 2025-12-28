# 修复嵌入 Git 仓库问题

## ⚠️ 问题说明

警告 `warning: adding embedded git repository: botA` 表示 `botA` 目录本身是一个 Git 仓库（有自己的 `.git` 文件夹）。

这会导致：
- botA 的内容不会被正确跟踪
- 克隆主仓库时不会包含 botA 的内容

## 🔧 解决方案

### 方法 1: 移除 botA 中的 .git 文件夹（推荐）

```powershell
# 移除 botA 中的 Git 仓库
Remove-Item -Recurse -Force .\botA\.git

# 检查 botB 是否也有同样的问题
if (Test-Path .\botB\.git) {
    Remove-Item -Recurse -Force .\botB\.git
    Write-Host "已移除 botB 中的 .git 文件夹"
}
```

### 方法 2: 使用 Git 命令移除

```bash
# 从 Git 索引中移除（如果需要）
git rm --cached botA

# 移除 botA 中的 .git 文件夹
rm -rf botA/.git

# 检查 botB
if [ -d "botB/.git" ]; then
    rm -rf botB/.git
    echo "已移除 botB 中的 .git 文件夹"
fi

# 重新添加
git add botA botB
```

## 📋 完整修复步骤

### 在 PowerShell 中执行：

```powershell
# 1. 移除 botA 中的 .git 文件夹
if (Test-Path .\botA\.git) {
    Remove-Item -Recurse -Force .\botA\.git
    Write-Host "✅ 已移除 botA/.git"
} else {
    Write-Host "ℹ️  botA/.git 不存在"
}

# 2. 检查并移除 botB 中的 .git 文件夹
if (Test-Path .\botB\.git) {
    Remove-Item -Recurse -Force .\botB\.git
    Write-Host "✅ 已移除 botB/.git"
} else {
    Write-Host "ℹ️  botB/.git 不存在"
}

# 3. 检查 .gitignore，确保 .git 被忽略
if (!(Select-String -Path .\.gitignore -Pattern "^\.git/$" -Quiet)) {
    Add-Content -Path .\.gitignore -Value "`.git/"
    Write-Host "✅ 已添加 .git/ 到 .gitignore"
}

# 4. 重新添加文件
git add botA botB

# 5. 提交
git commit -m "修复：移除 botA 和 botB 中的嵌入 Git 仓库"

# 6. 推送
git push origin main
```

### 或者在 Git Bash/CMD 中：

```bash
# 1. 移除 .git 文件夹
rm -rf botA/.git botB/.git

# 2. 重新添加
git add botA botB

# 3. 提交并推送
git commit -m "修复：移除 botA 和 botB 中的嵌入 Git 仓库"
git push origin main
```

## ✅ 验证

修复后，再次执行 `git add .` 应该不再有嵌入仓库的警告。

## 📝 关于 CRLF 警告

CRLF 警告是正常的，不影响功能。如果想消除：

```bash
git config core.autocrlf input
git add --renormalize .
```

