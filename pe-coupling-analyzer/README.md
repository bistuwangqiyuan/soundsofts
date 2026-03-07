# 聚乙烯粘接声力耦合分析系统 V1.0

独立桌面分析工具，封装核心声力耦合分析算法，支持 CLI 和 GUI 双模式运行。

## Features

- CSV/HDF5 data loading
- Signal preprocessing (bandpass filter, wavelet denoising)
- Feature extraction
- Bonding force prediction via ONNX models
- U-Net defect segmentation
- Word report generation
- Full GUI (PySide6) and CLI interface

## Quick Start

```bash
pip install -r requirements.txt

# GUI mode
python src/main.py --gui

# CLI mode
python src/main.py --input data.csv --output report.docx
```

## 打包为可执行文件

双击即可运行 GUI，无需安装 Python：

```bash
# Windows: 双击 build.bat 或在命令行执行
build.bat

# 或手动执行
pyinstaller --noconfirm --clean pe_analyzer.spec
```

打包完成后，可执行文件位于 `dist/聚乙烯粘接声力耦合分析系统.exe`，双击即可启动。

## Software Copyright

- Registration Number: 2026SR0XXXXXX
- Developer: 北京信息科技大学
- Completion Date: 2026-01
