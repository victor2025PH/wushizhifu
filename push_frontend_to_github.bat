@echo off
REM 推送前端代碼到 GitHub 倉庫 wushizhifu

echo ==========================================
echo 推送前端代碼到 GitHub
echo 倉庫: https://github.com/victor2025PH/wushizhifu
echo ==========================================
echo.

cd /d "%~dp0wushizhifu-frontend"

if not exist "package.json" (
    echo ❌ 錯誤：未找到前端代碼
    echo 提示：如果前端代碼在 GitHub 上已有，可以跳過此步驟
    echo 或者先運行 organize_and_push.bat 整理項目
    pause
    exit /b 1
)

echo 當前目錄: %CD%
echo.

REM 初始化 Git
if not exist ".git" (
    echo 初始化 Git 倉庫...
    git init
    git branch -M main
    echo ✅ Git 倉庫已初始化
    echo.
)

REM 檢查遠程倉庫
git remote show origin >nul 2>&1
if errorlevel 1 (
    echo 添加遠程倉庫...
    git remote add origin https://github.com/victor2025PH/wushizhifu.git
    echo ✅ 遠程倉庫已添加
) else (
    echo 當前遠程倉庫:
    git remote -v
    echo.
    echo ⚠️  注意：此倉庫可能已有內容
    set /p continue="是否繼續？(Y/N): "
    if /i not "!continue!"=="Y" (
        echo 已取消
        pause
        exit /b
    )
)

echo.
echo 添加文件到 Git...
git add .

echo.
echo 📋 準備提交的文件：
git status
echo.

set /p confirm="確認提交這些文件？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 已取消
    pause
    exit /b
)

echo.
echo 提交更改...
git commit -m "Update: Frontend code for WuShiPay MiniApp"
echo ✅ 已提交
echo.

set /p push="是否要推送到 GitHub？(Y/N): "
if /i "%push%"=="Y" (
    echo.
    echo 推送到 GitHub...
    echo ⚠️  如果遠程倉庫已有內容，可能需要先拉取：
    echo   git pull origin main --allow-unrelated-histories
    echo.
    git push -u origin main
    if %errorlevel% neq 0 (
        echo.
        echo ⚠️  推送失敗，可能需要先拉取遠程更改
        echo 執行以下命令：
        echo   git pull origin main --allow-unrelated-histories
        echo   然後解決衝突後再推送
    ) else (
        echo.
        echo ✅ 推送成功！
        echo.
        echo 訪問倉庫: https://github.com/victor2025PH/wushizhifu
    )
) else (
    echo 已跳過推送
    echo.
    echo 手動推送命令：
    echo   git push -u origin main
)

echo.
pause

