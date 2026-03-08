#!/usr/bin/env python3
"""Launch the Image Report System GUI."""

import sys
from pathlib import Path

# Ensure project root is in path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gui.app import run_gui

if __name__ == "__main__":
    run_gui()
