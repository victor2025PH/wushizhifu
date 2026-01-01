"""
Service for importing sensitive words from text
"""
import re
import logging

logger = logging.getLogger(__name__)


def parse_sensitive_words_import(text: str) -> list:
    """
    Parse sensitive words from text.
    Supports multiple formats:
    1. One word per line
    2. Comma-separated: word,action
    3. Tab-separated: word\taction
    4. CSV-like format: word,action
    
    Args:
        text: Input text containing sensitive words
        
    Returns:
        List of tuples (word, action) where action defaults to 'warn' if not specified
    """
    words = []
    lines = text.strip().split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue
        
        # Try comma-separated format: word,action
        if ',' in line:
            parts = [p.strip() for p in line.split(',', 1)]
            if parts[0]:  # Word must not be empty
                word = parts[0]
                action = parts[1].lower() if len(parts) > 1 and parts[1] else 'warn'
                # Validate action
                if action not in ['warn', 'delete', 'ban']:
                    action = 'warn'
                words.append((word, action))
        # Try tab-separated format: word\taction
        elif '\t' in line:
            parts = [p.strip() for p in line.split('\t', 1)]
            if parts[0]:
                word = parts[0]
                action = parts[1].lower() if len(parts) > 1 and parts[1] else 'warn'
                if action not in ['warn', 'delete', 'ban']:
                    action = 'warn'
                words.append((word, action))
        # Single word per line
        else:
            if line:
                words.append((line, 'warn'))
    
    return words
