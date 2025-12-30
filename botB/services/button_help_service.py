"""
Button help service for Bot B
Provides help information for each button
"""
from typing import Dict, Optional
from database import db

# Button help content
BUTTON_HELP: Dict[str, Dict[str, str]] = {
    "💱 汇率": {
        "title": "💱 汇率查询",
        "description": "查看实时 USDT/CNY 汇率和币安 P2P 商户报价",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 点击「💱 汇率」按钮\n"
            "2. 选择支付方式（银行卡/支付宝/微信）\n"
            "3. 查看实时商户报价列表\n"
            "4. 使用翻页按钮查看更多商户\n\n"
            "💡 <i>提示：汇率数据来自币安 P2P，实时更新</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 实时币安 P2P 商户报价\n"
            "• 支持多种支付方式切换\n"
            "• 显示商户限额和成单数\n"
            "• 专业市场统计数据"
        )
    },
    "💰 结算": {
        "title": "💰 结算计算",
        "description": "快速计算人民币金额对应的 USDT 结算数量",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 点击「💰 结算」按钮\n"
            "2. 选择金额模板或算式模板\n"
            "3. 或直接输入金额（如：10000）\n"
            "4. 或输入算式（如：20000-200）\n"
            "5. 系统自动计算并生成结算单\n\n"
            "💡 <i>提示：支持批量结算，用逗号分隔多个金额</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 快速结算计算\n"
            "• 支持金额模板和算式模板\n"
            "• 自动记录交易\n"
            "• 支持批量结算"
        )
    },
    "📊 今日": {
        "title": "📊 今日账单",
        "description": "查看群组今日的交易统计和账单列表",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 在群组中点击「📊 今日」按钮\n"
            "2. 查看今日交易统计\n"
            "3. 查看最近 5 笔交易记录\n\n"
            "💡 <i>提示：仅群组可用，显示当日所有交易</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 实时交易统计\n"
            "• 交易次数和总金额\n"
            "• 最近交易记录\n"
            "• 群组专属功能"
        )
    },
    "📜 历史": {
        "title": "📜 历史账单",
        "description": "查看群组的历史交易记录，支持分页浏览",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 在群组中点击「📜 历史」按钮\n"
            "2. 查看历史交易列表（分页显示）\n"
            "3. 使用翻页按钮查看更多\n"
            "4. 点击交易可查看详情\n\n"
            "💡 <i>提示：仅群组可用，支持分页浏览</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 完整历史记录\n"
            "• 分页浏览\n"
            "• 交易详情查看\n"
            "• 高级搜索筛选"
        )
    },
    "📜 我的账单": {
        "title": "📜 我的账单",
        "description": "查看您个人的所有交易记录",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 在私聊中点击「📜 我的账单」按钮\n"
            "2. 查看您的所有交易记录\n"
            "3. 使用翻页按钮查看更多\n"
            "4. 点击交易可查看详情\n\n"
            "💡 <i>提示：仅私聊可用，显示您的所有交易</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 个人交易记录\n"
            "• 分页浏览\n"
            "• 交易详情查看\n"
            "• 状态跟踪"
        )
    },
    "🔗 地址": {
        "title": "🔗 收款地址",
        "description": "查看 USDT 收款地址（群组或全局）",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 点击「🔗 地址」按钮\n"
            "2. 查看当前群组或全局的 USDT 收款地址\n"
            "3. 复制地址用于转账\n\n"
            "💡 <i>提示：群组优先使用群组地址，否则使用全局地址</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 快速查看地址\n"
            "• 群组独立地址\n"
            "• 全局默认地址\n"
            "• 地址安全显示"
        )
    },
    "📞 客服": {
        "title": "📞 联系客服",
        "description": "获取人工客服联系方式",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 点击「📞 客服」按钮\n"
            "2. 查看客服联系方式\n"
            "3. 联系管理员获取帮助\n\n"
            "💡 <i>提示：7×24小时在线服务</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 快速联系客服\n"
            "• 7×24小时服务\n"
            "• 快速响应\n"
            "• 专业支持"
        )
    },
    "🔔 预警": {
        "title": "🔔 价格预警",
        "description": "设置价格预警，当汇率达到设定值时自动通知",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 点击「🔔 预警」按钮\n"
            "2. 创建价格预警\n"
            "3. 选择预警类型（高于/低于）\n"
            "4. 设置预警价格阈值\n"
            "5. 当价格达到阈值时自动通知\n\n"
            "💡 <i>提示：支持多个预警，实时监控价格变化</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 价格实时监控\n"
            "• 自动通知提醒\n"
            "• 支持多个预警\n"
            "• 灵活阈值设置"
        )
    },
    "⚙️ 设置": {
        "title": "⚙️ 群组设置",
        "description": "管理员专用：配置群组的加价和收款地址",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 管理员点击「⚙️ 设置」按钮\n"
            "2. 查看群组设置菜单\n"
            "3. 设置群组加价\n"
            "4. 设置群组收款地址\n"
            "5. 查看待支付/待确认交易\n"
            "6. 导出报表和查看日志\n\n"
            "💡 <i>提示：仅管理员可用，群组独立配置</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 群组独立配置\n"
            "• 加价和地址管理\n"
            "• 交易管理\n"
            "• 数据导出"
        )
    },
    "⚙️ 管理": {
        "title": "⚙️ 全局管理",
        "description": "管理员专用：配置全局默认设置和查看所有群组",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 管理员在私聊中点击「⚙️ 管理」按钮\n"
            "2. 查看全局管理菜单\n"
            "3. 设置全局默认加价\n"
            "4. 设置全局默认地址\n"
            "5. 查看所有群组列表\n"
            "6. 查看全局统计\n\n"
            "💡 <i>提示：仅管理员可用，影响所有未配置独立设置的群组</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 全局默认配置\n"
            "• 所有群组管理\n"
            "• 全局统计\n"
            "• 集中管理"
        )
    },
    "📈 统计": {
        "title": "📈 群组统计",
        "description": "管理员专用：查看群组的详细统计数据",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 管理员在群组中点击「📈 统计」按钮\n"
            "2. 查看群组交易统计\n"
            "3. 查看待支付/待确认交易\n"
            "4. 导出统计数据\n\n"
            "💡 <i>提示：仅管理员可用，群组专属统计</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 详细交易统计\n"
            "• 待处理交易管理\n"
            "• 数据导出\n"
            "• 可视化图表"
        )
    },
    "📊 数据": {
        "title": "📊 全局数据",
        "description": "管理员专用：查看全局统计数据和可视化图表",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 管理员在私聊中点击「📊 数据」按钮\n"
            "2. 查看全局统计数据\n"
            "3. 查看数据可视化图表\n"
            "4. 导出全局数据\n\n"
            "💡 <i>提示：仅管理员可用，全局数据统计</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 全局数据统计\n"
            "• 可视化图表\n"
            "• 数据导出\n"
            "• 多维度分析"
        )
    },
    "查看全局设置": {
        "title": "📋 查看全局设置",
        "description": "查看全局默认加价和收款地址设置",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 在全局管理菜单中点击「📋 查看全局设置」\n"
            "2. 查看当前全局默认加价\n"
            "3. 查看当前全局默认地址\n"
            "4. 了解哪些群组使用全局设置\n\n"
            "💡 <i>提示：全局设置将应用于所有未配置独立设置的群组</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 查看全局默认加价\n"
            "• 查看全局默认地址\n"
            "• 设置说明和提示"
        )
    },
    "所有群组列表": {
        "title": "📊 所有群组列表",
        "description": "查看所有有交易记录的群组，包括已配置和未配置的群组",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 在全局管理菜单中点击「📊 所有群组列表」\n"
            "2. 查看所有活跃群组列表\n"
            "3. 查看每个群组的配置状态\n"
            "4. 查看群组交易统计\n"
            "5. 点击「🔄 刷新列表」更新群组信息\n\n"
            "💡 <i>提示：显示所有有交易记录的群组，包括已配置和未配置的</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 显示所有活跃群组\n"
            "• 显示配置状态\n"
            "• 显示交易统计\n"
            "• 自动获取群组名称\n"
            "• 刷新功能"
        )
    },
    "全局统计": {
        "title": "📈 全局统计",
        "description": "查看全局交易统计数据，包括所有群组的汇总数据",
        "usage": (
            "📖 <b>使用方法：</b>\n\n"
            "1. 在全局管理菜单中点击「📈 全局统计」\n"
            "2. 查看全局交易统计数据\n"
            "3. 查看总交易次数和金额\n"
            "4. 查看活跃群组和用户数\n"
            "5. 导出统计数据（可选）\n\n"
            "💡 <i>提示：统计包括所有群组和私聊的交易数据</i>"
        ),
        "features": (
            "✨ <b>功能特点：</b>\n"
            "• 全局交易统计\n"
            "• 活跃群组统计\n"
            "• 用户统计\n"
            "• 数据导出\n"
            "• 可视化图表"
        )
    }
}


def get_button_help(button_text: str) -> Optional[Dict[str, str]]:
    """
    Get help information for a button.
    
    Args:
        button_text: Button text
        
    Returns:
        Dictionary with help information or None
    """
    return BUTTON_HELP.get(button_text)


def format_button_help_message(button_text: str) -> Optional[str]:
    """
    Format help message for a button.
    
    Args:
        button_text: Button text
        
    Returns:
        Formatted help message or None
    """
    help_info = get_button_help(button_text)
    if not help_info:
        return None
    
    message = f"{help_info['title']}\n\n"
    message += f"📝 <b>功能说明：</b>\n{help_info['description']}\n\n"
    message += help_info['usage'] + "\n\n"
    message += help_info['features']
    
    return message


def should_show_help(user_id: int, button_text: str) -> bool:
    """
    Check if help should be shown for a button.
    
    Args:
        user_id: User ID
        button_text: Button text
        
    Returns:
        True if help should be shown
    """
    # Check user preference
    help_key = f"button_help_shown_{button_text}"
    help_shown = db.get_user_setting(user_id, help_key)
    
    # If help was never shown, show it
    if help_shown is None:
        return True
    
    # If user explicitly disabled help, don't show
    if help_shown == "false":
        return False
    
    # Otherwise, show help (user can close it)
    return True


def mark_help_shown(user_id: int, button_text: str, shown: bool = True):
    """
    Mark help as shown or hidden for a button.
    
    Args:
        user_id: User ID
        button_text: Button text
        shown: Whether help was shown (True) or hidden (False)
    """
    help_key = f"button_help_shown_{button_text}"
    db.set_user_preference(user_id, help_key, "true" if shown else "false")


def reset_all_help(user_id: int):
    """
    Reset all button help preferences (show all help again).
    
    Args:
        user_id: User ID
    """
    for button_text in BUTTON_HELP.keys():
        help_key = f"button_help_shown_{button_text}"
        db.set_user_preference(user_id, help_key, None)

