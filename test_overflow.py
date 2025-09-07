#!/usr/bin/env python3
"""
Test overflow protection in GUI
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_truncate_function():
    """Test the truncate_text function"""
    try:
        from src.gui import ModernTrelloGUI
        import tkinter as tk
        
        # Create a minimal GUI instance to test truncate function
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        gui = ModernTrelloGUI()
        
        # Test truncate function
        print("🧪 Testing text truncation...")
        
        # Test short text (should not be truncated)
        short_text = "Short text"
        result = gui.truncate_text(short_text, 20)
        assert result == short_text, f"Short text should not be truncated: {result}"
        print("✅ Short text not truncated")
        
        # Test long text (should be truncated)
        long_text = "This is a very long text that should be truncated to prevent overflow in the GUI interface"
        result = gui.truncate_text(long_text, 30)
        assert len(result) <= 30, f"Text should be truncated to 30 chars: {len(result)}"
        assert result.endswith("..."), f"Truncated text should end with '...': {result}"
        print("✅ Long text truncated correctly")
        
        # Test exact length
        exact_text = "This is exactly twenty characters"
        result = gui.truncate_text(exact_text, 20)
        assert len(result) <= 20, f"Text should be truncated to 20 chars: {len(result)}"
        print("✅ Exact length text handled correctly")
        
        root.destroy()
        print("\n🎉 All overflow protection tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Overflow test failed: {e}")
        return False

def test_gui_dimensions():
    """Test GUI widget dimensions"""
    try:
        from src.gui import ModernTrelloGUI
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        gui = ModernTrelloGUI()
        
        print("\n🧪 Testing GUI dimensions...")
        
        # Test that entry fields have reasonable widths
        assert gui.api_key_entry['width'] <= 40, "API Key field too wide"
        assert gui.token_entry['width'] <= 40, "Token field too wide"
        assert gui.board_id_entry['width'] <= 40, "Board ID field too wide"
        assert gui.file_entry['width'] <= 35, "File entry field too wide"
        assert gui.list_combo['width'] <= 30, "List combo field too wide"
        
        print("✅ All entry fields have appropriate widths")
        
        # Test preview text dimensions
        assert gui.preview_text['height'] <= 8, "Preview text too tall"
        assert gui.preview_text['width'] <= 80, "Preview text too wide"
        
        print("✅ Preview text has appropriate dimensions")
        
        root.destroy()
        print("\n🎉 All dimension tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Dimension test failed: {e}")
        return False

def main():
    """Run all overflow tests"""
    print("🧪 Trello Sprint Generator - Overflow Protection Test Suite")
    print("=" * 60)
    
    truncate_ok = test_truncate_function()
    dimensions_ok = test_gui_dimensions()
    
    if truncate_ok and dimensions_ok:
        print("\n🎉 All overflow protection tests passed!")
        print("✅ GUI is protected against text overflow")
        print("✅ All widgets have appropriate dimensions")
        print("✅ Text truncation works correctly")
    else:
        print("\n❌ Some overflow tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
