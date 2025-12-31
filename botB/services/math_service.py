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


def is_batch_amounts(text: str) -> bool:
    """
    Check if text contains multiple amounts (batch format).
    
    Supports formats:
    - Comma-separated: "1000,2000,3000"
    - Newline-separated: "1000\n2000\n3000"
    - Mixed: "1000, 2000\n3000"
    
    Args:
        text: Input text
        
    Returns:
        True if text contains multiple amounts
    """
    text = text.strip()
    
    # Exclude text that contains @ symbol (likely usernames, not amounts)
    if '@' in text:
        return False
    
    # Check for comma or newline separators
    if ',' in text or '\n' in text:
        # Split by comma or newline and check if at least 2 parts
        parts = re.split(r'[,,\n]+', text)
        parts = [p.strip() for p in parts if p.strip()]
        
        # Must have at least 2 parts
        if len(parts) < 2:
            return False
        
        # Check if at least one part looks like a number (to avoid false positives)
        # This helps distinguish between amounts and other multi-line text
        has_number_like = False
        for part in parts:
            # Remove common currency symbols and spaces
            cleaned = part.replace('¥', '').replace('$', '').replace('€', '').replace(' ', '')
            # Check if it's a number or simple math expression
            if is_number(cleaned) or is_simple_math(cleaned):
                has_number_like = True
                break
        
        return has_number_like
    
    return False


def parse_batch_amounts(text: str) -> list[float]:
    """
    Parse multiple amounts from text.
    
    Supports formats:
    - Comma-separated: "1000,2000,3000"
    - Newline-separated: "1000\n2000\n3000"
    - Mixed: "1000, 2000\n3000"
    - With math expressions: "1000-100, 2000+50, 3000*2"
    
    Args:
        text: Input text containing multiple amounts
        
    Returns:
        List of parsed amounts as floats
        
    Raises:
        ValueError: If any amount cannot be parsed
    """
    text = text.strip()
    
    # Split by comma or newline
    parts = re.split(r'[,,\n]+', text)
    
    amounts = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Parse each part (supports numbers and math expressions)
        try:
            amount = parse_amount(part)
            if amount > 0:
                amounts.append(amount)
        except ValueError as e:
            raise ValueError(f"无法解析金额 '{part}': {str(e)}")
    
    if not amounts:
        raise ValueError("未找到有效的金额")
    
    return amounts

