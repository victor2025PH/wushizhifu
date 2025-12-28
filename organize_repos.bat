@echo off
REM 整理項目：將前端和 Bot 代碼分離到不同目錄

echo ==========================================
echo 整理項目結構：分離前端和 Bot 代碼
echo ==========================================
echo.

set "CURRENT_DIR=%~dp0"
set "PARENT_DIR=%CURRENT_DIR%.."
set "BOT_DIR=%CURRENT_DIR%wushizhifu-bot"
set "FRONTEND_DIR=%CURRENT_DIR%wushizhifu-frontend"

echo 當前目錄: %CURRENT_DIR%
echo Bot 目錄: %BOT_DIR%
echo 前端目錄: %FRONTEND_DIR%
echo.

REM 創建 Bot 目錄
if not exist "%BOT_DIR%" (
    mkdir "%BOT_DIR%"
    echo ✅ 創建 Bot 目錄
)

REM 創建前端目錄
if not exist "%FRONTEND_DIR%" (
    mkdir "%FRONTEND_DIR%"
    echo ✅ 創建前端目錄
)

echo.
echo 📋 開始複製 Bot 文件...
echo.

REM 複製 Bot 相關文件
copy /Y bot.py "%BOT_DIR%\" >nul 2>&1
copy /Y config.py "%BOT_DIR%\" >nul 2>&1
copy /Y requirements.txt "%BOT_DIR%\" >nul 2>&1
copy /Y *.md "%BOT_DIR%\" >nul 2>&1
copy /Y *.bat "%BOT_DIR%\" >nul 2>&1
copy /Y .gitignore "%BOT_DIR%\" >nul 2>&1
copy /Y .gitattributes "%BOT_DIR%\" >nul 2>&1

REM 複製 Bot 目錄
xcopy /E /I /Y database "%BOT_DIR%\database\" >nul 2>&1
xcopy /E /I /Y handlers "%BOT_DIR%\handlers\" >nul 2>&1
xcopy /E /I /Y keyboards "%BOT_DIR%\keyboards\" >nul 2>&1
xcopy /E /I /Y middleware "%BOT_DIR%\middleware\" >nul 2>&1
xcopy /E /I /Y services "%BOT_DIR%\services\" >nul 2>&1
xcopy /E /I /Y utils "%BOT_DIR%\utils\" >nul 2>&1
xcopy /E /I /Y deploy "%BOT_DIR%\deploy\" >nul 2>&1

echo ✅ Bot 文件已複製
echo.

REM 檢查是否有前端代碼
if exist "wushizhifu-full" (
    echo 📋 發現前端代碼目錄，開始複製...
    xcopy /E /I /Y "wushizhifu-full\*" "%FRONTEND_DIR%\" /EXCLUDE:exclude_list.txt >nul 2>&1
    echo ✅ 前端文件已複製
) else (
    echo ⚠️  未找到前端代碼目錄 wushizhifu-full
    echo 將從 GitHub 克隆前端代碼
)

echo.
echo ==========================================
echo ✅ 文件整理完成！
echo ==========================================
echo.
echo 📁 目錄結構：
echo.
echo %CURRENT_DIR%
echo ├── wushizhifu-bot\      (Bot 代碼，推送到 wushizhifu_bot 倉庫)
echo └── wushizhifu-frontend\ (前端代碼，推送到 wushizhifu 倉庫)
echo.
echo 下一步：
echo 1. 檢查 wushizhifu-bot 目錄
echo 2. 檢查 wushizhifu-frontend 目錄
echo 3. 分別推送到 GitHub
echo.
pause

