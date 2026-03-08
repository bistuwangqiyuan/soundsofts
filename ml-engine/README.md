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

## 运行方式

### 1. 单元测试
```bash
pytest tests/ -v
```

### 2. 桌面 GUI
```bash
python run_gui.py
```
双击运行后打开图形界面，可选择模型、设置参数并训练。

### 3. 打包为可执行文件
```bash
pip install pyinstaller
pyinstaller build_exe.spec
```
生成 `dist/S2_ML_Engine.exe`，双击即可运行 GUI。

### 4. 本地 API 服务
```bash
python scripts/serve_api.py
```
API 运行于 http://127.0.0.1:8001

### 5. 部署到 Vercel
```bash
vercel deploy --prod
```
部署后前端 `public/index.html` 与 API 一同上线。API 端点：
- `GET /api/health` - 健康检查
- `GET /api/models` - 模型列表
- `POST /api/train` - 训练
- `POST /api/predict` - 预测

> 注意：`vercel dev` 在 Windows 上可能因 AF_UNIX 报错，云端部署不受影响。若 API 返回 401，请在 Vercel 项目设置中关闭 Deployment Protection 以允许公开访问。

## API 测试
```bash
# 使用 TestClient（无需启动服务器）
pytest tests/test_api.py -v

# 测试已部署的 API
set ML_ENGINE_API_URL=https://your-vercel-url.vercel.app
pytest tests/test_api.py -v
```
