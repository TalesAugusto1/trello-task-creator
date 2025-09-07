#!/usr/bin/env python3
"""
GUI Launcher for Trello Sprint Generator

A modern graphical interface for the Trello Sprint Generator.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui import main

if __name__ == "__main__":
    main()
