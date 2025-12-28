# 快速部署指南

## 🎯 當前狀態

- ✅ 域名解析正常：50zf.usdt2026.cc → 165.154.203.182
- ✅ 服務器環境已準備
- ⚠️ Bot 代碼需要上傳到服務器

## 📋 執行步驟

### 在服務器上執行以下命令：

```bash
# 1. 創建項目目錄
sudo mkdir -p /opt/wushizhifu
sudo chown $USER:$USER /opt/wushizhifu
cd /opt/wushizhifu

# 2. 克隆前端項目
git clone https://github.com/victor2025PH/wushizhifu.git frontend

# 3. 創建 Bot 目錄
mkdir -p bot
cd bot

# 4. 如果 Bot 代碼在 home 目錄，複製過來
# 或者使用 Git 克隆 Bot 倉庫
# git clone <your-bot-repo-url> .

# 5. 如果代碼在其他位置，請先上傳或複製到此目錄
# 確保包含以下文件：
# - bot.py
# - config.py
# - requirements.txt
# - deploy/ 文件夾
# - 所有其他項目文件

# 6. 設置 .env 文件（如果還沒有）
# 確保 .env 文件存在並包含 BOT_TOKEN
nano .env

# 7. 給部署腳本執行權限
chmod +x deploy/*.sh

# 8. 執行完整部署
./deploy/full_deploy.sh
```

## 📤 上傳代碼方式

### 方式 1: 使用 Git（推薦）

如果將 Bot 代碼推送到 GitHub，然後在服務器上克隆：

```bash
# 在服務器上
cd /opt/wushizhifu/bot
git clone <your-bot-github-repo-url> .
# 然後複製 .env 文件
cp ~/.env .env  # 如果 .env 在 home 目錄
```

### 方式 2: 使用 SCP 上傳

在本地機器（Windows）上：

```powershell
# 使用 PowerShell 或 Git Bash
cd d:\wushizhifu
scp -r * ubuntu@165.154.203.182:/opt/wushizhifu/bot/
```

### 方式 3: 使用 WinSCP

1. 下載並安裝 WinSCP
2. 連接到服務器：`ubuntu@165.154.203.182`
3. 上傳所有文件到 `/opt/wushizhifu/bot/`

## 🔍 檢查清單

部署前確保：
- [ ] Bot 代碼已上傳到服務器
- [ ] .env 文件存在並設置了 BOT_TOKEN
- [ ] deploy/ 文件夾存在
- [ ] 域名 50zf.usdt2026.cc 已解析到服務器 IP

