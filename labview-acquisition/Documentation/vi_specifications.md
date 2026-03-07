# LabVIEW VI Specifications

## Main.vi
- **Purpose**: Main application entry point with state machine architecture
- **Front Panel**: Start/Stop buttons, status indicators, tabbed display
- **States**: Init → Configure → Acquire → Process → Save → Idle

## SubVIs

### FPGA_Trigger.vi
- Interfaces with Xilinx Artix-7 FPGA via NI RIO
- Reads encoder pulses and generates trigger every 1mm displacement
- Sync error monitoring with <= 1ms accuracy
- Inputs: FPGA reference, trigger interval, enable
- Outputs: trigger pulse, sync status, error count

### DAQ_Config.vi
- Configures NI USB-6363 DAQ channels
- AI0: Force sensor (differential, ±10V)
- AI1: Auxiliary analog input
- Counter: Encoder pulse counting
- Sample rate: 250 kS/s, 16-bit resolution

### Ultrasonic_Interface.vi
- TCP/IP communication with PAUT instrument
- Commands: SetGain, SetGate, StartAcquisition, ReadAScan
- Receives raw A-scan data (40 MHz sampling)
- Supports 2-10 MHz frequency range

### Force_Acquisition.vi
- Continuous force measurement at 1000 Hz
- Real-time calibration voltage → force conversion
- Configurable moving average filter
- Auto-zero on startup

### Position_Tracking.vi
- Reads incremental encoder via counter input
- Resolution: 0.01 mm per pulse (configurable)
- Direction detection via quadrature signals
- Absolute position tracking with home reference

### RealTime_Display.vi
- Waveform chart: A-scan display (2000 points)
- Force chart: Rolling 60-second history
- Position indicator: Current displacement
- Update rate: 30 Hz

### Data_Storage.vi
- HDF5 output with hierarchical structure
- Metadata attributes per acquisition run
- Auto-flush every 5 seconds
- CSV backup option for compatibility

### Alarm_Handler.vi
- Force out-of-range detection (0-450 N)
- Sync error threshold (> 5 ms)
- Temperature monitoring (< 50°C)
- Visual and audio alerts

### Sync_Monitor.vi
- Displays FPGA trigger timing vs actual acquisition
- Calculates and logs sync error per point
- Rolling statistics: mean, max, std of sync error
- Alert when sync error exceeds threshold

### Calibration.vi
- Multi-point force sensor calibration
- Encoder resolution verification
- Ultrasonic probe characterization
- Results saved to calibration_data.json
