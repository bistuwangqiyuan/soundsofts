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

The `python_interface/` directory provides Python scripts for:
- Reading acquisition data (HDF5/CSV)
- Real-time data streaming via TCP
- Calibration data management
