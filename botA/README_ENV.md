# 環境變量配置說明

## 📋 .env 文件配置

創建 `.env` 文件並設置以下環境變量：

### 必需配置

```env
# Telegram Bot Token（必需）
# 從 @BotFather 獲取
BOT_TOKEN=your_bot_token_here
```

### AI 服務配置（至少配置一個）

```env
# OpenAI API Key（優先使用）
# 從 https://platform.openai.com/api-keys 獲取
OPENAI_API_KEY=your_openai_api_key_here

# Gemini API Key（備選）
# 從 https://makersuite.google.com/app/apikey 獲取
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI 模型（可選，默認：gpt-3.5-turbo）
# 可選值：gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview 等
OPENAI_MODEL=gpt-3.5-turbo
```

## 🔄 AI 服務自動切換機制

系統會按照以下優先級使用 AI 服務：

1. **優先使用 OpenAI**（如果配置了 `OPENAI_API_KEY`）
   - 如果 OpenAI 可用，優先使用
   - 如果 OpenAI 調用失敗，自動切換到 Gemini

2. **備選使用 Gemini**（如果配置了 `GEMINI_API_KEY`）
   - 當 OpenAI 不可用或調用失敗時使用
   - 如果只配置了 Gemini，直接使用 Gemini

3. **都不可用**
   - 如果兩個服務都不可用，AI 助手會提示用戶聯繫人工客服

## 📝 使用步驟

### 1. 複製模板文件

```bash
cp .env.template .env
```

### 2. 編輯 .env 文件

```bash
nano .env
# 或使用其他編輯器
```

### 3. 填寫配置項

- **BOT_TOKEN**: 必需，從 @BotFather 獲取
- **OPENAI_API_KEY**: 推薦配置，優先使用
- **GEMINI_API_KEY**: 推薦配置，作為備選

### 4. 驗證配置

```bash
# 檢查配置是否正確加載
python3 -c "from config import Config; print('BOT_TOKEN:', '已設置' if Config.BOT_TOKEN else '未設置')"
```

## 🔑 API Key 獲取方式

### OpenAI API Key

1. 訪問 https://platform.openai.com/
2. 註冊/登錄賬號
3. 進入 API Keys 頁面
4. 創建新的 API Key
5. 複製 Key 並保存到 `.env` 文件

### Gemini API Key

1. 訪問 https://makersuite.google.com/app/apikey
2. 使用 Google 賬號登錄
3. 創建新的 API Key
4. 複製 Key 並保存到 `.env` 文件

## ⚠️ 注意事項

1. **安全性**：`.env` 文件包含敏感信息，不要提交到 Git 倉庫
2. **API 限制**：注意 OpenAI 和 Gemini 的 API 調用限額
3. **費用**：OpenAI API 是付費服務，注意控制使用量
4. **備選方案**：建議同時配置兩個 API Key，以確保服務可用性

## 🔍 測試配置

### 測試 AI 服務是否正常工作

```bash
# 啟動 Bot
python bot.py

# 在 Telegram 中發送消息給 Bot
# 如果 AI 服務配置正確，Bot 會使用 AI 回復
```

### 檢查日誌

啟動 Bot 後，查看日誌輸出：

```
✅ OpenAI service initialized successfully
✅ Gemini service initialized successfully (as fallback)
```

或

```
✅ Gemini service initialized successfully (as primary)
```

## 📚 相關文檔

- [OpenAI API 文檔](https://platform.openai.com/docs)
- [Gemini API 文檔](https://ai.google.dev/docs)

