"""Professional multi-panel GUI for 超声图像检测与报告生成系统."""

from __future__ import annotations

import os
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

VERSION = "2.0.0"

# ---------------------------------------------------------------------------
# Helper: resize PIL image to fit a box while keeping aspect ratio
# ---------------------------------------------------------------------------

def _fit_image(pil_img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    w, h = pil_img.size
    scale = min(max_w / w, max_h / h, 1.0)
    return pil_img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)


# ===================================================================
# Main application
# ===================================================================

class ImageReportApp:
    """4-tab professional GUI application."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(f"超声图像检测与报告生成系统 v{VERSION}")
        self.root.geometry("960x700")
        self.root.minsize(800, 600)

        # State
        self._image_path: str = ""
        self._analysis_result = None
        self._preview_photo = None  # prevent GC

        self._build_menu()
        self._build_toolbar()
        self._build_notebook()
        self._build_statusbar()

    # ------------------------------------------------------------------
    # Menu bar
    # ------------------------------------------------------------------
    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开图像...", command=self._browse_image, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="开始分析", command=self._run_analysis)
        menubar.add_cascade(label="分析", menu=analysis_menu)

        report_menu = tk.Menu(menubar, tearoff=0)
        report_menu.add_command(label="生成报告...", command=self._generate_report)
        menubar.add_cascade(label="报告", menu=report_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.bind("<Control-o>", lambda e: self._browse_image())

    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------
    def _build_toolbar(self) -> None:
        tb = ttk.Frame(self.root, padding=(4, 2))
        tb.pack(fill=tk.X)

        ttk.Button(tb, text="打开", width=8, command=self._browse_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(tb, text="分析", width=8, command=self._run_analysis).pack(side=tk.LEFT, padx=2)
        ttk.Button(tb, text="报告", width=8, command=self._generate_report).pack(side=tk.LEFT, padx=2)

        ttk.Separator(tb, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        ttk.Label(tb, text="文件:").pack(side=tk.LEFT)
        self._var_filepath = tk.StringVar(value="未选择")
        ttk.Label(tb, textvariable=self._var_filepath, foreground="gray", width=60).pack(side=tk.LEFT, padx=4)

    # ------------------------------------------------------------------
    # Notebook (4 tabs)
    # ------------------------------------------------------------------
    def _build_notebook(self) -> None:
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 2))

        self._tab_image = ttk.Frame(self.notebook, padding=10)
        self._tab_config = ttk.Frame(self.notebook, padding=10)
        self._tab_results = ttk.Frame(self.notebook, padding=10)
        self._tab_report = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self._tab_image, text="  图像加载  ")
        self.notebook.add(self._tab_config, text="  分析配置  ")
        self.notebook.add(self._tab_results, text="  检测结果  ")
        self.notebook.add(self._tab_report, text="  报告导出  ")

        self._build_tab_image()
        self._build_tab_config()
        self._build_tab_results()
        self._build_tab_report()

    # ---- Tab 1: Image Loading ----
    def _build_tab_image(self) -> None:
        top = ttk.Frame(self._tab_image)
        top.pack(fill=tk.X)

        ttk.Button(top, text="选择C扫图像...", command=self._browse_image).pack(side=tk.LEFT)
        self._var_img_info = tk.StringVar(value="")
        ttk.Label(top, textvariable=self._var_img_info, foreground="gray").pack(side=tk.LEFT, padx=12)

        self._canvas_preview = tk.Canvas(self._tab_image, bg="#1e1e1e", highlightthickness=0)
        self._canvas_preview.pack(fill=tk.BOTH, expand=True, pady=8)

    # ---- Tab 2: Analysis Config ----
    def _build_tab_config(self) -> None:
        # Parameters frame
        pf = ttk.LabelFrame(self._tab_config, text="分割参数", padding=10)
        pf.pack(fill=tk.X, pady=4)

        self._var_block_size = tk.IntVar(value=51)
        self._var_c_offset = tk.IntVar(value=15)
        self._var_morph_kernel = tk.IntVar(value=5)
        self._var_min_area = tk.IntVar(value=30)
        self._var_conf_thresh = tk.DoubleVar(value=0.5)

        params = [
            ("自适应阈值块大小:", self._var_block_size, 11, 101),
            ("阈值偏移量:", self._var_c_offset, 1, 50),
            ("形态学核大小:", self._var_morph_kernel, 3, 15),
            ("最小缺陷面积(px):", self._var_min_area, 10, 500),
        ]
        for i, (label, var, lo, hi) in enumerate(params):
            ttk.Label(pf, text=label).grid(row=i, column=0, sticky=tk.W, padx=(0, 8), pady=3)
            ttk.Scale(pf, from_=lo, to=hi, variable=var, orient=tk.HORIZONTAL, length=200).grid(
                row=i, column=1, sticky=tk.W, pady=3
            )
            ttk.Label(pf, textvariable=var, width=5).grid(row=i, column=2, padx=4)

        # Fusion weights
        ff = ttk.LabelFrame(self._tab_config, text="融合权重", padding=10)
        ff.pack(fill=tk.X, pady=4)

        self._var_w_visual = tk.DoubleVar(value=0.4)
        self._var_w_acoustic = tk.DoubleVar(value=0.3)
        self._var_w_rules = tk.DoubleVar(value=0.3)

        weights = [
            ("视觉分支:", self._var_w_visual),
            ("声力分支:", self._var_w_acoustic),
            ("规则引擎:", self._var_w_rules),
        ]
        for i, (label, var) in enumerate(weights):
            ttk.Label(ff, text=label).grid(row=i, column=0, sticky=tk.W, padx=(0, 8), pady=3)
            ttk.Scale(ff, from_=0.0, to=1.0, variable=var, orient=tk.HORIZONTAL, length=200).grid(
                row=i, column=1, sticky=tk.W, pady=3
            )
            ttk.Label(ff, textvariable=var, width=5).grid(row=i, column=2, padx=4)

        # Run button + progress
        bf = ttk.Frame(self._tab_config)
        bf.pack(fill=tk.X, pady=10)

        self._btn_analyze = ttk.Button(bf, text="开始分析", command=self._run_analysis)
        self._btn_analyze.pack(side=tk.LEFT, padx=4)

        self._var_step = tk.StringVar(value="就绪")
        ttk.Label(bf, textvariable=self._var_step, foreground="gray").pack(side=tk.LEFT, padx=12)

        self._progress = ttk.Progressbar(self._tab_config, mode="determinate", maximum=100)
        self._progress.pack(fill=tk.X, pady=4)

        # Log
        lf = ttk.LabelFrame(self._tab_config, text="分析日志", padding=4)
        lf.pack(fill=tk.BOTH, expand=True, pady=4)

        self._log_text = tk.Text(lf, height=8, state=tk.DISABLED, bg="#1e1e1e", fg="#dfe6e9",
                                 font=("Consolas", 9), wrap=tk.WORD)
        self._log_text.pack(fill=tk.BOTH, expand=True)

    # ---- Tab 3: Results Dashboard ----
    def _build_tab_results(self) -> None:
        top = ttk.Frame(self._tab_results)
        top.pack(fill=tk.X, pady=4)

        # Verdict
        self._var_verdict = tk.StringVar(value="--")
        lbl_v = ttk.Label(top, textvariable=self._var_verdict, font=("Microsoft YaHei", 18, "bold"))
        lbl_v.pack(side=tk.LEFT, padx=8)
        self._lbl_verdict = lbl_v

        self._var_confidence = tk.StringVar(value="")
        ttk.Label(top, textvariable=self._var_confidence, font=("Microsoft YaHei", 12)).pack(side=tk.LEFT, padx=12)

        # Summary cards
        sf = ttk.Frame(self._tab_results)
        sf.pack(fill=tk.X, pady=4)

        self._var_defect_count = tk.StringVar(value="0")
        self._var_defect_ratio = tk.StringVar(value="0.00%")
        self._var_pred_force = tk.StringVar(value="-- N/cm")

        cards = [("缺陷数量", self._var_defect_count), ("面积占比", self._var_defect_ratio), ("粘接力", self._var_pred_force)]
        for label, var in cards:
            cf = ttk.LabelFrame(sf, text=label, padding=8)
            cf.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
            ttk.Label(cf, textvariable=var, font=("Microsoft YaHei", 14, "bold")).pack()

        # Defect TreeView
        tf = ttk.LabelFrame(self._tab_results, text="缺陷明细", padding=4)
        tf.pack(fill=tk.BOTH, expand=True, pady=4)

        cols = ("id", "type", "severity", "area", "location", "confidence")
        self._tree = ttk.Treeview(tf, columns=cols, show="headings", height=8)
        headings = {"id": "编号", "type": "类型", "severity": "严重度", "area": "面积(px)", "location": "位置", "confidence": "置信度"}
        widths = {"id": 50, "type": 80, "severity": 70, "area": 80, "location": 120, "confidence": 70}
        for c in cols:
            self._tree.heading(c, text=headings[c])
            self._tree.column(c, width=widths[c], anchor=tk.CENTER)

        sb = ttk.Scrollbar(tf, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Rule checks
        rf = ttk.LabelFrame(self._tab_results, text="规则校核", padding=4)
        rf.pack(fill=tk.X, pady=4)
        self._var_rules = tk.StringVar(value="")
        ttk.Label(rf, textvariable=self._var_rules, wraplength=800, justify=tk.LEFT).pack(fill=tk.X)

    # ---- Tab 4: Report Export ----
    def _build_tab_report(self) -> None:
        # Metadata
        mf = ttk.LabelFrame(self._tab_report, text="报告信息", padding=10)
        mf.pack(fill=tk.X, pady=4)

        self._var_specimen = tk.StringVar(value="PIPE-001")
        self._var_operator = tk.StringVar(value="检测员")
        self._var_equipment = tk.StringVar(value="PAUT-500")
        self._var_org = tk.StringVar(value="超声检测实验室")

        fields = [
            ("试样编号:", self._var_specimen),
            ("操作人员:", self._var_operator),
            ("检测设备:", self._var_equipment),
            ("检测机构:", self._var_org),
        ]
        for i, (label, var) in enumerate(fields):
            ttk.Label(mf, text=label).grid(row=i, column=0, sticky=tk.W, padx=(0, 8), pady=3)
            ttk.Entry(mf, textvariable=var, width=30).grid(row=i, column=1, sticky=tk.W, pady=3)

        # Output
        of = ttk.LabelFrame(self._tab_report, text="输出路径", padding=10)
        of.pack(fill=tk.X, pady=4)

        self._var_output = tk.StringVar()
        ttk.Entry(of, textvariable=self._var_output, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(of, text="浏览...", command=self._browse_output).pack(side=tk.RIGHT)

        # Buttons
        bf = ttk.Frame(self._tab_report)
        bf.pack(fill=tk.X, pady=10)
        ttk.Button(bf, text="生成报告", command=self._generate_report).pack(side=tk.LEFT, padx=4)

        self._var_open_after = tk.BooleanVar(value=True)
        ttk.Checkbutton(bf, text="生成后打开", variable=self._var_open_after).pack(side=tk.LEFT, padx=8)

        # Preview summary
        pf = ttk.LabelFrame(self._tab_report, text="报告预览", padding=8)
        pf.pack(fill=tk.BOTH, expand=True, pady=4)
        self._report_preview = tk.Text(pf, height=12, state=tk.DISABLED, bg="#fafafa", fg="#333",
                                       font=("Microsoft YaHei", 10), wrap=tk.WORD)
        self._report_preview.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------
    def _build_statusbar(self) -> None:
        sb = ttk.Frame(self.root, padding=(6, 2))
        sb.pack(fill=tk.X, side=tk.BOTTOM)

        self._var_status = tk.StringVar(value="就绪")
        ttk.Label(sb, textvariable=self._var_status, foreground="gray").pack(side=tk.LEFT)

        self._var_time = tk.StringVar(value="")
        ttk.Label(sb, textvariable=self._var_time, foreground="gray").pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _browse_image(self) -> None:
        p = filedialog.askopenfilename(
            title="选择C扫图像",
            filetypes=[("图像文件", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif"), ("所有文件", "*.*")],
        )
        if not p:
            return
        self._image_path = p
        self._var_filepath.set(p)
        self._load_preview(p)
        self.notebook.select(0)

    def _load_preview(self, path: str) -> None:
        try:
            pil_img = Image.open(path)
            self._var_img_info.set(f"{pil_img.size[0]}x{pil_img.size[1]}  {pil_img.mode}  {Path(path).suffix}")
            self._canvas_preview.update_idletasks()
            cw = max(self._canvas_preview.winfo_width(), 400)
            ch = max(self._canvas_preview.winfo_height(), 300)
            fitted = _fit_image(pil_img.convert("RGB"), cw - 20, ch - 20)
            self._preview_photo = ImageTk.PhotoImage(fitted)
            self._canvas_preview.delete("all")
            self._canvas_preview.create_image(cw // 2, ch // 2, image=self._preview_photo, anchor=tk.CENTER)
        except Exception as e:
            self._var_img_info.set(f"预览失败: {e}")

    def _browse_output(self) -> None:
        p = filedialog.asksaveasfilename(
            title="保存报告", defaultextension=".docx",
            filetypes=[("Word文档", "*.docx"), ("所有文件", "*.*")],
        )
        if p:
            self._var_output.set(p)

    def _log(self, msg: str) -> None:
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self._log_text.see(tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def _run_analysis(self) -> None:
        if not self._image_path:
            messagebox.showwarning("提示", "请先选择C扫图像")
            return

        self._btn_analyze.configure(state=tk.DISABLED)
        self._var_status.set("分析中...")
        self._progress["value"] = 0
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.delete("1.0", tk.END)
        self._log_text.configure(state=tk.DISABLED)
        self.notebook.select(1)

        def _step_cb(step: str, pct: int) -> None:
            self.root.after(0, lambda: self._var_step.set(step))
            self.root.after(0, lambda: self._progress.configure(value=pct))
            self.root.after(0, lambda: self._log(f"{step}  ({pct}%)"))

        def _worker() -> None:
            t0 = time.time()
            try:
                from src.pipeline import AnalysisPipeline, PipelineConfig
                cfg = PipelineConfig(
                    seg_block_size=self._var_block_size.get() | 1,  # ensure odd
                    seg_c_offset=self._var_c_offset.get(),
                    seg_morph_kernel=self._var_morph_kernel.get() | 1,
                    min_defect_area=self._var_min_area.get(),
                    confidence_threshold=self._var_conf_thresh.get(),
                )
                pipeline = AnalysisPipeline(config=cfg)
                pipeline.set_step_callback(_step_cb)
                result = pipeline.run(self._image_path)
                self._analysis_result = result
                elapsed = time.time() - t0
                self.root.after(0, lambda: self._on_analysis_done(result, elapsed))
            except Exception as e:
                self.root.after(0, lambda: self._on_analysis_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_analysis_done(self, result, elapsed: float) -> None:
        self._btn_analyze.configure(state=tk.NORMAL)
        self._var_status.set(f"分析完成 ({elapsed:.1f}s)")
        self._var_time.set(f"耗时: {elapsed:.1f}s")
        self._log(f"分析完成，耗时 {elapsed:.1f}s，检出 {result.defect_count} 处缺陷")

        # Update results tab
        self._var_verdict.set(result.fusion_result.overall_quality)
        self._var_confidence.set(f"置信度: {result.fusion_result.confidence:.2%}")
        self._var_defect_count.set(str(result.defect_count))
        self._var_defect_ratio.set(f"{result.defect_area_ratio:.2%}")
        self._var_pred_force.set(f"{result.fusion_result.predicted_force:.1f} N/cm")

        # Color verdict
        q = result.fusion_result.overall_quality
        color = {"合格": "green", "不合格": "red", "待复核": "orange"}.get(q, "black")
        self._lbl_verdict.configure(foreground=color)

        # Populate tree
        self._tree.delete(*self._tree.get_children())
        for d in result.defects:
            self._tree.insert("", tk.END, values=(
                d.defect_id, d.defect_type.value, d.severity.value,
                d.area_px, f"({d.centroid[0]:.0f},{d.centroid[1]:.0f})", f"{d.confidence:.0%}",
            ))

        # Rules
        lines = []
        for c in result.fusion_result.rule_checks:
            icon = "PASS" if c.passed else "FAIL"
            lines.append(f"[{icon}] {c.rule_name}: {c.message}")
        self._var_rules.set("\n".join(lines))

        # Update report preview
        self._update_report_preview(result)

        self.notebook.select(2)

    def _on_analysis_error(self, msg: str) -> None:
        self._btn_analyze.configure(state=tk.NORMAL)
        self._var_status.set("分析失败")
        self._log(f"错误: {msg}")
        messagebox.showerror("分析失败", msg)

    def _update_report_preview(self, result) -> None:
        self._report_preview.configure(state=tk.NORMAL)
        self._report_preview.delete("1.0", tk.END)
        lines = [
            f"综合判定: {result.fusion_result.overall_quality}",
            f"置信度: {result.fusion_result.confidence:.2%}",
            f"缺陷数量: {result.defect_count}",
            f"面积占比: {result.defect_area_ratio:.2%}",
            f"预测粘接力: {result.fusion_result.predicted_force:.1f} N/cm",
            "",
            "--- 缺陷列表 ---",
        ]
        for d in result.defects:
            lines.append(f"  #{d.defect_id} {d.defect_type.value} | {d.severity.value} | {d.area_px}px | {d.confidence:.0%}")
        if not result.defects:
            lines.append("  无缺陷检出")
        lines.append("")
        lines.append("--- 规则校核 ---")
        for c in result.fusion_result.rule_checks:
            lines.append(f"  {'PASS' if c.passed else 'FAIL'} {c.rule_name}")
        self._report_preview.insert("1.0", "\n".join(lines))
        self._report_preview.configure(state=tk.DISABLED)

    def _generate_report(self) -> None:
        if self._analysis_result is None:
            messagebox.showwarning("提示", "请先完成分析")
            return

        out = self._var_output.get().strip()
        if not out:
            self._browse_output()
            out = self._var_output.get().strip()
            if not out:
                return

        self._var_status.set("正在生成报告...")
        self.root.update()

        try:
            from src.report_generation.exporter import export_report
            from src.report_generation.data_binder import ReportData

            result = self._analysis_result
            data = ReportData(
                specimen_id=self._var_specimen.get() or "UNKNOWN",
                inspection_date=datetime.now().strftime("%Y-%m-%d"),
                operator=self._var_operator.get() or "系统",
                equipment=self._var_equipment.get() or "PAUT",
                fusion_result=result.fusion_result,
                defect_count=result.defect_count,
                defect_area_ratio=result.defect_area_ratio,
                image_path=self._image_path,
                defects=result.defects,
                analysis_result=result,
                organization=self._var_org.get() or "超声检测实验室",
            )
            warnings = export_report(data, out)
            self._var_status.set("报告生成完成")
            if warnings:
                self._log("报告警告: " + "; ".join(warnings))
            messagebox.showinfo("完成", f"报告已保存至:\n{out}")

            if self._var_open_after.get():
                os.startfile(out)  # Windows
        except Exception as e:
            self._var_status.set("就绪")
            messagebox.showerror("报告生成失败", str(e))

    def _show_about(self) -> None:
        messagebox.showinfo(
            "关于",
            f"超声图像检测与报告生成系统\n"
            f"版本: {VERSION}\n\n"
            f"C扫分析 · 多模态融合 · 自动报告生成\n"
            f"三路融合: 视觉(U-Net) + 声力(RF) + 规则(GB/T 23257)\n\n"
            f"Build: {datetime.now().strftime('%Y-%m-%d')}",
        )

    def run(self) -> None:
        self.root.mainloop()


def run_gui() -> None:
    app = ImageReportApp()
    app.run()


if __name__ == "__main__":
    run_gui()
