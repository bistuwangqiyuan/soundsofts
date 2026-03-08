# 后端 API 说明（Vercel 部署）

部署到 Vercel 后，前端可通过以下接口访问校准与配置功能。所有接口均支持 CORS（`Access-Control-Allow-Origin: *`），可直接被浏览器前端调用。

**Base URL**：`https://<你的项目>.vercel.app`（部署后替换为实际域名）

---

## 1. 获取校准数据

**GET** `/api/calibration`

返回完整的 `Config/calibration_data.json` 内容，包括力传感器、位置编码器、超声探头等校准与元数据。

**响应示例**（200）：

```json
{
  "force_sensor": {
    "model": "S-Type 500N",
    "calibration_points": [
      { "voltage_v": 0, "force_n": 0 },
      { "voltage_v": 5, "force_n": 500 }
    ],
    "zero_offset_mv": 0.5
  },
  "position_encoder": {
    "mm_per_pulse": 0.02
  },
  "ultrasonic_probe": { ... }
}
```

**前端示例**：

```javascript
const res = await fetch('https://<你的项目>.vercel.app/api/calibration');
const calibration = await res.json();
```

---

## 2. 校准换算（电压→力、脉冲→位移）

**POST** `/api/calibration/convert`

根据当前校准数据，将原始电压换算为力（N）、脉冲数换算为位移（mm）。请求体为 JSON。

**请求体**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `voltage_v` | number（可选） | 力传感器电压 (V)，换算为力 (N) |
| `pulses` | number（可选） | 编码器脉冲数，换算为位移 (mm) |
| `apply_zero` | boolean（可选，默认 true） | 是否先减去力传感器零点偏移 |

**响应**（200）：

```json
{
  "force_n": 100.0,
  "position_mm": 2.0
}
```

未提供的输入对应字段在响应中为 `null`。

**前端示例**：

```javascript
const res = await fetch('https://<你的项目>.vercel.app/api/calibration/convert', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ voltage_v: 1.0, pulses: 100 })
});
const { force_n, position_mm } = await res.json();
```

---

## 3. 获取默认参数配置

**GET** `/api/config`

返回 `Config/default_params.ini` 解析后的 JSON（按 section 分组），用于 DAQ、FPGA、超声、力/位置、存储、显示、报警等参数。

**响应示例**（200）：

```json
{
  "DAQ": {
    "device": "USB-6363",
    "sample_rate": "250000",
    "channels": "ai0,ai1,ai2"
  },
  "FPGA": { "trigger_interval_mm": "1.0", ... },
  "Ultrasonic": { ... },
  "Force": { ... },
  "Position": { ... },
  "Storage": { ... },
  "Display": { ... },
  "Alarm": { ... }
}
```

**前端示例**：

```javascript
const res = await fetch('https://<你的项目>.vercel.app/api/config');
const config = await res.json();
const sampleRate = config.DAQ?.sample_rate;
```

---

## 错误与 CORS

- **405**：不支持的 HTTP 方法（仅允许文档中标注的 GET/POST）。
- **500**：服务器内部错误，响应体为 `{ "error": "错误信息" }`。
- 所有响应均带 CORS 头，支持浏览器跨域请求；预检请求 **OPTIONS** 返回 204。
