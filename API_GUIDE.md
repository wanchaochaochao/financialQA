# FastAPI 后端服务使用指南

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

新增的FastAPI依赖：
- `fastapi` - Web框架
- `uvicorn` - ASGI服务器
- `pydantic` - 数据验证

### 2. 启动服务

#### 方式1: 使用Python脚本（推荐）

```bash
# 开发模式（自动重载）
python start_api.py --dev

# 生产模式
python start_api.py

# 自定义端口
python start_api.py --port 8080

# 多进程（生产环境）
python start_api.py --workers 4
```

#### 方式2: 使用Shell脚本（Linux/Mac）

```bash
# 开发模式
./start_api.sh --dev

# 生产模式
./start_api.sh

# 自定义端口
./start_api.sh --port=8080
```

#### 方式3: 使用批处理脚本（Windows）

```cmd
start_api.bat
```

#### 方式4: 直接使用uvicorn

```bash
# 开发模式
uvicorn ai_agent.api:app --reload --host 0.0.0.0 --port 8000

# 生产模式（多进程）
uvicorn ai_agent.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. 访问服务

启动后访问以下地址：

- **API服务**: http://localhost:8000
- **Swagger文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

---

## 📖 API 端点说明

### 1. 根端点

**GET /**

返回API基本信息和可用端点列表。

**响应示例：**
```json
{
  "name": "Financial Asset QA System API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "endpoints": {
    "chat": "POST /api/chat",
    "health": "GET /api/health",
    "status": "GET /api/status"
  }
}
```

---

### 2. 问答接口（核心功能）

**POST /api/chat**

向AI Agent提问，获取智能回答。

**请求体：**
```json
{
  "question": "阿里巴巴现在的股价是多少？"
}
```

**响应示例：**
```json
{
  "question": "阿里巴巴现在的股价是多少？",
  "answer": "📈 Alibaba Group Holding Limited (BABA)\n  最新价：85.23 USD\n  涨跌幅：+1.2% (+1.01)\n  成交量：15234567\n  总市值：2.3B\n  数据时间：2026-03-14 15:30",
  "timestamp": "2026-03-14T15:30:45.123456",
  "model": "gpt-4.1-mini"
}
```

**cURL示例：**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "阿里巴巴现在的股价是多少？"}'
```

**Python示例：**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"question": "阿里巴巴现在的股价是多少？"}
)

print(response.json()["answer"])
```

**JavaScript示例：**
```javascript
fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: '阿里巴巴现在的股价是多少？'
  })
})
.then(response => response.json())
.then(data => console.log(data.answer));
```

---

### 3. 健康检查

**GET /api/health**

检查服务健康状态。

**响应示例：**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-14T15:30:45.123456",
  "agent_ready": true
}
```

**用途：**
- 负载均衡器健康检查
- 监控系统集成
- 服务可用性检测

---

### 4. 系统状态

**GET /api/status**

获取详细的系统状态信息。

**响应示例：**
```json
{
  "agent_ready": true,
  "model": "gpt-4.1-mini",
  "embedding_model": "text-embedding-ada-002",
  "knowledge_base_docs": 5,
  "config": {
    "chunk_size": 500,
    "chunk_overlap": 100,
    "retrieval_top_k": 3,
    "agent_max_iterations": 5,
    "agent_verbose": true
  }
}
```

---

### 5. 重建知识库

**POST /api/rebuild-kb**

重建向量数据库（管理功能）。

**响应示例：**
```json
{
  "status": "success",
  "message": "知识库重建完成",
  "timestamp": "2026-03-14T15:30:45.123456"
}
```

**注意：** 此操作可能需要较长时间，建议在非高峰期执行。

---

### 6. 模型信息

**GET /api/models**

获取正在使用的模型信息。

**响应示例：**
```json
{
  "llm": {
    "model": "gpt-4.1-mini",
    "temperature": 0,
    "base_url": "https://api.openai-proxy.org/v1"
  },
  "embedding": {
    "model": "text-embedding-ada-002"
  }
}
```

---

### 7. 配置信息

**GET /api/config**

获取系统配置信息（管理端点）。

**响应示例：**
```json
{
  "rag": {
    "chunk_size": 500,
    "chunk_overlap": 100,
    "retrieval_top_k": 3
  },
  "agent": {
    "max_iterations": 5,
    "verbose": true
  },
  "paths": {
    "knowledge_base": "/Users/wanchao/financialQA/knowledge_base",
    "faiss_index": "/Users/wanchao/financialQA/faiss_index"
  }
}
```

---

## 🧪 测试API

### 使用Swagger UI（推荐）

1. 访问 http://localhost:8000/docs
2. 点击端点展开详情
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"

### 使用curl

```bash
# 健康检查
curl http://localhost:8000/api/health

# 提问
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是市盈率？"}'

# 系统状态
curl http://localhost:8000/api/status
```

### 使用Python

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000"

# 健康检查
health = requests.get(f"{BASE_URL}/api/health")
print(health.json())

# 问答
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={"question": "特斯拉最近7天涨跌如何？"}
)
print(response.json()["answer"])

# 系统状态
status = requests.get(f"{BASE_URL}/api/status")
print(status.json())
```

---

## 🔧 配置和优化

### 环境变量

可以通过 `.env` 文件配置：

```bash
# OpenAI API
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# LLM
LLM_MODEL=gpt-4.1-mini
LLM_TEMPERATURE=0

# Agent
AGENT_MAX_ITERATIONS=5
AGENT_VERBOSE=true
```

### 生产环境部署

#### 使用多进程

```bash
# 4个worker进程
uvicorn ai_agent.api:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 使用Gunicorn + Uvicorn

```bash
pip install gunicorn

gunicorn ai_agent.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

#### 使用Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "ai_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 反向代理（Nginx）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🎯 使用场景示例

### 场景1: 股价查询

**请求：**
```json
{
  "question": "阿里巴巴当前股价是多少？"
}
```

**Agent行为：**
1. 识别为市场数据查询
2. 调用 `get_stock_price_tool`
3. 返回实时股价信息

---

### 场景2: 涨跌分析

**请求：**
```json
{
  "question": "BABA最近7天涨跌情况如何？"
}
```

**Agent行为：**
1. 识别为历史数据查询
2. 调用 `get_stock_history_tool`
3. 计算并返回涨跌分析

---

### 场景3: 金融知识

**请求：**
```json
{
  "question": "什么是市盈率？"
}
```

**Agent行为：**
1. 识别为知识库查询
2. 调用 `knowledge_base_qa`
3. 从向量数据库检索相关文档
4. 返回专业解释

---

### 场景4: 综合查询

**请求：**
```json
{
  "question": "贵州茅台最近30天走势如何？公司基金有持仓吗？"
}
```

**Agent行为：**
1. 识别为综合查询
2. 调用 `get_stock_history_tool` 获取涨跌数据
3. 调用 `knowledge_base_qa` 查询持仓信息
4. 综合两个工具的结果返回答案

---

## 📊 性能优化

### 1. Agent预加载

服务启动时就初始化Agent，避免首次请求慢：
- ✅ 已实现（使用lifespan事件）

### 2. 向量库缓存

向量数据库持久化到磁盘，重启服务快速加载：
- ✅ 已实现（FAISS持久化）

### 3. 响应缓存

对于相同问题，可以缓存结果：
```python
# 可以添加Redis缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_answer(question: str) -> str:
    return agent.chat(question)
```

---

## 🔒 安全建议

### 1. API Key保护

- 不要将API Key提交到代码仓库
- 使用环境变量或密钥管理服务

### 2. CORS配置

生产环境限制允许的源：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],  # 指定域名
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. 速率限制

添加请求速率限制：
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_req: ChatRequest):
    ...
```

---

## 🐛 故障排查

### 问题1: 服务启动失败

**症状：** `ModuleNotFoundError: No module named 'fastapi'`

**解决：**
```bash
pip install -r requirements.txt
```

---

### 问题2: Agent初始化失败

**症状：** `Agent not initialized`

**解决：**
- 检查OpenAI API Key是否配置
- 查看服务启动日志
- 确保知识库文件存在

---

### 问题3: 响应很慢

**可能原因：**
1. 首次请求需要初始化（正常）
2. LLM响应慢（OpenAI API延迟）
3. 网络问题（访问Yahoo Finance慢）

**优化：**
- 使用多进程部署
- 添加响应缓存
- 使用更快的LLM模型

---

## 📚 更多资源

- **Swagger文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **FastAPI官方文档**: https://fastapi.tiangolo.com
- **项目README**: [README.md](README.md)

---

**API版本**: 1.0.0
**最后更新**: 2026-03-14
