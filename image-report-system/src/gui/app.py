"""GUI application for 超声图像检测与报告生成系统."""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run_gui() -> None:
    """Launch the main GUI window."""
    root = tk.Tk()
    root.title("S5 超声图像检测与报告生成系统")
    root.geometry("720x520")
    root.minsize(560, 400)

    # Style
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Microsoft YaHei", 10, "bold"))
    style.configure("TLabel", font=("Microsoft YaHei", 10))
    style.configure("Header.TLabel", font=("Microsoft YaHei", 14, "bold"))

    main = ttk.Frame(root, padding=20)
    main.pack(fill=tk.BOTH, expand=True)

    # Header
    ttk.Label(main, text="超声图像检测与报告生成系统", style="Header.TLabel").pack(pady=(0, 8))
    ttk.Label(main, text="C扫分析 · 多模态融合 · Word报告自动生成", foreground="gray").pack(pady=(0, 20))

    # Input image
    f_input = ttk.LabelFrame(main, text="输入图像", padding=10)
    f_input.pack(fill=tk.X, pady=5)

    var_input = tk.StringVar()
    ttk.Entry(f_input, textvariable=var_input, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

    def browse_input():
        p = filedialog.askopenfilename(
            title="选择C扫图像",
            filetypes=[("图像文件", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif"), ("所有文件", "*.*")],
        )
        if p:
            var_input.set(p)

    ttk.Button(f_input, text="浏览...", command=browse_input).pack(side=tk.RIGHT)

    # Output report
    f_output = ttk.LabelFrame(main, text="输出报告", padding=10)
    f_output.pack(fill=tk.X, pady=5)

    var_output = tk.StringVar()
    ttk.Entry(f_output, textvariable=var_output, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

    def browse_output():
        p = filedialog.asksaveasfilename(
            title="保存报告",
            defaultextension=".docx",
            filetypes=[("Word文档", "*.docx"), ("所有文件", "*.*")],
        )
        if p:
            var_output.set(p)

    ttk.Button(f_output, text="浏览...", command=browse_output).pack(side=tk.RIGHT)

    # Options
    f_opts = ttk.LabelFrame(main, text="检测信息", padding=10)
    f_opts.pack(fill=tk.X, pady=5)

    ttk.Label(f_opts, text="试样编号:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=2)
    var_specimen = tk.StringVar(value="UNKNOWN")
    ttk.Entry(f_opts, textvariable=var_specimen, width=20).grid(row=0, column=1, sticky=tk.W, pady=2)

    ttk.Label(f_opts, text="操作人员:").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=2)
    var_operator = tk.StringVar(value="系统")
    ttk.Entry(f_opts, textvariable=var_operator, width=20).grid(row=1, column=1, sticky=tk.W, pady=2)

    ttk.Label(f_opts, text="检测设备:").grid(row=2, column=0, sticky=tk.W, padx=(0, 8), pady=2)
    var_equipment = tk.StringVar(value="PAUT")
    ttk.Entry(f_opts, textvariable=var_equipment, width=20).grid(row=2, column=1, sticky=tk.W, pady=2)

    # Status
    var_status = tk.StringVar(value="就绪")
    lbl_status = ttk.Label(main, textvariable=var_status, foreground="gray")
    lbl_status.pack(pady=8)

    # Generate button
    def do_generate():
        inp = var_input.get().strip()
        out = var_output.get().strip()
        if not inp:
            messagebox.showwarning("提示", "请选择输入图像")
            return
        if not out:
            messagebox.showwarning("提示", "请指定输出报告路径")
            return

        var_status.set("正在生成报告...")
        root.update()

        try:
            from src.report_generation.exporter import run_pipeline

            run_pipeline(
                inp,
                out,
                specimen_id=var_specimen.get() or "UNKNOWN",
                operator=var_operator.get() or "系统",
                equipment=var_equipment.get() or "PAUT",
            )
            var_status.set("报告生成完成")
            messagebox.showinfo("完成", f"报告已保存至:\n{out}")
        except FileNotFoundError as e:
            var_status.set("就绪")
            messagebox.showerror("错误", str(e))
        except Exception as e:
            var_status.set("就绪")
            messagebox.showerror("错误", f"生成失败: {e}")

    ttk.Button(main, text="生成报告", style="Accent.TButton", command=do_generate).pack(pady=15)

    # Fusion demo section
    sep = ttk.Separator(main, orient=tk.HORIZONTAL)
    sep.pack(fill=tk.X, pady=15)

    ttk.Label(main, text="融合分析演示", style="Header.TLabel").pack(pady=(0, 8))

    f_demo = ttk.Frame(main)
    f_demo.pack(fill=tk.X, pady=5)

    ttk.Label(f_demo, text="预测粘接力 (N/cm):").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=2)
    var_force = tk.DoubleVar(value=85.0)
    ttk.Spinbox(f_demo, from_=0, to=200, textvariable=var_force, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)

    ttk.Label(f_demo, text="缺陷面积比:").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=2)
    var_ratio = tk.DoubleVar(value=0.01)
    ttk.Spinbox(f_demo, from_=0, to=1, increment=0.01, textvariable=var_ratio, width=10).grid(
        row=1, column=1, sticky=tk.W, pady=2
    )

    ttk.Label(f_demo, text="视觉置信度:").grid(row=2, column=0, sticky=tk.W, padx=(0, 8), pady=2)
    var_conf = tk.DoubleVar(value=0.9)
    ttk.Spinbox(f_demo, from_=0, to=1, increment=0.05, textvariable=var_conf, width=10).grid(
        row=2, column=1, sticky=tk.W, pady=2
    )

    var_result = tk.StringVar(value="")
    lbl_result = ttk.Label(main, textvariable=var_result, font=("Microsoft YaHei", 11, "bold"))
    lbl_result.pack(pady=8)

    def do_analyze():
        try:
            from src.multimodal_fusion.fusion import fuse_results
            from src.multimodal_fusion.rule_engine import RuleEngine

            import numpy as np

            engine = RuleEngine()
            force = var_force.get()
            ratio = var_ratio.get()
            conf = var_conf.get()
            checks = engine.run_all_checks(force, int(ratio * 10000), 10000)
            mask = np.zeros((100, 100), dtype=np.float32)
            if ratio > 0:
                mask.flat[: int(ratio * 10000)] = 1.0
            result = fuse_results(mask, conf, force, checks)
            var_result.set(f"综合判定: {result.overall_quality} | 置信度: {result.confidence:.2%}")
        except Exception as e:
            var_result.set(f"分析失败: {e}")

    ttk.Button(f_demo, text="融合分析", command=do_analyze).grid(row=3, column=0, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
