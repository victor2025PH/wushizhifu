# 修复导入错误

## 🐛 问题描述

服务器上出现导入错误，导致 `otc-bot.service` 不断重启：

```
ImportError: cannot import name 'generate_transaction_trend_chart' from 'services.chart_service'
```

## 🔍 问题原因

`botB/handlers/chart_handlers.py` 试图从 `services.chart_service` 导入以下函数：
- `generate_transaction_trend_chart`
- `generate_transaction_volume_chart`
- `generate_user_distribution_chart`
- `generate_price_trend_chart`

但这些函数在 `chart_service.py` 中不存在。`chart_service.py` 已经被重构为只提供文本图表功能（`ChartService` 类）。

## ✅ 修复方案

已注释掉 `bot.py` 中对 `chart_handlers` 的导入和相关命令注册，因为：
1. 这些函数在 `chart_service.py` 中不存在
2. 当前系统使用文本图表（`ChartService.generate_simple_bar()`），而不是图像图表
3. 这些功能不是核心功能，可以暂时禁用

## 📝 修复内容

- 注释掉 `chart_handlers` 的导入
- 注释掉所有图表相关的命令处理函数
- 注释掉图表命令的注册

## 🚀 部署

修复已推送到 GitHub，GitHub Actions 会自动部署，或手动执行：

```bash
# 在服务器上
cd /home/ubuntu/wushizhifu
git pull origin main
cd botB
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart otc-bot.service
```

## 💡 后续改进

如果需要图表功能，可以：
1. 重新实现 `chart_handlers.py` 使用 `ChartService` 的文本图表方法
2. 或者添加图像图表库（如 matplotlib）并实现相应的函数

---

**修复已完成并已推送，服务应该可以正常启动了。**
