# 数据库统一合并完成总结

## ✅ 完成状态

数据库统一合并已完成！现在 **Miniapp、BotA 和 BotB 都使用同一个数据库 `wushipay.db`**。

## 📊 合并结果

### 统一数据库文件
- **数据库路径**: `wushipay.db` (项目根目录)
- **备选路径**: `botA/wushipay.db` (如果根目录不存在时使用)

### 数据库包含的所有表

#### BotA/Miniapp 原有表
- `users` - 用户表
- `transactions` - BotA交易表（订单系统）
- `rate_configs` - 汇率配置
- `admins` - 管理员表
- `groups` - 群组表
- `group_members` - 群组成员
- `sensitive_words` - 敏感词
- `video_configs` - 视频配置

#### BotB 新增表（已合并）
- `settings` - 全局设置（admin_markup, usdt_address）
- `group_settings` - 群组设置（markup, usdt_address）
- `user_settings` - 用户设置（onboarding_completed等）
- `price_history` - 价格历史
- `price_alerts` - 价格预警
- `settlement_templates` - 结算模板
- `usdt_addresses` - USDT地址管理
- `operation_logs` - 操作日志
- `otc_transactions` - BotB交易表（结算系统，**已重命名**以避免冲突）
- `customer_service_accounts` - 客服账号
- `customer_service_assignments` - 客服分配记录

## 🔧 实施的技术改动

### 1. 数据库模型扩展
**文件**: `database/models.py`
- ✅ 添加了所有BotB的表定义
- ✅ BotB的交易表重命名为 `otc_transactions` 以避免与BotA的 `transactions` 表冲突

### 2. BotB数据库连接修改
**文件**: `botB/database.py`
- ✅ 修改数据库路径逻辑，使用共享数据库 `wushipay.db`
- ✅ 保留 `_init_database()` 方法用于初始化BotB特定的默认数据
- ✅ 所有 `transactions` 表引用已改为 `otc_transactions`

### 3. 代码更新
**文件**: `botB/services/chart_service.py`
- ✅ 所有 `transactions` 表引用已改为 `otc_transactions`

## ⚠️ 重要注意事项

### 表名冲突处理
- **BotA的transactions表**: 用于订单系统，字段包括 `order_id`, `payment_channel`, `amount`, `fee` 等
- **BotB的transactions表**: 已重命名为 `otc_transactions`，用于结算系统，字段包括 `group_id`, `cny_amount`, `usdt_amount`, `exchange_rate` 等
- 两个表结构完全不同，分别服务于不同的业务逻辑

### 数据库初始化
- **BotA**: 调用 `database.models.init_database()` 初始化所有表
- **BotB**: 保留自己的 `_init_database()` 方法，用于初始化BotB特定的默认数据（如settings默认值、settlement_templates预设值等）
- 由于使用 `CREATE TABLE IF NOT EXISTS`，表创建是安全的，不会冲突

### 向后兼容性
- ✅ BotB仍然可以独立运行，不影响现有功能
- ✅ 如果BotA先启动，BotB的表会在BotB首次运行时自动创建
- ✅ 如果BotB先启动，BotA的表会在BotA首次运行时自动创建

## 📝 后续工作建议

### 数据迁移（如需要）
如果生产环境中已有 `botB/otc_bot.db` 的数据需要迁移：

1. 备份现有数据库
2. 使用SQLite工具导出BotB的表数据
3. 导入到统一的 `wushipay.db`
4. 如果 `transactions` 表已存在，需要重命名为 `otc_transactions`

### 验证检查清单
- [ ] BotA功能正常（用户管理、交易记录等）
- [ ] BotB功能正常（结算、群组设置等）
- [ ] Miniapp API正常（用户认证、数据同步等）
- [ ] 三个系统能够正确访问共享数据库

## 🎉 优势

1. **数据一致性**: 所有数据统一管理，避免数据不同步
2. **简化维护**: 只需备份一个数据库文件
3. **便于扩展**: 未来功能可以共享数据表
4. **性能优化**: 减少数据库连接开销（虽然当前是SQLite，影响较小）

