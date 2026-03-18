# FastAPI 后端服务 - 快速开始

## 🚀 3分钟上手

### 1. 安装FastAPI依赖 (30秒)

```bash
pip install fastapi uvicorn
```

或安装完整依赖：
```bash
pip install -r requirements.txt
```

### 2. 启动服务 (10秒)

```bash
python start_api.py --dev
```

看到这个输出表示成功：
```
✅ Dependencies OK
🚀 Starting API server...
📖 API Documentation: http://localhost:8000/docs
```

### 3. 测试API (1分钟)

#### 方式1: 浏览器访问Swagger UI（推荐）

打开浏览器访问：http://localhost:8000/docs

点击端点 → "Try it out" → 填入问题 → "Execute"

#### 方式2: 使用curl

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "阿里巴巴现在的股价是多少？"}'
```

#### 方式3: 运行测试脚本

```bash
python test_api.py
```

---

## 📖 核心端点

### 1. 问答接口（最重要）

```bash
POST /api/chat
```

**请求：**
```json
{
  "question": "你的问题"
}
```

**示例问题：**
- "阿里巴巴现在的股价是多少？"
- "特斯拉最近7天涨跌如何？"
- "什么是市盈率？"

### 2. 健康检查

```bash
GET /api/health
```

### 3. 系统状态

```bash
GET /api/status
```

---

## 🛠️ 启动选项

### 开发模式（自动重载）

```bash
python start_api.py --dev
```

### 生产模式

```bash
python start_api.py
```

### 自定义端口

```bash
python start_api.py --port 8080
```

### 多进程（生产环境）

```bash
python start_api.py --workers 4
```

---

## 🔗 访问地址

- **API服务**: http://localhost:8000
- **Swagger文档**: http://localhost:8000/docs ⭐
- **ReDoc文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/health

---

## 💻 代码示例

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"question": "阿里巴巴现在的股价是多少？"}
)

print(response.json()["answer"])
```

### JavaScript

```javascript
fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({question: '阿里巴巴现在的股价是多少？'})
})
.then(r => r.json())
.then(data => console.log(data.answer));
```

### curl

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "阿里巴巴现在的股价是多少？"}'
```

---

## ⚡ 性能优化

### Agent预加载 ✅
服务启动时自动初始化Agent，避免首次请求慢。

### 向量库缓存 ✅
向量数据库持久化，重启快速加载。

### 并发处理
```bash
# 使用多进程
python start_api.py --workers 4
```

---

## 🐛 常见问题

### Q: 服务启动失败？

**检查依赖：**
```bash
pip install -r requirements.txt
```

### Q: 首次请求很慢？

**正常现象！** Agent初始化需要时间。第二次请求会快很多。

### Q: 如何查看日志？

服务启动时会在终端输出详细日志。

---

## 📚 更多信息

- **详细API文档**: [API_GUIDE.md](API_GUIDE.md)
- **完整README**: [README.md](README.md)
- **在线Swagger**: http://localhost:8000/docs

---

**就是这么简单！** 🎉

现在可以开始构建你的前端了，或直接通过API调用使用。
