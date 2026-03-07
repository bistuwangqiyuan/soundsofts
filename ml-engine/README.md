# ML Engine - 声力耦合回归模型训练与推理引擎

6 种回归模型（Linear Regression, SVR, Random Forest, XGBoost, LightGBM, 1D-CNN）的统一训练、超参优化、评估、对比与部署。

## Target Metrics
- Random Forest: MAPE <= 1.30%, R² >= 0.9956
- Training time < 1s (RF)

## Quick Start
```bash
pip install -r requirements.txt
python scripts/train_all.py
```
