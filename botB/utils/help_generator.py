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
