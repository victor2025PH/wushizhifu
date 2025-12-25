# 上傳 Bot 代碼到服務器指南

## 📤 從本地機器上傳代碼到服務器

### 步驟 1: 在本地機器準備代碼

確保您在本地機器的 Bot 項目目錄中（包含所有文件）。

### 步驟 2: 上傳代碼到服務器

**在您的本地機器上執行（Windows PowerShell 或 CMD）：**

```powershell
# 替換 your-server-ip 為您的服務器 IP (例如: 165.154.203.182)
# 或者如果使用域名：50zf.usdt2026.cc

# 方法 1: 使用 scp (如果已安裝)
scp -r * ubuntu@165.154.203.182:/home/ubuntu/bot/

# 方法 2: 使用 WinSCP 或其他圖形化工具
# 連接到服務器，然後上傳所有文件到 /home/ubuntu/bot/
```

**或者在服務器上直接使用 Git（推薦）：**

如果您的 Bot 代碼已經在 GitHub 上：

```bash
# 在服務器上執行
cd ~
git clone <your-bot-repo-url> bot
# 然後將 .env 文件複製進去
```

### 步驟 3: 執行部署腳本

**在服務器上執行：**

```bash
cd ~/bot  # 或 /home/ubuntu/bot
chmod +x deploy/*.sh
./deploy/full_deploy.sh
```

## 🚀 快速部署命令（服務器端）

如果您想直接在服務器上從頭開始，可以執行：

```bash
# 1. 創建目錄
sudo mkdir -p /opt/wushizhifu
sudo chown $USER:$USER /opt/wushizhifu

# 2. 如果代碼在 ~/bot，直接使用
cd ~/bot
chmod +x deploy/*.sh
./deploy/full_deploy.sh
```

