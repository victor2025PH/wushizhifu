# 將代碼推送到 GitHub 指南

## 📤 步驟 1: 在 GitHub 創建新倉庫

1. 登錄 GitHub: https://github.com
2. 點擊右上角 "+" → "New repository"
3. 倉庫名稱：`wushizhifu-bot`（或您喜歡的名稱）
4. 設置為 Private 或 Public
5. **不要**初始化 README、.gitignore 或 license（我們已有文件）
6. 點擊 "Create repository"

## 🚀 步驟 2: 在本地推送代碼

### 方法 1: 使用 Git 命令行（推薦）

在本地項目目錄執行：

```bash
# 1. 進入項目目錄
cd d:\wushizhifu

# 2. 初始化 Git（如果還沒有）
git init
git branch -M main

# 3. 添加所有文件
git add .

# 4. 提交
git commit -m "Initial commit: WuShiPay Telegram Bot"

# 5. 添加遠程倉庫（替換為您的倉庫 URL）
git remote add origin https://github.com/YOUR_USERNAME/wushizhifu-bot.git

# 6. 推送代碼
git push -u origin main
```

### 方法 2: 使用 GitHub Desktop（圖形界面）

1. 下載 GitHub Desktop: https://desktop.github.com/
2. 登錄 GitHub 賬號
3. File → Add Local Repository
4. 選擇 `d:\wushizhifu` 目錄
5. Publish repository
6. 輸入倉庫名稱並發布

### 方法 3: 使用 VS Code

1. 在 VS Code 中打開項目
2. 點擊左側的 Source Control 圖標
3. 點擊 "Publish to GitHub"
4. 選擇倉庫名稱並發布

## ⚠️ 重要提示

`.gitignore` 文件已經配置，以下文件**不會**被上傳：
- `.env` - 包含敏感信息（BOT_TOKEN）
- `*.db` - 數據庫文件
- `venv/` - Python 虛擬環境
- `__pycache__/` - Python 緩存文件
- 其他臨時文件

**重要：** `.env` 文件包含您的 Bot Token，**永遠不要**提交到 GitHub！

## ✅ 驗證上傳

上傳完成後，訪問您的 GitHub 倉庫，應該看到：
- ✅ bot.py
- ✅ config.py
- ✅ requirements.txt
- ✅ database/ 文件夾
- ✅ handlers/ 文件夾
- ✅ keyboards/ 文件夾
- ✅ middleware/ 文件夾
- ✅ services/ 文件夾
- ✅ utils/ 文件夾
- ✅ deploy/ 文件夾
- ✅ .gitignore
- ✅ README.md
- ❌ .env（不應出現）
- ❌ *.db（不應出現）

## 🔄 後續更新

當您修改代碼後，可以使用：

```bash
git add .
git commit -m "描述您的更改"
git push
```

## 📥 在服務器上克隆

部署完成後，在服務器上可以這樣克隆：

```bash
cd /home/ubuntu/wushizhifu
git clone https://github.com/YOUR_USERNAME/wushizhifu-bot.git bot
cd bot
# 然後複製 .env 文件
cp ~/.env .env
```

