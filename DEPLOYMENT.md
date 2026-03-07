# Vercel 部署指南

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

## 部署后测试

- 健康检查: `GET /api/health`
- API 文档: `/api/docs`
- 登录: `POST /api/auth/login`（需先通过 `/api/auth/register` 注册用户）
