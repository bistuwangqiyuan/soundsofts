# pyhton 的b/s架构 上位机采集控制软件

基于 pyhton 的b/s架构 的工控采集软件，控制 FPGA 硬件触发，实现超声-位置-力三类数据的毫秒级同步采集。

## Hardware Requirements

- NI USB-6363 DAQ (16-bit, 250 kS/s)
- Xilinx Artix-7 FPGA trigger board
- PAUT ultrasonic instrument (2-10 MHz, >= 40 MHz sampling)
- S-type load cell (1000 Hz)
- Incremental optical encoder

## Key Specifications

| Metric | Requirement |
|--------|-------------|
| Sync trigger accuracy | <= 1 ms |
| Spatial trigger interval | 1 mm |
| DAQ precision | 16-bit, 250 kS/s |
| Force sampling rate | 1000 Hz |
| Ultrasonic sampling | >= 40 MHz |
| Continuous stability | >= 8 hours |

## Software Architecture

```
Main.vi
├── FPGA_Trigger.vi      — FPGA trigger control
├── DAQ_Config.vi         — DAQ configuration
├── Ultrasonic_Interface.vi — PAUT communication
├── Force_Acquisition.vi   — Load cell acquisition
├── Position_Tracking.vi   — Encoder position tracking
├── RealTime_Display.vi    — Real-time waveform display
├── Parameter_Panel.vi     — Parameter settings
├── Data_Storage.vi        — HDF5/CSV data storage
├── Alarm_Handler.vi       — Exception alarm handling
├── Sync_Monitor.vi        — Synchronization monitoring
└── Calibration.vi         — Sensor calibration
```

## Python Interface

The `python_interface/` directory provides Python modules for:
- **data_reader**: Reading acquisition data (HDF5 produced by Data_Storage.vi)
- **tcp_stream**: Real-time data streaming via TCP
- **calibration_manager**: Calibration data management

## 运行方式

### 方式一：直接运行 Python GUI（开发/调试）

```bash
pip install -r requirements.txt
python main.py
```

启动后出现图形界面，可：打开 HDF5 数据文件、打开技术文档、查看校准信息、连接 TCP 实时流。

### 方式二：打包为可执行文件（点击即运行）

```bash
# Windows: 双击或在命令行执行
build_exe.bat
```

或手动执行：

```bash
pip install pyinstaller
pyinstaller -y build_exe.spec
```

打包完成后，可执行文件位于 `dist/LabVIEW_B_S_Acquisition.exe`，双击即可运行软件 GUI（无需安装 Python）。

## 测试

```bash
pip install -r requirements.txt
python -m pytest tests -v
```

## Vercel 部署（后端 API）

将本项目部署到 Vercel 后，可提供 REST API 供前端调用：

- **GET /api/calibration** — 获取完整校准数据（JSON）
- **POST /api/calibration/convert** — 电压/脉冲换算为力(N)、位移(mm)，请求体 `{ voltage_v?, pulses?, apply_zero? }`
- **GET /api/config** — 获取默认参数配置（INI 解析为 JSON）

部署步骤：

1. 在 [Vercel](https://vercel.com) 导入本仓库（或执行 `vercel` 关联项目）。
2. 保持根目录 `vercel.json`、`api/`、`Config/`、`package.json`；构建输出为 `public`，API 自动识别 `api/` 下 Node 函数。
3. 部署完成后，前端使用 `https://<项目>.vercel.app/api/...` 调用上述接口。所有接口已设置 CORS，支持浏览器跨域。

详细请求/响应格式与前端示例见 **Documentation/api.md**。

**API 测试**（本地验证，与 Vercel 行为一致）：

```bash
npm install
npm run test:api
```

共 14 个用例：校准 GET/OPTIONS/405、换算 POST（电压/脉冲、空 body、仅电压、仅脉冲）、配置 GET/OPTIONS/405 及 CORS 头。
