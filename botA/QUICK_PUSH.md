# 快速推送指南 - 推送到現有倉庫

## 🎯 最簡單的方式：推送到 bot/ 子目錄

### 步驟 1: 在本地準備

由於現有倉庫已經有前端代碼，我們有兩個選擇：

**選擇 A: 創建新的 Bot 專用倉庫（推薦）**

```powershell
# 在 d:\wushizhifu 目錄
cd d:\wushizhifu

# 初始化並推送
git init
git branch -M main
git add .
git commit -m "Initial commit: WuShiPay Telegram Bot"

# 在 GitHub 創建新倉庫 wushizhifu-bot，然後：
git remote add origin https://github.com/victor2025PH/wushizhifu-bot.git
git push -u origin main
```

**選擇 B: 添加到現有倉庫的 bot/ 目錄**

```powershell
# 1. 先克隆現有倉庫到另一個位置
cd d:\
git clone https://github.com/victor2025PH/wushizhifu.git wushizhifu-full
cd wushizhifu-full

# 2. 複製 Bot 代碼到 bot/ 目錄
mkdir bot
# 然後手動複製所有 Bot 文件到 bot/ 目錄（使用文件管理器或命令）

# 3. 提交並推送
git add bot/
git commit -m "Add Telegram Bot in bot/ directory"
git push origin main
```

## 📤 我推薦的方式（最簡單）

**直接在服務器上部署，不需要推送到 GitHub：**

```bash
# 在服務器上執行
cd /home/ubuntu/wushizhifu

# 1. 克隆前端（已有倉庫）
git clone https://github.com/victor2025PH/wushizhifu.git frontend

# 2. 創建 Bot 目錄
mkdir bot

# 3. 使用 WinSCP 或其他工具上傳 Bot 代碼到 /home/ubuntu/wushizhifu/bot/

# 4. 執行部署腳本
cd bot
chmod +x deploy/*.sh
./deploy/deploy_home.sh
```

這樣：
- ✅ 前端代碼從 GitHub 自動拉取
- ✅ Bot 代碼直接上傳到服務器
- ✅ 不需要處理 Git 合併問題
- ✅ 部署最快

您想使用哪種方式？

