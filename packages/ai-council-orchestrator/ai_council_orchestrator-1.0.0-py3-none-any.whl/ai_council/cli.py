#!/usr/bin/env python3
"""
Command-line interface for AI Council.

This module provides a simple CLI for interacting with the AI Council system.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import ai_council
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_council.main import main

if __name__ == "__main__":
    main()