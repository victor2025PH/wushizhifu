"""
Data export service for Bot B
Handles CSV and Excel file generation for transactions and statistics
"""
import logging
import io
import csv
import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


def export_transactions_to_csv(transactions: List[Dict[str, Any]], filename: str = None) -> io.BytesIO:
    """
    Export transactions to CSV format.
    
    Args:
        transactions: List of transaction dictionaries
        filename: Optional filename (not used, for compatibility)
        
    Returns:
        BytesIO object containing CSV data
    """
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            '交易编号', '群组ID', '用户ID', '用户名', '姓名',
            'CNY金额', 'USDT金额', '汇率', '加价', 'USDT地址',
            '状态', '支付哈希', '创建时间', '支付时间', '确认时间', '取消时间'
        ])
        
        # Write data rows
        for tx in transactions:
            writer.writerow([
                tx.get('transaction_id', ''),
                tx.get('group_id', ''),
                tx.get('user_id', ''),
                tx.get('username', '') or '',
                tx.get('first_name', '') or '',
                tx.get('cny_amount', 0.0),
                tx.get('usdt_amount', 0.0),
                tx.get('exchange_rate', 0.0),
                tx.get('markup', 0.0) or 0.0,
                tx.get('usdt_address', '') or '',
                tx.get('status', 'pending'),
                tx.get('payment_hash', '') or '',
                tx.get('created_at', ''),
                tx.get('paid_at', '') or '',
                tx.get('confirmed_at', '') or '',
                tx.get('cancelled_at', '') or ''
            ])
        
        # Convert to BytesIO
        csv_bytes = io.BytesIO()
        csv_bytes.write(output.getvalue().encode('utf-8-sig'))  # UTF-8 with BOM for Excel compatibility
        csv_bytes.seek(0)
        
        logger.info(f"Exported {len(transactions)} transactions to CSV")
        return csv_bytes
        
    except Exception as e:
        logger.error(f"Error exporting transactions to CSV: {e}", exc_info=True)
        raise


def export_transactions_to_excel(transactions: List[Dict[str, Any]], filename: str = None) -> io.BytesIO:
    """
    Export transactions to Excel format.
    
    Args:
        transactions: List of transaction dictionaries
        filename: Optional filename (not used, for compatibility)
        
    Returns:
        BytesIO object containing Excel data
    """
    try:
        # Prepare data for DataFrame
        data = []
        for tx in transactions:
            data.append({
                '交易编号': tx.get('transaction_id', ''),
                '群组ID': tx.get('group_id', '') or '',
                '用户ID': tx.get('user_id', ''),
                '用户名': tx.get('username', '') or '',
                '姓名': tx.get('first_name', '') or '',
                'CNY金额': tx.get('cny_amount', 0.0),
                'USDT金额': tx.get('usdt_amount', 0.0),
                '汇率': tx.get('exchange_rate', 0.0),
                '加价': tx.get('markup', 0.0) or 0.0,
                'USDT地址': tx.get('usdt_address', '') or '',
                '状态': tx.get('status', 'pending'),
                '支付哈希': tx.get('payment_hash', '') or '',
                '创建时间': tx.get('created_at', ''),
                '支付时间': tx.get('paid_at', '') or '',
                '确认时间': tx.get('confirmed_at', '') or '',
                '取消时间': tx.get('cancelled_at', '') or ''
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='交易记录')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['交易记录']
            for idx, col in enumerate(df.columns, 1):
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length, 50)
        
        output.seek(0)
        
        logger.info(f"Exported {len(transactions)} transactions to Excel")
        return output
        
    except Exception as e:
        logger.error(f"Error exporting transactions to Excel: {e}", exc_info=True)
        raise


def export_stats_to_excel(stats_data: Dict[str, Any], group_name: str = None) -> io.BytesIO:
    """
    Export statistics to Excel format.
    
    Args:
        stats_data: Dictionary containing statistics
        group_name: Optional group name for the filename
        
    Returns:
        BytesIO object containing Excel data
    """
    try:
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                '指标': [],
                '数值': []
            }
            
            if 'today' in stats_data:
                today_stats = stats_data['today']
                summary_data['指标'].extend([
                    '今日交易次数',
                    '今日总金额 (CNY)',
                    '今日应结算 (USDT)',
                    '今日平均金额 (CNY)',
                    '今日活跃用户'
                ])
                summary_data['数值'].extend([
                    today_stats.get('count', 0),
                    today_stats.get('total_cny', 0.0),
                    today_stats.get('total_usdt', 0.0),
                    today_stats.get('avg_cny', 0.0),
                    today_stats.get('unique_users', 0)
                ])
            
            if 'week' in stats_data:
                week_stats = stats_data['week']
                summary_data['指标'].extend([
                    '本周交易次数',
                    '本周总金额 (CNY)',
                    '本周应结算 (USDT)',
                    '本周日均交易'
                ])
                summary_data['数值'].extend([
                    week_stats.get('count', 0),
                    week_stats.get('total_cny', 0.0),
                    week_stats.get('total_usdt', 0.0),
                    week_stats.get('count', 0) / 7 if week_stats.get('count', 0) > 0 else 0
                ])
            
            if 'month' in stats_data:
                month_stats = stats_data['month']
                summary_data['指标'].extend([
                    '本月交易次数',
                    '本月总金额 (CNY)',
                    '本月应结算 (USDT)',
                    '本月活跃用户',
                    '本月最近活跃'
                ])
                summary_data['数值'].extend([
                    month_stats.get('count', 0),
                    month_stats.get('total_cny', 0.0),
                    month_stats.get('total_usdt', 0.0),
                    month_stats.get('unique_users', 0),
                    month_stats.get('last_active', '') or ''
                ])
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, index=False, sheet_name='统计摘要')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['统计摘要']
            worksheet.column_dimensions['A'].width = 25
            worksheet.column_dimensions['B'].width = 20
        
        output.seek(0)
        
        logger.info(f"Exported statistics to Excel (group: {group_name})")
        return output
        
    except Exception as e:
        logger.error(f"Error exporting statistics to Excel: {e}", exc_info=True)
        raise


def generate_export_filename(prefix: str, file_type: str = 'csv') -> str:
    """
    Generate export filename with timestamp.
    
    Args:
        prefix: Filename prefix (e.g., 'transactions', 'stats')
        file_type: File type ('csv' or 'xlsx')
        
    Returns:
        Generated filename
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    extension = 'xlsx' if file_type == 'excel' else 'csv'
    return f"{prefix}_{timestamp}.{extension}"

