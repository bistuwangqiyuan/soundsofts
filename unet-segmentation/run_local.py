"""Local server entry: serves API + static frontend. Used by GUI launcher and dev."""

from __future__ import annotations

import sys
from pathlib import Path

# Run from project root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import uvicorn
from api.index import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
