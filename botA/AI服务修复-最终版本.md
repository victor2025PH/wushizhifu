# AI 服务修复 - 最终版本

## 🔍 问题总结

根据最新日志，发现：

1. **OpenAI API 密钥无效** ❌
   - 错误：`401 Unauthorized - Incorrect API key provided`
   - 需要更新 `.env` 文件中的 `OPENAI_API_KEY`

2. **Gemini 模型名称问题** ❌
   - 错误：`404 models/gemini-1.5-flash is not found for API version v1beta`
   - `gemini-1.5-flash` 不支持 `v1beta` API 版本
   - 已修复：添加了降级处理，先尝试 `gemini-1.5-pro-latest`，失败则使用 `gemini-pro`

## ✅ 已修复

### 修复 1：Gemini 模型降级处理
- 先尝试使用 `gemini-1.5-pro-latest`
- 如果失败，自动降级到 `gemini-pro`（兼容 v1beta）

### 修复 2：响应处理改进
- 兼容不同的响应格式
- 处理字符串和对象类型的响应

## 🛠️ 需要您操作的步骤

### 步骤 1：修复 OpenAI API 密钥

```bash
# 编辑 .env 文件
cd ~/wushizhifu/bot
nano .env

# 检查并更新 OPENAI_API_KEY
# 访问 https://platform.openai.com/account/api-keys 获取新密钥
```

### 步骤 2：拉取最新代码并重启

```bash
cd ~/wushizhifu/bot
git pull origin main

# 清理缓存
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# 重启服务
sudo systemctl restart wushizhifu-bot

# 查看日志
sleep 3
sudo journalctl -u wushizhifu-bot -n 50 | grep -i "ai\|gemini\|openai\|error"
```

### 步骤 3：验证修复

应该看到：
- ✅ `Gemini service initialized successfully`（如果 Gemini 可用）
- ✅ 或 `OpenAI service initialized successfully`（如果 OpenAI 密钥修复后可用）
- ✅ 不再有 `404 models/gemini-1.5-flash is not found` 错误

## 📝 模型选择逻辑

修复后的逻辑：
1. **Gemini**：
   - 先尝试 `gemini-1.5-pro-latest`（最新模型）
   - 失败则使用 `gemini-pro`（兼容 v1beta）
   
2. **OpenAI**：
   - 使用 `gpt-3.5-turbo`（默认）或 `.env` 中配置的 `OPENAI_MODEL`

3. **优先级**：
   - OpenAI（如果可用）→ Gemini（如果 OpenAI 失败）

## ⚠️ 重要提示

**至少需要配置一个有效的 API 密钥**：
- ✅ 配置有效的 `OPENAI_API_KEY`，或
- ✅ 配置有效的 `GEMINI_API_KEY`

两个都配置更好（有自动降级）。

## 🔍 如果仍然失败

执行以下诊断命令：

```bash
cd ~/wushizhifu/bot
source venv/bin/activate

# 列出可用的 Gemini 模型
python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    print("=== 可用的 Gemini 模型 ===")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
else:
    print("❌ GEMINI_API_KEY 未配置")
EOF
```

根据输出结果，我们可以进一步调整模型名称。

