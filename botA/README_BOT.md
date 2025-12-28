# WuShiPay Telegram Bot

> **獨立倉庫版本** - 這是 Telegram Bot 的專用倉庫

前端項目請訪問：[https://github.com/victor2025PH/wushizhifu](https://github.com/victor2025PH/wushizhifu)

---

高端金融科技 Telegram Bot，作為支付閘道提供 Alipay/WeChat 支付服務。

## ✨ 特性

- 🏗️ **企業級架構**：分層設計，職責清晰，易於維護和擴展
- 👤 **智能用戶管理**：自動追蹤用戶活動，區分新老用戶
- 💼 **專業化界面**：企業級消息格式，動態問候語，實時系統狀態
- 🔒 **安全可靠**：完善的錯誤處理，詳細的日誌記錄
- 📊 **用戶統計**：自動記錄用戶數據，支持用戶分析
- 👥 **群組支持**：進群審核、敏感詞過濾
- ⚙️ **管理員系統**：完整的管理員功能和權限管理

## 技術棧

- Python 3.10+
- aiogram 3.x (最新版本)
- SQLite 數據庫
- python-dotenv (配置管理)

## 專案結構

```
.
├── bot.py                      # 入口點，Bot 初始化
├── config.py                   # 配置管理
├── database/                   # 數據庫層
│   ├── models.py              # 數據表定義
│   ├── db.py                  # 數據庫連接
│   └── *_repository.py        # 數據訪問層
├── handlers/                   # 處理器層
│   ├── user_handlers.py       # 用戶命令處理器
│   ├── payment_handlers.py    # 支付處理器
│   ├── calculator_handlers.py # 計算器處理器
│   ├── transaction_handlers.py # 交易記錄處理器
│   ├── admin_handlers.py      # 管理員處理器
│   └── group_handlers.py      # 群組處理器
├── keyboards/                  # 鍵盤布局
│   ├── main_kb.py             # 主鍵盤
│   ├── payment_kb.py          # 支付鍵盤
│   ├── calculator_kb.py       # 計算器鍵盤
│   └── transaction_kb.py      # 交易記錄鍵盤
├── middleware/                 # 中間件層
│   ├── user_tracking.py       # 用戶追蹤中間件
│   └── group_middleware.py    # 群組中間件
├── services/                   # 服務層（業務邏輯）
│   ├── user_service.py        # 用戶服務
│   ├── message_service.py     # 消息生成服務
│   ├── calculator_service.py  # 計算器服務
│   └── transaction_service.py # 交易服務
├── utils/                      # 工具函數
│   └── text_utils.py          # 文本處理工具
├── deploy/                     # 部署腳本
│   ├── deploy_home.sh         # 部署到 home 目錄
│   ├── full_deploy.sh         # 完整部署腳本
│   └── nginx.conf             # Nginx 配置
└── requirements.txt            # 依賴套件
```

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數

創建 `.env` 文件：

```env
BOT_TOKEN=your_telegram_bot_token_here
```

### 3. 運行 Bot

```bash
python bot.py
```

## 部署

詳細部署文檔請參考：[DEPLOYMENT.md](DEPLOYMENT.md)

## 功能

- `/start` - 啟動命令，顯示歡迎訊息
- 💳 支付通道（支付寶、微信）
- 📜 交易記錄查詢
- 🧮 費率計算器
- 👥 管理員功能（`/admin`）
- 🔒 群組管理（進群審核、敏感詞過濾）

## 相關項目

- **前端項目**: [wushizhifu](https://github.com/victor2025PH/wushizhifu) - React/TypeScript 前端應用

## 許可證

Private - All Rights Reserved

