"""
Tests for the markdown parser.
"""

import pytest
from src.markdown_parser import MarkdownParser, MarkdownParseError


class TestMarkdownParser:
    """Test cases for MarkdownParser"""
    
    def test_parse_sprint_title(self):
        """Test sprint title extraction"""
        content = "# 🎯 **Sprint 1 - Test Sprint**"
        parser = MarkdownParser.__new__(MarkdownParser)
        parser.content = content
        
        title = parser._extract_sprint_title()
        assert title == "Sprint 1 - Test Sprint"
    
    def test_parse_sprint_info(self):
        """Test sprint info extraction"""
        content = """
        **Duração**: 5 dias
        **Foco**: Test focus
        **Prioridade**: Crítica
        **Dependências**: None
        """
        parser = MarkdownParser.__new__(MarkdownParser)
        parser.content = content
        
        info = parser._extract_sprint_info()
        assert info['duration'] == "5 dias"
        assert info['focus'] == "Test focus"
        assert info['priority'] == "Crítica"
        assert info['dependencies'] == "None"
    
    def test_clean_title(self):
        """Test title cleaning functionality"""
        from src.utils import clean_title
        
        # Test markdown bold removal
        assert clean_title("**Test Title**") == "Test Title"
        
        # Test header removal
        assert clean_title("### Test Title") == "Test Title"
        
        # Test metadata removal
        assert clean_title("Test Title **Duração**: 2 dias") == "Test Title"
        
        # Test complex case
        title = "### **MARCO 1.1: Test** **Duração**: 2 dias | **Prioridade**: Crítica"
        expected = "MARCO 1.1: Test"
        assert clean_title(title) == expected


class TestMarkdownParseError:
    """Test error handling"""
    
    def test_file_not_found(self):
        """Test file not found error"""
        with pytest.raises(MarkdownParseError):
            MarkdownParser("nonexistent_file.md")
    
    def test_empty_file(self):
        """Test empty file error"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("")
            temp_file = f.name
        
        try:
            with pytest.raises(MarkdownParseError):
                MarkdownParser(temp_file)
        finally:
            os.unlink(temp_file)
