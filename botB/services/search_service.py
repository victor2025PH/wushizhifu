"""
Search and filter service for Bot B
Handles advanced search and filtering logic
"""
import logging
import re
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


def parse_amount_range(amount_text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse amount range from text (e.g., "1000-5000", ">1000", "<5000", "1000").
    
    Args:
        amount_text: Text containing amount range
        
    Returns:
        Tuple of (min_amount, max_amount)
    """
    try:
        amount_text = amount_text.strip()
        
        # Range: "1000-5000" or "1000~5000"
        range_match = re.match(r'^(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)$', amount_text)
        if range_match:
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            return min_val, max_val
        
        # Greater than: ">1000" or ">=1000"
        gt_match = re.match(r'^>=\s*(\d+(?:\.\d+)?)$', amount_text)
        if gt_match:
            return float(gt_match.group(1)), None
        
        gt_match = re.match(r'^>\s*(\d+(?:\.\d+)?)$', amount_text)
        if gt_match:
            # Slightly above to exclude the value
            return float(gt_match.group(1)) + 0.01, None
        
        # Less than: "<5000" or "<=5000"
        lt_match = re.match(r'^<=\s*(\d+(?:\.\d+)?)$', amount_text)
        if lt_match:
            return None, float(lt_match.group(1))
        
        lt_match = re.match(r'^<\s*(\d+(?:\.\d+)?)$', amount_text)
        if lt_match:
            # Slightly below to exclude the value
            return None, float(lt_match.group(1)) - 0.01
        
        # Single value: "1000"
        single_match = re.match(r'^(\d+(?:\.\d+)?)$', amount_text)
        if single_match:
            val = float(single_match.group(1))
            return val, val
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error parsing amount range: {e}", exc_info=True)
        return None, None


def parse_date_range(date_text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse date range from text.
    
    Supported formats:
    - "2025-01-01 2025-01-31" (date range)
    - "2025-01-01" (single date)
    - "今天", "今日" (today)
    - "本周", "本周" (this week)
    - "本月" (this month)
    - "最近7天" (last 7 days)
    - "最近30天" (last 30 days)
    
    Args:
        date_text: Text containing date range
        
    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    import datetime
    
    try:
        date_text = date_text.strip()
        today = datetime.date.today()
        
        # Date range: "2025-01-01 2025-01-31"
        range_match = re.match(r'^(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})$', date_text)
        if range_match:
            start = range_match.group(1)
            end = range_match.group(2)
            return start, end
        
        # Single date: "2025-01-01"
        single_match = re.match(r'^(\d{4}-\d{2}-\d{2})$', date_text)
        if single_match:
            date_str = single_match.group(1)
            return date_str, date_str
        
        # Quick date shortcuts
        if date_text in ['今天', '今日', 'today']:
            today_str = today.strftime('%Y-%m-%d')
            return today_str, today_str
        
        if date_text in ['本周', 'this_week']:
            week_start = today - datetime.timedelta(days=today.weekday())
            return week_start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        
        if date_text in ['本月', 'this_month']:
            month_start = today.replace(day=1)
            return month_start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        
        if date_text in ['最近7天', 'last_7_days']:
            start = today - datetime.timedelta(days=6)
            return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        
        if date_text in ['最近30天', 'last_30_days']:
            start = today - datetime.timedelta(days=29)
            return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error parsing date range: {e}", exc_info=True)
        return None, None


def parse_status_filter(status_text: str) -> Optional[str]:
    """
    Parse status filter from text.
    
    Args:
        status_text: Status text (e.g., "待支付", "已支付", "pending", "paid")
        
    Returns:
        Status code (pending, paid, confirmed, cancelled) or None
    """
    status_map = {
        'pending': 'pending',
        'paid': 'paid',
        'confirmed': 'confirmed',
        'cancelled': 'cancelled',
        '待支付': 'pending',
        '已支付': 'paid',
        '已确认': 'confirmed',
        '已取消': 'cancelled',
        '待确认': 'paid'
    }
    
    status_text_lower = status_text.strip().lower()
    return status_map.get(status_text_lower) or status_map.get(status_text)


def parse_user_filter(user_text: str) -> Optional[int]:
    """
    Parse user filter from text (user ID or username).
    
    Args:
        user_text: User ID or username
        
    Returns:
        User ID or None
    """
    try:
        # Try as user ID first
        if user_text.strip().isdigit():
            return int(user_text.strip())
        
        # If it's a mention format: @username or just username
        user_text = user_text.strip().lstrip('@')
        # Note: This would require a database lookup to convert username to user_id
        # For now, we'll return None and handle it in the handler
        return None
        
    except Exception as e:
        logger.error(f"Error parsing user filter: {e}", exc_info=True)
        return None


def parse_search_query(search_text: str) -> Dict:
    """
    Parse comprehensive search query with multiple filters.
    
    Format examples:
    - "金额:1000-5000 日期:2025-01-01 状态:已支付"
    - ">1000 本周 已确认"
    - "用户:123456 本月"
    
    Args:
        search_text: Search query text
        
    Returns:
        Dictionary with parsed filters:
        {
            'min_amount': float or None,
            'max_amount': float or None,
            'start_date': str or None,
            'end_date': str or None,
            'status': str or None,
            'user_id': int or None,
            'transaction_id': str or None
        }
    """
    filters = {
        'min_amount': None,
        'max_amount': None,
        'start_date': None,
        'end_date': None,
        'status': None,
        'user_id': None,
        'transaction_id': None
    }
    
    # Check for transaction ID (usually starts with T and is long)
    tx_id_match = re.search(r'\bT\d{14}\d{4}\b', search_text)
    if tx_id_match:
        filters['transaction_id'] = tx_id_match.group(0)
        return filters  # Transaction ID is unique, return early
    
    # Parse labeled filters: "金额:1000-5000", "日期:2025-01-01", etc.
    labeled_patterns = {
        'amount': r'金额[：:]\s*([^\s]+)',
        'date': r'日期[：:]\s*([^\s]+)',
        'status': r'状态[：:]\s*([^\s]+)',
        'user': r'用户[：:]\s*([^\s]+)'
    }
    
    for key, pattern in labeled_patterns.items():
        match = re.search(pattern, search_text, re.IGNORECASE)
        if match:
            value = match.group(1)
            if key == 'amount':
                min_a, max_a = parse_amount_range(value)
                filters['min_amount'] = min_a
                filters['max_amount'] = max_a
            elif key == 'date':
                start_d, end_d = parse_date_range(value)
                filters['start_date'] = start_d
                filters['end_date'] = end_d
            elif key == 'status':
                filters['status'] = parse_status_filter(value)
            elif key == 'user':
                filters['user_id'] = parse_user_filter(value)
    
    # Parse unlabeled filters (try to detect type)
    # Remove labeled parts
    remaining = search_text
    for pattern in labeled_patterns.values():
        remaining = re.sub(pattern, '', remaining, flags=re.IGNORECASE)
    
    remaining = remaining.strip()
    if remaining:
        # Try amount range
        min_a, max_a = parse_amount_range(remaining)
        if min_a is not None or max_a is not None:
            if filters['min_amount'] is None:
                filters['min_amount'] = min_a
            if filters['max_amount'] is None:
                filters['max_amount'] = max_a
        else:
            # Try date range
            start_d, end_d = parse_date_range(remaining)
            if start_d or end_d:
                if filters['start_date'] is None:
                    filters['start_date'] = start_d
                if filters['end_date'] is None:
                    filters['end_date'] = end_d
            else:
                # Try status
                status = parse_status_filter(remaining)
                if status:
                    if filters['status'] is None:
                        filters['status'] = status
    
    return filters

