"""
Safe math expression evaluation service
Safely evaluates simple math expressions without using eval()
"""
import re
import logging

logger = logging.getLogger(__name__)


def is_number(text: str) -> bool:
    """
    Check if text is a pure number (integer or decimal).
    
    Args:
        text: Input text
        
    Returns:
        True if text is a number
    """
    try:
        float(text.strip())
        return True
    except (ValueError, AttributeError):
        return False


def is_simple_math(text: str) -> bool:
    """
    Check if text is a simple math expression (e.g., "29981-125", "100+50", "200*2").
    Only allows: numbers, +, -, *, /, spaces, decimal points.
    
    Args:
        text: Input text
        
    Returns:
        True if text matches simple math pattern
    """
    # Pattern: optional spaces, number, optional spaces, operator, optional spaces, number
    # Allows: +, -, *, /, decimal numbers
    pattern = r'^\s*-?\d+\.?\d*\s*[\+\-\*\/]\s*\d+\.?\d*\s*$'
    return bool(re.match(pattern, text.strip()))


def safe_calculate(expression: str) -> float:
    """
    Safely calculate a simple math expression.
    Only supports: +, -, *, / operations.
    
    Args:
        expression: Math expression string (e.g., "29981-125", "100+50")
        
    Returns:
        Calculated result as float
        
    Raises:
        ValueError: If expression is invalid or contains unsupported operations
    """
    expression = expression.strip()
    
    # If it's just a number
    if is_number(expression):
        return float(expression)
    
    # Parse simple expressions
    # Find operator
    operators = ['+', '-', '*', '/']
    operator = None
    operator_pos = -1
    
    # Check for operators (avoid matching negative sign at start)
    for i, char in enumerate(expression):
        if i > 0 and char in operators:
            operator = char
            operator_pos = i
            break
    
    if operator is None:
        raise ValueError(f"Invalid expression: no operator found")
    
    # Split by operator
    left = expression[:operator_pos].strip()
    right = expression[operator_pos + 1:].strip()
    
    # Validate both sides are numbers
    try:
        left_num = float(left)
        right_num = float(right)
    except ValueError:
        raise ValueError(f"Invalid expression: non-numeric operands")
    
    # Calculate
    if operator == '+':
        result = left_num + right_num
    elif operator == '-':
        result = left_num - right_num
    elif operator == '*':
        result = left_num * right_num
    elif operator == '/':
        if right_num == 0:
            raise ValueError("Division by zero")
        result = left_num / right_num
    else:
        raise ValueError(f"Unsupported operator: {operator}")
    
    logger.info(f"Calculated: {expression} = {result}")
    return result


def parse_amount(text: str) -> float:
    """
    Parse amount from text. Handles pure numbers and simple math expressions.
    
    Args:
        text: Input text
        
    Returns:
        Calculated amount as float
        
    Raises:
        ValueError: If text cannot be parsed as a number or math expression
    """
    text = text.strip()
    
    # Try as pure number first
    if is_number(text):
        return float(text)
    
    # Try as simple math expression
    if is_simple_math(text):
        return safe_calculate(text)
    
    # If neither, raise error
    raise ValueError(f"Cannot parse amount from: {text}")

