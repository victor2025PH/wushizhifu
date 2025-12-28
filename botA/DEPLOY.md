# 🚀 WuShiPay 部署指南

## 📋 快速開始

### 在服務器上執行：

```bash
# 1. 下載部署腳本
curl -O https://raw.githubusercontent.com/victor2025PH/wushizhifu_bot/main/deploy/deploy_from_github.sh
chmod +x deploy_from_github.sh

# 2. 執行部署
./deploy_from_github.sh
```

## 📝 詳細步驟

### 前置條件

1. **域名配置**: 確保 `50zf.usdt2026.cc` 已解析到服務器 IP
2. **防火牆**: 開放 80 和 443 端口
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```
3. **準備 Bot Token**: 準備您的 Telegram Bot Token

### 部署步驟

1. **登錄服務器**
   ```bash
   ssh ubuntu@your-server-ip
   ```

2. **下載並執行部署腳本**
   ```bash
   curl -O https://raw.githubusercontent.com/victor2025PH/wushizhifu_bot/main/deploy/deploy_from_github.sh
   chmod +x deploy_from_github.sh
   ./deploy_from_github.sh
   ```

3. **設置 BOT_TOKEN**
   
   腳本會提示您設置 BOT_TOKEN，如果未設置，請執行：
   ```bash
   nano ~/wushizhifu/bot/.env
   # 設置: BOT_TOKEN=your_actual_token_here
   sudo systemctl restart wushipay-bot
   ```

4. **驗證部署**
   ```bash
   # 檢查 Bot 狀態
   sudo systemctl status wushipay-bot
   
   # 查看日誌
   sudo journalctl -u wushipay-bot -f
   
   # 訪問前端
   # https://50zf.usdt2026.cc
   ```

## 🔧 常用命令

### 服務管理

```bash
# Bot 服務
sudo systemctl start wushipay-bot      # 啟動
sudo systemctl stop wushipay-bot       # 停止
sudo systemctl restart wushipay-bot    # 重啟
sudo systemctl status wushipay-bot     # 狀態
sudo journalctl -u wushipay-bot -f     # 日誌

# Nginx 服務
sudo systemctl restart nginx           # 重啟
sudo systemctl status nginx            # 狀態
```

### 更新代碼

```bash
# 更新前端
cd ~/wushizhifu/frontend
git pull
npm run build
sudo systemctl reload nginx

# 更新 Bot
cd ~/wushizhifu/bot
git pull
sudo systemctl restart wushipay-bot
```

## ⚠️ 故障排除

### Bot 無法啟動

1. 檢查 BOT_TOKEN: `cat ~/wushizhifu/bot/.env`
2. 查看日誌: `sudo journalctl -u wushipay-bot -n 100`
3. 手動測試: `cd ~/wushizhifu/bot && source venv/bin/activate && python bot.py`

### SSL 證書問題

1. 確認域名解析: `ping 50zf.usdt2026.cc`
2. 確認端口開放: `sudo ufw status`
3. 手動申請: `sudo certbot --nginx -d 50zf.usdt2026.cc`

### 前端無法訪問

1. 確認構建成功: `ls ~/wushizhifu/frontend/dist`
2. 檢查 Nginx: `sudo nginx -t`
3. 查看錯誤日誌: `sudo tail -f /var/log/nginx/error.log`

## 📁 項目結構

部署完成後的目錄結構：

```
~/wushizhifu/
├── bot/              # Bot 代碼
│   ├── bot.py
│   ├── .env          # 環境變數（包含 BOT_TOKEN）
│   ├── venv/         # Python 虛擬環境
│   └── ...
└── frontend/         # 前端代碼
    ├── dist/         # 構建後的靜態文件
    └── ...
```

## ✅ 部署完成

部署成功後：

- 🌐 前端地址: https://50zf.usdt2026.cc
- 🤖 Bot 服務: 自動運行中
- 📊 查看日誌: `sudo journalctl -u wushipay-bot -f`

更多詳細信息請查看 `deploy/README_FULL.md`

