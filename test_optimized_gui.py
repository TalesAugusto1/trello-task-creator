#!/usr/bin/env python3
"""
Test optimized GUI dimensions and layout
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gui_dimensions():
    """Test optimized GUI dimensions"""
    try:
        print("🧪 Testing optimized GUI dimensions...")
        
        import tkinter as tk
        from src.gui import ModernTrelloGUI
        
        # Create root window but don't show it
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create GUI instance
        gui = ModernTrelloGUI()
        
        # Test window dimensions
        assert gui.root.winfo_reqwidth() <= 900, f"Window width too large: {gui.root.winfo_reqwidth()}"
        assert gui.root.winfo_reqheight() <= 600, f"Window height too large: {gui.root.winfo_reqheight()}"
        print("✅ Window dimensions optimized")
        
        # Test entry field widths
        assert gui.api_key_entry['width'] <= 35, f"API Key field too wide: {gui.api_key_entry['width']}"
        assert gui.token_entry['width'] <= 35, f"Token field too wide: {gui.token_entry['width']}"
        assert gui.board_id_entry['width'] <= 35, f"Board ID field too wide: {gui.board_id_entry['width']}"
        assert gui.file_entry['width'] <= 30, f"File entry field too wide: {gui.file_entry['width']}"
        assert gui.list_combo['width'] <= 25, f"List combo field too wide: {gui.list_combo['width']}"
        print("✅ Entry field widths optimized")
        
        # Test preview text dimensions
        assert gui.preview_text['height'] <= 6, f"Preview text too tall: {gui.preview_text['height']}"
        assert gui.preview_text['width'] <= 70, f"Preview text too wide: {gui.preview_text['width']}"
        print("✅ Preview text dimensions optimized")
        
        # Test progress bar length
        assert gui.progress_bar['length'] <= 300, f"Progress bar too long: {gui.progress_bar['length']}"
        print("✅ Progress bar length optimized")
        
        root.destroy()
        print("\n🎉 All dimension optimizations verified!")
        return True
        
    except Exception as e:
        print(f"❌ Dimension test failed: {e}")
        return False

def test_compact_layout():
    """Test compact layout elements"""
    try:
        print("\n🧪 Testing compact layout...")
        
        import tkinter as tk
        from src.gui import ModernTrelloGUI
        
        root = tk.Tk()
        root.withdraw()
        
        gui = ModernTrelloGUI()
        
        # Test button text lengths (should be compact)
        test_button_text = gui.test_button['text']
        load_button_text = gui.load_button['text']
        save_button_text = gui.save_button['text']
        
        assert len(test_button_text) <= 10, f"Test button text too long: {test_button_text}"
        assert len(load_button_text) <= 10, f"Load button text too long: {load_button_text}"
        assert len(save_button_text) <= 10, f"Save button text too long: {save_button_text}"
        print("✅ Button text lengths optimized")
        
        # Test truncate function
        long_text = "This is a very long text that should be truncated properly"
        truncated = gui.truncate_text(long_text, 20)
        assert len(truncated) <= 20, f"Truncation failed: {len(truncated)}"
        assert truncated.endswith("..."), f"Truncation should end with '...': {truncated}"
        print("✅ Text truncation working correctly")
        
        root.destroy()
        print("\n🎉 All compact layout tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Compact layout test failed: {e}")
        return False

def main():
    """Run all optimization tests"""
    print("🧪 Trello Sprint Generator - GUI Optimization Test Suite")
    print("=" * 60)
    
    dimensions_ok = test_gui_dimensions()
    layout_ok = test_compact_layout()
    
    if dimensions_ok and layout_ok:
        print("\n🎉 All GUI optimization tests passed!")
        print("✅ Window dimensions optimized (900x600)")
        print("✅ Entry field widths reduced")
        print("✅ Preview text dimensions compact")
        print("✅ Progress bar length optimized")
        print("✅ Button text lengths shortened")
        print("✅ Text truncation working correctly")
        print("\n🚀 GUI is optimized and overflow-free!")
    else:
        print("\n❌ Some optimization tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
