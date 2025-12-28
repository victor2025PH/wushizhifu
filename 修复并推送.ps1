# 修复 Git 配置并推送到 GitHub

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "配置 Git 远程仓库并推送" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查远程仓库
Write-Host "检查远程仓库配置..." -ForegroundColor Yellow
$remote = git remote -v
if ($remote -match "origin") {
    Write-Host "✅ 远程仓库已配置" -ForegroundColor Green
    Write-Host $remote -ForegroundColor Gray
} else {
    Write-Host "⚠️  远程仓库未配置，正在添加..." -ForegroundColor Yellow
    git remote add origin https://github.com/victor2025PH/wushizhifu.git
    Write-Host "✅ 已添加远程仓库" -ForegroundColor Green
}

Write-Host ""

# 2. 检查 botA/.git
Write-Host "检查 botA/.git..." -ForegroundColor Yellow
if (Test-Path ".\botA\.git") {
    Write-Host "⚠️  发现 botA/.git，正在移除..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .\botA\.git
    Write-Host "✅ 已移除 botA/.git" -ForegroundColor Green
    
    # 从索引中移除并重新添加
    Write-Host "修复 botA 子模块问题..." -ForegroundColor Yellow
    git rm --cached botA 2>$null
    git add botA/
    Write-Host "✅ botA 已修复" -ForegroundColor Green
} else {
    Write-Host "✅ botA/.git 不存在" -ForegroundColor Green
}

Write-Host ""

# 3. 检查 botB/.git
Write-Host "检查 botB/.git..." -ForegroundColor Yellow
if (Test-Path ".\botB\.git") {
    Write-Host "⚠️  发现 botB/.git，正在移除..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .\botB\.git
    Write-Host "✅ 已移除 botB/.git" -ForegroundColor Green
} else {
    Write-Host "✅ botB/.git 不存在" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "修复完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "  1. git add ." -ForegroundColor White
Write-Host "  2. git commit -m `"修复：移除嵌入 Git 仓库`"" -ForegroundColor White
Write-Host "  3. git push -u origin main" -ForegroundColor White
Write-Host ""

