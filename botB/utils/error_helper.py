"""
Error helper utilities for providing better error messages and solutions
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ErrorHelper:
    """Helper class for generating user-friendly error messages"""
    
    @staticmethod
    def get_user_friendly_error(error_type: str, context: dict = None) -> str:
        """
        Get user-friendly error message with solution suggestions.
        
        Args:
            error_type: Type of error (e.g., 'invalid_user_id', 'permission_denied', 'not_found')
            context: Additional context (e.g., {'user_id': 123, 'command': '/disable_user'})
            
        Returns:
            User-friendly error message with solution
        """
        context = context or {}
        
        error_messages = {
            'invalid_user_id': (
                "❌ <b>无效的用户ID</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• 用户ID必须是数字\n"
                "• 示例：<code>/disable_user 123456789</code>\n"
                "• 如何获取用户ID：用户可以通过 @userinfobot 查询自己的ID"
            ),
            'invalid_group_id': (
                "❌ <b>无效的群组ID</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• 群组ID必须是数字（通常以-100开头）\n"
                "• 示例：<code>/delgroup -1001234567890</code>\n"
                "• 如何获取群组ID：将机器人添加到群组后，使用 /group_list 查看"
            ),
            'invalid_vip_level': (
                "❌ <b>无效的VIP等级</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• VIP等级必须在 0-10 之间\n"
                "• 示例：<code>/set_vip 123456789 1</code>\n"
                "• 0 = 普通用户，1-10 = VIP用户"
            ),
            'permission_denied': (
                "❌ <b>权限不足</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• 此操作需要管理员权限\n"
                "• 请联系超级管理员添加您的管理员权限\n"
                "• 使用 <code>/admin</code> 查看管理员面板"
            ),
            'admin_manage_permission_denied': (
                "❌ <b>权限不足</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• 只有超级管理员可以管理管理员\n"
                "• 如果您需要添加/删除管理员，请联系超级管理员\n"
                "• 普通管理员可以管理用户、敏感词、群组等"
            ),
            'user_not_found': (
                "❌ <b>用户不存在</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• 请检查用户ID是否正确\n"
                "• 使用 <code>/search_user &lt;user_id&gt;</code> 搜索用户\n"
                "• 或使用 <code>/search_user &lt;username&gt;</code> 搜索用户名"
            ),
            'admin_not_found': (
                "❌ <b>管理员不存在</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• 该用户可能不是管理员或已被删除\n"
                "• 使用管理员面板的"添加管理员"功能查看所有管理员\n"
                "• 或使用 <code>/search_user &lt;user_id&gt;</code> 检查用户是否存在"
            ),
            'group_not_found': (
                "❌ <b>群组不存在</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• 请检查群组ID是否正确\n"
                "• 使用 <code>/search_group &lt;group_id&gt;</code> 搜索群组\n"
                "• 使用 <code>/group_list</code> 查看所有管理的群组\n"
                "• 确保机器人仍在群组中"
            ),
            'word_not_found': (
                "❌ <b>敏感词不存在</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• 该敏感词可能已被删除\n"
                "• 使用敏感词管理功能查看所有敏感词\n"
                "• 使用 <code>/export_words</code> 导出所有敏感词列表"
            ),
            'self_operation': (
                "❌ <b>不能对自己执行此操作</b>\n\n"
                "💡 <b>说明：</b>\n"
                "• 出于安全考虑，不能删除或禁用自己的账户\n"
                "• 如需操作，请联系其他管理员"
            ),
            'operation_failed': (
                "❌ <b>操作失败</b>\n\n"
                "💡 <b>可能的原因：</b>\n"
                "• 数据可能已被其他操作修改\n"
                "• 请稍后重试\n"
                "• 如问题持续，请检查操作日志"
            ),
            'system_error': (
                "❌ <b>系统错误</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• 请稍后重试\n"
                "• 如问题持续，请联系技术支持\n"
                "• 操作日志已记录，便于排查问题"
            ),
            'already_exists': (
                "❌ <b>已存在</b>\n\n"
                "💡 <b>说明：</b>\n"
                "• 该记录已存在，无需重复添加\n"
                "• 如需修改，请使用相应的编辑功能"
            ),
            'batch_limit_exceeded': (
                "❌ <b>批量操作数量超限</b>\n\n"
                "💡 <b>解决方案：</b>\n"
                "• 批量操作最多支持50个项\n"
                "• 请分批执行操作\n"
                "• 或使用导出功能处理后导入"
            ),
            'no_pending_confirmation': (
                "❌ <b>没有待确认的操作</b>\n\n"
                "💡 <b>说明：</b>\n"
                "• 请先执行需要确认的操作（如删除、禁用等）\n"
                "• 确认请求会在5分钟后自动过期\n"
                "• 如需操作，请重新执行相应的命令"
            ),
        }
        
        message = error_messages.get(error_type, 
            "❌ 操作失败\n\n"
            "💡 请稍后重试，如问题持续请联系技术支持"
        )
        
        return message
    
    @staticmethod
    def format_command_help(command: str, description: str, usage: str, examples: list = None) -> str:
        """
        Format command help message.
        
        Args:
            command: Command name
            description: Command description
            usage: Usage format
            examples: List of example usage strings
            
        Returns:
            Formatted help message
        """
        help_text = (
            f"📖 <b>{command} 命令说明</b>\n\n"
            f"<b>功能：</b>{description}\n\n"
            f"<b>格式：</b><code>{usage}</code>\n\n"
        )
        
        if examples:
            help_text += "<b>示例：</b>\n"
            for example in examples:
                help_text += f"• <code>{example}</code>\n"
            help_text += "\n"
        
        help_text += "💡 使用 <code>/help</code> 查看所有命令"
        
        return help_text
