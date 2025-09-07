#!/usr/bin/env python3
"""
Trello Sprint Generator - Main Entry Point

A tool to automatically generate Trello cards from markdown sprint files.
Parses sprint markdown files and creates organized cards with checklists, labels, and due dates.

Usage:
    python main.py --file sprint1.md --board-id YOUR_BOARD_ID
"""

# Import the new modular CLI
from src.cli import main

if __name__ == "__main__":
    main()
