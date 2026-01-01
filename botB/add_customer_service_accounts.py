#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量添加客服账号脚本
用于一次性添加多个客服账号到系统
"""
import sys
import os

# Add botB to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 10个客服账号列表（移除@符号）
CUSTOMER_SERVICE_ACCOUNTS = [
    "zxc123456cxsj",
    "wubaizhifuaran",
    "Mark77585",
    "Moon727888",
    "yuanpay_01",
    "wushizhifu888",
    "wushi987",
    "xiaoyue5918",
    "Aeight888",
    "wuzhifu_8"
]

def add_customer_service_accounts():
    """批量添加客服账号"""
    logger.info("开始批量添加客服账号...")
    
    added_count = 0
    skipped_count = 0
    error_count = 0
    
    for username in CUSTOMER_SERVICE_ACCOUNTS:
        try:
            # 检查账号是否已存在
            existing = db.get_customer_service_account(username=username)
            if existing:
                logger.warning(f"客服账号 @{username} 已存在，跳过")
                skipped_count += 1
                continue
            
            # 添加账号
            success = db.add_customer_service_account(
                username=username,
                display_name=username,
                weight=5,  # 默认权重
                max_concurrent=50  # 默认最大并发数
            )
            
            if success:
                logger.info(f"✅ 成功添加客服账号: @{username}")
                added_count += 1
            else:
                logger.error(f"❌ 添加客服账号失败: @{username}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"❌ 添加客服账号 @{username} 时出错: {e}")
            error_count += 1
    
    logger.info(f"\n添加完成！")
    logger.info(f"✅ 成功添加: {added_count} 个")
    logger.info(f"⚠️  已存在跳过: {skipped_count} 个")
    logger.info(f"❌ 失败: {error_count} 个")
    logger.info(f"📊 总计: {len(CUSTOMER_SERVICE_ACCOUNTS)} 个")
    
    return added_count, skipped_count, error_count


def set_assignment_strategy(strategy='round_robin'):
    """设置客服分配策略"""
    logger.info(f"设置客服分配策略为: {strategy}")
    
    try:
        conn = db.connect()
        cursor = conn.cursor()
        
        # 插入或更新设置
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES ('customer_service_strategy', ?, CURRENT_TIMESTAMP)
        """, (strategy,))
        
        conn.commit()
        logger.info(f"✅ 分配策略已设置为: {strategy}")
        
        # 验证设置
        cursor.execute("SELECT value FROM settings WHERE key = 'customer_service_strategy'")
        result = cursor.fetchone()
        if result:
            logger.info(f"✅ 验证成功，当前策略: {result[0]}")
        else:
            logger.warning("⚠️  设置可能未生效")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 设置分配策略时出错: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("客服账号批量添加工具")
    print("=" * 60)
    print(f"\n将要添加 {len(CUSTOMER_SERVICE_ACCOUNTS)} 个客服账号：")
    for idx, username in enumerate(CUSTOMER_SERVICE_ACCOUNTS, 1):
        print(f"  {idx}. @{username}")
    
    print("\n" + "=" * 60)
    
    # 添加账号
    added, skipped, errors = add_customer_service_accounts()
    
    # 设置分配策略为 round_robin
    print("\n" + "=" * 60)
    set_assignment_strategy('round_robin')
    
    print("\n" + "=" * 60)
    print("✅ 所有操作完成！")
    print("=" * 60)
    
    # 显示当前所有客服账号
    print("\n当前所有客服账号：")
    try:
        accounts = db.get_customer_service_accounts(active_only=False)
        if accounts:
            for idx, account in enumerate(accounts, 1):
                active_icon = "✅" if account.get('is_active', 0) else "❌"
                print(f"  {idx}. {active_icon} @{account['username']} ({account.get('display_name', 'N/A')})")
        else:
            print("  暂无客服账号")
    except Exception as e:
        logger.error(f"获取客服账号列表时出错: {e}")


if __name__ == "__main__":
    main()
