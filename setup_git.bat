@echo off
REM Windows 批次檔：設置 Git 並準備推送到 GitHub

echo ==========================================
echo 設置 Git 倉庫並準備推送到 GitHub
echo ==========================================
echo.

REM 檢查是否已初始化 Git
if not exist ".git" (
    echo 初始化 Git 倉庫...
    git init
    git branch -M main
    echo ✅ Git 倉庫已初始化
    echo.
) else (
    echo ✅ Git 倉庫已存在
    echo.
)

REM 添加所有文件
echo 添加文件到 Git...
git add .

REM 顯示狀態
echo.
echo 📋 準備提交的文件：
git status
echo.

REM 提示用戶確認
set /p confirm="確認提交這些文件？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 已取消
    pause
    exit /b
)

REM 提交
echo.
echo 提交更改...
git commit -m "Initial commit: WuShiPay Telegram Bot with full features"
echo ✅ 已提交
echo.

REM 檢查遠程倉庫
git remote show origin >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 遠程倉庫已設置
    git remote -v
    echo.
    set /p push="是否要推送到 GitHub？(Y/N): "
    if /i "%push%"=="Y" (
        git push -u origin main
    )
) else (
    echo ⚠️  未設置遠程倉庫
    echo.
    echo 請執行以下命令設置遠程倉庫：
    echo   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
    echo   git push -u origin main
    echo.
)

echo.
echo ✅ 完成！
pause

