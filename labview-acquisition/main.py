#!/usr/bin/env python3
"""LabVIEW B/S 上位机采集控制软件 — GUI 主程序入口。"""

from __future__ import annotations

import sys
import webbrowser
from pathlib import Path

# 支持 PyInstaller 打包：资源在 _MEIPASS，数据目录在 exe 同目录
if getattr(sys, "frozen", False):
    _ROOT = Path(sys.executable).resolve().parent
    _RESOURCE_ROOT = Path(sys._MEIPASS)
else:
    _ROOT = Path(__file__).resolve().parent
    _RESOURCE_ROOT = _ROOT
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))

CONFIG_DIR = _RESOURCE_ROOT / "Config"
PUBLIC_DIR = _RESOURCE_ROOT / "public"
DATA_DIR = _ROOT / "data"


def _run_gui() -> None:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext

    from python_interface import AcquisitionDataReader, CalibrationManager, StreamClient

    class Application:
        def __init__(self) -> None:
            self.win = tk.Tk()
            self.win.title("LabVIEW B/S 上位机采集控制软件")
            self.win.minsize(520, 420)
            self.win.geometry("640x480")

            self.stream_client: StreamClient | None = None
            self._build_ui()

        def _build_ui(self) -> None:
            main = ttk.Frame(self.win, padding=10)
            main.pack(fill=tk.BOTH, expand=True)

            ttk.Label(main, text="LabVIEW B/S 上位机采集控制软件", font=("", 14, "bold")).pack(pady=(0, 8))
            ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

            btn_frame = ttk.Frame(main)
            btn_frame.pack(fill=tk.X, pady=6)
            ttk.Button(btn_frame, text="打开数据文件 (HDF5)", command=self._open_data_file).pack(side=tk.LEFT, padx=4)
            ttk.Button(btn_frame, text="打开技术文档", command=self._open_docs).pack(side=tk.LEFT, padx=4)
            ttk.Button(btn_frame, text="校准信息", command=self._show_calibration).pack(side=tk.LEFT, padx=4)
            ttk.Button(btn_frame, text="TCP 流连接", command=self._toggle_tcp).pack(side=tk.LEFT, padx=4)

            self.tcp_status = ttk.Label(main, text="TCP: 未连接", foreground="gray")
            self.tcp_status.pack(anchor=tk.W, pady=2)

            ttk.Label(main, text="日志 / 数据摘要:").pack(anchor=tk.W, pady=(8, 2))
            self.log = scrolledtext.ScrolledText(main, height=14, width=72, state=tk.DISABLED, wrap=tk.WORD)
            self.log.pack(fill=tk.BOTH, expand=True, pady=4)

            status = ttk.Frame(main)
            status.pack(fill=tk.X, pady=6)
            self.status_label = ttk.Label(status, text="就绪")
            self.status_label.pack(side=tk.LEFT)

            self._log("程序已启动。可打开 HDF5 数据文件、查看技术文档或校准信息。")

        def _log(self, msg: str) -> None:
            self.log.configure(state=tk.NORMAL)
            self.log.insert(tk.END, msg + "\n")
            self.log.see(tk.END)
            self.log.configure(state=tk.DISABLED)

        def _open_data_file(self) -> None:
            path = filedialog.askopenfilename(
                title="选择 HDF5 数据文件",
                filetypes=[("HDF5 文件", "*.h5 *.hdf5"), ("所有文件", "*.*")],
                initialdir=str(DATA_DIR) if DATA_DIR.is_dir() else str(_ROOT),
            )
            if not path:
                return
            try:
                reader = AcquisitionDataReader(path)
                meta = reader.get_metadata()
                df = reader.to_dataframe()
                self._log(f"已打开: {path}")
                self._log(f"  元数据: {meta}")
                self._log(f"  采集点数: {len(df)}")
                if len(df) > 0:
                    self._log(f"  示例: specimen_id={df['specimen_id'].iloc[0]}, point_id={df['point_id'].iloc[0]}")
                self.status_label.config(text=f"已加载 {len(df)} 条记录")
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败:\n{e}")
                self._log(f"错误: {e}")

        def _open_docs(self) -> None:
            index = PUBLIC_DIR / "index.html"
            if index.is_file():
                webbrowser.open(index.as_uri())
                self._log("已打开技术文档 (浏览器)")
            else:
                messagebox.showwarning("提示", f"未找到文档: {index}")
                self._log(f"未找到: {index}")

        def _show_calibration(self) -> None:
            cal_path = CONFIG_DIR / "calibration_data.json"
            if not cal_path.is_file():
                messagebox.showwarning("提示", f"未找到校准文件: {cal_path}")
                self._log(f"未找到: {cal_path}")
                return
            try:
                cal = CalibrationManager(cal_path)
                lines = [
                    "力传感器: " + str(cal.force_sensor.get("model", "")),
                    "  校准点数: " + str(len(cal.force_sensor.get("calibration_points", []))),
                    "位置编码器 mm_per_pulse: " + str(cal.position_encoder.get("mm_per_pulse", "")),
                ]
                msg = "\n".join(lines)
                self._log("校准信息:\n" + msg)
                messagebox.showinfo("校准信息", msg)
            except Exception as e:
                messagebox.showerror("错误", f"读取校准失败:\n{e}")
                self._log(f"错误: {e}")

        def _toggle_tcp(self) -> None:
            if self.stream_client is not None:
                try:
                    self.stream_client.disconnect()
                except Exception:
                    pass
                self.stream_client = None
                self.tcp_status.config(text="TCP: 未连接", foreground="gray")
                self._log("TCP 已断开")
                return
            host = "127.0.0.1"
            port = 5000
            try:
                client = StreamClient(host=host, port=port)
                client.connect()
                self.stream_client = client
                self.tcp_status.config(text=f"TCP: 已连接 {host}:{port}", foreground="green")
                self._log(f"TCP 已连接 {host}:{port}")
            except Exception as e:
                messagebox.showerror("连接失败", f"无法连接 {host}:{port}\n{e}")
                self._log(f"TCP 连接失败: {e}")

        def run(self) -> None:
            if self.stream_client:
                try:
                    self.stream_client.disconnect()
                except Exception:
                    pass
            self.win.mainloop()

    app = Application()
    app.run()

    if app.stream_client:
        try:
            app.stream_client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    _run_gui()
