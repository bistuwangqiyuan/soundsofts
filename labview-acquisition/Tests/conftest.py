"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

# 确保项目根在 path 中，便于导入 python_interface
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
