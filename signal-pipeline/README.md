# Signal Pipeline - 数据预处理与信号处理流水线

超声信号预处理、特征提取与空间对齐流水线，为声力耦合建模和 U-Net 分割提供数据基础。

## Quick Start

```bash
pip install -r requirements.txt
python -m pytest tests/
```

## 运行 GUI

```bash
python run_gui.py
```

启动后自动打开浏览器，显示信号预处理与特征提取界面。

## 打包为可执行文件

双击运行，无需安装 Python：

```bash
build_exe.bat
```

生成的可执行文件位于 `dist/信号处理流水线.exe`，双击即可启动 GUI。

## Architecture

```
pipeline → preprocessing → feature_extraction → spatial alignment → quality check → output
```

## Performance Target

- Throughput: >= 500 points/sec
