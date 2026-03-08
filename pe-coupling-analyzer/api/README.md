# 聚乙烯粘接声力耦合分析系统 — 后端 API

部署在 Vercel 上的 Serverless 后端，为前端提供分析接口。

## 基础 URL

- 本地：`http://localhost:3000`（`vercel dev`）
- 生产：`https://<your-project>.vercel.app`

## 端点一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api` | API 说明与端点列表 |
| GET | `/api/health` | 健康检查 |
| POST | `/api/analyze` | 波形 → 预处理 → 特征 → 预测 |
| POST | `/api/report` | 根据预测值生成报告摘要 |
| POST | `/api/features` | 仅提取特征 |
| POST | `/api/predict` | 仅预测（传入特征矩阵） |
| GET | `/api/docs` | Swagger UI（若 FastAPI 挂载） |

## 请求/响应示例

### 1. 健康检查

```http
GET /api/health
```

```json
{ "status": "healthy", "service": "pe-coupling-analyzer", "version": "1.0.0" }
```

### 2. 全流程分析 `POST /api/analyze`

请求体：

```json
{
  "waveforms": [
    [0.1, -0.2, 0.15, ...],
    [0.05, 0.1, -0.1, ...]
  ]
}
```

响应：

```json
{
  "processed_count": 2,
  "features_shape": [2, 6],
  "predictions": [72.5, 68.3],
  "mean_force": 70.4
}
```

### 3. 报告摘要 `POST /api/report`

请求体：

```json
{
  "specimen_id": "PE-001",
  "predictions": [72.5, 68.3, 75.0, 71.2, 69.8]
}
```

响应：

```json
{
  "specimen_id": "PE-001",
  "prediction_count": 5,
  "mean_force": 71.36,
  "min_force": 68.3,
  "max_force": 75.0,
  "std_force": 2.41,
  "quality": "合格",
  "summary": "试样 PE-001 共 5 个检测点，预测粘接力均值 71.4 N/cm，判定结果：合格。"
}
```

### 4. 仅特征提取 `POST /api/features`

请求体同 `/api/analyze` 的 `waveforms`。响应包含 `features` 二维数组及 `features_shape`。

### 5. 仅预测 `POST /api/predict`

请求体：

```json
{
  "features": [
    [1.2, 0.8, 100, 0.5, 5e6, ...],
    [1.1, 0.7, 95, 0.48, 4.9e6, ...]
  ]
}
```

响应包含 `predictions`、`mean_force`、`count`。

## 前端调用示例

```javascript
// 1. 分析波形
const resAnalyze = await fetch('/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ waveforms: [[0.1, -0.2, ...], ...] }),
});
const { predictions, mean_force } = await resAnalyze.json();

// 2. 生成报告摘要
const resReport = await fetch('/api/report', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ specimen_id: 'PE-001', predictions }),
});
const { quality, summary, mean_force: mean } = await resReport.json();
```

## 部署

- 将本仓库与 Vercel 关联，或使用 `vercel` CLI 部署。
- 根目录需有 `requirements.txt`（含 `fastapi`、`numpy`、`scipy` 等）。
- 静态页面放在 `public/`，会作为站点根路径；`/api/*` 由 `api/index.py` 的 FastAPI `app` 处理。

## 注意事项

- 服务端无 ONNX 模型文件时，预测使用内置线性 fallback，结果仅作演示。
- 请求体过大（如波形很长、条数很多）可能触发 Vercel 请求体或超时限制，可适当限制前端单次请求的波形数量与长度。
