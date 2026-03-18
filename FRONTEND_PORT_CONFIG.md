# 前端端口配置快速指南

## 📌 问题

用户发现部署文档中只提到了后端端口（8000）的配置，没有前端端口（3000）的配置说明。

## ✅ 解决方案

现在前后端端口都可以通过环境变量灵活配置。

---

## 🔧 配置方法

### 1. 修改根目录 `.env` 文件

```bash
# 复制模板
cp .env.example .env

# 编辑配置
vim .env
```

添加/修改以下配置：

```bash
# ==================== API Server Configuration ====================

# Backend (Python FastAPI)
API_HOST=0.0.0.0
API_PORT=8000          # 后端端口，默认 8000

# Frontend (Next.js)
PORT=3000              # 前端端口，默认 3000

# API Base URL
API_BASE_URL=http://localhost:8000
```

### 2. 修改前端后端地址（如果需要）

```bash
# web-app/.env.local
NEXT_PUBLIC_PYTHON_API_URL=http://localhost:8000
```

### 3. 启动服务

```bash
./start_fullstack.sh
```

启动脚本会自动：
1. 读取 `.env` 文件
2. 将 `PORT` 传递给 Next.js
3. 将 `API_PORT` 传递给 Python 后端

---

## 🌐 云服务器部署

### 默认端口（3000 + 8000）

**`.env`**:
```bash
API_HOST=0.0.0.0
API_PORT=8000
PORT=3000
API_BASE_URL=http://your-server-ip:8000
```

**`web-app/.env.local`**:
```bash
NEXT_PUBLIC_PYTHON_API_URL=http://your-server-ip:8000
```

**安全组配置**：开放 3000 和 8000 端口

**访问**：
- 前端：`http://your-server-ip:3000`
- 后端：`http://your-server-ip:8000/docs`

---

### 自定义端口（例如 9000 + 9001）

**`.env`**:
```bash
API_HOST=0.0.0.0
API_PORT=9000          # 后端自定义端口
PORT=9001              # 前端自定义端口
API_BASE_URL=http://your-server-ip:9000
```

**`web-app/.env.local`**:
```bash
NEXT_PUBLIC_PYTHON_API_URL=http://your-server-ip:9000
```

**`ecosystem.config.js`** (PM2):
```javascript
// 后端
env: {
  API_HOST: '0.0.0.0',
  API_PORT: 9000,
},

// 前端
env: {
  PORT: 9001,
},
```

**安全组配置**：开放 9000 和 9001 端口

**访问**：
- 前端：`http://your-server-ip:9001`
- 后端：`http://your-server-ip:9000/docs`

---

## 📋 完整配置清单

| 配置项 | 文件位置 | 变量名 | 默认值 | 说明 |
|--------|---------|--------|--------|------|
| 后端端口 | `.env` | `API_PORT` | 8000 | Python FastAPI 端口 |
| 前端端口 | `.env` | `PORT` | 3000 | Next.js 端口 |
| 后端地址 | `.env` | `API_BASE_URL` | - | 图表 URL 基础地址 |
| 前端后端地址 | `web-app/.env.local` | `NEXT_PUBLIC_PYTHON_API_URL` | - | 前端调用后端地址 |

---

## 🧪 测试

### 1. 检查配置

```bash
# 查看后端端口配置
cat .env | grep API_PORT

# 查看前端端口配置
cat .env | grep "^PORT"

# 查看前端后端地址
cat web-app/.env.local | grep PYTHON_API_URL
```

### 2. 启动并测试

```bash
# 启动服务
./start_fullstack.sh

# 测试后端（应返回 JSON）
curl http://localhost:8000/api/health

# 测试前端（应返回 HTML）
curl http://localhost:3000

# 查看监听端口
lsof -i:8000  # 后端
lsof -i:3000  # 前端
```

### 3. 浏览器测试

1. 打开 `http://localhost:3000`（前端）
2. 打开浏览器开发者工具（F12）
3. 查看 Network 标签
4. 发送一条消息
5. 确认 API 请求地址为 `http://localhost:8000/api/chat`

---

## ⚠️ 常见问题

### Q1: 前端端口不生效？

**检查**：
```bash
# 1. 确认 .env 中有 PORT 配置
cat .env | grep "^PORT"

# 2. 重启服务
./start_fullstack.sh

# 3. 检查 Next.js 是否使用正确端口
lsof -i:3000
```

### Q2: 端口被占用怎么办？

```bash
# 查看占用进程
lsof -i:3000

# 杀死进程
kill -9 <PID>

# 或修改 .env 使用其他端口
PORT=3001
```

### Q3: 云服务器无法访问？

**检查清单**：
- [ ] 安全组是否开放端口（前端 + 后端）
- [ ] 防火墙是否允许
- [ ] 服务是否正常运行（`pm2 status`）
- [ ] `API_BASE_URL` 配置是否正确（不能用 localhost）

---

## 📖 相关文档

- [端口配置完整指南](./PORT_CONFIGURATION_GUIDE.md) - 所有场景的详细配置
- [云服务器部署指南](./CLOUD_DEPLOYMENT_GUIDE.md) - 完整部署流程
- [PM2 配置示例](./ecosystem.config.js) - 生产环境进程管理

---

## 🎯 关键要点

1. **前端端口**通过根目录 `.env` 的 `PORT` 变量配置（不是 `FRONTEND_PORT`）
2. **后端端口**通过根目录 `.env` 的 `API_PORT` 变量配置
3. **启动脚本**会自动读取 `.env` 并传递给对应服务
4. **PM2 部署**需要在 `ecosystem.config.js` 中配置 `env.PORT`
5. **云服务器**需要同时开放前后端端口

配置完成后，前后端都可以灵活使用任意端口！🚀
