# 分離倉庫方案說明

## 🎯 為什麼要分離？

將前端和 Bot 代碼分開到兩個獨立倉庫的好處：

### ✅ 優勢

1. **清晰的職責分離**
   - 前端項目：React/TypeScript，面向用戶界面
   - Bot 項目：Python，後端服務
   - 各自獨立維護和更新

2. **避免混亂**
   - 不會有文檔衝突
   - 不會有依賴衝突
   - 不會有版本管理問題

3. **獨立部署**
   - 前端可以獨立更新
   - Bot 可以獨立更新
   - 互不影響

4. **權限管理**
   - 可以設置不同的協作者
   - 可以設置不同的訪問權限

5. **清晰的項目結構**
   - 每個倉庫都有明確的用途
   - 文檔和配置不會混淆

## 📁 建議的倉庫結構

### 前端倉庫
- **倉庫名**: `wushizhifu`
- **地址**: https://github.com/victor2025PH/wushizhifu
- **內容**: React/TypeScript 前端應用
- **技術棧**: TypeScript, React, Vite

### Bot 倉庫
- **倉庫名**: `wushizhifu-bot` (建議)
- **地址**: https://github.com/victor2025PH/wushizhifu-bot
- **內容**: Python Telegram Bot
- **技術棧**: Python, aiogram, SQLite

## 🚀 設置獨立 Bot 倉庫

### 步驟 1: 在 GitHub 創建新倉庫

1. 訪問 https://github.com/new
2. 倉庫名稱：`wushizhifu-bot`
3. 描述：`WuShiPay Telegram Bot - Payment Gateway Bot`
4. 選擇 Public 或 Private
5. **不要**初始化 README、.gitignore 或 license
6. 點擊 "Create repository"

### 步驟 2: 在本地推送 Bot 代碼

```powershell
# 進入 Bot 項目目錄
cd d:\wushizhifu

# 使用我創建的腳本（最簡單）
.\setup_new_repo.bat

# 或者手動執行：
git init
git branch -M main
git add .
git commit -m "Initial commit: WuShiPay Telegram Bot"
git remote add origin https://github.com/victor2025PH/wushizhifu-bot.git
git push -u origin main
```

### 步驟 3: 更新 README

我已創建了 `README_BOT.md`，它會自動成為新的 `README.md`，明確說明這是 Bot 專用倉庫。

## 📝 文檔組織

### Bot 倉庫的文檔
- `README.md` - Bot 項目說明
- `DEPLOYMENT.md` - 部署指南
- `ARCHITECTURE.md` - 架構說明
- `FUNCTIONAL_DESIGN.md` - 功能設計
- `deploy/` - 部署相關文檔

### 前端倉庫的文檔
- `README.md` - 前端項目說明
- 前端相關文檔

## 🔄 部署時的組織

在服務器上，兩個項目可以這樣組織：

```
/opt/wushizhifu/
├── frontend/          # 從 GitHub 克隆
│   └── (前端代碼)
└── bot/              # 從 GitHub 克隆
    └── (Bot 代碼)
```

或者使用 home 目錄：

```
/home/ubuntu/wushizhifu/
├── frontend/          # 從 GitHub 克隆
└── bot/              # 從 GitHub 克隆
```

## ✅ 最終建議

**強烈建議創建獨立的 Bot 倉庫**，這樣：
- ✅ 代碼組織清晰
- ✅ 不會有文檔混亂
- ✅ 獨立維護和更新
- ✅ 清晰的項目邊界

執行 `.\setup_new_repo.bat` 即可自動完成設置！

