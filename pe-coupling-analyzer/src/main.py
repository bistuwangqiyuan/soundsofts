"""聚乙烯粘接声力耦合分析系统 V1.0 — 主入口 (CLI + GUI 双模式)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def run_cli(args: argparse.Namespace) -> None:
    """Command-line analysis pipeline."""
    from core.data_loader import load_data
    from core.preprocessor import preprocess_signals
    from core.feature_engine import extract_features
    from core.predictor import predict_force
    from core.reporter import generate_report

    print(f"Loading data from {args.input}...")
    data = load_data(args.input)

    print("Preprocessing signals...")
    processed = preprocess_signals(data)

    print("Extracting features...")
    features = extract_features(processed)

    print("Predicting bonding force...")
    predictions = predict_force(features, model_path=args.model)

    if args.output:
        print(f"Generating report: {args.output}")
        generate_report(data, predictions, output_path=args.output)

    print("Analysis complete.")
    forces = data.get("force", [])
    for i, pred in enumerate(predictions[:5]):
        actual = forces[i] if i < len(forces) else None
        if actual is not None:
            print(f"  Point {i+1}: predicted={pred:.2f} N, actual={actual:.2f} N")
        else:
            print(f"  Point {i+1}: predicted={pred:.2f} N")


def run_gui() -> None:
    """Launch the PySide6 GUI application."""
    from PySide6.QtWidgets import QApplication
    from gui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("聚乙烯粘接声力耦合分析系统 V1.0")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="聚乙烯粘接声力耦合分析系统 V1.0",
        prog="pe-analyzer",
    )
    parser.add_argument("--gui", action="store_true", help="Launch GUI mode")
    parser.add_argument("--input", "-i", type=str, help="Input data file (CSV/HDF5)")
    parser.add_argument("--output", "-o", type=str, help="Output report path (.docx)")
    parser.add_argument("--model", "-m", type=str, default="resources/models/random_forest.onnx",
                        help="ONNX model path")

    args = parser.parse_args()

    if args.gui:
        run_gui()
    elif args.input:
        run_cli(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
