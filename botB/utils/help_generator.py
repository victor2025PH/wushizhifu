"""
Help message generator for commands and features
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class HelpGenerator:
    """Generator for help messages and usage instructions"""
    
    @staticmethod
    def get_admin_command_help() -> str:
        """Get comprehensive admin commands help"""
        help_text = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  📖 管理员命令帮助\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "<b>🔐 管理员管理</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• <code>/addadmin &lt;user_id&gt;</code> - 添加管理员（仅超级管理员）\n"
            "• <code>/deladmin &lt;user_id&gt;</code> - 删除管理员（需确认，仅超级管理员）\n"
            "• <code>/admin</code> - 打开管理员面板\n\n"
            
            "<b>👥 用户管理</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• <code>/search_user &lt;条件&gt;</code> - 搜索用户（ID/用户名/VIP/日期）\n"
            "• <code>/user_detail &lt;user_id&gt;</code> - 查看用户详情\n"
            "• <code>/set_vip &lt;user_id&gt; &lt;level&gt;</code> - 设置VIP等级（0-10）\n"
            "• <code>/batch_set_vip &lt;user_ids&gt; &lt;level&gt;</code> - 批量设置VIP（最多50个，需确认）\n"
            "• <code>/disable_user &lt;user_id&gt;</code> - 禁用用户（需确认）\n"
            "• <code>/enable_user &lt;user_id&gt;</code> - 启用用户\n"
            "• <code>/batch_disable_users &lt;user_ids&gt; disable</code> - 批量禁用用户（最多50个，需确认）\n"
            "• <code>/batch_enable_users &lt;user_ids&gt;</code> - 批量启用用户（最多50个，需确认）\n"
            "• <code>/export_users</code> - 导出所有用户数据（CSV）\n"
            "• <code>/batch_export_users &lt;user_ids&gt;</code> - 批量导出指定用户（最多100个，CSV）\n\n"
            
            "<b>🚫 敏感词管理</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• <code>/addword &lt;词&gt; [action]</code> - 添加敏感词\n"
            "• <code>/addword batch &lt;词1,词2&gt; [action]</code> - 批量添加（最多50个）\n"
            "• <code>/delword &lt;word_id&gt;</code> - 删除敏感词\n"
            "• <code>/delword batch &lt;id1,id2&gt;</code> - 批量删除（最多50个）\n"
            "• <code>/editword &lt;word_id&gt; &lt;action&gt;</code> - 编辑敏感词动作\n"
            "• <code>/import_words &lt;文本&gt;</code> - 批量导入敏感词（最多100个）\n"
            "• <code>/export_words</code> - 导出敏感词列表（CSV）\n\n"
            
            "<b>👥 群组管理</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• <code>/addgroup &lt;group_id&gt;</code> - 添加群组到管理系统\n"
            "• <code>/delgroup &lt;group_id&gt;</code> - 删除群组（需确认）\n"
            "• <code>/group_detail &lt;group_id&gt;</code> - 查看群组详情\n"
            "• <code>/search_group &lt;条件&gt;</code> - 搜索群组（ID/名称/状态）\n"
            "• <code>/group_verify &lt;group_id&gt; &lt;enable|disable&gt;</code> - 启用/禁用验证\n"
            "• <code>/group_mode &lt;group_id&gt; &lt;question|manual&gt;</code> - 设置验证模式\n\n"
            
            "<b>✅ 审核管理</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• <code>/pass_user &lt;user_id&gt; &lt;group_id&gt;</code> - 通过审核\n"
            "• <code>/reject_user &lt;user_id&gt; &lt;group_id&gt;</code> - 拒绝审核\n\n"
            
            "<b>🔧 其他命令</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• <code>/confirm</code> - 确认待处理的操作\n"
            "• <code>/admin</code> - 打开管理员面板（使用底部按钮更方便）\n\n"
            
            "<b>💡 使用提示</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• 使用 <code>/admin</code> 打开管理员面板，可使用底部按钮操作\n"
            "• 所有删除和禁用操作都需要确认（重复命令或使用 /confirm）\n"
            "• 批量操作有数量限制（敏感词50个，导入100个）\n"
            "• 使用搜索功能可以快速查找用户和群组\n"
            "• 操作日志会记录所有管理员操作，可在统计中查看\n\n"
            
            "💡 更多帮助：使用管理员面板的底部按钮进行操作，更直观便捷"
        )
        
        return help_text
    
    @staticmethod
    def get_button_tutorial(button_type: str) -> str:
        """Get button tutorial for specific button type"""
        tutorials = {
            'main_menu': HelpGenerator.get_main_menu_buttons_help(),
            'admin_panel': HelpGenerator.get_admin_panel_buttons_help(),
            'group_buttons': HelpGenerator.get_group_buttons_help(),
            'admin_submenus': HelpGenerator.get_admin_submenus_help(),
        }
        return tutorials.get(button_type, "💡 按钮教程暂未提供")
    
    @staticmethod
    def get_main_menu_buttons_help() -> str:
        """Get help for main menu buttons"""
        return (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  🏠 主菜单按钮教程\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "<b>第一行按钮：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💱 <b>汇率</b>\n"
            "• 功能：查看 Binance P2P 实时汇率\n"
            "• 显示：买一价、卖一价、中间价\n"
            "• 用途：了解当前市场价格\n\n"
            
            "💰 <b>结算</b>\n"
            "• 功能：计算 CNY 到 USDT 的结算金额\n"
            "• 用法：直接输入金额或算式（如：20000 或 20000-200）\n"
            "• 显示：汇率、加价、最终结算金额\n"
            "• 提示：支持加减运算，自动应用群组加价\n\n"
            
            "📜 <b>我的账单</b>\n"
            "• 功能：查看个人交易账单\n"
            "• 显示：待支付、已支付、失败、已取消订单\n"
            "• 用途：跟踪交易状态和历史记录\n\n"
            
            "<b>第二行按钮：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 <b>地址</b>\n"
            "• 功能：查看或设置 USDT 收款地址\n"
            "• 显示：当前群组的收款地址\n"
            "• 用途：获取结算时的收款地址\n\n"
            
            "📞 <b>客服</b>\n"
            "• 功能：联系客服支持\n"
            "• 操作：点击后自动分配客服账号\n"
            "• 用途：获取帮助、解决问题\n\n"
            
            "💎 <b>打开应用</b>（私聊时显示）\n"
            "• 功能：打开 MiniApp 网页应用\n"
            "• 用途：使用完整的 Web 界面功能\n"
            "• 注意：仅在私聊时可用，群组中不显示\n\n"
            
            "<b>第三行按钮（管理员）：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚙️ <b>管理</b>（私聊）/<b>设置</b>（群组）\n"
            "• 功能：打开管理员面板\n"
            "• 显示：所有管理功能的入口\n"
            "• 用途：进行系统管理操作\n\n"
            
            "💡 <b>使用提示</b>\n"
            "• 所有按钮都是点击即用，无需输入命令\n"
            "• 按钮会根据用户权限显示（管理员会看到额外按钮）\n"
            "• 群组和私聊的按钮布局略有不同\n"
        )
    
    @staticmethod
    def get_admin_panel_buttons_help() -> str:
        """Get help for admin panel buttons"""
        return (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  ⚙️ 管理员面板按钮教程\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "<b>第一行按钮：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👥 <b>用户管理</b>\n"
            "• 功能：管理所有用户\n"
            "• 包含：搜索用户、用户报表、用户详情、用户操作\n"
            "• 子菜单：搜索用户 | 用户报表 | 用户详情 | 用户操作\n"
            "• 用途：查看用户信息、设置VIP、启用/禁用用户\n\n"
            
            "📋 <b>群组管理</b>\n"
            "• 功能：管理所有群组\n"
            "• 包含：群组列表、群组审核、群组配置\n"
            "• 子菜单：群组列表 | 群组审核 | 添加群组 | 搜索群组 | 群组配置 | 删除群组\n"
            "• 用途：查看群组信息、审核新成员、配置群组设置\n\n"
            
            "🚫 <b>敏感词管理</b>\n"
            "• 功能：管理敏感词过滤\n"
            "• 包含：添加、编辑、删除、导出敏感词\n"
            "• 子菜单：添加敏感词 | 编辑敏感词 | 删除敏感词 | 导出列表 | 完整导出\n"
            "• 用途：维护敏感词库，设置过滤规则（warn/delete/ban）\n\n"
            
            "<b>第二行按钮：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>数据统计</b>\n"
            "• 功能：查看系统数据统计\n"
            "• 包含：系统统计、全局统计、时间统计、详细报表\n"
            "• 子菜单：系统统计 | 全局统计 | 时间统计 | 详细报表 | 操作日志\n"
            "• 用途：了解系统运行情况、交易数据、用户增长等\n\n"
            
            "📞 <b>客服管理</b>\n"
            "• 功能：管理客服账号和分配策略\n"
            "• 包含：客服账号列表、添加客服、分配策略设置、客服统计\n"
            "• 用途：配置客服系统、查看客服工作统计\n\n"
            
            "⚙️ <b>系统设置</b>\n"
            "• 功能：系统配置和管理员管理\n"
            "• 包含：添加管理员、删除管理员、管理员列表\n"
            "• 子菜单：添加管理员 | 删除管理员 | 管理员列表\n"
            "• 用途：管理管理员账号、系统配置\n\n"
            
            "<b>第三行按钮：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <b>帮助中心</b>\n"
            "• 功能：查看完整的使用教程和帮助\n"
            "• 包含：按钮教程、命令帮助、功能说明\n"
            "• 用途：学习如何使用各项功能\n\n"
            
            "🔙 <b>返回主菜单</b>\n"
            "• 功能：返回到主菜单\n"
            "• 用途：退出管理面板，回到用户界面\n\n"
            
            "💡 <b>使用提示</b>\n"
            "• 点击任意按钮进入对应功能\n"
            "• 使用「🔙 返回管理面板」返回主面板\n"
            "• 所有操作都有详细说明和引导\n"
        )
    
    @staticmethod
    def get_group_buttons_help() -> str:
        """Get help for group-specific buttons and commands"""
        return (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  👥 群组按钮和命令教程\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "<b>📋 群组快捷命令（w0-w9）：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "<b>w0 / SZ</b> - 查看群组设置\n"
            "• 功能：查看当前群组的加价、USDT地址等配置\n"
            "• 显示：群组加价、收款地址、验证设置\n"
            "• 示例：发送 <code>w0</code> 或 <code>SZ</code>\n\n"
            
            "<b>w1 / HL</b> - 查看价格详情\n"
            "• 功能：查看 Binance P2P 实时汇率和价格计算\n"
            "• 显示：买一价、卖一价、中间价、加价、最终价格\n"
            "• 示例：发送 <code>w1</code> 或 <code>HL</code>\n\n"
            
            "<b>w2 [数字] / SJJ [数字]</b> - 设置群组加价\n"
            "• 功能：为当前群组设置独立的加价值\n"
            "• 参数：加价值（正数表示加价，负数表示降价）\n"
            "• 示例：<code>w2 0.5</code>（加价0.5）或 <code>w2 -0.2</code>（降价0.2）\n"
            "• 注意：设置后该群组的所有结算都会使用此加价\n\n"
            
            "<b>w3 [地址] / SDZ [地址]</b> - 设置群组地址\n"
            "• 功能：为当前群组设置独立的 USDT 收款地址\n"
            "• 参数：TRC20 地址（TR开头）\n"
            "• 示例：<code>w3 TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t</code>\n"
            "• 注意：设置后该群组的结算账单会显示此地址\n\n"
            
            "<b>w4 / CKQJ</b> - 查看全局设置（私聊）\n"
            "• 功能：查看全局默认加价和地址\n"
            "• 显示：全局加价、全局地址\n"
            "• 示例：发送 <code>w4</code> 或 <code>CKQJ</code>\n"
            "• 注意：仅在私聊中可用\n\n"
            
            "<b>w7 / CKQL</b> - 查看所有群组列表（私聊）\n"
            "• 功能：查看所有已配置的群组及其设置\n"
            "• 显示：群组列表、加价、地址、交易统计\n"
            "• 示例：发送 <code>w7</code> 或 <code>CKQL</code>\n"
            "• 注意：仅在私聊中可用\n\n"
            
            "<b>w8 / CZSZ</b> - 重置群组设置\n"
            "• 功能：将群组的加价和地址重置为全局默认值\n"
            "• 操作：清除群组独立设置，恢复使用全局设置\n"
            "• 示例：发送 <code>w8</code> 或 <code>CZSZ</code>\n\n"
            
            "<b>w9 / SCSZ</b> - 删除群组配置\n"
            "• 功能：完全删除群组的独立配置\n"
            "• 操作：从数据库中移除群组配置\n"
            "• 示例：发送 <code>w9</code> 或 <code>SCSZ</code>\n"
            "• 注意：删除后群组将使用全局默认设置\n\n"
            
            "<b>📱 群组按钮：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💱 <b>汇率</b> - 查看实时汇率（与主菜单相同）\n"
            "💰 <b>结算</b> - 计算结算金额（与主菜单相同）\n"
            "📜 <b>我的账单</b> - 查看个人账单（与主菜单相同）\n"
            "🔗 <b>地址</b> - 查看群组收款地址\n"
            "📞 <b>客服</b> - 联系客服（自动分配客服账号）\n"
            "⚙️ <b>设置</b> - 打开管理员面板（仅管理员）\n\n"
            
            "💡 <b>使用提示</b>\n"
            "• 群组命令（w0-w9）仅在群组中可用\n"
            "• 部分命令（w4、w7）仅在私聊中可用\n"
            "• 管理员可以使用「⚙️ 设置」按钮管理群组\n"
            "• 所有命令都有简短形式（如 w0）和完整形式（如 SZ）\n"
        )
    
    @staticmethod
    def get_admin_submenus_help() -> str:
        """Get help for admin submenu buttons"""
        return (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  📋 管理员子菜单按钮教程\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "<b>👥 用户管理子菜单：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔍 <b>搜索用户</b>\n"
            "• 功能：搜索用户（ID/用户名/VIP/日期）\n"
            "• 用法：使用命令 <code>/search_user &lt;条件&gt;</code>\n"
            "• 示例：<code>/search_user 123456789</code> 或 <code>/search_user vip:1</code>\n\n"
            
            "📊 <b>用户报表</b>\n"
            "• 功能：查看用户数据报表和统计\n"
            "• 显示：用户概览、增长趋势、VIP分布\n"
            "• 用途：了解用户增长和分布情况\n\n"
            
            "👤 <b>用户详情</b>\n"
            "• 功能：查看单个用户的详细信息\n"
            "• 用法：使用命令 <code>/user_detail &lt;user_id&gt;</code>\n"
            "• 显示：基本信息、交易统计、注册信息、账户状态\n\n"
            
            "⚙️ <b>用户操作</b>\n"
            "• 功能：对用户进行操作（设置VIP、禁用/启用）\n"
            "• 命令：<code>/set_vip</code> <code>/disable_user</code> <code>/enable_user</code>\n"
            "• 用途：管理用户状态和权限\n\n"
            
            "<b>📋 群组管理子菜单：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 <b>群组列表</b>\n"
            "• 功能：查看所有群组及其详细信息\n"
            "• 显示：群组列表、加价、地址、成员数、交易统计\n"
            "• 用途：了解所有群组的状态\n\n"
            
            "✅ <b>群组审核</b>\n"
            "• 功能：审核待加入群组的新成员\n"
            "• 包含：全部通过、全部拒绝、审核详情、审核历史\n"
            "• 用途：管理群组成员审核流程\n\n"
            
            "➕ <b>添加群组</b>\n"
            "• 功能：将群组添加到管理系统\n"
            "• 用法：使用命令 <code>/addgroup &lt;group_id&gt;</code>\n"
            "• 示例：<code>/addgroup -1001234567890</code>\n\n"
            
            "🔍 <b>搜索群组</b>\n"
            "• 功能：搜索群组（ID/名称/状态）\n"
            "• 用法：使用命令 <code>/search_group &lt;条件&gt;</code>\n"
            "• 示例：<code>/search_group 测试群组</code>\n\n"
            
            "⚙️ <b>群组配置</b>\n"
            "• 功能：配置群组设置（验证模式等）\n"
            "• 用法：使用命令 <code>/group_mode</code> <code>/group_verify</code>\n"
            "• 用途：设置群组验证方式和规则\n\n"
            
            "🗑️ <b>删除群组</b>\n"
            "• 功能：从管理系统中删除群组\n"
            "• 用法：使用命令 <code>/delgroup &lt;group_id&gt;</code>（需确认）\n"
            "• 注意：删除操作不可恢复，需要确认\n\n"
            
            "<b>🚫 敏感词管理子菜单：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "➕ <b>添加敏感词</b>\n"
            "• 功能：添加新的敏感词\n"
            "• 用法：<code>/addword &lt;词&gt; [action]</code>\n"
            "• 动作：warn（警告）、delete（删除）、ban（封禁）\n"
            "• 示例：<code>/addword 广告 delete</code>\n\n"
            
            "✏️ <b>编辑敏感词</b>\n"
            "• 功能：修改敏感词的动作\n"
            "• 用法：<code>/editword &lt;word_id&gt; &lt;action&gt;</code>\n"
            "• 示例：<code>/editword 1 ban</code>\n\n"
            
            "🗑️ <b>删除敏感词</b>\n"
            "• 功能：删除敏感词\n"
            "• 用法：<code>/delword &lt;word_id&gt;</code>\n"
            "• 示例：<code>/delword 1</code>\n\n"
            
            "📋 <b>导出列表</b> / <b>完整导出</b>\n"
            "• 功能：导出敏感词列表（CSV格式）\n"
            "• 用法：使用命令 <code>/export_words</code>\n"
            "• 用途：备份敏感词库或进行数据分析\n\n"
            
            "<b>📊 数据统计子菜单：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>系统统计</b>\n"
            "• 功能：查看系统整体数据统计\n"
            "• 显示：交易统计、用户统计、支付渠道统计\n"
            "• 用途：了解系统整体运行情况\n\n"
            
            "📈 <b>全局统计</b>\n"
            "• 功能：查看所有群组的统计数据\n"
            "• 显示：今日汇总、本月汇总、群组分布\n"
            "• 用途：了解全局业务情况\n\n"
            
            "📅 <b>时间统计</b>\n"
            "• 功能：按时间段查看数据统计\n"
            "• 显示：今日、昨日、本周、本月数据及增长率\n"
            "• 用途：分析数据趋势和增长情况\n\n"
            
            "📋 <b>详细报表</b>\n"
            "• 功能：查看详细的数据分析报告\n"
            "• 显示：交易状态统计、支付渠道统计、交易类型统计、Top用户\n"
            "• 用途：深入了解业务数据\n\n"
            
            "📋 <b>操作日志</b>\n"
            "• 功能：查看所有管理员操作记录\n"
            "• 显示：操作类型、操作者、时间、详情\n"
            "• 用途：审计和追踪管理员操作\n\n"
            
            "<b>✅ 群组审核子菜单：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ <b>全部通过</b>\n"
            "• 功能：通过所有待审核成员\n"
            "• 操作：批量通过当前所有待审核申请\n"
            "• 用途：快速处理大量审核请求\n\n"
            
            "❌ <b>全部拒绝</b>\n"
            "• 功能：拒绝所有待审核成员\n"
            "• 操作：批量拒绝当前所有待审核申请\n"
            "• 用途：快速清理无效申请\n\n"
            
            "👤 <b>审核详情</b>\n"
            "• 功能：查看单个审核请求的详细信息\n"
            "• 用法：使用命令 <code>/pass_user</code> 或 <code>/reject_user</code>\n"
            "• 显示：用户信息、申请时间、审核状态\n\n"
            
            "📋 <b>审核历史</b>\n"
            "• 功能：查看历史审核记录\n"
            "• 显示：已通过和已拒绝的审核记录\n"
            "• 用途：了解审核历史和统计\n\n"
            
            "<b>⚙️ 系统设置子菜单：</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "➕ <b>添加管理员</b>\n"
            "• 功能：添加新的管理员账号\n"
            "• 用法：使用命令 <code>/addadmin &lt;user_id&gt;</code>\n"
            "• 权限：仅超级管理员可用\n\n"
            
            "🗑️ <b>删除管理员</b>\n"
            "• 功能：删除管理员账号\n"
            "• 用法：使用命令 <code>/deladmin &lt;user_id&gt;</code>（需确认）\n"
            "• 权限：仅超级管理员可用\n\n"
            
            "📋 <b>管理员列表</b>\n"
            "• 功能：查看所有管理员账号列表\n"
            "• 显示：管理员ID、用户名、添加时间\n"
            "• 用途：了解当前管理员情况\n\n"
            
            "💡 <b>通用操作</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔙 <b>返回管理面板</b>\n"
            "• 功能：返回管理员面板主页\n"
            "• 用途：在各子菜单之间导航\n\n"
            
            "💡 <b>使用提示</b>\n"
            "• 所有子菜单都提供详细的操作说明\n"
            "• 使用命令可以进行精确操作\n"
            "• 使用按钮可以快速访问功能\n"
            "• 删除和禁用操作需要确认，防止误操作\n"
        )
    
    @staticmethod
    def get_guided_tutorial_menu() -> str:
        """Get guided tutorial menu for help center"""
        return (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  ⚡ 帮助中心 - 引导式教程\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📚 <b>选择要学习的主题：</b>\n\n"
            "1️⃣ <b>主菜单按钮教程</b>\n"
            "   了解主菜单中所有按钮的功能和使用方法\n\n"
            "2️⃣ <b>管理员面板按钮教程</b>\n"
            "   学习如何使用管理员面板的各个功能\n\n"
            "3️⃣ <b>群组按钮和命令教程</b>\n"
            "   掌握群组中的按钮和快捷命令（w0-w9）\n\n"
            "4️⃣ <b>管理员子菜单教程</b>\n"
            "   详细了解各个管理子菜单的功能\n\n"
            "5️⃣ <b>管理员命令帮助</b>\n"
            "   查看所有管理员命令的详细说明\n\n"
            "💡 <b>使用方法：</b>\n"
            "• 输入 <code>1</code> 查看主菜单按钮教程\n"
            "• 输入 <code>2</code> 查看管理员面板按钮教程\n"
            "• 输入 <code>3</code> 查看群组按钮教程\n"
            "• 输入 <code>4</code> 查看管理员子菜单教程\n"
            "• 输入 <code>5</code> 查看管理员命令帮助\n"
            "• 或点击下方按钮直接查看对应教程\n\n"
            "💡 也可以使用 <code>/admin_help</code> 查看命令帮助"
        )
    
    @staticmethod
    def get_command_quick_reference() -> str:
        """Get quick reference for common commands"""
        return (
            "📋 <b>常用命令快速参考</b>\n\n"
            "<b>用户：</b> <code>/search_user</code> <code>/user_detail</code> <code>/set_vip</code>\n"
            "<b>敏感词：</b> <code>/addword</code> <code>/delword</code> <code>/export_words</code>\n"
            "<b>群组：</b> <code>/group_detail</code> <code>/search_group</code> <code>/delgroup</code>\n"
            "<b>审核：</b> <code>/pass_user</code> <code>/reject_user</code>\n\n"
            "💡 输入命令名可查看详细说明，或使用 <code>/admin</code> 打开管理面板"
        )
    
    @staticmethod
    def get_feature_help(feature: str) -> str:
        """Get help for specific feature"""
        feature_help = {
            'user_search': (
                "🔍 <b>用户搜索功能</b>\n\n"
                "<b>支持搜索方式：</b>\n"
                "• 按用户ID：<code>/search_user 123456789</code>\n"
                "• 按用户名：<code>/search_user @username</code>\n"
                "• 按VIP等级：<code>/search_user vip:1</code>\n"
                "• 按注册日期：<code>/search_user date:2025-01-01</code>\n\n"
                "💡 搜索结果显示前20个匹配结果"
            ),
            'group_search': (
                "🔍 <b>群组搜索功能</b>\n\n"
                "<b>支持搜索方式：</b>\n"
                "• 按群组ID：<code>/search_group -1001234567890</code>\n"
                "• 按群组名称：<code>/search_group 测试群组</code>\n"
                "• 按验证状态：<code>/search_group status:enabled</code>\n\n"
                "💡 使用 status:enabled 或 status:disabled 筛选"
            ),
            'batch_import': (
                "📥 <b>批量导入敏感词</b>\n\n"
                "<b>支持格式：</b>\n"
                "1. 每行一个词\n"
                "2. 逗号分隔：词,动作\n"
                "3. 空格分隔的多个词\n\n"
                "<b>示例：</b>\n"
                "<code>/import_words 广告\\n诈骗,delete\\n赌博,ban</code>\n\n"
                "💡 最多支持100个敏感词，动作：warn/delete/ban"
            ),
            'confirmation': (
                "⚠️ <b>操作确认机制</b>\n\n"
                "<b>需要确认的操作：</b>\n"
                "• 删除管理员\n"
                "• 禁用用户\n"
                "• 删除群组\n\n"
                "<b>确认方式：</b>\n"
                "• 方式1：再次执行相同命令\n"
                "• 方式2：发送 <code>/confirm</code> 命令\n\n"
                "💡 确认请求会在5分钟后自动过期"
            ),
        }
        
        return feature_help.get(feature, "💡 功能说明暂未提供")
    
    @staticmethod
    def format_usage_example(command: str, examples: List[str]) -> str:
        """Format usage examples for a command"""
        if not examples:
            return ""
        
        text = "<b>示例：</b>\n"
        for example in examples:
            text += f"• <code>{example}</code>\n"
        
        return text
