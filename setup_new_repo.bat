@echo off
REM 設置新的 Git 倉庫用於 Bot 代碼（獨立倉庫）

echo ==========================================
echo 設置 WuShiPay Bot 獨立 Git 倉庫
echo ==========================================
echo.
echo 這將創建一個新的 Git 倉庫專門用於 Bot 代碼
echo 避免與前端項目混合
echo.
echo 前端倉庫: https://github.com/victor2025PH/wushizhifu
echo Bot 倉庫: 建議創建 wushizhifu-bot 或 wushizhifu-telegram-bot
echo.

REM 檢查是否已初始化 Git
if exist ".git" (
    echo ⚠️  當前目錄已經是 Git 倉庫
    set /p continue="是否要重新初始化？(Y/N): "
    if /i not "!continue!"=="Y" (
        echo 已取消
        pause
        exit /b
    )
    rmdir /s /q .git
    echo ✅ 已移除舊的 Git 配置
    echo.
)

echo 初始化新的 Git 倉庫...
git init
git branch -M main
echo ✅ Git 倉庫已初始化
echo.

REM 檢查 README_BOT.md 是否存在，如果存在則使用它作為 README
if exist "README_BOT.md" (
    echo 使用 README_BOT.md 作為 README.md...
    copy /Y README_BOT.md README.md.temp
    if exist "README.md" (
        del README.md
    )
    ren README_BOT.md README.md
    echo ✅ README 已設置
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
git commit -m "Initial commit: WuShiPay Telegram Bot - Complete implementation with database, handlers, admin system, and deployment scripts"
echo ✅ 已提交
echo.

REM 提示設置遠程倉庫
echo.
echo ==========================================
echo 下一步：在 GitHub 創建新倉庫
echo ==========================================
echo.
echo 1. 訪問: https://github.com/new
echo 2. 倉庫名稱: wushizhifu-bot (或您喜歡的名稱)
echo 3. 描述: WuShiPay Telegram Bot
echo 4. 選擇 Public 或 Private
echo 5. 不要初始化 README
echo 6. 創建倉庫
echo.
set /p repo_name="GitHub 倉庫名稱（例如: wushizhifu-bot）: "
if "%repo_name%"=="" set repo_name=wushizhifu-bot

echo.
set /p username="GitHub 用戶名（victor2025PH）: "
if "%username%"=="" set username=victor2025PH

echo.
echo 添加遠程倉庫...
git remote add origin https://github.com/%username%/%repo_name%.git
echo ✅ 遠程倉庫已添加: https://github.com/%username%/%repo_name%.git
echo.

REM 提示推送
echo.
set /p push="是否要推送到 GitHub？(Y/N): "
if /i "%push%"=="Y" (
    echo.
    echo 推送到 GitHub...
    git push -u origin main
    if %errorlevel% equ 0 (
        echo.
        echo ✅ 推送成功！
        echo.
        echo 訪問倉庫: https://github.com/%username%/%repo_name%
    ) else (
        echo.
        echo ⚠️  推送失敗，請檢查：
        echo   1. 倉庫是否已創建
        echo   2. 是否有寫入權限
        echo   3. 認證信息是否正確
        echo.
        echo 手動推送命令：
        echo   git push -u origin main
    )
) else (
    echo 已跳過推送
    echo.
    echo 手動推送命令：
    echo   git push -u origin main
)

echo.
echo ✅ 完成！
echo.
echo 倉庫地址: https://github.com/%username%/%repo_name%
pause

