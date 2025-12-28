# 修复嵌入 Git 仓库问题
# 移除 botA 和 botB 中的 .git 文件夹

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "修复嵌入 Git 仓库问题" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 botA
if (Test-Path ".\botA\.git") {
    Write-Host "发现 botA/.git 文件夹，正在移除..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .\botA\.git
    Write-Host "✅ 已移除 botA/.git" -ForegroundColor Green
} else {
    Write-Host "ℹ️  botA/.git 不存在" -ForegroundColor Gray
}

Write-Host ""

# 检查 botB
if (Test-Path ".\botB\.git") {
    Write-Host "发现 botB/.git 文件夹，正在移除..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .\botB\.git
    Write-Host "✅ 已移除 botB/.git" -ForegroundColor Green
} else {
    Write-Host "ℹ️  botB/.git 不存在" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "修复完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "  1. git add ." -ForegroundColor White
Write-Host "  2. git commit -m `"修复：移除嵌入 Git 仓库`"" -ForegroundColor White
Write-Host "  3. git push origin main" -ForegroundColor White
Write-Host ""

