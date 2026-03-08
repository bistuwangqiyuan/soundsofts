# U-Net Segmentation - 超声C扫缺陷语义分割系统

U-Net + ResNet34 encoder for pixel-level defect segmentation of ultrasonic C-scan images.

## Target Metrics
- IoU >= 0.92
- Dice >= 0.96

## 桌面可执行文件（点击即运行 GUI）

- **直接运行（开发环境）**：`python gui_launcher.py` — 启动本地服务并打开浏览器。
- **打包为 exe**：`pip install pyinstaller` 后执行 `python scripts/build_exe.py`，产物在 `dist/`，双击 `U-Net超声C扫分割系统.exe` 即可运行。

## 后端部署（Vercel）

- 将项目连接 Vercel，或使用 `vercel` CLI 部署。
- 前端静态在 `public/`，API 在 `api/index.py`（FastAPI），提供 `/api/health`、`/api/metrics`、`/api/architecture`、`/api/simulate`。
- 依赖使用 `api/requirements.txt`（FastAPI + numpy），以减小 serverless 体积。

## 本地运行后端 + 前端

```bash
python run_local.py
# 或: uvicorn api.index:app --host 127.0.0.1 --port 8000
```
浏览器访问 http://127.0.0.1:8000 。

## Quick Start（训练）

```bash
pip install -r requirements.txt
# 1) 将 C 扫图像放入 data/images，掩码放入 data/masks（同名）
python scripts/prepare_data.py   # 划分 train/val/test
python scripts/train.py         # 训练
```

## Test

```bash
pytest tests/ -v
```

**API 测试（本地）**：先启动服务 `python run_local.py`，再在另一终端执行：
```bash
pytest tests/test_api.py -v
```

**API 测试（Vercel 部署后）**：设置部署地址后运行：
```bash
set API_BASE_URL=https://你的项目.vercel.app
pytest tests/test_api.py -v
```
