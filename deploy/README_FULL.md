# 完整自動化部署指南

## 🎯 部署目標

自動部署以下服務：
1. **Telegram Bot** (Python) - 後端服務
2. **前端 MiniApp** (React/TypeScript) - 從 GitHub 部署
3. **SSL 證書** - 自動申請 Let's Encrypt 證書
4. **Nginx** - Web 服務器和反向代理

## 📋 前置要求

### 服務器準備

1. **域名解析**
   - 確保域名 `50zf.usdt2026.cc` 已正確解析到服務器 IP 地址
   - DNS A 記錄指向服務器公網 IP

2. **防火牆配置**
   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP (SSL 證書申請需要)
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

3. **系統依賴**（腳本會自動安裝）
   - Python 3.10+
   - Node.js 18+
   - Nginx
   - Certbot

## 🚀 自動化部署步驟

### 方法 1: 完整自動化部署（推薦）

```bash
# 1. 上傳部署腳本到服務器
# 確保 Bot 代碼和 .env 文件在 /home/ubuntu/ 目錄

# 2. 運行完整部署腳本
cd /opt/wushizhifu/bot  # 或您的 Bot 目錄
chmod +x deploy/full_deploy.sh
./deploy/full_deploy.sh
```

腳本會自動執行：
- ✅ 創建項目目錄結構
- ✅ 克隆前端項目（GitHub）
- ✅ 複製 Bot 代碼
- ✅ 設置 Python 虛擬環境
- ✅ 安裝依賴
- ✅ 初始化數據庫
- ✅ 構建前端應用
- ✅ 配置 Nginx
- ✅ 申請 SSL 證書
- ✅ 設置 systemd 服務
- ✅ 啟動所有服務

### 方法 2: 分步驟部署

如果自動化腳本遇到問題，可以手動執行：

#### 步驟 1: 準備環境

```bash
# 創建目錄
sudo mkdir -p /opt/wushizhifu
sudo chown $USER:$USER /opt/wushizhifu
cd /opt/wushizhifu

# 克隆前端
git clone https://github.com/victor2025PH/wushizhifu.git frontend

# 設置 Bot 目錄
mkdir -p bot
# 上傳或複製 Bot 代碼到此目錄
```

#### 步驟 2: 部署 Bot

```bash
cd /opt/wushizhifu/bot

# 設置虛擬環境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 確保 .env 文件存在並設置了 BOT_TOKEN
# nano .env

# 初始化數據庫
python -c "from database.models import init_database; init_database()"

# 創建 systemd 服務
sudo cp deploy/wushipay-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wushipay-bot
sudo systemctl start wushipay-bot
```

#### 步驟 3: 部署前端

```bash
cd /opt/wushizhifu/frontend

# 安裝依賴並構建
npm install
npm run build
```

#### 步驟 4: 配置 Nginx 和 SSL

```bash
# 安裝 Certbot
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 複製 Nginx 配置
sudo cp /opt/wushizhifu/bot/deploy/nginx.conf /etc/nginx/sites-available/wushizhifu
sudo ln -s /etc/nginx/sites-available/wushizhifu /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 編輯配置（修改域名）
sudo nano /etc/nginx/sites-available/wushizhifu

# 測試並重啟
sudo nginx -t
sudo systemctl restart nginx

# 申請 SSL 證書
sudo certbot --nginx -d 50zf.usdt2026.cc --non-interactive --agree-tos --email victor2018zzz@gmail.com --redirect
```

## 📤 將 Bot 代碼上傳到 GitHub

### 選項 1: 在服務器上設置 GitHub 倉庫

```bash
cd /opt/wushizhifu/bot
chmod +x deploy/setup_github.sh
./deploy/setup_github.sh
```

然後按照提示添加遠程倉庫並推送。

### 選項 2: 從本地推送

在本地機器上：

```bash
cd /path/to/your/bot
git init
git add .
git commit -m "Initial commit: WuShiPay Bot"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## ✅ 驗證部署

### 1. 檢查服務狀態

```bash
# Bot 服務
sudo systemctl status wushipay-bot

# Nginx 服務
sudo systemctl status nginx

# 查看 Bot 日誌
sudo journalctl -u wushipay-bot -f
```

### 2. 檢查網站

訪問：`https://50zf.usdt2026.cc`

### 3. 測試 Bot

在 Telegram 中發送 `/start` 給您的 Bot，確認正常運行。

## 🔄 更新部署

### 更新前端

```bash
cd /opt/wushizhifu/frontend
git pull
npm install
npm run build
sudo systemctl reload nginx
```

### 更新 Bot

```bash
cd /opt/wushizhifu/bot
# 如果有 Git 倉庫
git pull
# 或手動上傳新代碼

source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart wushipay-bot
```

## 🛠️ 故障排除

### SSL 證書申請失敗

1. 檢查域名解析：
   ```bash
   dig 50zf.usdt2026.cc
   ping 50zf.usdt2026.cc
   ```

2. 檢查端口是否開放：
   ```bash
   sudo ufw status
   sudo netstat -tlnp | grep -E ':(80|443)'
   ```

3. 檢查 Nginx 配置：
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

### Bot 無法啟動

1. 檢查日誌：
   ```bash
   sudo journalctl -u wushipay-bot -n 50
   ```

2. 檢查 .env 文件：
   ```bash
   cat /opt/wushizhifu/bot/.env
   ```

3. 手動測試運行：
   ```bash
   cd /opt/wushizhifu/bot
   source venv/bin/activate
   python bot.py
   ```

### 前端無法訪問

1. 檢查 Nginx 錯誤日誌：
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

2. 檢查文件權限：
   ```bash
   ls -la /opt/wushizhifu/frontend/dist
   sudo chown -R www-data:www-data /opt/wushizhifu/frontend/dist
   ```

3. 檢查 Nginx 配置：
   ```bash
   sudo nginx -t
   ```

## 📝 注意事項

1. **.env 文件不會上傳到 GitHub**（已在 .gitignore 中排除）
2. **SSL 證書自動續期**：Certbot 會設置自動續期
3. **備份數據庫**：定期備份 `/opt/wushizhifu/bot/wushipay.db`
4. **日誌管理**：定期清理日誌文件避免磁盤空間不足

## 🔒 安全建議

1. 使用強密碼
2. 定期更新系統和依賴
3. 配置防火牆規則
4. 定期備份數據
5. 監控服務狀態

