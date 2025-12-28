# AI 服务关键问题修复方案

## 🔍 发现的关键问题

### 问题 1：Gemini 模型已弃用 ❌

**错误信息**：
```
404 models/gemini-pro is not found for API version v1beta, 
or is not supported for generateContent
```

**原因**：
- `gemini-pro` 模型已经不可用
- 需要使用新的模型名称，如 `gemini-1.5-flash` 或 `gemini-1.5-pro`

### 问题 2：google.generativeai 包已弃用 ⚠️

**警告信息**：
```
FutureWarning: All support for the google.generativeai package has ended.
It will no longer be receiving updates or bug fixes. 
Please switch to the google.genai package
```

**建议**：
- 短期：更新模型名称继续使用 `google.generativeai`
- 长期：迁移到新的 `google.genai` 包

### 问题 3：仍有 MarkdownV2 格式化错误 ⚠️

**错误信息**：
```
TelegramBadRequest: can't parse entities: Character '.' is reserved 
and must be escaped
```

**位置**：`handlers/user_handlers.py:199` - `callback_settings`

## 🛠️ 修复方案

### 方案一：更新 Gemini 模型名称（立即修复）

将 `gemini-pro` 更新为 `gemini-1.5-flash`（推荐，更快）或 `gemini-1.5-pro`。

**修改文件**：`services/ai_service.py`

**需要修改的地方**：
```python
# 旧代码（第 70 行）
self.gemini_model = genai.GenerativeModel('gemini-pro')

# 新代码
self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
```

### 方案二：修复 user_handlers.py 中的 MarkdownV2 错误

检查 `callback_settings` 函数中的文本格式化。

### 方案三：增强错误处理

添加更详细的错误日志和用户友好的错误消息。

## 📋 立即执行步骤

### 步骤 1：修复 Gemini 模型名称

```bash
cd ~/wushizhifu/bot
nano services/ai_service.py
```

找到第 70 行，将：
```python
self.gemini_model = genai.GenerativeModel('gemini-pro')
```

改为：
```python
self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
```

### 步骤 2：检查并修复 user_handlers.py

查看 `callback_settings` 函数，确保所有文本都正确转义。

### 步骤 3：重启服务

```bash
sudo systemctl restart wushizhifu-bot
sleep 3
sudo journalctl -u wushizhifu-bot -n 50 | grep -i "ai\|gemini\|error"
```

## ✅ 验证修复

修复后应该看到：
- ✅ `Gemini service initialized successfully`
- ✅ AI 服务可以正常生成响应
- ✅ 不再有 `404 models/gemini-pro is not found` 错误

