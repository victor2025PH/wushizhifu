# OKX 接口分析和替换方案

## 📊 OKX 接口分析

### 接口信息

**URL：**
```
https://www.okx.com/v3/c2c/tradingOrders/books?t=%7B$t%7D&quoteCurrency=cny&baseCurrency=usdt&side=sell&paymentMethod=aliPay&userType=all&receivingAds=false
```

**请求方式：** GET

**参数说明：**
- `quoteCurrency=cny` - 报价货币（人民币）
- `baseCurrency=usdt` - 基础货币（USDT）
- `side=sell` - 交易方向（卖出，即商家卖 USDT）
- `paymentMethod=aliPay` - 支付方式（支付宝）
- `userType=all` - 用户类型（所有）
- `receivingAds=false` - 是否接收广告

### 返回数据结构分析

根据提供的 JSON 数据，OKX 接口返回结构：

```json
{
  "code": 0,
  "data": {
    "buy": [],
    "sell": [
      {
        "price": "6.88",  // 价格（字符串格式）
        "availableAmount": "1120.72",  // 可用金额
        "paymentMethods": ["aliPay"],  // 支付方式
        "quoteMinAmountPerOrder": "2500.00",  // 最小订单金额
        "quoteMaxAmountPerOrder": "7710.55",  // 最大订单金额
        "avgCompletedTime": 20,  // 平均完成时间（秒）
        "avgPaymentTime": 125,  // 平均支付时间（秒）
        "completedRate": "0.9999",  // 完成率
        "completedOrderQuantity": 247007,  // 已完成订单数
        "nickName": "祥合生财贸易",  // 商家昵称
        "merchantId": "4cf3c7d359",  // 商家ID
        // ... 其他字段
      },
      // ... 更多商家
    ]
  }
}
```

### 接口特点

1. **实时报价接口** ✅
   - 这是 OKX 的 C2C 交易订单簿接口
   - 类似于币安的 P2P 接口
   - 返回实时的商家报价列表

2. **数据结构**
   - `code: 0` 表示成功
   - `data.sell[]` 包含所有卖家的报价
   - 每个商家有 `price` 字段（字符串格式，需要转换为 float）

3. **支付方式过滤**
   - 可以通过 `paymentMethod=aliPay` 参数过滤支付宝商家
   - 返回的数据中 `paymentMethods` 数组包含支持的支付方式

4. **价格计算**
   - 需要从多个商家中计算平均价格（类似币安的处理方式）
   - 可以过滤掉最小/最大金额不符合要求的商家

## 🔍 当前系统使用币安接口的情况

### Bot B（机器人）

**文件：** `botB/services/price_service.py`

**当前实现：**
- 使用币安 P2P API：`https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search`
- POST 请求，需要 JSON payload
- 获取 20 个商家，计算平均价格
- 只使用支付宝（`payTypes: ["ALIPAY"]`）
- 有 60 秒缓存机制
- 失败时回退到 CoinGecko API

**使用场景：**
- 结算计算时获取汇率
- 显示汇率信息时
- 所有需要 USDT/CNY 价格的地方

### MiniApp（小程序）

**文件：** `wushizhifu-full/components/Dashboard.tsx`

**当前实现：**
- 调用后端 API：`/api/binance/p2p`
- 用于显示币安 P2P 商家排行榜（`BinanceRateModal`）
- 前端使用固定汇率：`EXCHANGE_RATE_CNY_USDT = 7.24`（在 `types.ts` 中）

**使用场景：**
- 显示币安 P2P 商家排行榜
- 计算器中使用固定汇率（需要改为动态获取）

### API 服务器（Bot A）

**需要检查：** `botA/api_server.py` 中是否有 `/api/binance/p2p` 端点

## 📋 替换方案

### 方案概述

**目标：** 将币安 P2P 接口替换为 OKX C2C 接口

**替换范围：**
1. Bot B 的 `price_service.py` - 获取汇率的核心服务
2. API 服务器的 `/api/binance/p2p` 端点（如果存在）
3. MiniApp 中的币安相关显示和计算

### 详细替换方案

#### 1. Bot B - `price_service.py`

**需要修改：**

1. **接口 URL 和请求方式**
   - 从 POST 改为 GET
   - URL：`https://www.okx.com/v3/c2c/tradingOrders/books`
   - 参数通过 URL query string 传递

2. **请求参数映射**
   ```
   币安参数 → OKX 参数
   - fiat: CNY → quoteCurrency: cny
   - asset: USDT → baseCurrency: usdt
   - tradeType: BUY → side: sell
   - payTypes: ["ALIPAY"] → paymentMethod: aliPay
   - rows: 20 → 需要查看 OKX 是否支持分页参数
   ```

3. **响应解析**
   - 币安：`data[].adv.price`（字符串）
   - OKX：`data.sell[].price`（字符串）
   - 都需要转换为 float 并计算平均值

4. **错误处理**
   - 保持相同的错误处理逻辑
   - 保持 CoinGecko 作为回退方案

5. **缓存机制**
   - 保持 60 秒缓存不变

#### 2. API 服务器 - `/api/binance/p2p` 端点

**需要修改：**

1. **端点重命名（可选）**
   - 可以保留 `/api/binance/p2p` 但内部调用 OKX
   - 或者新增 `/api/okx/c2c` 端点
   - 或者统一改为 `/api/exchange-rate` 或 `/api/p2p-rate`

2. **响应格式**
   - 保持与币安接口相同的响应格式（如果前端依赖）
   - 或者更新前端以适配新的响应格式

#### 3. MiniApp - 前端代码

**需要修改：**

1. **API 调用**
   - `api.ts` 中的 `getBinanceP2P()` 方法
   - 改为调用 OKX 接口或新的统一端点

2. **组件显示**
   - `BinanceRateModal.tsx` 可能需要重命名为 `ExchangeRateModal.tsx`
   - 更新显示文本（从"币安 P2P"改为"OKX C2C"或通用名称）

3. **固定汇率**
   - `types.ts` 中的 `EXCHANGE_RATE_CNY_USDT`
   - 改为从 API 动态获取

4. **计算器**
   - `CalculatorModal.tsx` 和 `PaymentForm.tsx`
   - 使用动态汇率而不是固定值

### 技术对比

| 特性 | 币安 P2P | OKX C2C |
|------|---------|---------|
| **请求方式** | POST | GET |
| **URL** | `p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search` | `www.okx.com/v3/c2c/tradingOrders/books` |
| **参数格式** | JSON body | URL query string |
| **响应结构** | `data[]` 数组 | `data.sell[]` 数组 |
| **价格字段** | `adv.price` | `price` |
| **支付方式过滤** | `payTypes: ["ALIPAY"]` | `paymentMethod=aliPay` |
| **分页支持** | `page`, `rows` | 需要确认 |
| **商家信息** | 较详细 | 较详细（包含更多统计信息） |

### 优势分析

**使用 OKX 的优势：**
1. ✅ **更丰富的商家信息** - 包含完成率、平均时间等统计
2. ✅ **GET 请求更简单** - 不需要 JSON payload
3. ✅ **可能更稳定** - 作为备选数据源
4. ✅ **多数据源** - 可以与币安并行使用，取平均值

**潜在问题：**
1. ⚠️ **分页参数** - 需要确认 OKX 是否支持 `page` 和 `limit` 参数
2. ⚠️ **响应格式不同** - 需要适配代码
3. ⚠️ **API 稳定性** - 需要测试 OKX 接口的可用性和限流情况

### 推荐方案

#### 方案 A：完全替换（推荐）

**步骤：**
1. 修改 `price_service.py`，将币安接口替换为 OKX
2. 更新 API 服务器端点（如果存在）
3. 更新 MiniApp 前端调用
4. 更新所有显示文本（"币安 P2P" → "OKX C2C" 或通用名称）

**优点：**
- 代码更简洁
- 维护成本低
- 统一数据源

**缺点：**
- 失去币安作为备选
- 如果 OKX 接口不稳定，影响较大

#### 方案 B：双数据源（更稳健）

**步骤：**
1. 保留币安接口作为主要数据源
2. 添加 OKX 接口作为次要数据源
3. 计算两个数据源的平均价格
4. 如果其中一个失败，使用另一个

**优点：**
- 更高的可靠性
- 价格更准确（多数据源平均）
- 有备选方案

**缺点：**
- 代码更复杂
- 需要维护两个接口
- API 调用次数增加

#### 方案 C：智能切换

**步骤：**
1. 同时调用币安和 OKX
2. 比较两个价格
3. 选择更合理的价格（或取平均值）
4. 如果其中一个失败，自动使用另一个

**优点：**
- 最佳价格选择
- 高可用性
- 自动故障转移

**缺点：**
- 实现最复杂
- 需要价格比较逻辑

### 实施建议

**推荐：方案 B（双数据源）**

**理由：**
1. 提高系统可靠性
2. 价格更准确（多数据源验证）
3. 有备选方案，降低单点故障风险
4. 可以逐步迁移，先添加 OKX，再考虑是否移除币安

**实施步骤：**
1. 先添加 OKX 接口支持（不删除币安）
2. 实现双数据源价格计算
3. 测试稳定性
4. 根据实际使用情况决定是否完全替换

## 🔧 需要修改的文件清单

### Bot B
- `botB/services/price_service.py` - 核心价格服务

### API 服务器（Bot A）
- `botA/api_server.py` - `/api/binance/p2p` 端点（如果存在）

### MiniApp
- `wushizhifu-full/api.ts` - API 客户端
- `wushizhifu-full/components/BinanceRateModal.tsx` - 汇率显示组件
- `wushizhifu-full/components/Dashboard.tsx` - 主面板
- `wushizhifu-full/components/CalculatorModal.tsx` - 计算器
- `wushizhifu-full/components/PaymentForm.tsx` - 支付表单
- `wushizhifu-full/types.ts` - 类型定义（固定汇率）

## ⚠️ 注意事项

1. **API 限流**
   - 需要测试 OKX 接口的限流情况
   - 保持缓存机制，避免频繁请求

2. **错误处理**
   - 确保有完善的错误处理和回退机制
   - 保留 CoinGecko 作为最后回退

3. **数据格式**
   - OKX 的价格是字符串，需要转换为 float
   - 注意精度问题

4. **测试**
   - 需要充分测试新接口的稳定性
   - 对比币安和 OKX 的价格差异
   - 确保不影响现有功能

5. **向后兼容**
   - 如果前端依赖特定的响应格式，需要保持兼容
   - 或者同时更新前端代码

## 📝 总结

**OKX 接口确认：**
- ✅ 这是 OKX 的实时 C2C 交易订单簿接口
- ✅ 可以获取支付宝商家的 USDT/CNY 报价
- ✅ 数据结构清晰，易于解析

**替换建议：**
- 推荐使用**方案 B（双数据源）**，提高系统可靠性
- 先添加 OKX 支持，保留币安作为备选
- 根据实际使用情况决定是否完全替换

**下一步：**
- 确认 OKX 接口的分页参数
- 测试接口的稳定性和限流情况
- 实施代码修改
