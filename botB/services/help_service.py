"""
Context-aware help service for Bot B
Provides contextual help based on user actions
"""
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Help content database
HELP_CONTENT = {
    'settlement': {
        'title': '💰 结算功能',
        'content': (
            "💡 <b>如何使用结算功能：</b>\n\n"
            "• 直接输入金额：<code>10000</code>\n"
            "• 输入算式：<code>20000-200</code>\n"
            "• 批量结算：<code>1000,2000,3000</code>\n\n"
            "系统会自动计算应结算的 USDT 数量。"
        )
    },
    'price': {
        'title': '💱 汇率查询',
        'content': (
            "💡 <b>汇率说明：</b>\n\n"
            "• 基础价格来自 Binance P2P 实时数据\n"
            "• 最终价格 = 基础价格 + 加价\n"
            "• 不同群组可以设置不同的加价\n\n"
            "💡 提示：您可以设置价格预警，当价格变动时自动通知。"
        )
    },
    'templates': {
        'title': '📝 模板功能',
        'content': (
            "💡 <b>使用模板快速结算：</b>\n\n"
            "• 预设了常用金额模板（1000、5000、10000等）\n"
            "• 预设了常用算式模板（20000-200等）\n"
            "• 您可以创建自定义模板\n\n"
            "💡 提示：使用模板可以避免重复输入，提高效率。"
        )
    },
    'bills': {
        'title': '📜 账单查询',
        'content': (
            "💡 <b>账单功能说明：</b>\n\n"
            "• 查看今日账单：查看当天的交易记录\n"
            "• 历史账单：支持分页和筛选\n"
            "• 高级筛选：按金额、日期、状态筛选\n\n"
            "💡 提示：管理员可以导出账单为 CSV/Excel 格式。"
        )
    },
    'alerts': {
        'title': '🔔 价格预警',
        'content': (
            "💡 <b>价格预警功能：</b>\n\n"
            "• 设置价格上限：价格高于设定值时提醒\n"
            "• 设置价格下限：价格低于设定值时提醒\n"
            "• 自动通知：价格触发条件时自动发送通知\n\n"
            "💡 提示：预警通知频率限制为每5分钟一次。"
        )
    },
    'filter': {
        'title': '🔍 高级筛选',
        'content': (
            "💡 <b>筛选功能使用：</b>\n\n"
            "• 金额筛选：<code>1000-5000</code> 或 <code>>1000</code>\n"
            "• 日期筛选：<code>2025-01-01 2025-01-31</code> 或 <code>今天</code>\n"
            "• 状态筛选：待支付、已支付、已确认、已取消\n"
            "• 综合搜索：<code>金额:1000-5000 日期:今天 状态:已支付</code>\n\n"
            "💡 提示：可以组合多个筛选条件。"
        )
    },
    'export': {
        'title': '📥 数据导出',
        'content': (
            "💡 <b>导出功能说明：</b>\n\n"
            "• CSV 格式：轻量级，适合 Excel 打开\n"
            "• Excel 格式：带格式化，自动列宽调整\n"
            "• 支持筛选后导出\n\n"
            "💡 提示：导出功能仅限管理员使用。"
        )
    },
    'batch': {
        'title': '📦 批量结算',
        'content': (
            "💡 <b>批量结算功能：</b>\n\n"
            "• 逗号分隔：<code>1000,2000,3000</code>\n"
            "• 换行分隔：每行一个金额\n"
            "• 自动计算每一笔的 USDT 数量\n\n"
            "💡 提示：批量结算会自动创建多笔交易记录。"
        )
    },
    'error_invalid_amount': {
        'title': '❌ 金额格式错误',
        'content': (
            "💡 <b>正确的金额格式：</b>\n\n"
            "✅ 正确示例：\n"
            "• <code>10000</code> - 纯数字\n"
            "• <code>20000-200</code> - 算式\n"
            "• <code>10000+5000</code> - 加法\n\n"
            "❌ 错误示例：\n"
            "• <code>abc</code> - 包含字母\n"
            "• <code>10,000</code> - 包含逗号（应使用 10000）\n\n"
            "💡 提示：您可以使用模板功能快速选择常用金额。"
        )
    },
    'error_no_price': {
        'title': '❌ 无法获取价格',
        'content': (
            "💡 <b>价格获取失败的可能原因：</b>\n\n"
            "• 网络连接问题\n"
            "• API 服务暂时不可用\n\n"
            "💡 <b>解决方案：</b>\n"
            "• 稍后重试\n"
            "• 检查网络连接\n"
            "• 如果问题持续，请联系管理员"
        )
    }
}


def get_contextual_help(context: str) -> Optional[Dict[str, str]]:
    """
    Get contextual help content.
    
    Args:
        context: Help context identifier
        
    Returns:
        Dictionary with 'title' and 'content' or None
    """
    return HELP_CONTENT.get(context)


def get_button_help(button_text: str) -> Optional[str]:
    """
    Get help text for a button.
    
    Args:
        button_text: Button text
        
    Returns:
        Help text or None
    """
    button_help_map = {
        "💱 汇率": "查看当前 USDT/CNY 汇率（Binance P2P 数据源）",
        "📊 今日": "查看今日交易统计和账单列表",
        "📜 历史": "查看历史交易记录，支持筛选和分页",
        "💰 结算": "快速结算：输入金额或选择模板",
        "🔗 地址": "查看 USDT 收款地址",
        "📞 客服": "联系人工客服",
        "📝 模板": "使用常用金额或算式模板快速结算",
        "🔔 预警": "设置价格预警，价格变动时自动通知",
        "📜 我的账单": "查看您的个人交易记录",
        "📊 我的统计": "查看您的个人交易统计",
        "⚙️ 设置": "群组设置管理（管理员）",
        "⚙️ 管理": "全局管理（管理员）",
        "📈 统计": "查看群组统计数据（管理员）",
        "📊 数据": "查看全局统计数据（管理员）"
    }
    
    return button_help_map.get(button_text)


def get_error_help(error_type: str) -> Optional[Dict[str, str]]:
    """
    Get help content for an error.
    
    Args:
        error_type: Error type identifier
        
    Returns:
        Dictionary with 'title' and 'content' or None
    """
    return get_contextual_help(f'error_{error_type}')

