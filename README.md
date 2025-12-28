# 伍拾支付 - 双 Bot 系统

Telegram Bot 系统，包含两个独立的 Bot：
- **Bot A**: 支付和用户管理 Bot
- **Bot B**: OTC 群组管理 Bot

## 📁 项目结构

```
wushizhifu/
├── .env                    # 环境变量配置（包含 BOT_TOKEN 和 BOT_TOKEN_B）
├── .github/
│   └── workflows/
│       ├── deploy-botA.yml    # Bot A 自动部署
│       └── deploy-botB.yml    # Bot B 自动部署
├── botA/                   # Bot A (支付 Bot)
│   ├── bot.py
│   ├── config.py
│   ├── database/
│   ├── handlers/
│   ├── services/
│   └── requirements.txt
├── botB/                   # Bot B (OTC 群组管理 Bot)
│   ├── bot.py
│   ├── config.py
│   ├── database.py
│   ├── services/
│   └── requirements.txt
└── README.md
```

## 🚀 快速开始

### 1. 本地开发

```bash
# 克隆仓库
git clone https://github.com/victor2025PH/wushizhifu.git
cd wushizhifu

# 创建 .env 文件
cat > .env << EOF
BOT_TOKEN=your_bot_a_token_here
BOT_TOKEN_B=your_bot_b_token_here
EOF

# 运行 Bot A
cd botA
pip install -r requirements.txt
python bot.py

# 运行 Bot B (新终端)
cd botB
pip install -r requirements.txt
python bot.py
```

### 2. 服务器部署

#### 手动部署：

```bash
# 在服务器上
cd /home/ubuntu/wushizhifu
git clone https://github.com/victor2025PH/wushizhifu.git .
# 或更新现有代码
git pull origin main

# 设置 .env 文件
nano .env
# 添加: BOT_TOKEN=... 和 BOT_TOKEN_B=...

# 部署 Bot A
cd botA
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 部署 Bot B
cd ../botB
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 使用 systemd 服务：

参考 `迁移说明.md` 创建和配置 systemd 服务。

### 3. GitHub Actions 自动部署

1. 配置 GitHub Secrets（见 `迁移说明.md`）
2. 推送代码到 `main` 分支
3. GitHub Actions 会自动部署到服务器

## 🔧 配置说明

### 环境变量 (.env)

```env
# Bot A Token
BOT_TOKEN=your_bot_a_token_here

# Bot B Token
BOT_TOKEN_B=your_bot_b_token_here
```

### Bot A 配置

- 配置文件：`botA/config.py`
- 从根目录 `.env` 读取 `BOT_TOKEN`
- 数据库：SQLite (在 `botA/` 目录)

### Bot B 配置

- 配置文件：`botB/config.py`
- 从根目录 `.env` 读取 `BOT_TOKEN_B`
- 数据库：SQLite (`otc_bot.db` 在 `botB/` 目录)

## 📚 文档

- [项目结构规划](项目结构规划.md)
- [迁移说明](迁移说明.md)
- [Bot A 文档](botA/README.md)
- [Bot B 文档](botB/README.md)

## 🔄 更新和维护

### 手动更新：

```bash
cd /home/ubuntu/wushizhifu
git pull origin main
cd botA && source venv/bin/activate && pip install -r requirements.txt -q
cd ../botB && source venv/bin/activate && pip install -r requirements.txt -q
sudo systemctl restart botA.service botB.service
```

### 自动更新：

推送代码到 GitHub，Actions 会自动处理。

## 📞 支持

如有问题，请查看各 Bot 的 README 文档或提交 Issue。

---

**© 2025 伍拾支付 | WUSHI PAY**

