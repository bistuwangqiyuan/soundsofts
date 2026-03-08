"""S2 声力耦合回归模型 — 桌面 GUI 应用。"""

from __future__ import annotations

import sys
import threading
import webbrowser
from pathlib import Path

# 确保 src 在路径中（支持 PyInstaller 打包）
if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).resolve().parent
else:
    ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import numpy as np

# 延迟导入 ML 模块，避免启动时加载过重
def _get_models():
    from src.models import ALL_MODELS
    return ALL_MODELS


class MLEngineGUI:
    """主窗口：模型选择、训练、推理、结果展示。"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("S2 声力耦合回归模型训练与推理引擎")
        self.root.geometry("720x580")
        self.root.minsize(560, 420)

        self.model = None
        self.X_train = None
        self.y_train = None
        self._build_ui()

    def _build_ui(self):
        # 顶部标题
        header = ttk.Frame(self.root, padding=(12, 8))
        header.pack(fill=tk.X)
        ttk.Label(header, text="S2 声力耦合回归模型", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
        ttk.Label(header, text="6 种回归模型 · Random Forest MAPE=1.30%", foreground="gray").pack(side=tk.LEFT, padx=(12, 0))

        # 主内容
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # 模型选择
        model_frame = ttk.LabelFrame(main, text="模型选择", padding=8)
        model_frame.pack(fill=tk.X, pady=(0, 8))
        self.model_var = tk.StringVar(value="random_forest")
        models = [
            ("random_forest", "随机森林"),
            ("xgboost", "XGBoost"),
            ("lightgbm", "LightGBM"),
            ("svr", "SVR"),
            ("linear_regression", "线性回归"),
            ("cnn_1d", "1D-CNN"),
        ]
        for val, label in models:
            ttk.Radiobutton(model_frame, text=label, variable=self.model_var, value=val).pack(side=tk.LEFT, padx=(0, 16))

        # 训练参数
        train_frame = ttk.LabelFrame(main, text="训练参数（合成数据）", padding=8)
        train_frame.pack(fill=tk.X, pady=(0, 8))
        params = ttk.Frame(train_frame)
        params.pack(fill=tk.X)
        ttk.Label(params, text="样本数:").pack(side=tk.LEFT, padx=(0, 4))
        self.n_samples = ttk.Spinbox(params, from_=50, to=2000, width=8)
        self.n_samples.insert(0, "500")
        self.n_samples.pack(side=tk.LEFT, padx=(0, 16))
        ttk.Label(params, text="特征数:").pack(side=tk.LEFT, padx=(0, 4))
        self.n_features = ttk.Spinbox(params, from_=2, to=20, width=6)
        self.n_features.insert(0, "5")
        self.n_features.pack(side=tk.LEFT, padx=(0, 16))
        ttk.Label(params, text="噪声:").pack(side=tk.LEFT, padx=(0, 4))
        self.noise = ttk.Spinbox(params, from_=0, to=100, increment=5, width=6)
        self.noise.insert(0, "0.1")
        self.noise.pack(side=tk.LEFT, padx=(0, 16))
        self.train_btn = ttk.Button(params, text="开始训练", command=self._on_train)
        self.train_btn.pack(side=tk.LEFT, padx=(16, 0))

        # 指标
        metrics_frame = ttk.LabelFrame(main, text="评估指标", padding=8)
        metrics_frame.pack(fill=tk.X, pady=(0, 8))
        self.metrics_text = tk.StringVar(value="训练后显示 MAE / RMSE / R² / MAPE")
        ttk.Label(metrics_frame, textvariable=self.metrics_text, font=("Consolas", 10)).pack(anchor=tk.W)

        # 日志
        log_frame = ttk.LabelFrame(main, text="运行日志", padding=8)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.log = scrolledtext.ScrolledText(log_frame, height=10, font=("Consolas", 9), state=tk.DISABLED)
        self.log.pack(fill=tk.BOTH, expand=True)

        # 底部按钮
        footer = ttk.Frame(main)
        footer.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(footer, text="打开 Web 演示", command=self._open_web).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(footer, text="清空日志", command=self._clear_log).pack(side=tk.LEFT)

    def _log(self, msg: str):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log.config(state=tk.NORMAL)
        self.log.delete(1.0, tk.END)
        self.log.config(state=tk.DISABLED)

    def _open_web(self):
        index_path = ROOT / "public" / "index.html"
        if index_path.exists():
            webbrowser.open(f"file://{index_path}")
        else:
            self._log("未找到 public/index.html，请先部署或从项目根目录运行。")

    def _on_train(self):
        self.train_btn.config(state=tk.DISABLED)
        self._log("训练中…")

        def run():
            try:
                n_samples = int(self.n_samples.get())
                n_features = int(self.n_features.get())
                noise = float(self.noise.get())
                model_type = self.model_var.get()

                np.random.seed(42)
                X = np.random.randn(n_samples, n_features).astype(np.float32)
                y = (2.0 * X[:, 0] + 0.5 * X[:, 1] - X[:, 2] + 80 + np.random.randn(n_samples) * noise * 5).astype(np.float32)
                split = int(0.8 * n_samples)
                X_train, X_test = X[:split], X[split:]
                y_train, y_test = y[:split], y[split:]

                models = _get_models()
                model_cls = models.get(model_type)
                if model_cls is None:
                    raise ValueError(f"未知模型: {model_type}")
                model = model_cls()
                model.train(X_train, y_train)
                preds = model.predict(X_test)

                from src.utils.metrics import compute_metrics
                m = compute_metrics(y_test, preds)
                self.model = model
                self.X_train, self.y_train = X_train, y_train

                def update():
                    self.metrics_text.set(
                        f"MAE={m['MAE']:.4f}  RMSE={m['RMSE']:.4f}  R²={m['R2']:.4f}  MAPE={m['MAPE']:.2f}%"
                    )
                    self._log(f"训练完成: {model_type} — MAPE={m['MAPE']:.2f}%, R²={m['R2']:.4f}")
                    self.train_btn.config(state=tk.NORMAL)

                self.root.after(0, update)
            except Exception as e:
                def err():
                    self._log(f"错误: {e}")
                    self.train_btn.config(state=tk.NORMAL)
                    messagebox.showerror("训练失败", str(e))
                self.root.after(0, err)

        threading.Thread(target=run, daemon=True).start()

    def run(self):
        self.root.mainloop()


def main():
    app = MLEngineGUI()
    app.run()


if __name__ == "__main__":
    main()
