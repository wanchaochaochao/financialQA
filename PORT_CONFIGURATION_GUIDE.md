# 端口配置指南

本文档说明如何通过环境变量灵活配置前后端端口，适用于本地开发和云服务器部署。

---

## 📝 快速配置

### 方式 1: 使用 .env 文件（推荐）

#### 后端配置

```bash
# 在项目根目录创建 .env 文件
cp .env.example .env
vim .env
```

修改以下配置：

```bash
# API Server Configuration
API_HOST=0.0.0.0      # 0.0.0.0 监听所有网络接口，127.0.0.1 仅本地
API_PORT=8000          # 修改为你想要的端口号

# API Base URL（用于生成图表的 HTTP URL）
API_BASE_URL=http://localhost:8000  # 本地开发
# API_BASE_URL=http://your-server-ip:9000  # 云服务器
```

#### 前端配置

```bash
# 在 web-app 目录创建 .env.local 文件
cd web-app
cp .env.example .env.local
vim .env.local
```

修改 Python 后端地址：

```bash
# Python FastAPI Backend URL
NEXT_PUBLIC_PYTHON_API_URL=http://localhost:8000  # 本地开发
# NEXT_PUBLIC_PYTHON_API_URL=http://your-server-ip:9000  # 云服务器
```

### 方式 2: 使用命令行参数

```bash
# 启动后端时指定端口
./start_api.sh --port=9000 --host=0.0.0.0

# 或使用环境变量
API_HOST=0.0.0.0 API_PORT=9000 ./start_api.sh
```

### 方式 3: 直接设置环境变量

```bash
# 临时设置（当前 shell 会话）
export API_HOST=0.0.0.0
export API_PORT=9000
export API_BASE_URL=http://localhost:9000

# 启动服务
python -m ai_agent.api

# 或启动脚本会自动读取
./start_api.sh
```

---

## 🌐 不同场景的配置示例

### 场景 1: 本地开发（默认端口）

**根目录 .env**:
```bash
# 后端配置
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000

# 前端配置
PORT=3000
```

**前端 web-app/.env.local**:
```bash
NEXT_PUBLIC_PYTHON_API_URL=http://localhost:8000
```

**访问地址**:
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000/docs

---

### 场景 2: 本地开发（自定义端口）

假设你想使用后端 9000 端口、前端 3001 端口（例如默认端口被占用）。

**根目录 .env**:
```bash
# 后端配置
API_HOST=0.0.0.0
API_PORT=9000
API_BASE_URL=http://localhost:9000

# 前端配置
PORT=3001
```

**前端 web-app/.env.local**:
```bash
NEXT_PUBLIC_PYTHON_API_URL=http://localhost:9000
```

**访问地址**:
- 前端: http://localhost:3001
- 后端 API: http://localhost:9000/docs

---

### 场景 3: 云服务器直接访问（无域名）

假设服务器 IP 是 `123.45.67.89`，使用默认端口。

**根目录 .env**:
```bash
# 后端配置
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://123.45.67.89:8000

# 前端配置
PORT=3000
```

**前端 web-app/.env.local**:
```bash
NEXT_PUBLIC_PYTHON_API_URL=http://123.45.67.89:8000
```

**访问地址**:
- 前端: http://123.45.67.89:3000
- 后端 API: http://123.45.67.89:8000/docs

**⚠️ 注意**：需要在云服务器安全组开放 **3000** 和 **8000** 端口。

---

### 场景 4: 云服务器自定义端口

假设使用非标准端口 **9001（后端）** 和 **9002（前端）**。

**根目录 .env**:
```bash
# 后端配置
API_HOST=0.0.0.0
API_PORT=9001
API_BASE_URL=http://123.45.67.89:9001

# 前端配置
PORT=9002
```

**前端 web-app/.env.local**:
```bash
NEXT_PUBLIC_PYTHON_API_URL=http://123.45.67.89:9001
```

**PM2 配置 (ecosystem.config.js)**:
```javascript
// 后端
env: {
  API_HOST: '0.0.0.0',
  API_PORT: 9001,
  API_BASE_URL: 'http://123.45.67.89:9001',
},

// 前端
env: {
  PORT: 9002,
  NEXT_PUBLIC_PYTHON_API_URL: 'http://123.45.67.89:9001',
},
```

**访问地址**:
- 前端: http://123.45.67.89:9002
- 后端 API: http://123.45.67.89:9001/docs

**⚠️ 注意**：需要在云服务器安全组开放 **9001** 和 **9002** 端口。

---

### 场景 5: 云服务器 + Nginx 反向代理（推荐）

使用域名 `api.yourdomain.com`，通过 Nginx 统一 80/443 端口访问。

**根目录 .env**:
```bash
# 后端配置（内部端口，不对外暴露）
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=https://api.yourdomain.com

# 前端配置（内部端口，不对外暴露）
PORT=3000
```

**前端 web-app/.env.local**:
```bash
NEXT_PUBLIC_PYTHON_API_URL=https://api.yourdomain.com
```

**Nginx 配置**:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8000/api/;
    }

    location /charts/ {
        proxy_pass http://localhost:8000/charts/;
    }
}
```

**访问地址**:
- 前端: https://www.yourdomain.com
- 后端 API: https://api.yourdomain.com/docs

**优势**:
- ✅ 统一使用 80/443 端口，无需开放其他端口
- ✅ 支持 HTTPS/SSL
- ✅ 更安全（后端不直接暴露）

---

## 🔧 配置文件位置

| 配置项 | 文件路径 | 说明 |
|--------|---------|------|
| 后端端口 | `/.env` | Python FastAPI 后端配置 |
| 前端后端地址 | `/web-app/.env.local` | Next.js 前端配置 |
| 后端模板 | `/.env.example` | 后端环境变量模板 |
| 前端模板 | `/web-app/.env.example` | 前端环境变量模板 |

---

## 📋 环境变量完整列表

### 后端环境变量（根目录 .env）

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `API_HOST` | `0.0.0.0` | 后端监听地址（0.0.0.0 = 所有接口） |
| `API_PORT` | `8000` | **后端端口号**（Python FastAPI） |
| `API_BASE_URL` | `http://localhost:8000` | 用于生成图表 URL 的基础地址 |
| `PORT` | `3000` | **前端端口号**（Next.js） |
| `OPENAI_API_KEY` | - | OpenAI API 密钥 |
| `AGENT_MAX_ITERATIONS` | `15` | Agent 最大迭代次数 |
| `AGENT_MAX_EXECUTION_TIME` | `60` | Agent 最大执行时间（秒） |
| `TUZI_API_KEY` | - | AI 图像生成 API 密钥（可选） |

### 前端环境变量（web-app/.env.local）

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `NEXT_PUBLIC_PYTHON_API_URL` | `http://localhost:8000` | Python 后端地址 |

**注意**：
- **前端端口**通过根目录 `.env` 的 `PORT` 变量配置
- Next.js 会自动读取 `PORT` 环境变量
- 启动脚本会将 `PORT` 传递给 Next.js

---

---

## 🔍 前端端口配置详解

### Next.js 端口配置方式

Next.js 使用 `PORT` 环境变量来指定端口，有以下几种配置方式：

#### 方式 1: 通过根目录 .env 文件（推荐）

```bash
# /Users/wanchao/financialQA/.env
PORT=3000
```

启动脚本会自动读取并传递给 Next.js：
```bash
./start_fullstack.sh  # 会使用 .env 中的 PORT
```

#### 方式 2: 直接设置环境变量

```bash
PORT=3001 npm run dev
# 或
export PORT=3001
npm run dev
```

#### 方式 3: 通过 PM2 配置

```javascript
// ecosystem.config.js
env: {
  PORT: 3000,  // Next.js 会读取这个环境变量
}
```

### 前端端口与后端端口的关系

**独立配置**：
- 前端端口（PORT）：用户访问前端页面的端口
- 后端端口（API_PORT）：前端调用后端 API 的端口

**示例**：
```bash
# .env
API_PORT=8000       # 后端在 8000
PORT=3000           # 前端在 3000

# web-app/.env.local
NEXT_PUBLIC_PYTHON_API_URL=http://localhost:8000  # 前端调用后端
```

用户访问：
- 前端页面：http://localhost:3000
- 前端通过 NEXT_PUBLIC_PYTHON_API_URL 调用后端 http://localhost:8000

---

## ⚠️ 重要提示

### 1. 前后端地址必须一致

确保前端的 `NEXT_PUBLIC_PYTHON_API_URL` 与后端的实际访问地址匹配：

```bash
# 后端实际运行在
http://123.45.67.89:9000

# 前端必须配置为
NEXT_PUBLIC_PYTHON_API_URL=http://123.45.67.89:9000
```

### 2. API_BASE_URL 的作用

`API_BASE_URL` 用于生成图表图片的可访问 HTTP URL。

**错误配置**：
```bash
API_BASE_URL=http://localhost:8000  # 云服务器上用 localhost
```
→ 前端无法访问图表图片（localhost 指向浏览器本地）

**正确配置**：
```bash
API_BASE_URL=http://your-server-ip:8000  # 或域名
```

### 3. 修改配置后需重启

```bash
# 本地开发（Ctrl+C 停止后重新运行）
python -m ai_agent.api

# PM2 部署
pm2 restart financial-backend
pm2 restart financial-frontend

# Next.js 需要重新构建
cd web-app
npm run build
pm2 restart financial-frontend
```

### 4. CORS 跨域问题

如果前后端使用不同域名/端口，后端已配置 CORS：

```python
# ai_agent/api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 测试配置

### 测试后端端口

```bash
# 查看后端是否监听正确端口
lsof -i:8000  # 或你配置的端口

# 测试 API 访问
curl http://localhost:8000/api/health

# 或浏览器访问
http://localhost:8000/docs
```

### 测试前端端口

```bash
# 查看前端是否监听正确端口
lsof -i:3000  # 或你配置的端口

# 浏览器访问
http://localhost:3000
```

### 测试前后端连接

1. 打开浏览器开发者工具（F12）
2. 访问前端页面 `http://localhost:3000`
3. 查看 Network 标签，观察 API 请求地址是否正确
4. 请求地址应该是 `NEXT_PUBLIC_PYTHON_API_URL` 配置的地址

### 完整测试流程

```bash
# 1. 检查配置文件
cat .env | grep PORT
cat web-app/.env.local | grep PYTHON_API_URL

# 2. 启动服务
./start_fullstack.sh

# 3. 测试后端
curl http://localhost:8000/api/health
# 应返回: {"status": "healthy"}

# 4. 测试前端
curl http://localhost:3000
# 应返回: HTML 页面

# 5. 查看监听端口
lsof -i:8000  # 后端
lsof -i:3000  # 前端
```

---

## 📚 相关文档

- [云服务器部署指南](./CLOUD_DEPLOYMENT_GUIDE.md) - 完整的云服务器部署流程
- [AI 图像生成指南](./AI_IMAGE_GENERATION_GUIDE.md) - AI 图像生成功能配置
- [快速开始](./README.md) - 项目快速开始指南

---

## 💡 常见问题

**Q: 端口被占用怎么办？**

A: 修改 .env 中的 `API_PORT` 为其他端口（如 9000），然后重启服务。

**Q: 云服务器无法访问怎么办？**

A: 检查：
1. 安全组是否开放端口
2. 防火墙是否允许端口
3. 服务是否正常运行（`pm2 status`）

**Q: 图表图片显示 404？**

A: 检查 `API_BASE_URL` 是否配置为可访问的地址（不能是 localhost）。

---

配置完成后，重启服务即可生效！🚀
