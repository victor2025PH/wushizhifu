"""
检查 Bot A 的敏感词和群组设置
用于诊断消息被删除的问题
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from database.sensitive_words_repository import SensitiveWordsRepository
from database.group_repository import GroupRepository
from database.db import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_sensitive_words():
    """检查所有敏感词"""
    print("\n" + "="*60)
    print("📋 敏感词列表")
    print("="*60)
    
    # 获取所有活跃的敏感词
    words = SensitiveWordsRepository.get_words()
    
    if not words:
        print("✅ 没有活跃的敏感词")
        return
    
    print(f"\n共 {len(words)} 个活跃的敏感词：\n")
    
    # 按动作分组
    warn_words = [w for w in words if w.get('action') == 'warn']
    delete_words = [w for w in words if w.get('action') == 'delete']
    ban_words = [w for w in words if w.get('action') == 'ban']
    
    if warn_words:
        print(f"⚠️ 警告 (warn) - {len(warn_words)} 个：")
        for w in warn_words[:20]:
            group_info = f" [群组: {w.get('group_id')}]" if w.get('group_id') else " [全局]"
            print(f"   - {w['word']}{group_info}")
        if len(warn_words) > 20:
            print(f"   ... 还有 {len(warn_words) - 20} 个")
        print()
    
    if delete_words:
        print(f"🗑️  删除 (delete) - {len(delete_words)} 个：")
        for w in delete_words[:20]:
            group_info = f" [群组: {w.get('group_id')}]" if w.get('group_id') else " [全局]"
            print(f"   - {w['word']}{group_info}")
        if len(delete_words) > 20:
            print(f"   ... 还有 {len(delete_words) - 20} 个")
        print()
    
    if ban_words:
        print(f"🚫 封禁 (ban) - {len(ban_words)} 个：")
        for w in ban_words[:20]:
            group_info = f" [群组: {w.get('group_id')}]" if w.get('group_id') else " [全局]"
            print(f"   - {w['word']}{group_info}")
        if len(ban_words) > 20:
            print(f"   ... 还有 {len(ban_words) - 20} 个")
        print()
    
    # 检查是否有可疑的敏感词（太短或太常见）
    suspicious_words = []
    for w in words:
        word = w['word']
        # 检查长度
        if len(word) <= 2:
            suspicious_words.append(f"{word} (太短，只有 {len(word)} 个字符)")
        # 检查是否是常见字符
        if word in ['的', '是', '在', 'a', 'e', 'i', 'o', 'u', ' ', '\n', '\t']:
            suspicious_words.append(f"{word} (常见字符)")
    
    if suspicious_words:
        print("⚠️  可疑的敏感词（可能导致误匹配）：")
        for sw in suspicious_words:
            print(f"   - {sw}")
        print()


def check_groups():
    """检查群组设置"""
    print("\n" + "="*60)
    print("👥 群组设置")
    print("="*60)
    
    # 获取所有群组
    cursor = db.execute("SELECT * FROM groups")
    groups = cursor.fetchall()
    
    if not groups:
        print("✅ 没有配置的群组")
        return
    
    print(f"\n共 {len(groups)} 个群组：\n")
    
    for group in groups:
        group_dict = dict(group)
        group_id = group_dict['group_id']
        verification_enabled = group_dict.get('verification_enabled', 0)
        
        status = "✅" if verification_enabled else "❌"
        print(f"{status} 群组 {group_id}:")
        print(f"   - 验证功能: {'已开启' if verification_enabled else '已关闭'}")
        print(f"   - 群组标题: {group_dict.get('group_title', 'N/A')}")
        
        # 检查该群组的敏感词
        group_words = SensitiveWordsRepository.get_words(group_id)
        if group_words:
            print(f"   - 群组专用敏感词: {len(group_words)} 个")
        print()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔍 Bot A 敏感词和设置检查工具")
    print("="*60)
    
    try:
        check_sensitive_words()
        check_groups()
        
        print("\n" + "="*60)
        print("✅ 检查完成")
        print("="*60)
        print("\n💡 提示：")
        print("   如果发现消息被删除，请检查：")
        print("   1. 是否有验证功能开启（未验证用户的消息会被删除）")
        print("   2. 是否有可疑的敏感词（太短或太常见）")
        print("   3. 是否有动作设置为 'delete' 或 'ban' 的敏感词")
        print()
        
    except Exception as e:
        logger.error(f"检查时出错: {e}", exc_info=True)
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()

