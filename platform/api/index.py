"""Vercel serverless entry - exports FastAPI app for platform backend."""

import sys
from pathlib import Path

# Add platform root to path so backend package is importable
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from backend.main import app
