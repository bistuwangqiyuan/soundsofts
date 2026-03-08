# S4 信号处理流水线 API 文档

部署到 Vercel 后，后端 API 基地址为：`https://<你的项目>.vercel.app/api`。

## 基地址

| 环境     | 基地址 |
|----------|--------|
| 生产     | `https://<project>.vercel.app/api` |
| 本地开发 | `http://localhost:3000/api`（`vercel dev` 时） |

## 接口列表

### 1. 健康检查

**GET** `/api/health`

用于部署验证与监控探活。

**响应示例：**
```json
{
  "status": "healthy",
  "service": "S4-signal-pipeline",
  "version": "1.0.0"
}
```

---

### 2. 信号预处理

**POST** `/api/preprocess`

对一维超声波形做 DC 去除、带通滤波、小波去噪、中值滤波、基线校正、归一化等可选步骤。

**请求体：**
```json
{
  "signal": [0.1, -0.2, 0.15, ...],
  "sampling_rate": 40000000,
  "steps": ["dc_removal", "bandpass", "normalize"]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| signal | float[] | 是 | 一维波形采样点 |
| sampling_rate | number | 否 | 采样率 (Hz)，默认 40e6 |
| steps | string[] | 否 | 步骤列表，默认 `["dc_removal","bandpass","normalize"]` |

**可选步骤：** `dc_removal`、`bandpass`、`wavelet`、`median`、`baseline`、`normalize`。

**响应示例：**
```json
{
  "processed": [-0.01, 0.02, ...],
  "length": 500
}
```

---

### 3. 特征提取

**POST** `/api/features`

从波形中提取时域与频域特征（Vpp、RMS、过零率、中心频率、带宽、谱熵等）。

**请求体：**
```json
{
  "signal": [0.1, -0.2, 0.15, ...],
  "sampling_rate": 40000000
}
```

**响应示例：**
```json
{
  "features": {
    "vpp": 1.2,
    "rms": 0.35,
    "zero_crossing_rate": 0.02,
    "center_frequency": 5000000,
    "bandwidth": 1200000,
    "spectral_entropy": 0.45,
    ...
  }
}
```

---

### 4. 包络提取

**POST** `/api/envelope`

使用 Hilbert 变换提取信号包络。

**请求体：** 同 `/api/features`。

**响应示例：**
```json
{
  "envelope": [0.1, 0.15, 0.2, ...]
}
```

---

## 前端调用示例

### fetch

```javascript
const base = 'https://<project>.vercel.app/api';

// 健康检查
const health = await fetch(`${base}/health`).then(r => r.json());

// 预处理
const preprocess = await fetch(`${base}/preprocess`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    signal: waveformArray,
    sampling_rate: 40e6,
    steps: ['dc_removal', 'bandpass', 'normalize'],
  }),
}).then(r => r.json());

// 特征提取
const features = await fetch(`${base}/features`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ signal: waveformArray, sampling_rate: 40e6 }),
}).then(r => r.json());
```

### axios

```javascript
import axios from 'axios';

const api = axios.create({ baseURL: 'https://<project>.vercel.app/api' });

const { data } = await api.post('/preprocess', {
  signal: waveform,
  sampling_rate: 40e6,
  steps: ['dc_removal', 'bandpass', 'normalize'],
});
```

---

## 交互式文档

部署后可用：

- **Swagger UI:** `https://<project>.vercel.app/api/docs`
- **ReDoc:** `https://<project>.vercel.app/api/redoc`
- **OpenAPI JSON:** `https://<project>.vercel.app/api/openapi.json`

---

## CORS

接口已配置 `Access-Control-Allow-Origin: *`，任意前端域名均可直接调用。若需限制来源，可在 Vercel 项目或 API 中修改 CORS 配置。
