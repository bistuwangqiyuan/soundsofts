"""Vercel serverless function entry point.

Wraps the FastAPI application from platform/backend so that all /api/* routes
are handled by a single serverless function on Vercel.
"""

import os
import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent / "platform" / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault("VERCEL", "1")

from main import app  # noqa: E402, F401
