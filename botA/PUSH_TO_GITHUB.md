# 📤 將代碼推送到 GitHub - 完整指南

## ⚠️ 當前狀態

您的代碼目前**還沒有**推送到 GitHub。需要先初始化 Git 倉庫並推送。

## 🚀 快速步驟

### 步驟 1: 在 GitHub 創建新倉庫

1. 訪問 https://github.com 並登錄
2. 點擊右上角 **"+"** → **"New repository"**
3. 倉庫名稱：`wushizhifu-bot`（或您喜歡的名稱）
4. 描述（可選）：`WuShiPay Telegram Bot - Payment Gateway Bot`
5. 選擇 **Public** 或 **Private**
6. **不要勾選** "Initialize this repository with a README"（我們已有文件）
7. 點擊 **"Create repository"**

### 步驟 2: 在本地初始化並推送

**方法 A: 使用 Git 命令行（推薦）**

在 PowerShell 或 CMD 中執行：

```powershell
# 1. 進入項目目錄
cd d:\wushizhifu

# 2. 初始化 Git（如果還沒有）
git init
git branch -M main

# 3. 添加所有文件
git add .

# 4. 查看將要提交的文件
git status

# 5. 提交
git commit -m "Initial commit: WuShiPay Telegram Bot with full features"

# 6. 添加遠程倉庫（替換 YOUR_USERNAME 為您的 GitHub 用戶名）
git remote add origin https://github.com/YOUR_USERNAME/wushizhifu-bot.git

# 7. 推送到 GitHub
git push -u origin main
```

**方法 B: 使用我創建的批次檔**

```powershell
# 在項目目錄執行
cd d:\wushizhifu
.\setup_git.bat
# 然後按照提示操作
```

### 步驟 3: 驗證上傳

訪問您的 GitHub 倉庫，應該看到所有文件都已上傳。

## ✅ 確認上傳的文件

上傳成功後，您應該在 GitHub 上看到：

✅ **應該包含的文件：**
- `bot.py`
- `config.py`
- `requirements.txt`
- `database/` 文件夾
- `handlers/` 文件夾
- `keyboards/` 文件夾
- `middleware/` 文件夾
- `services/` 文件夾
- `utils/` 文件夾
- `deploy/` 文件夾
- `.gitignore`
- `README.md`
- 所有文檔文件（*.md）

❌ **不應該包含的文件（已自動排除）：**
- `.env` - 包含敏感信息
- `*.db` - 數據庫文件
- `venv/` - 虛擬環境
- `__pycache__/` - Python 緩存
- 其他臨時文件

## 📥 在服務器上克隆

推送完成後，在服務器上可以這樣克隆：

```bash
# 在服務器上執行
cd /home/ubuntu/wushizhifu
git clone https://github.com/YOUR_USERNAME/wushizhifu-bot.git bot
cd bot

# 複製 .env 文件（需要手動設置）
nano .env
# 添加：BOT_TOKEN=your_token_here

# 然後運行部署腳本
chmod +x deploy/*.sh
./deploy/deploy_home.sh
```

## 🔄 後續更新代碼

當您修改代碼後，可以使用：

```bash
git add .
git commit -m "描述您的更改"
git push
```

## ❓ 常見問題

### 1. 提示需要身份驗證

如果 Git 要求輸入用戶名和密碼：
- 用戶名：您的 GitHub 用戶名
- 密碼：使用 **Personal Access Token**（不是 GitHub 密碼）
  - 創建 Token：GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

### 2. 如果已經有遠程倉庫

```bash
# 查看現有遠程倉庫
git remote -v

# 如果需要更換
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### 3. 如果遇到衝突

```bash
# 先拉取遠程更改
git pull origin main --rebase

# 然後再推送
git push
```

