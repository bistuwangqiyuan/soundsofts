# Integration Tests & Acceptance Verification

全系统集成测试套件，覆盖性能基准、兼容性、稳定性与安全性测试。

## Test Categories

1. **Performance Benchmark** — Single C-scan analysis < 0.65s, MAPE < 1.30%
2. **Compatibility** — 3 browsers x 3 resolutions x 3 OS
3. **Stability** — 72-hour continuous operation, memory leak detection
4. **Security** — OWASP Top 10, dependency vulnerability scan
5. **End-to-End** — Full pipeline from raw data to report generation

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v --tb=short
python benchmarks/benchmark_inference.py
```
