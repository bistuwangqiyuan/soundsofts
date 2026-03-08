"""Desktop launcher: start local server and open browser. Pack with PyInstaller for .exe."""

from __future__ import annotations

import sys
import threading
import time
import webbrowser
from pathlib import Path

# Ensure project root is on path (and for PyInstaller bundle)
ROOT = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PORT = 8000
URL = f"http://127.0.0.1:{PORT}"


def run_server():
    import uvicorn
    from api.index import app
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


def main():
    try:
        import tkinter as tk
    except ImportError:
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(URL)
        threading.Thread(target=open_browser, daemon=True).start()
        run_server()
        return

    # Run server in thread so GUI stays responsive
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1.2)
    webbrowser.open(URL)

    root = tk.Tk()
    root.title("U-Net 超声C扫缺陷语义分割系统")
    root.geometry("380x140")
    root.resizable(False, False)

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text="U-Net 超声C扫缺陷语义分割系统", font=("", 12, "bold")).pack(pady=(0, 8))
    tk.Label(frame, text=f"系统已启动 · 浏览器已打开 {URL}", fg="gray").pack(pady=(0, 12))
    tk.Label(frame, text="关闭此窗口将停止服务。", fg="gray", font=("", 9)).pack(pady=(0, 12))

    def on_closing():
        root.destroy()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    tk.Button(frame, text="关闭", command=on_closing, width=12).pack()
    root.mainloop()


if __name__ == "__main__":
    main()
