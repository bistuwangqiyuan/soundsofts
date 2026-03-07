"""S4 数据预处理与信号处理流水线 — GUI 启动入口（可打包为可执行文件）."""

from __future__ import annotations

import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


def _get_base_path() -> Path:
    """获取资源根路径，兼容开发环境与 PyInstaller 打包后."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def _find_free_port(start: int = 8765) -> int:
    """查找可用端口."""
    for port in range(start, start + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return start


def main() -> None:
    base = _get_base_path()
    public_dir = base / "public"
    api_dir = base / "api"

    # 确保路径正确
    if not public_dir.exists():
        public_dir = base
    if not (api_dir / "index.py").exists():
        api_dir = base / "api"

    sys.path.insert(0, str(base))
    sys.path.insert(0, str(base / "src"))

    port = _find_free_port(8765)
    url = f"http://127.0.0.1:{port}/"

    # 延迟打开浏览器，等服务器启动
    def open_browser() -> None:
        time.sleep(1.2)
        webbrowser.open(url, new=1)

    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    from fastapi.staticfiles import StaticFiles

    # 动态加载 app（API 路由已注册）
    sys.path.insert(0, str(api_dir))
    from index import app

    # 挂载静态文件，API 路由优先匹配
    app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="static")

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
