# AI 服务不可用问题诊断与修复方案

## 🔍 问题分析

根据代码分析，AI 服务显示"暂时不可用"的可能原因：

### 1. **环境变量未配置**（最可能）
- `.env` 文件中缺少 `OPENAI_API_KEY` 或 `GEMINI_API_KEY`
- 环境变量未正确加载

### 2. **API 密钥无效或过期**
- 配置的密钥格式错误
- 密钥已过期或被撤销
- 密钥权限不足

### 3. **依赖包未安装**
- `openai` 包未安装
- `google-generativeai` 包未安装

### 4. **API 调用失败**
- 网络连接问题
- API 配额用完
- API 服务暂时不可用
- 请求超时

### 5. **初始化错误**
- 服务启动时初始化失败
- 错误被捕获但未正确记录

## 📋 诊断步骤

### 第一步：检查环境变量配置

在服务器上执行：

```bash
# 1. 进入项目目录
cd ~/wushizhifu/bot

# 2. 检查 .env 文件是否存在
ls -la .env

# 3. 检查是否配置了 API 密钥（不显示实际密钥值）
grep -E "OPENAI_API_KEY|GEMINI_API_KEY" .env | sed 's/=.*/=***/'

# 4. 检查环境变量是否被正确加载
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OPENAI_API_KEY:', '已配置' if os.getenv('OPENAI_API_KEY') else '未配置'); print('GEMINI_API_KEY:', '已配置' if os.getenv('GEMINI_API_KEY') else '未配置')"
```

### 第二步：检查依赖包

```bash
# 检查是否安装了必要的包
source venv/bin/activate
pip list | grep -E "openai|google-generativeai"
```

### 第三步：查看日志

```bash
# 查看 Bot 启动日志，查找 AI 服务初始化信息
sudo journalctl -u wushizhifu-bot -n 100 | grep -i "ai\|openai\|gemini"

# 查看完整日志
sudo journalctl -u wushizhifu-bot -f
```

### 第四步：测试 AI 服务初始化

```bash
# 进入虚拟环境
cd ~/wushizhifu/bot
source venv/bin/activate

# 测试 AI 服务初始化
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('=== 环境变量检查 ===')
print('OPENAI_API_KEY:', '已配置' if os.getenv('OPENAI_API_KEY') else '❌ 未配置')
print('GEMINI_API_KEY:', '已配置' if os.getenv('GEMINI_API_KEY') else '❌ 未配置')

print('\n=== 依赖包检查 ===')
try:
    import openai
    print('✅ openai 包已安装')
except ImportError:
    print('❌ openai 包未安装')

try:
    import google.generativeai
    print('✅ google-generativeai 包已安装')
except ImportError:
    print('❌ google-generativeai 包未安装')

print('\n=== AI 服务初始化测试 ===')
try:
    from services.ai_service import get_ai_service
    ai_service = get_ai_service()
    print('AI 服务可用:', ai_service.is_available())
    print('OpenAI 可用:', ai_service.openai_available)
    print('Gemini 可用:', ai_service.gemini_available)
    print('当前提供商:', ai_service.current_provider)
except Exception as e:
    print(f'❌ 初始化失败: {e}')
"
```

## 🛠️ 修复方案

### 方案一：配置 API 密钥（如果未配置）

1. **编辑 .env 文件**
   ```bash
   cd ~/wushizhifu/bot
   nano .env
   ```

2. **添加以下配置**（至少配置一个）：
   ```env
   # OpenAI API 密钥（推荐，优先使用）
   OPENAI_API_KEY=sk-your-openai-api-key-here
   
   # Gemini API 密钥（备选）
   GEMINI_API_KEY=your-gemini-api-key-here
   
   # OpenAI 模型（可选，默认 gpt-3.5-turbo）
   OPENAI_MODEL=gpt-3.5-turbo
   ```

3. **保存并重启服务**
   ```bash
   sudo systemctl restart wushizhifu-bot
   ```

### 方案二：安装缺失的依赖包

```bash
cd ~/wushizhifu/bot
source venv/bin/activate

# 安装 OpenAI 包
pip install openai

# 安装 Gemini 包
pip install google-generativeai

# 重启服务
sudo systemctl restart wushizhifu-bot
```

### 方案三：验证 API 密钥有效性

#### 测试 OpenAI API
```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=10
    )
    print('✅ OpenAI API 密钥有效')
except Exception as e:
    print(f'❌ OpenAI API 密钥无效: {e}')
"
```

#### 测试 Gemini API
```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content('Hello')
    print('✅ Gemini API 密钥有效')
except Exception as e:
    print(f'❌ Gemini API 密钥无效: {e}')
"
```

### 方案四：增强错误处理和日志

如果 API 密钥已配置但仍不可用，需要：
1. 增强错误日志记录
2. 添加更详细的错误信息
3. 提供降级方案

## 🔧 快速修复命令

### 一键诊断脚本

```bash
#!/bin/bash
cd ~/wushizhifu/bot
source venv/bin/activate

echo "=== AI 服务诊断 ==="
echo ""

echo "1. 检查环境变量..."
python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
gemini_key = os.getenv('GEMINI_API_KEY')

print(f"OPENAI_API_KEY: {'✅ 已配置' if openai_key else '❌ 未配置'}")
print(f"GEMINI_API_KEY: {'✅ 已配置' if gemini_key else '❌ 未配置'}")
EOF

echo ""
echo "2. 检查依赖包..."
pip list | grep -E "openai|google-generativeai" || echo "❌ 依赖包未安装"

echo ""
echo "3. 测试 AI 服务..."
python3 << 'EOF'
try:
    from services.ai_service import get_ai_service
    ai_service = get_ai_service()
    print(f"AI 服务可用: {'✅ 是' if ai_service.is_available() else '❌ 否'}")
    print(f"OpenAI 可用: {'✅ 是' if ai_service.openai_available else '❌ 否'}")
    print(f"Gemini 可用: {'✅ 是' if ai_service.gemini_available else '❌ 否'}")
except Exception as e:
    print(f"❌ 测试失败: {e}")
EOF
```

## 📝 配置建议

### 推荐配置（至少配置一个）

1. **优先配置 OpenAI**（推荐）
   - 访问 https://platform.openai.com/api-keys
   - 创建 API 密钥
   - 添加到 `.env` 文件

2. **备选配置 Gemini**（推荐）
   - 访问 https://makersuite.google.com/app/apikey
   - 创建 API 密钥
   - 添加到 `.env` 文件

### 最小配置要求

至少配置 **一个** API 密钥（OpenAI 或 Gemini），AI 服务才能正常工作。

## ⚠️ 注意事项

1. **API 密钥安全**
   - 不要将 `.env` 文件提交到 Git
   - 确保 `.env` 文件权限正确（`chmod 600 .env`）

2. **API 配额**
   - 注意 API 使用配额和费用
   - 监控 API 使用情况

3. **网络连接**
   - 确保服务器可以访问 OpenAI/Gemini API
   - 检查防火墙设置

## 🎯 预期结果

修复后，AI 服务应该：
- ✅ 初始化时显示 "✅ OpenAI service initialized successfully" 或 "✅ Gemini service initialized successfully"
- ✅ `ai_service.is_available()` 返回 `True`
- ✅ 用户发送消息时能正常获得 AI 回复
- ✅ 不再显示"AI 服务暂时不可用"的错误

