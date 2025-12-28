# AI 服务错误原因分析

## 🔍 错误消息来源

错误消息 "抱歉,處理您的問題時遇到錯誤" 可能来自两个地方：

### 1. **AI 服务返回的错误**（`services/ai_service.py:199`）
```python
if not answer:
    logger.error("Both OpenAI and Gemini failed to generate response")
    return "抱歉，處理您的問題時遇到錯誤，請聯繫人工客服 @wushizhifu_jianglai"
```

**触发条件**：
- `generate_response()` 被调用
- OpenAI 调用返回 `None`
- Gemini 调用也返回 `None`
- 最终没有生成答案

### 2. **异常处理返回的错误**（`handlers/ai_handlers.py:184`）
```python
except Exception as e:
    logger.error(f"Error in handle_ai_message: {e}", exc_info=True)
    await message.answer("抱歉，处理您的消息时遇到错误。...")
```

**触发条件**：
- 整个消息处理过程中抛出异常
- 可能是：导入错误、API 调用异常、网络错误、格式错误等

## 🔎 根据日志分析的可能原因

### 原因 1：AI 包未安装（最可能）✅

**证据**：
```
WARNING - openai package not installed
WARNING - google-generativeai package not installed  
WARNING - No AI service available
```

**影响**：
- `AIService.__init__()` 时两个包都导入失败
- `self.openai_available = False`
- `self.gemini_available = False`
- `is_available()` 返回 `False`

**但是**：如果包未安装，`is_available()` 检查会提前返回，不会走到 `generate_response()`。

### 原因 2：包已安装但 API 调用失败 ⚠️

**可能的失败场景**：

1. **API 密钥无效**
   - 密钥格式错误
   - 密钥已过期
   - 密钥权限不足

2. **网络连接问题**
   - 无法连接到 OpenAI/Gemini API
   - 请求超时
   - DNS 解析失败

3. **API 配额用完**
   - OpenAI 账户余额不足
   - 免费额度已用完
   - 请求频率超限

4. **API 服务暂时不可用**
   - OpenAI/Gemini 服务维护
   - 服务器端错误

5. **请求参数错误**
   - 消息内容格式问题
   - 模型名称错误
   - 参数类型错误

### 原因 3：MarkdownV2 格式化错误 ⚠️

**可能的问题**：
- AI 返回的文本包含特殊字符
- `escape_markdown_v2()` 处理时出错
- 发送消息到 Telegram 时解析失败

### 原因 4：其他异常 💥

- 数据库连接问题
- 内存不足
- 权限问题
- 代码逻辑错误

## 📊 诊断步骤

### 步骤 1：查看详细错误日志

```bash
# 查看最近的错误日志
sudo journalctl -u wushizhifu-bot -n 200 --no-pager | grep -i "error\|exception\|traceback" -A 10

# 查看 AI 相关的日志
sudo journalctl -u wushizhifu-bot -n 200 --no-pager | grep -i "ai_service\|openai\|gemini" -A 5
```

### 步骤 2：测试 AI 服务初始化

```bash
cd ~/wushizhifu/bot
source venv/bin/activate

python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()

print("=== AI 服务诊断 ===")
from services.ai_service import get_ai_service

try:
    ai_service = get_ai_service()
    print(f"✅ AI 服务初始化成功")
    print(f"   - OpenAI 可用: {ai_service.openai_available}")
    print(f"   - Gemini 可用: {ai_service.gemini_available}")
    print(f"   - 总体可用: {ai_service.is_available()}")
    
    if ai_service.is_available():
        print("\n=== 测试 AI 响应生成 ===")
        try:
            response = ai_service.generate_response("你好")
            print(f"✅ 成功生成响应: {response[:50]}...")
        except Exception as e:
            print(f"❌ 生成响应失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ AI 服务不可用")
        print("   检查：")
        print("   1. 是否安装了 openai 或 google-generativeai 包")
        print("   2. 是否配置了 OPENAI_API_KEY 或 GEMINI_API_KEY")
        
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
EOF
```

### 步骤 3：检查 API 密钥有效性

```bash
# 测试 OpenAI API
python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"✅ OPENAI_API_KEY 已配置（长度: {len(api_key)}）")
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': 'Hello'}],
            max_tokens=10
        )
        print("✅ OpenAI API 密钥有效，测试成功")
    except Exception as e:
        print(f"❌ OpenAI API 测试失败: {e}")
else:
    print("❌ OPENAI_API_KEY 未配置")
EOF

# 测试 Gemini API
python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print(f"✅ GEMINI_API_KEY 已配置（长度: {len(api_key)}）")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content('Hello')
        print("✅ Gemini API 密钥有效，测试成功")
    except Exception as e:
        print(f"❌ Gemini API 测试失败: {e}")
else:
    print("❌ GEMINI_API_KEY 未配置")
EOF
```

## 🛠️ 修复方案

### 方案 1：确保包已安装

```bash
cd ~/wushizhifu/bot
source venv/bin/activate
pip install openai google-generativeai
sudo systemctl restart wushizhifu-bot
```

### 方案 2：增强错误日志

在 `handlers/ai_handlers.py` 的异常处理中添加更详细的日志：

```python
except Exception as e:
    logger.error(f"Error in handle_ai_message: {e}", exc_info=True)
    # 添加详细错误信息
    logger.error(f"AI service available: {ai_service.is_available()}")
    logger.error(f"OpenAI available: {ai_service.openai_available}")
    logger.error(f"Gemini available: {ai_service.gemini_available}")
    # ...
```

### 方案 3：改进错误处理

添加更细粒度的错误处理，区分不同类型的错误，给用户更明确的提示。

## ✅ 立即执行的诊断命令

```bash
# 一键诊断脚本
cd ~/wushizhifu/bot
source venv/bin/activate

echo "=== 完整诊断 ==="

echo "1. 检查包安装..."
pip list | grep -E "openai|google-generativeai" || echo "❌ 包未安装"

echo ""
echo "2. 检查环境变量..."
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OPENAI_API_KEY:', '✅' if os.getenv('OPENAI_API_KEY') else '❌'); print('GEMINI_API_KEY:', '✅' if os.getenv('GEMINI_API_KEY') else '❌')"

echo ""
echo "3. 测试 AI 服务..."
python3 -c "
from services.ai_service import get_ai_service
ai = get_ai_service()
print(f'AI 可用: {\"✅\" if ai.is_available() else \"❌\"}')
print(f'OpenAI: {\"✅\" if ai.openai_available else \"❌\"}')
print(f'Gemini: {\"✅\" if ai.gemini_available else \"❌\"}')
"

echo ""
echo "4. 查看最新日志..."
sudo journalctl -u wushizhifu-bot -n 50 --no-pager | tail -20
```

## 🎯 总结

**最可能的原因排序**：

1. **🔴 最可能**：AI 包未安装在虚拟环境中
2. **🟡 可能**：API 密钥无效或 API 调用失败
3. **🟢 较少**：网络问题或 API 服务不可用
4. **⚪ 很少**：代码逻辑错误或其他异常

**建议**：
1. 先执行诊断命令确认具体原因
2. 根据诊断结果进行相应修复
3. 查看详细日志了解具体错误信息

