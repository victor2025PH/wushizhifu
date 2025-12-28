# 部署指南

本文檔說明如何將 WuShiPay Telegram Bot 部署到服務器上。

## 📋 前置要求

- Ubuntu 20.04+ 或 Debian 11+ 服務器
- Python 3.10+
- Node.js 18+ (僅用於前端部署)
- Git
- sudo 權限

## 🚀 快速部署（自動化）

### 1. 克隆倉庫到服務器

```bash
cd /opt
git clone https://github.com/victor2025PH/wushizhifu.git frontend
cd wushizhifu
git clone <your-bot-repo-url> bot  # 或將現有代碼上傳到服務器
```

### 2. 部署 Telegram Bot

```bash
cd /opt/wushizhifu/bot
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### 3. 設置環境變數

編輯 `.env` 文件：
```bash
nano .env
```

設置以下內容：
```env
BOT_TOKEN=your_telegram_bot_token_here
```

### 4. 測試運行

```bash
source venv/bin/activate
python bot.py
```

### 5. 設置為系統服務（推薦）

```bash
sudo cp wushipay-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wushipay-bot
sudo systemctl start wushipay-bot
sudo systemctl status wushipay-bot
```

## 🌐 部署前端應用（可選）

### 1. 構建前端

```bash
cd /opt/wushizhifu/frontend
npm install
npm run build
```

### 2. 配置 Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/wushizhifu
sudo ln -s /etc/nginx/sites-available/wushizhifu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. 設置文件權限

```bash
sudo chown -R www-data:www-data /opt/wushizhifu/frontend/dist
```

## 🔧 手動部署步驟

如果自動化腳本無法運行，可以手動執行以下步驟：

### 1. 安裝 Python 依賴

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 初始化數據庫

```bash
python3 -c "from database.models import init_database; init_database()"
```

### 3. 配置環境變數

創建 `.env` 文件並設置 `BOT_TOKEN`

### 4. 運行 Bot

```bash
source venv/bin/activate
python bot.py
```

## 📊 監控和日誌

### 查看服務狀態

```bash
sudo systemctl status wushipay-bot
```

### 查看日誌

```bash
sudo journalctl -u wushipay-bot -f
```

### 重啟服務

```bash
sudo systemctl restart wushipay-bot
```

## 🔒 安全建議

1. **防火牆配置**
   ```bash
   sudo ufw allow 22/tcp  # SSH
   sudo ufw allow 80/tcp  # HTTP (如果部署前端)
   sudo ufw allow 443/tcp # HTTPS (如果部署前端)
   sudo ufw enable
   ```

2. **SSL 證書（如果部署前端）**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

3. **定期備份數據庫**
   ```bash
   # 添加到 crontab
   0 2 * * * cp /opt/wushizhifu/bot/wushipay.db /opt/wushizhifu/bot/backups/wushipay_$(date +\%Y\%m\%d).db
   ```

## 🐛 故障排除

### Bot 無法啟動

1. 檢查 `.env` 文件中的 `BOT_TOKEN` 是否正確
2. 檢查數據庫文件權限
3. 查看日誌：`sudo journalctl -u wushipay-bot -n 50`

### 數據庫錯誤

```bash
# 重新初始化數據庫（注意：會刪除現有數據）
rm wushipay.db
python3 -c "from database.models import init_database; init_database()"
```

## 📝 注意事項

- 確保服務器有足夠的磁盤空間
- 建議使用 `screen` 或 `tmux` 進行手動測試
- 生產環境建議使用 systemd 服務管理
- 定期備份數據庫文件

