# Signal Pipeline - 数据预处理与信号处理流水线

超声信号预处理、特征提取与空间对齐流水线，为声力耦合建模和 U-Net 分割提供数据基础。

## Quick Start

```bash
pip install -r requirements.txt
python -m pytest tests/
```

## 运行 GUI

```bash
python run_gui.py
```

启动后自动打开浏览器，显示信号预处理与特征提取界面。

## 打包为可执行文件

双击运行，无需安装 Python：

```bash
build_exe.bat
```

生成的可执行文件位于 `dist/信号处理流水线.exe`，双击即可启动 GUI。

## 部署到 Vercel（后端 API）

将本项目部署到 Vercel 后，可作为后端服务为前端提供 API：

1. 在 [Vercel](https://vercel.com) 导入本仓库（或包含本目录的 monorepo，并设置 Root Directory 为 `signal-pipeline`）。
2. 保持默认：`installCommand` 会执行 `pip install -r requirements.txt`，静态资源来自 `public/`，`/api/*` 转发到 Python 函数。
3. 部署完成后，API 基地址为：`https://<项目名>.vercel.app/api`。

前端可调用接口示例：

- **GET** `/api/health` — 健康检查
- **POST** `/api/preprocess` — 信号预处理
- **POST** `/api/features` — 特征提取
- **POST** `/api/envelope` — 包络提取

详细请求/响应格式与示例见 [API.md](API.md)。交互式文档：`/api/docs`、`/api/redoc`。

## Architecture

```
pipeline → preprocessing → feature_extraction → spatial alignment → quality check → output
```

## Performance Target

- Throughput: >= 500 points/sec
