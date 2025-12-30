# 客服管理系统优化方案

## 一、产品需求分析

### 1.1 业务背景
- 现有系统：用户在 Miniapp 中点击"开户"按钮，通过轮询方式分配给客服账号
- 当前限制：客服账号硬编码在前端代码中，无法动态管理
- 业务需求：支持 10+ 个客服账号的动态管理，包括增加、删除、分配策略配置

### 1.2 核心功能需求
1. **客服账号管理**
   - 增加客服账号
   - 删除客服账号
   - 查看客服账号列表
   - 启用/禁用客服账号

2. **分配策略管理**
   - 配置分配方式（轮询、最少任务、权重等）
   - 配置每个客服的权重/优先级
   - 配置客服的在线状态/接待能力

3. **统计和监控**
   - 查看每个客服的接待统计
   - 查看分配记录
   - 客服工作量分析

## 二、客服分配策略分析

### 2.1 常见分配方式对比

#### 方式一：简单轮询（Round-Robin）
**工作原理**：
- 按顺序依次分配给客服账号 1、2、3...、10、1、2...

**优点**：
- ✅ 实现简单
- ✅ 分配均匀
- ✅ 可预测性强

**缺点**：
- ❌ 不考虑客服在线状态
- ❌ 不考虑客服当前工作量
- ❌ 客服能力差异无法体现

**适用场景**：
- 客服能力相当
- 客服都长期在线
- 对响应时间要求不高

#### 方式二：最少任务优先（Least Busy）
**工作原理**：
- 实时统计每个客服当前接待的客户数
- 分配给当前接待最少的客服

**优点**：
- ✅ 负载均衡
- ✅ 响应速度快
- ✅ 考虑实际工作量

**缺点**：
- ❌ 需要实时统计机制
- ❌ 需要客服状态管理
- ❌ 实现复杂度较高

**适用场景**：
- 客服工作量差异较大
- 需要快速响应
- 有完善的统计系统

#### 方式三：权重分配（Weighted Round-Robin）
**工作原理**：
- 为每个客服设置权重（如：客服A权重3，客服B权重1）
- 按权重比例分配（客服A分配3个，客服B分配1个，循环）

**优点**：
- ✅ 可体现客服能力差异
- ✅ 分配相对均匀
- ✅ 配置灵活

**缺点**：
- ❌ 需要手动配置权重
- ❌ 权重调整需要经验
- ❌ 仍不考虑在线状态

**适用场景**：
- 客服能力有明显差异
- 需要差异化服务
- 有固定的客服等级体系

#### 方式四：智能混合分配（推荐⭐）
**工作原理**：
1. **第一层过滤**：只考虑启用且在线/可用的客服
2. **第二层选择**：在可用客服中，选择当前接待最少的
3. **第三层均衡**：如果接待数相同，使用权重或轮询
4. **第四层保底**：如果所有客服都不可用，使用轮询（可能分配给离线客服）

**优点**：
- ✅ 结合多种策略优势
- ✅ 灵活可配置
- ✅ 响应速度快
- ✅ 负载均衡

**缺点**：
- ❌ 实现复杂度高
- ❌ 需要完善的客服状态管理

**适用场景**：
- **最适合当前业务场景** ⭐
- 客服数量较多（10+）
- 需要高质量服务
- 客服在线状态不固定

### 2.2 推荐方案：智能混合分配

基于当前业务特点，**推荐使用"智能混合分配"策略**：

#### 核心逻辑
```
1. 筛选可用客服（启用 + 在线/可用）
   ↓
2. 如果无可用客服，使用轮询（保底机制）
   ↓
3. 在可用客服中，选择当前接待数最少的
   ↓
4. 如果接待数相同，按权重优先
   ↓
5. 如果权重相同，使用轮询
```

#### 配置参数
- **分配策略**：智能混合（默认）/ 简单轮询 / 最少任务 / 权重分配
- **客服状态**：在线（available）/ 离线（offline）/ 忙碌（busy）/ 禁用（disabled）
- **客服权重**：1-10（默认5）
- **最大接待数**：每个客服最多同时接待的客户数（默认50）

## 三、功能设计方案

### 3.1 数据库设计

#### 表：`customer_service_accounts`
```sql
CREATE TABLE customer_service_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,          -- 客服账号用户名（不含@）
    display_name TEXT,                      -- 显示名称
    status TEXT DEFAULT 'available',        -- 状态：available/offline/busy/disabled
    weight INTEGER DEFAULT 5,               -- 权重：1-10
    max_concurrent INTEGER DEFAULT 50,      -- 最大同时接待数
    current_count INTEGER DEFAULT 0,        -- 当前接待数
    total_served INTEGER DEFAULT 0,         -- 累计接待总数
    is_active INTEGER DEFAULT 1,            -- 是否启用：1=启用，0=禁用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 表：`customer_service_assignments`
```sql
CREATE TABLE customer_service_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,               -- 用户ID
    username TEXT,                          -- 用户名
    service_account TEXT NOT NULL,          -- 分配的客服账号
    assignment_method TEXT,                 -- 分配方式：round_robin/least_busy/weighted/smart
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',           -- 状态：active/completed/cancelled
    completed_at TIMESTAMP                  -- 完成时间
);
```

### 3.2 管理界面设计

#### 3.2.1 全局管理菜单增加"客服管理"
```
🌐 全局管理菜单
├── 📊 所有群组列表
├── 📈 全局统计
├── 👥 客服管理          ← 新增
├── ⚡ 管理员指令教程
└── 🔙 返回主菜单
```

#### 3.2.2 客服管理主菜单
```
👥 客服管理

📋 客服账号列表
➕ 添加客服账号
⚙️ 分配策略设置
📊 客服统计报表

🔙 返回
```

#### 3.2.3 客服账号列表
```
📋 客服账号列表（共 10 个）

1. @wushizhifu_jianglai
   状态：🟢 在线
   权重：5 | 当前接待：3/50
   累计接待：1,234 次
   [编辑] [禁用]

2. @service_account_02
   状态：🟡 忙碌
   权重：7 | 当前接待：48/50
   累计接待：2,456 次
   [编辑] [启用]

...

[➕ 添加客服] [🔙 返回]
```

#### 3.2.4 添加/编辑客服账号
```
➕ 添加客服账号

请输入客服账号用户名（不含@）：
[输入框：_________________]

显示名称（可选）：
[输入框：_________________]

权重设置（1-10，默认5）：
[输入框：5]

最大同时接待数（默认50）：
[输入框：50]

[✅ 确认] [❌ 取消]
```

#### 3.2.5 分配策略设置
```
⚙️ 分配策略设置

当前策略：智能混合分配 ⭐

可选策略：
○ 智能混合分配（推荐）
  - 综合考虑在线状态、工作量、权重
  - 响应快、负载均衡

○ 简单轮询
  - 按顺序依次分配
  - 实现简单、分配均匀

○ 最少任务优先
  - 分配给当前接待最少的客服
  - 负载均衡最优

○ 权重分配
  - 按权重比例分配
  - 可体现能力差异

[✅ 保存设置] [🔙 返回]
```

### 3.3 API 接口设计（后端）

#### 3.3.1 客服账号管理接口
```python
# 获取所有客服账号
GET /api/admin/customer-service/list
Response: List[CustomerServiceAccount]

# 添加客服账号
POST /api/admin/customer-service/add
Body: {username, display_name, weight, max_concurrent}
Response: {success, account_id}

# 更新客服账号
PUT /api/admin/customer-service/{id}/update
Body: {display_name, weight, max_concurrent, status}
Response: {success}

# 删除客服账号
DELETE /api/admin/customer-service/{id}
Response: {success}

# 启用/禁用客服账号
POST /api/admin/customer-service/{id}/toggle
Response: {success, is_active}
```

#### 3.3.2 分配策略接口
```python
# 获取当前分配策略
GET /api/admin/customer-service/strategy
Response: {method, config}

# 设置分配策略
POST /api/admin/customer-service/strategy
Body: {method, config}
Response: {success}

# 分配客服给用户（供前端调用）
GET /api/customer-service/assign?user_id={user_id}
Response: {service_account, method}
```

#### 3.3.3 统计接口
```python
# 获取客服统计
GET /api/admin/customer-service/stats
Response: {
    total_accounts: int,
    active_accounts: int,
    total_served: int,
    today_served: int,
    accounts: List[AccountStats]
}
```

### 3.4 前端集成（Miniapp）

#### 3.4.1 修改支持服务工具
```typescript
// utils/supportService.ts

// 从后端API获取客服账号（替代硬编码）
async function getCustomerServiceAccount(): Promise<string> {
  const response = await apiClient.get('/api/customer-service/assign', {
    params: { user_id: userId }
  });
  return response.data.service_account;
}

// 打开客服对话
export function openSupportChat(account?: string) {
  // 如果指定了账号，直接使用；否则从后端获取
  const targetAccount = account || await getCustomerServiceAccount();
  // 打开 Telegram 对话
  window.open(`https://t.me/${targetAccount}`);
}
```

## 四、用户体验优化建议

### 4.1 分配策略推荐

#### 场景一：客服能力相当、长期在线
- **推荐策略**：简单轮询
- **理由**：实现简单，分配均匀，满足基本需求

#### 场景二：客服数量多、在线状态不固定
- **推荐策略**：智能混合分配 ⭐
- **理由**：自动过滤离线客服，负载均衡，响应快

#### 场景三：有资深客服和新手客服
- **推荐策略**：权重分配 或 智能混合分配
- **理由**：可以通过权重体现能力差异，或通过智能分配自动优化

### 4.2 客服状态管理建议

#### 状态定义
- **🟢 在线（available）**：正常工作，可接受新客户
- **🟡 忙碌（busy）**：正在处理，接近最大接待数，谨慎分配
- **🔴 离线（offline）**：不在线，不分配新客户（但保留历史记录）
- **⚫ 禁用（disabled）**：被管理员禁用，不参与分配

#### 状态切换机制
1. **自动检测**（可选）：
   - 定期检查客服账号是否在线（通过 Telegram Bot API）
   - 如果检测到离线，自动标记为 offline

2. **手动设置**（推荐）：
   - 管理员手动设置状态
   - 客服可以通过特定命令切换状态（如：`/busy`, `/available`）

### 4.3 负载均衡优化

#### 实时统计机制
- 每次分配时，更新 `current_count`
- 定期（每5分钟）清理过期分配记录（超过24小时未活跃）
- 当客服完成服务时，手动或自动减少 `current_count`

#### 防溢出保护
- 如果所有客服都达到 `max_concurrent`，使用轮询（可能分配给忙碌的客服）
- 显示警告提示管理员增加客服或调整 `max_concurrent`

### 4.4 数据统计和分析

#### 关键指标
1. **客服效率**：
   - 平均响应时间
   - 平均服务时长
   - 客户满意度（如果后续添加）

2. **负载均衡**：
   - 各客服的接待数分布
   - 各客服的峰值时间

3. **分配效果**：
   - 各分配策略的使用情况
   - 分配成功率（成功分配到可用客服的比例）

## 五、实施优先级

### 阶段一：基础功能（MVP）
1. ✅ 数据库表设计
2. ✅ 客服账号CRUD（增加、删除、查看、编辑）
3. ✅ 简单轮询分配（保底机制）
4. ✅ 管理界面（列表、添加、删除）

### 阶段二：分配策略
1. ✅ 智能混合分配策略
2. ✅ 分配策略配置界面
3. ✅ 客服状态管理（在线/离线/忙碌/禁用）
4. ✅ 权重配置

### 阶段三：统计和优化
1. ✅ 客服统计报表
2. ✅ 分配记录查询
3. ✅ 负载均衡优化
4. ✅ 状态自动检测（可选）

## 六、技术实现要点

### 6.1 数据库层
- 使用 SQLite（与现有系统一致）
- 添加索引优化查询（username, status, is_active）
- 使用事务保证数据一致性

### 6.2 业务逻辑层
- 分配算法封装为独立服务类
- 支持策略模式，易于扩展新的分配策略
- 添加缓存机制（Redis可选，或使用内存缓存）提高性能

### 6.3 API层
- RESTful API 设计
- 添加权限验证（仅管理员可管理）
- 添加日志记录（分配记录、操作日志）

### 6.4 前端层
- 复用现有的 Miniapp 组件
- 保持用户体验一致性
- 添加加载状态和错误处理

## 七、风险评估和应对

### 7.1 潜在风险
1. **所有客服都不可用**：
   - 风险：用户无法联系客服
   - 应对：使用轮询保底机制，至少分配一个客服（即使离线）

2. **分配算法性能问题**：
   - 风险：客服数量多时，查询和计算耗时
   - 应对：添加缓存，优化数据库查询，限制查询范围

3. **数据不一致**：
   - 风险：current_count 与实际不符
   - 应对：定期清理过期记录，添加手动重置功能

### 7.2 兼容性考虑
- 保持现有前端代码兼容（支持硬编码账号作为fallback）
- 支持平滑迁移（先添加新功能，再逐步替换旧逻辑）

## 八、总结

### 8.1 推荐方案
- **分配策略**：智能混合分配（默认），支持切换到其他策略
- **实现方式**：数据库存储 + 后端API + 管理界面
- **用户体验**：保持现有流程，后端自动分配，用户无感知

### 8.2 核心优势
1. ✅ 灵活可配置：支持多种分配策略
2. ✅ 智能优化：自动过滤离线客服，负载均衡
3. ✅ 易于管理：完整的管理界面
4. ✅ 可扩展性：易于添加新功能和策略
5. ✅ 用户体验：分配过程对用户透明

### 8.3 下一步
1. 确认分配策略选择
2. 确认数据库设计方案
3. 确认管理界面设计
4. 开始技术实现

