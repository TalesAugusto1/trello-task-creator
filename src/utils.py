"""
Utility functions for the Trello Sprint Generator.
"""

import re
from typing import List, Optional


def clean_title(title: str) -> str:
    """Clean title by removing markdown formatting and metadata"""
    # Remove markdown bold formatting
    title = re.sub(r'\*\*(.+?)\*\*', r'\1', title)
    
    # Remove markdown headers
    title = re.sub(r'^#+\s*', '', title)
    
    # Remove any trailing metadata patterns
    title = re.sub(r'\s*\*\*Duração\*\*:.*$', '', title)
    title = re.sub(r'\s*\*\*Prioridade\*\*:.*$', '', title)
    title = re.sub(r'\s*\*\*Dependências\*\*:.*$', '', title)
    
    # Clean up extra whitespace
    title = title.strip()
    
    return title


def format_duration(duration_str: str) -> str:
    """Format duration string for better readability"""
    if not duration_str:
        return "Not specified"
    
    # Clean up common duration formats
    duration = duration_str.strip()
    
    # Convert common abbreviations
    duration = duration.replace("dias", "days")
    duration = duration.replace("horas", "hours")
    duration = duration.replace("semanas", "weeks")
    
    return duration


def extract_priority_from_text(text: str) -> str:
    """Extract priority level from text"""
    text_lower = text.lower()
    
    if 'crítica' in text_lower or 'critical' in text_lower:
        return 'Critical'
    elif 'alta' in text_lower or 'high' in text_lower:
        return 'High'
    elif 'média' in text_lower or 'medium' in text_lower:
        return 'Medium'
    elif 'baixa' in text_lower or 'low' in text_lower:
        return 'Low'
    else:
        return 'Medium'


def validate_board_id(board_id: str) -> bool:
    """Validate Trello board ID format"""
    if not board_id:
        return False
    
    # Trello board IDs are typically 8 characters long and alphanumeric
    if len(board_id) < 6 or len(board_id) > 10:
        return False
    
    # Should be alphanumeric
    if not board_id.isalnum():
        return False
    
    return True


def format_list_for_display(items: List[str], max_items: int = 5) -> str:
    """Format a list of items for display, truncating if necessary"""
    if not items:
        return "None"
    
    if len(items) <= max_items:
        return ", ".join(items)
    else:
        visible_items = items[:max_items]
        return ", ".join(visible_items) + f" (+{len(items) - max_items} more)"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def parse_estimated_time(time_str: str) -> Optional[dict]:
    """Parse estimated time string into structured format"""
    if not time_str:
        return None
    
    time_str = time_str.strip().lower()
    
    # Extract number and unit
    match = re.search(r'(\d+)\s*(hora|hour|dia|day|semana|week)s?', time_str)
    if not match:
        return None
    
    number = int(match.group(1))
    unit = match.group(2)
    
    # Normalize units
    if unit in ['hora', 'hour']:
        unit = 'hours'
    elif unit in ['dia', 'day']:
        unit = 'days'
    elif unit in ['semana', 'week']:
        unit = 'weeks'
    
    return {
        'value': number,
        'unit': unit,
        'original': time_str
    }
