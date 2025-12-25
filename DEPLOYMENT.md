# 部署文檔

## 🎯 部署目標

將以下兩個項目部署到服務器：
1. **Telegram Bot** (Python) - 當前項目
2. **前端應用** (TypeScript/React) - https://github.com/victor2025PH/wushizhifu

## 📦 項目結構

```
/opt/wushizhifu/
├── bot/              # Telegram Bot (Python)
│   ├── bot.py
│   ├── database/
│   ├── handlers/
│   └── ...
└── frontend/         # 前端應用 (React/TypeScript)
    ├── src/
    ├── dist/         # 構建後的靜態文件
    └── ...
```

## 🚀 自動化部署

### 步驟 1: 準備服務器

**需要手動執行：**
1. 登錄服務器（SSH）
2. 確保已安裝：
   - Python 3.10+
   - Node.js 18+
   - Git
   - Nginx (可選，用於前端)

### 步驟 2: 克隆項目

執行以下命令：

```bash
# 創建項目目錄
sudo mkdir -p /opt/wushizhifu
sudo chown $USER:$USER /opt/wushizhifu
cd /opt/wushizhifu

# 克隆前端項目
git clone https://github.com/victor2025PH/wushizhifu.git frontend

# 如果 Bot 代碼在 Git 倉庫中，也克隆它
# git clone <your-bot-repo-url> bot

# 或者將 Bot 代碼上傳到服務器（使用 scp 或 sftp）
```

### 步驟 3: 部署 Telegram Bot

進入 Bot 目錄並運行部署腳本：

```bash
cd /opt/wushizhifu/bot  # 或您的 Bot 項目路徑
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### 步驟 4: 配置環境變數

**需要手動執行：**

編輯 `.env` 文件：
```bash
nano .env
```

設置：
```env
BOT_TOKEN=your_telegram_bot_token_here
```

### 步驟 5: 測試 Bot

```bash
cd /opt/wushizhifu/bot
source venv/bin/activate
python bot.py
```

如果運行正常，按 Ctrl+C 停止，然後繼續下一步。

### 步驟 6: 設置為系統服務

```bash
cd /opt/wushizhifu/bot
sudo cp wushipay-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wushipay-bot
sudo systemctl start wushipay-bot
sudo systemctl status wushipay-bot
```

## 🌐 部署前端應用（可選）

### 步驟 1: 安裝依賴並構建

```bash
cd /opt/wushizhifu/frontend
npm install
npm run build
```

### 步驟 2: 配置 Nginx

**需要手動修改：**

1. 編輯 Nginx 配置文件：
```bash
sudo nano /etc/nginx/sites-available/wushizhifu
```

2. 修改域名和路徑：
```nginx
server_name your-domain.com;  # 改為您的域名
root /opt/wushizhifu/frontend/dist;  # 確認路徑正確
```

3. 啟用站點：
```bash
sudo ln -s /etc/nginx/sites-available/wushizhifu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## ✅ 驗證部署

### 檢查 Bot 狀態

```bash
sudo systemctl status wushipay-bot
sudo journalctl -u wushipay-bot -f
```

### 檢查前端（如果部署）

訪問 `http://your-domain.com` 查看前端應用。

## 🔄 更新部署

### 更新 Bot

```bash
cd /opt/wushizhifu/bot
git pull  # 如果有 Git 倉庫
# 或重新上傳新代碼
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart wushipay-bot
```

### 更新前端

```bash
cd /opt/wushizhifu/frontend
git pull
npm install
npm run build
sudo systemctl reload nginx
```

## 📋 手動操作清單

以下是需要手動操作的步驟（自動化腳本無法完成的部分）：

- [ ] 登錄服務器
- [ ] 安裝系統依賴（Python, Node.js, Git, Nginx）
- [ ] 克隆前端項目到服務器
- [ ] 將 Bot 代碼上傳到服務器（或克隆 Git 倉庫）
- [ ] 在 `.env` 文件中設置 `BOT_TOKEN`
- [ ] 如果部署前端：配置 Nginx 域名和路徑
- [ ] 如果部署前端：設置 SSL 證書（可選但推薦）

## 🆘 常見問題

### Bot 無法啟動

1. 檢查 `.env` 文件是否存在且 `BOT_TOKEN` 正確
2. 檢查虛擬環境是否激活
3. 查看日誌：`sudo journalctl -u wushipay-bot -n 50`

### 前端無法訪問

1. 檢查 Nginx 配置：`sudo nginx -t`
2. 檢查文件權限：`sudo chown -R www-data:www-data /opt/wushizhifu/frontend/dist`
3. 檢查防火牆：`sudo ufw status`

