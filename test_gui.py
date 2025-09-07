#!/usr/bin/env python3
"""
Test script for GUI components
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all GUI imports"""
    try:
        print("🔍 Testing imports...")
        
        # Test basic imports
        from src.config import ConfigManager
        print("✅ ConfigManager imported")
        
        from src.trello_client import TrelloClient
        print("✅ TrelloClient imported")
        
        from src.markdown_parser import MarkdownParser
        print("✅ MarkdownParser imported")
        
        from src.sprint_generator import SprintGenerator
        print("✅ SprintGenerator imported")
        
        from src.gui import ModernTrelloGUI
        print("✅ ModernTrelloGUI imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_gui_creation():
    """Test GUI creation without showing window"""
    try:
        print("\n🔍 Testing GUI creation...")
        
        import tkinter as tk
        from src.gui import ModernTrelloGUI
        
        # Create root window but don't show it
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create GUI instance
        gui = ModernTrelloGUI()
        
        # Test basic functionality
        gui.setup_variables()
        gui.setup_styles()
        
        print("✅ GUI creation successful")
        
        # Clean up
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI creation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Trello Sprint Generator - GUI Test Suite")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test GUI creation
        gui_ok = test_gui_creation()
        
        if gui_ok:
            print("\n🎉 All tests passed! GUI is ready to use.")
            print("\n🚀 To launch the GUI, run:")
            print("   python gui.py")
            print("   or")
            print("   make gui")
        else:
            print("\n❌ GUI creation failed")
            sys.exit(1)
    else:
        print("\n❌ Import tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
