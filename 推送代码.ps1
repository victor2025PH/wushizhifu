# 推送代码到 GitHub

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "推送到 GitHub" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查目录名称
Write-Host "检查目录名称..." -ForegroundColor Yellow
$dirs = Get-ChildItem -Directory | Where-Object { $_.Name -like "bot*" } | Select-Object -ExpandProperty Name
foreach ($dir in $dirs) {
    Write-Host "  发现: $dir" -ForegroundColor Gray
}

# 检查是否有 bota（错误的名称）
if (Test-Path "bota") {
    Write-Host ""
    Write-Host "警告: 发现 'bota' 目录，应该是 'botA'" -ForegroundColor Yellow
    $response = Read-Host "是否重命名为 botA? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Rename-Item -Path "bota" -NewName "botA"
        Write-Host "已重命名 bota -> botA" -ForegroundColor Green
        git add .
        git commit -m "修复：重命名 bota 为 botA"
    }
}

Write-Host ""

# 获取远程信息
Write-Host "获取远程仓库信息..." -ForegroundColor Yellow
git fetch origin 2>&1 | Out-Null

# 检查远程是否有新的提交
$remoteCommits = git log HEAD..origin/main --oneline 2>&1
if ($remoteCommits -and $remoteCommits -notmatch "fatal") {
    Write-Host "远程仓库包含以下新提交：" -ForegroundColor Yellow
    Write-Host $remoteCommits -ForegroundColor Gray
    Write-Host ""
    Write-Host "选择操作：" -ForegroundColor Yellow
    Write-Host "  1. 拉取并合并 (推荐，保留远程更改)" -ForegroundColor White
    Write-Host "  2. 强制推送 (覆盖远程更改)" -ForegroundColor White
    Write-Host "  3. 取消" -ForegroundColor White
    Write-Host ""
    $choice = Read-Host "请输入选项 (1/2/3)"
    
    switch ($choice) {
        "1" {
            Write-Host "正在拉取并合并..." -ForegroundColor Yellow
            git pull origin main --allow-unrelated-histories
            if ($LASTEXITCODE -eq 0) {
                Write-Host "合并成功！" -ForegroundColor Green
                git push -u origin main
            } else {
                Write-Host "合并时出现冲突，请手动解决后推送" -ForegroundColor Red
            }
        }
        "2" {
            Write-Host "警告：这将覆盖远程仓库的所有更改！" -ForegroundColor Red
            $confirm = Read-Host "确认强制推送？(yes/no)"
            if ($confirm -eq "yes") {
                git push -u origin main --force
                Write-Host "强制推送完成！" -ForegroundColor Green
            } else {
                Write-Host "已取消" -ForegroundColor Yellow
            }
        }
        default {
            Write-Host "已取消" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "远程仓库没有新提交，直接推送..." -ForegroundColor Yellow
    git push -u origin main
    if ($LASTEXITCODE -eq 0) {
        Write-Host "推送成功！" -ForegroundColor Green
    } else {
        Write-Host "推送失败，可能需要强制推送" -ForegroundColor Red
        Write-Host "运行: git push -u origin main --force" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "完成" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

