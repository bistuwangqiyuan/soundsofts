# Signal Pipeline - 数据预处理与信号处理流水线

超声信号预处理、特征提取与空间对齐流水线，为声力耦合建模和 U-Net 分割提供数据基础。

## Quick Start

```bash
pip install -r requirements.txt
python -m pytest tests/
```

## Architecture

```
pipeline → preprocessing → feature_extraction → spatial alignment → quality check → output
```

## Performance Target

- Throughput: >= 500 points/sec
