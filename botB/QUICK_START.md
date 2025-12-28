# Bot B 快速启动指南

## 📋 前置要求

- Python 3.8+
- 已安装 pip
- 已创建 `.env` 文件（在项目根目录，与 `wushizhifu-otc-bot` 同级）

## 🚀 快速开始

### 1. 安装依赖

```bash
cd wushizhifu-otc-bot
pip install -r requirements.txt
```

### 2. 配置 .env 文件

确保项目根目录（`wushizhifu`）下的 `.env` 文件包含两个 Bot Token：

```env
BOT_TOKEN=your_first_bot_token_here
BOT_TOKEN_B=your_second_bot_token_here
```

**重要**：Bot B 会读取第二行的 `BOT_TOKEN_B`。

### 3. 验证配置

运行测试脚本验证所有配置是否正确：

```bash
python test_setup.py
```

如果所有测试通过，你会看到：
```
✅ All tests passed! Bot B is ready to run.
```

### 4. 启动 Bot

```bash
python bot.py
```

## 📝 可用命令

启动 Bot 后，在 Telegram 中可以使用以下命令：

- `/start` - 启动 Bot 并显示欢迎消息
- `/help` - 显示帮助信息
- `/price` - 获取当前 USDT/CNY 价格（包含管理员加价）
- `/settings` - 查看当前设置（管理员加价和 USDT 地址）

## 🔧 数据库操作

数据库文件会自动创建在 `wushizhifu-otc-bot/otc_bot.db`。

### 默认设置

- **admin_markup**: 0.0（管理员加价，添加到汇率上）
- **usdt_address**: （空，USDT 收款地址）

### 通过代码修改设置

```python
from database import db

# 设置管理员加价
db.set_admin_markup(0.5)  # 加价 0.5 CNY

# 设置 USDT 地址
db.set_usdt_address("TYourUSDTAddressHere")

# 读取设置
markup = db.get_admin_markup()
address = db.get_usdt_address()
```

## 🌐 OKX API 价格获取

Bot 使用 OKX Public API 获取 USDT/CNY 实时价格：

- **端点**: `https://www.okx.com/api/v5/market/ticker`
- **交易对**: USDT-CNY
- **错误处理**: 如果 API 失败，使用默认价格 7.20 CNY

### 价格计算逻辑

```
最终价格 = OKX 基础价格 + 管理员加价
```

例如：
- OKX 价格：7.2345 CNY
- 管理员加价：0.5 CNY
- 最终价格：7.7345 CNY

## 🐛 故障排除

### 问题 1: Bot Token 未找到

**错误信息**:
```
Configuration error: BOT_TOKEN_B is not set...
```

**解决方法**:
1. 检查 `.env` 文件是否存在
2. 确认第二行包含 `BOT_TOKEN_B=your_token_here`
3. 或设置环境变量：`export BOT_TOKEN_B=your_token_here`

### 问题 2: 数据库初始化失败

**错误信息**:
```
Database initialization failed
```

**解决方法**:
1. 检查目录权限
2. 确保有写入权限
3. 手动删除 `otc_bot.db` 后重新运行

### 问题 3: OKX API 请求失败

**现象**: `/price` 命令返回回退价格

**原因**: OKX API 可能暂时不可用或网络问题

**解决方法**:
- 这是正常的，Bot 会自动使用回退价格
- 检查网络连接
- 稍后重试

## 📁 项目结构

```
wushizhifu-otc-bot/
├── bot.py                 # Bot 主入口
├── config.py              # 配置管理
├── database.py            # 数据库操作
├── requirements.txt       # Python 依赖
├── test_setup.py         # 测试脚本
├── README.md             # 详细文档
├── QUICK_START.md        # 本文件
└── services/
    └── price_service.py  # OKX 价格服务
```

## 🔄 双 Bot 模式

这个项目支持双 Bot 模式：

- **Bot A** (wushizhifu-bot): 主支付 Bot
- **Bot B** (wushizhifu-otc-bot): OTC 群组管理 Bot

两个 Bot 可以同时运行，使用不同的 Token 和数据库。

## 📞 需要帮助？

如果遇到问题：

1. 运行 `python test_setup.py` 检查配置
2. 查看日志输出
3. 检查 `.env` 文件格式
4. 确认所有依赖已安装

---

**祝使用愉快！** 🎉

