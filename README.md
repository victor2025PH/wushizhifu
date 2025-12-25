# WuShiPay Telegram Bot

高端金融科技 Telegram Bot，作為支付閘道提供 Alipay/WeChat 支付服務。

## ✨ 特性

- 🏗️ **企業級架構**：分層設計，職責清晰，易於維護和擴展
- 👤 **智能用戶管理**：自動追蹤用戶活動，區分新老用戶
- 💼 **專業化界面**：企業級消息格式，動態問候語，實時系統狀態
- 🔒 **安全可靠**：完善的錯誤處理，詳細的日誌記錄
- 📊 **用戶統計**：自動記錄用戶數據，支持用戶分析

## 技術棧

- Python 3.10+
- aiogram 3.x (最新版本)
- python-dotenv (配置管理)
- logging (標準庫)

## 專案結構

```
.
├── bot.py                      # 入口點，Bot 初始化
├── config.py                   # 配置管理
├── handlers/                   # 處理器層
│   └── user_handlers.py        # 用戶命令處理器
├── keyboards/                  # 鍵盤布局
│   └── main_kb.py              # 主鍵盤
├── middleware/                 # 中間件層
│   └── user_tracking.py        # 用戶追蹤中間件
├── services/                   # 服務層（業務邏輯）
│   ├── user_service.py         # 用戶數據服務
│   └── message_service.py      # 消息生成服務
├── utils/                      # 工具函數
│   └── text_utils.py           # 文本處理工具
├── ARCHITECTURE.md             # 架構說明文檔
├── requirements.txt            # 依賴套件
└── README.md                   # 本文件
```

詳細架構說明請參閱 [ARCHITECTURE.md](ARCHITECTURE.md)

## 安裝與運行

### 1. 安裝依賴

```bash
pip install aiogram python-dotenv
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數

在項目根目錄創建 `.env` 文件，設置您的 Bot Token：

```env
BOT_TOKEN=your_actual_bot_token_here
```

您可以從 [@BotFather](https://t.me/BotFather) 獲取 Bot Token。

### 3. 運行 Bot

```bash
python bot.py
```

啟動後，您將看到詳細的系統初始化日誌。

## 核心功能

### 用戶交互

- `/start` - 個性化歡迎消息，智能識別新老用戶
- 支付通道選擇（支付寶、微信）- 已預留接口
- 費率標準查詢 - 專業的費率信息展示
- 客戶服務與商務合作連結

### 系統特性

- **用戶追蹤**：自動記錄用戶首次訪問、最後活動時間、消息統計
- **個性化問候**：根據時間段動態生成問候語
- **專業消息格式**：企業級消息模板，包含系統狀態、用戶信息等
- **錯誤處理**：完善的異常處理機制，友好的錯誤提示
- **日誌記錄**：結構化日誌，便於監控和調試

## 架構設計

### 分層架構

- **Handlers 層**：處理用戶交互，僅負責接收和響應
- **Services 層**：業務邏輯處理，核心功能實現
- **Utils 層**：可復用的工具函數
- **Middleware 層**：橫切關注點（日誌、追蹤等）

### 設計原則

- 職責分離：每個模組都有清晰的職責
- 易於測試：業務邏輯與框架代碼分離
- 易於擴展：模組化設計，方便添加新功能

## 開發說明

- Bot 使用 MarkdownV2 作為預設訊息格式
- 所有特殊字符已正確轉義
- 使用 aiogram 3.x 的 Router 架構
- 支援異步處理和 WebSocket 連接
- 中間件自動追蹤用戶活動

## 未來擴展

- [ ] 數據庫集成（用戶數據持久化）
- [ ] 支付 API 集成（支付寶、微信支付）
- [ ] 訂單管理系統
- [ ] 管理員面板
- [ ] 多語言支持
- [ ] 安全增強（認證、速率限制）

