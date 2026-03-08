# Image Report System - 超声图像检测与报告生成系统

C-scan image analysis with multi-modal fusion (U-Net + RF + rules) and automated Word report generation.

## Quick Start

```bash
pip install -r requirements.txt
```

### CLI 报告生成
```bash
python -m src.report_generation.exporter --input image.png --output report.docx
```

### GUI 图形界面
```bash
python run_gui.py
```

### 打包为可执行文件
```bash
pip install pyinstaller
pyinstaller --clean --noconfirm build.spec
# 生成 dist/ImageReportSystem.exe，双击即可运行
```

## API 部署 (Vercel)

1. 连接 Git 仓库到 Vercel，或使用 `vercel deploy`
2. 使用 `requirements-api.txt` 作为轻量依赖（无 torch/opencv）
3. 前端 `public/index.html` 自动部署，API 位于 `/api/*`

### API 端点
- `GET /api/health` - 健康检查
- `POST /api/analyze` - 规则分析 `{force, defect_area, total_area}`
- `POST /api/fuse` - 融合决策 `{predicted_force, defect_ratio, visual_confidence}`
- `GET /api/terminology` - 术语表

### 测试 Vercel 部署 API
```bash
BASE_URL=https://your-app.vercel.app pytest tests/test_vercel_api.py -v
```

## 本地测试

```bash
pytest tests/ -v
# 排除 Vercel 远程测试（需设置 BASE_URL 才运行）
```
