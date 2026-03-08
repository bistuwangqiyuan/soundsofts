"""本地启动 API 服务（用于测试）。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.index:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
    )
