# 腐蚀与应力在线监测平台 V2.0

聚乙烯补口粘接质量智能无损检测与评估 B/S 架构在线平台。

## Architecture

- **Frontend**: React 18 + TypeScript + Ant Design + ECharts + Vite
- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15 + Redis 7.2
- **Model Serving**: ONNX Runtime + TorchServe
- **Deployment**: Docker + Docker Compose + Nginx

## Quick Start

```bash
cp .env.example .env
# Edit .env with your passwords
docker compose up -d
```

Access at http://localhost:8080

## Performance Targets

- Single C-scan analysis: <= 0.65s (contract < 10s)
- Prediction MAPE: <= 1.30% (contract < 10%)
- API response P99: <= 200ms

## 8 Core Modules

1. Data Visualization (waveform / spectrum / force curves)
2. Acoustic-Force Data Cards
3. Preprocessing Preview
4. Model Training & Comparison
5. Inference Monitoring
6. Coupling View
7. Defect Analysis & Report Generation
8. RBAC & Audit Logging
