"""
Template service for Bot B
Handles settlement templates management
"""
import logging
from typing import List, Dict, Optional
from database import db

logger = logging.getLogger(__name__)


def get_all_templates(user_id: int = None) -> Dict[str, List[Dict]]:
    """
    Get all available templates (preset + user templates).
    
    Args:
        user_id: Optional user ID to include user templates
        
    Returns:
        Dictionary with 'amount' and 'formula' template lists
    """
    templates = {
        'amount': [],
        'formula': []
    }
    
    # Get preset templates
    preset_amount = db.get_templates(user_id=None, template_type='amount')
    preset_formula = db.get_templates(user_id=None, template_type='formula')
    
    templates['amount'].extend(preset_amount)
    templates['formula'].extend(preset_formula)
    
    # Get user templates if user_id provided
    if user_id:
        user_amount = db.get_templates(user_id=user_id, template_type='amount')
        user_formula = db.get_templates(user_id=user_id, template_type='formula')
        
        templates['amount'].extend(user_amount)
        templates['formula'].extend(user_formula)
    
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

