# 清空 GitHub 仓库并重新推送

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "清空 GitHub 并重新推送" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查目录名称
Write-Host "步骤 1: 检查目录名称..." -ForegroundColor Yellow
$dirs = Get-ChildItem -Directory | Where-Object { $_.Name -like "bot*" } | Select-Object -ExpandProperty Name
foreach ($dir in $dirs) {
    Write-Host "  发现: $dir" -ForegroundColor Gray
}

# 检查是否有 bota（错误的名称）
if (Test-Path "bota") {
    Write-Host ""
    Write-Host "警告: 发现 'bota' 目录，应该是 'botA'" -ForegroundColor Yellow
    Rename-Item -Path "bota" -NewName "botA" -Force
    Write-Host "已自动重命名 bota -> botA" -ForegroundColor Green
    git add .
    git commit -m "修复：重命名 bota 为 botA" 2>&1 | Out-Null
}

Write-Host ""

# 2. 检查本地更改
Write-Host "步骤 2: 检查本地更改..." -ForegroundColor Yellow
$status = git status --short
if ($status) {
    Write-Host "发现未提交的更改，正在提交..." -ForegroundColor Yellow
    git add .
    git commit -m "最终提交：分离 botA 和 botB" 2>&1 | Out-Null
    Write-Host "已提交所有更改" -ForegroundColor Green
} else {
    Write-Host "没有未提交的更改" -ForegroundColor Green
}

Write-Host ""

# 3. 确认操作
Write-Host "步骤 3: 准备强制推送到 GitHub" -ForegroundColor Yellow
Write-Host "这将覆盖远程仓库的所有内容！" -ForegroundColor Red
Write-Host ""
$confirm = Read-Host "确认继续？(yes/no)"
if ($confirm -ne "yes" -and $confirm -ne "y") {
    Write-Host "已取消操作" -ForegroundColor Yellow
    exit
}

Write-Host ""

# 4. 强制推送
Write-Host "步骤 4: 正在强制推送..." -ForegroundColor Yellow
Write-Host ""
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "推送成功！" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "请访问以下链接验证：" -ForegroundColor Yellow
    Write-Host "https://github.com/victor2025PH/wushizhifu" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "推送失败" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "  1. 需要身份验证（GitHub Personal Access Token）" -ForegroundColor White
    Write-Host "  2. 网络连接问题" -ForegroundColor White
    Write-Host "  3. 权限不足" -ForegroundColor White
    Write-Host ""
    Write-Host "请检查错误信息并重试" -ForegroundColor Yellow
}

Write-Host ""

