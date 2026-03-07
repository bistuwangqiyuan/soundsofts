"""Vercel serverless entry - exports FastAPI app for platform backend."""

import sys
from pathlib import Path

# Add backend dir to path so main.py's "from api.routes" resolves to backend.api
root = Path(__file__).resolve().parent.parent
backend_dir = root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app

if __name__ == "__main__":
    print("App loaded:", app.title)
