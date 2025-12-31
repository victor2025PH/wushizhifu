# Bot B 部署指南

## 🚀 快速部署（從 GitHub）

### 方法 1: 使用部署腳本（推薦）

```bash
# 1. SSH 連接到服務器
ssh ubuntu@your-server-ip

# 2. 如果是首次部署，先克隆倉庫
cd /home/ubuntu/wushizhifu
git clone https://github.com/victor2025PH/wushizhifu.git .
cd botB

# 3. 設置執行權限
chmod +x deploy_update.sh

# 4. 執行部署腳本
./deploy_update.sh
```

### 方法 2: 手動部署

```bash
# 1. SSH 連接到服務器
ssh ubuntu@your-server-ip

# 2. 進入 Bot 目錄
cd /home/ubuntu/wushizhifu/botB

# 3. 拉取最新代碼
git pull origin main

# 4. 激活虛擬環境（如果存在）
source venv/bin/activate

# 5. 安裝/更新依賴
pip install -r requirements.txt

# 6. 重啟服務
sudo systemctl restart otc-bot.service

# 7. 檢查服務狀態
sudo systemctl status otc-bot.service
```

## 📋 首次部署步驟

### 1. 克隆倉庫

```bash
cd /home/ubuntu/wushizhifu
git clone https://github.com/victor2025PH/wushizhifu.git .
cd botB
```

### 2. 設置虛擬環境

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 配置環境變數

確保 `.env` 文件存在並包含 `BOT_TOKEN_B`：

```bash
# 檢查 .env 文件
cat ../bot/.env  # 或 ~/wushizhifu/bot/.env

# 如果不存在，創建它
nano ../bot/.env
```

添加以下內容：
```env
BOT_TOKEN_B=your_bot_b_token_here
```

### 4. 設置 systemd 服務

```bash
# 複製服務文件
sudo cp otc-bot.service /etc/systemd/system/

# 編輯服務文件（如果需要調整路徑）
sudo nano /etc/systemd/system/otc-bot.service

# 重新加載 systemd
sudo systemctl daemon-reload

# 啟用並啟動服務
sudo systemctl enable otc-bot.service
sudo systemctl start otc-bot.service

# 檢查狀態
sudo systemctl status otc-bot.service
```

### 5. 查看日誌

```bash
# 實時查看日誌
sudo journalctl -u otc-bot.service -f

# 查看最近 100 行日誌
sudo journalctl -u otc-bot.service -n 100
```

## 🔄 更新部署

### 使用部署腳本（推薦）

```bash
cd /home/ubuntu/wushizhifu/botB
./deploy_update.sh
```

### 手動更新

```bash
cd /home/ubuntu/wushizhifu/botB
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart otc-bot.service
```

## 📁 服務器目錄結構

```
/home/ubuntu/wushizhifu/
├── bot/              # Bot A
│   ├── .env          # 包含 BOT_TOKEN 和 BOT_TOKEN_B
│   └── ...
└── botB/             # Bot B (OTC 群組管理 Bot)
    ├── bot.py
    ├── config.py
    ├── database.py
    ├── requirements.txt
    ├── venv/         # Python 虛擬環境
    ├── otc-bot.service
    └── ...
```

## 🔧 服務配置

服務文件位置：`/etc/systemd/system/otc-bot.service`

確保服務文件中的路徑正確：
- `WorkingDirectory`: `/home/ubuntu/wushizhifu/botB`
- `ExecStart`: `/home/ubuntu/wushizhifu/botB/venv/bin/python bot.py`

## 🐛 故障排除

### 服務無法啟動

```bash
# 查看詳細錯誤
sudo journalctl -u otc-bot.service -n 50

# 檢查配置文件
python3 bot.py  # 手動運行測試
```

### 依賴問題

```bash
# 重新安裝依賴
source venv/bin/activate
pip install --force-reinstall -r requirements.txt
```

### 權限問題

```bash
# 確保文件權限正確
chmod +x bot.py
chmod +x deploy_update.sh
```

## 📞 支援

如有問題，請查看：
- 日誌：`sudo journalctl -u otc-bot.service -f`
- 配置文件：`config.py`
- 環境變數：`.env` 文件
