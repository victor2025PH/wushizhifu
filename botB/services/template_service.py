"""
Template service for Bot B
Handles settlement templates management
"""
import logging
from typing import List, Dict, Optional
from database import db

logger = logging.getLogger(__name__)


def get_all_templates(user_id: int = None, limit: int = 10) -> Dict[str, List[Dict]]:
    """
    Get all available templates (preset + user templates), limited to top N.
    
    Args:
        user_id: Optional user ID to include user templates
        limit: Maximum number of templates per type (default: 10)
        
    Returns:
        Dictionary with 'amount' and 'formula' template lists (max limit each)
    """
    templates = {
        'amount': [],
        'formula': []
    }
    
    # Get preset templates (always include these first)
    preset_amount = db.get_templates(user_id=None, template_type='amount')
    preset_formula = db.get_templates(user_id=None, template_type='formula')
    
    # Add preset templates (they're already sorted by usage_count DESC in DB)
    templates['amount'].extend(preset_amount)
    templates['formula'].extend(preset_formula)
    
    # Get user templates if user_id provided and we haven't reached limit
    if user_id:
        user_amount = db.get_templates(user_id=user_id, template_type='amount')
        user_formula = db.get_templates(user_id=user_id, template_type='formula')
        
        # Add user templates, but limit total to 'limit'
        remaining_amount_slots = limit - len(templates['amount'])
        if remaining_amount_slots > 0:
            templates['amount'].extend(user_amount[:remaining_amount_slots])
        
        remaining_formula_slots = limit - len(templates['formula'])
        if remaining_formula_slots > 0:
            templates['formula'].extend(user_formula[:remaining_formula_slots])
    
    # Ensure we don't exceed limit (safety check)
    templates['amount'] = templates['amount'][:limit]
    templates['formula'] = templates['formula'][:limit]
    
    return templates


def format_template_display_name(template: Dict) -> str:
    """
    Format template for display.
    
    Args:
        template: Template dictionary
        
    Returns:
        Formatted display string
    """
    value = template['template_value']
    name = template['template_name']
    
    # Format amount templates
    if template['template_type'] == 'amount':
        try:
            amount = float(value)
            if amount >= 10000:
                display = f"{amount/10000:.1f}万"
            else:
                display = f"{amount:,.0f}"
            return f"{display} CNY"
        except:
            return value
    
    # Formula templates
    return value


def get_template_by_id(template_id: int) -> Optional[Dict]:
    """
    Get template by ID.
    
    Args:
        template_id: Template ID
        
    Returns:
        Template dictionary or None
    """
    conn = db.connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM settlement_templates WHERE id = ?
    """, (template_id,))
    
    row = cursor.fetchone()
    if row:
        return {
            'id': row['id'],
            'user_id': row['user_id'],
            'template_name': row['template_name'],
            'template_value': row['template_value'],
            'template_type': row['template_type'],
            'is_preset': bool(row['is_preset']),
            'usage_count': int(row['usage_count']),
            'created_at': row['created_at']
        }
    return None

