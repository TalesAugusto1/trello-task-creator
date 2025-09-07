#!/usr/bin/env python3
"""
GUI Launcher for Trello Sprint Generator

A modern graphical interface for the Trello Sprint Generator.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.gui import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"❌ Error importing GUI modules: {e}")
    print("\n🔧 Please ensure all dependencies are installed:")
    print("   pip install -r requirements.txt")
    print("\n📚 For more help, see the documentation in docs/")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting GUI: {e}")
    print("\n🔧 Try running:")
    print("   python -m pip install --upgrade pip")
    print("   pip install -r requirements.txt")
    print("\n📚 For more help, see the documentation in docs/")
    sys.exit(1)
