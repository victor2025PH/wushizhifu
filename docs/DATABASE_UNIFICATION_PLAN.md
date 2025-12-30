# 数据库统一合并方案

## 一、当前数据库状态分析

### 1.1 数据库分布

#### BotA 和 Miniapp（已共享）
- **数据库路径**: `wushipay.db` (在项目根目录或 `botA/wushipay.db`)
- **数据库模块**: `database/db.py` 和 `database/models.py`
- **状态**: ✅ 已共享同一个数据库

#### BotB（独立）
- **数据库路径**: `botB/otc_bot.db`
- **数据库模块**: `botB/database.py`
- **状态**: ❌ 使用独立数据库

### 1.2 需要合并的表

BotB 数据库包含以下表（需要合并到共享数据库）：
1. `settings` - 全局设置（admin_markup, usdt_address）
2. `group_settings` - 群组设置（markup, usdt_address）
3. `user_settings` - 用户设置（onboarding_completed等）
4. `price_history` - 价格历史
5. `price_alerts` - 价格预警
6. `settlement_templates` - 结算模板
7. `usdt_addresses` - USDT地址管理
8. `operation_logs` - 操作日志
9. `transactions` - 交易记录（BotB特有格式）
10. `customer_service_accounts` - 客服账号（新增）
11. `customer_service_assignments` - 客服分配记录（新增）

## 二、合并方案

### 2.1 策略选择

**方案：统一使用共享数据库 `wushipay.db`**

- ✅ 统一数据访问
- ✅ 简化维护
- ✅ 数据一致性
- ✅ 便于后续扩展

### 2.2 实施步骤

#### 步骤1：扩展共享数据库模型
在 `database/models.py` 中添加 BotB 的所有表定义

#### 步骤2：修改 BotB 数据库连接
修改 `botB/database.py` 使用共享数据库路径

#### 步骤3：数据迁移（如果需要）
如果已有数据，需要迁移 `otc_bot.db` 到 `wushipay.db`

#### 步骤4：测试验证
确保所有功能正常工作

## 三、表结构对比

### 3.1 BotA/Miniapp 已有表
- `users` - 用户表
- `transactions` - 交易表（BotA格式）
- `rate_configs` - 汇率配置
- `admins` - 管理员表
- `groups` - 群组表
- `group_members` - 群组成员
- `sensitive_words` - 敏感词
- `video_configs` - 视频配置

### 3.2 BotB 独有表（需要添加）
- `settings` - 全局设置
- `group_settings` - 群组设置
- `user_settings` - 用户设置
- `price_history` - 价格历史
- `price_alerts` - 价格预警
- `settlement_templates` - 结算模板
- `usdt_addresses` - USDT地址管理
- `operation_logs` - 操作日志
- `customer_service_accounts` - 客服账号
- `customer_service_assignments` - 客服分配记录

### 3.3 冲突处理

**`transactions` 表冲突**：
- BotA 的 `transactions` 表结构与 BotB 不同
- 需要检查表结构差异，决定：
  - 方案A：合并为一个表（需要统一字段）
  - 方案B：重命名 BotB 的交易表为 `otc_transactions`（推荐，避免破坏现有数据）

## 四、实施计划

### 阶段1：准备工作
1. 备份现有数据库
2. 分析表结构差异
3. 确定表名冲突解决方案

### 阶段2：扩展共享数据库模型
1. 在 `database/models.py` 中添加 BotB 的表定义
2. 处理表名冲突（如有）

### 阶段3：修改 BotB 代码
1. 修改 `botB/database.py` 使用共享数据库
2. 更新所有导入语句
3. 确保方法兼容性

### 阶段4：数据迁移
1. 如果 `otc_bot.db` 有数据，迁移到 `wushipay.db`
2. 验证数据完整性

### 阶段5：测试和验证
1. 测试 BotA 功能
2. 测试 BotB 功能
3. 测试 Miniapp API
4. 验证数据一致性

