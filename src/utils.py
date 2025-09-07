"""
Utility functions for the Trello Sprint Generator.
"""

import re


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
