# Vercel 部署指南

## Platform 部署 (platform 目录)

1. 在 Vercel 中导入仓库，**根目录** 设置为 `platform`（或部署时在 `platform` 下执行 `vercel`）。
2. 构建与 API 由 `vercel.json` 配置：前端构建输出 `frontend/dist`，`/api/*` 转发到 `api/index.py`（FastAPI）。
3. 若构建阶段 Python 依赖安装失败（如 numpy/asyncpg 在 Python 3.14 下编译失败），可在 Vercel 项目 **Settings → General** 中检查是否可指定 **Python 版本**（如 3.12）；或使用仅含 SQLite 的轻量依赖（当前 `platform/requirements.txt` 未包含 asyncpg，部署后使用 SQLite，或设置 `DATABASE_URL` 为 Neon 并自行在本地构建后部署）。

## 环境变量配置

在 Vercel 项目设置中配置以下环境变量：

### 必需

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DATABASE_URL` | Neon 数据库连接字符串 | `postgresql://user:pass@host.neon.tech/dbname?sslmode=require` |
| `JWT_SECRET` | JWT 签名密钥（生产环境必须修改） | 随机长字符串 |

### 可选

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `CORS_ORIGINS` | 允许的跨域来源，逗号分隔 | 自动包含 Vercel 部署 URL |
| `JWT_EXPIRE_MINUTES` | Token 过期时间（分钟） | 120 |

## Neon 数据库设置

1. 访问 [Neon Console](https://console.neon.tech/) 创建项目
2. 复制连接字符串，确保包含 `?sslmode=require`
3. 在 Vercel 项目 Settings → Environment Variables 中添加 `DATABASE_URL`
4. 首次部署后，数据库表会自动创建（users, audit_logs）

**说明**：若未安装 asyncpg（当前 Vercel 用 requirements 未包含），后端在 Vercel 环境下会使用 SQLite（`/tmp/soundsofts.sqlite`）。要使用 Neon PostgreSQL，需在能安装 asyncpg 的环境（如 Python 3.12）下构建，或在 Vercel 中配置 Python 3.12 后加入 `asyncpg` 到 `platform/requirements.txt`。

## 部署后测试

- 健康检查: `GET /api/health`
- API 文档: `/api/docs`
- 登录: `POST /api/auth/login`（需先通过 `/api/auth/register` 注册用户）
