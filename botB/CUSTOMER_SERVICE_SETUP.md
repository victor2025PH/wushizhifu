# 客服账号配置指南

## 📋 配置10个客服账号并启用顺序轮转

### 步骤1: 运行批量添加脚本

在服务器上执行以下命令：

```bash
cd /home/ubuntu/wushizhifu/botB
python3 add_customer_service_accounts.py
```

脚本会自动：
1. ✅ 添加10个客服账号到数据库
2. ✅ 设置分配策略为 `round_robin`（顺序轮转）

### 步骤2: 验证配置

运行脚本后，会显示：
- 成功添加的账号数量
- 已存在跳过的账号数量
- 失败的账号数量
- 当前所有客服账号列表

### 步骤3: 手动验证（可选）

如果需要手动检查或调整，可以：

```bash
# 连接到数据库
sqlite3 /home/ubuntu/wushizhifu/wushipay.db

# 查看所有客服账号
SELECT id, username, display_name, is_active, status, weight, total_served FROM customer_service_accounts;

# 查看当前分配策略
SELECT * FROM settings WHERE key = 'customer_service_strategy';

# 退出
.quit
```

## 🔄 分配策略说明

脚本会自动将分配策略设置为 **`round_robin`（简单轮询）**，这意味着：

- ✅ 按账号顺序依次分配
- ✅ 每个新用户会被分配给最近最少分配的客服
- ✅ 确保客服账号负载均衡

### 如何更改分配策略

如果需要在Bot B中手动更改分配策略：

1. 在Bot B中点击 "⚙️ 管理" → "📞 客服管理" → "⚙️ 分配策略设置"
2. 选择 "○ 简单轮询"（round_robin）

或者在数据库中直接设置：

```sql
INSERT OR REPLACE INTO settings (key, value, updated_at)
VALUES ('customer_service_strategy', 'round_robin', CURRENT_TIMESTAMP);
```

## ✅ 配置的10个客服账号

脚本会添加以下账号：

1. @zxc123456cxsj
2. @wubaizhifuaran
3. @Mark77585
4. @Moon727888
5. @yuanpay_01
6. @wushizhifu888
7. @wushi987
8. @xiaoyue5918
9. @Aeight888
10. @wuzhifu_8

## 🔗 使用场景

配置完成后，以下按钮/功能都会使用相同的顺序轮转逻辑：

1. **Telegram Bot B 群组中的"客服"按钮**
   - 点击后自动分配客服账号
   - 直接跳转到分配的客服对话

2. **Web前端的"Telegram"客服按钮**（CustomerSupport组件）
   - 点击后调用 `/api/customer-service/assign` API
   - 分配客服并跳转

3. **MiniApp的"立即开户"按钮**（Dashboard组件）
   - 点击后调用 `assignCustomerService` 函数
   - 分配客服并显示跳转链接

4. **MiniApp的"客服支持"按钮**（ProfileView组件）
   - 点击后同样使用客服分配逻辑

## 📝 注意事项

1. **账号格式**: 脚本会自动移除用户名前的 `@` 符号
2. **重复添加**: 如果账号已存在，脚本会跳过并显示警告
3. **默认配置**: 
   - 权重 (weight): 5
   - 最大并发数 (max_concurrent): 50
   - 状态 (status): available
   - 是否激活 (is_active): 1 (激活)

## 🔧 故障排查

### 问题1: 脚本运行失败

```bash
# 检查Python环境
python3 --version

# 检查数据库文件权限
ls -la /home/ubuntu/wushizhifu/wushipay.db

# 检查Bot B目录
cd /home/ubuntu/wushizhifu/botB
ls -la
```

### 问题2: 账号添加失败

- 检查数据库连接
- 检查账号用户名格式是否正确
- 查看脚本输出错误信息

### 问题3: 分配策略未生效

```bash
# 在数据库中检查
sqlite3 /home/ubuntu/wushizhifu/wushipay.db "SELECT * FROM settings WHERE key = 'customer_service_strategy';"
```

如果值为空或不是 `round_robin`，手动设置：

```sql
INSERT OR REPLACE INTO settings (key, value, updated_at)
VALUES ('customer_service_strategy', 'round_robin', CURRENT_TIMESTAMP);
```

### 问题4: 客服分配不工作

1. 检查是否有激活的客服账号：
   ```sql
   SELECT COUNT(*) FROM customer_service_accounts WHERE is_active = 1;
   ```

2. 检查API服务是否正常运行：
   ```bash
   sudo systemctl status api-server
   ```

3. 查看API日志：
   ```bash
   sudo journalctl -u api-server -f
   ```
