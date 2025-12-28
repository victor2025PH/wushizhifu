# 項目整理指南

## 🎯 目標

將 D:\wushizhifu 目錄整理為兩個獨立項目：
1. **wushizhifu-bot** - Bot 代碼（推送至 wushizhifu_bot 倉庫）
2. **wushizhifu-frontend** - 前端代碼（推送至 wushizhifu 倉庫）

## 📁 整理後的目錄結構

```
D:\wushizhifu\
├── wushizhifu-bot\          # Bot 項目
│   ├── bot.py
│   ├── config.py
│   ├── database/
│   ├── handlers/
│   ├── keyboards/
│   ├── middleware/
│   ├── services/
│   ├── utils/
│   ├── deploy/
│   ├── requirements.txt
│   ├── README.md
│   └── ...
│
└── wushizhifu-frontend\     # 前端項目
    ├── src/
    ├── components/
    ├── package.json
    ├── vite.config.ts
    ├── README.md
    └── ...
```

## 🚀 執行步驟

### 步驟 1: 運行整理腳本

```powershell
cd d:\wushizhifu
.\organize_repos.bat
```

或者手動整理：

### 步驟 2: 手動整理（如果腳本無法運行）

#### 2.1 創建目錄

```powershell
cd d:\wushizhifu
mkdir wushizhifu-bot
mkdir wushizhifu-frontend
```

#### 2.2 複製 Bot 文件

```powershell
# Bot 文件
copy bot.py wushizhifu-bot\
copy config.py wushizhifu-bot\
copy requirements.txt wushizhifu-bot\
copy *.md wushizhifu-bot\
copy .gitignore wushizhifu-bot\
copy .gitattributes wushizhifu-bot\

# Bot 目錄
xcopy /E /I database wushizhifu-bot\database\
xcopy /E /I handlers wushizhifu-bot\handlers\
xcopy /E /I keyboards wushizhifu-bot\keyboards\
xcopy /E /I middleware wushizhifu-bot\middleware\
xcopy /E /I services wushizhifu-bot\services\
xcopy /E /I utils wushizhifu-bot\utils\
xcopy /E /I deploy wushizhifu-bot\deploy\
```

#### 2.3 複製前端文件

如果 `wushizhifu-full` 目錄存在：

```powershell
xcopy /E /I wushizhifu-full\* wushizhifu-frontend\
```

或者從 GitHub 克隆：

```powershell
cd wushizhifu-frontend
git clone https://github.com/victor2025PH/wushizhifu.git .
```

### 步驟 3: 清理不需要的文件

從兩個目錄中刪除：
- `*.db` - 數據庫文件
- `__pycache__/` - Python 緩存
- `venv/` - 虛擬環境（如果存在）
- `.env` - 環境變數文件（不應該提交）

## ✅ 驗證整理結果

### Bot 目錄應包含：
- ✅ bot.py
- ✅ config.py
- ✅ requirements.txt
- ✅ database/
- ✅ handlers/
- ✅ keyboards/
- ✅ middleware/
- ✅ services/
- ✅ utils/
- ✅ deploy/
- ✅ README.md
- ✅ .gitignore

### 前端目錄應包含：
- ✅ src/ 或 components/
- ✅ package.json
- ✅ vite.config.ts
- ✅ tsconfig.json
- ✅ index.html
- ✅ README.md

## 📤 下一步：推送到 GitHub

整理完成後，分別推送到各自的倉庫。

