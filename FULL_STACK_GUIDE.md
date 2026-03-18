# 金融资产问答系统 - 完整启动指南

## 🎯 系统架构

```
┌─────────────────────────────────────────────────┐
│         用户浏览器 (http://localhost:3000)       │
└────────────────────┬────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────┐
│   Next.js 前端 (Port 3000)                      │
│   - 聊天界面                                     │
│   - 消息管理                                     │
│   - UI组件                                       │
└────────────────────┬────────────────────────────┘
                     │ HTTP API Calls
┌────────────────────▼────────────────────────────┐
│   Python FastAPI 后端 (Port 8000)              │
│   - AI Agent (LangChain)                        │
│   - RAG System (FAISS)                          │
│   - Financial Data API (yfinance)               │
└─────────────────────────────────────────────────┘
```

## 🚀 完整启动流程

### 前置条件

1. **Python 环境**
   - Python 3.8+
   - Conda环境：`financial`

2. **Node.js 环境**
   - Node.js 18+
   - npm/yarn/pnpm

### Step 1: 启动Python后端 (FastAPI)

```bash
# 1. 激活conda环境
conda activate financial

# 2. 确保在项目根目录
cd /Users/wanchao/financialQA

# 3. 启动FastAPI服务
python start_api.py --dev

# 看到以下输出表示成功：
# 🚀 Starting API server...
# 📖 API Documentation: http://localhost:8000/docs
```

**验证后端**：
- 访问 http://localhost:8000/docs
- 应该看到Swagger API文档

### Step 2: 启动Next.js前端

在**新的终端窗口**中：

```bash
# 1. 进入web-app目录
cd /Users/wanchao/financialQA/web-app

# 2. 安装依赖（仅首次需要）
npm install

# 3. 启动开发服务器
npm run dev

# 看到以下输出表示成功：
# ▲ Next.js 14.x.x
# - Local:   http://localhost:3000
```

**验证前端**：
- 访问 http://localhost:3000
- 应该看到聊天界面

### Step 3: 测试系统

1. **点击示例问题**：
   - "阿里巴巴现在的股价是多少？"
   - "什么是市盈率？"

2. **输入自定义问题**：
   - 在输入框中输入问题
   - 点击"发送"或按Enter键

3. **查看回答**：
   - AI会自动分析问题类型
   - 调用相应的工具（股价API或知识库）
   - 返回结构化的回答

## 📊 系统功能演示

### 示例1：股价查询

**输入**：
```
阿里巴巴现在的股价是多少？
```

**预期输出**：
```
📈 Alibaba Group Holding Limited (BABA)
  最新价：85.23 USD
  涨跌幅：+1.2% (+1.01)
  成交量：15234567
  总市值：2.3B
  数据时间：2026-03-14 15:30
```

### 示例2：涨跌分析

**输入**：
```
特斯拉最近7天涨跌情况如何？
```

**预期输出**：
```
📊 特斯拉 7日涨跌分析
  期初价格：245.50
  期末价格：258.80
  涨跌幅：+5.42% (+13.30)
  期间最高：262.10
  期间最低：243.20
  趋势判断：上涨
```

### 示例3：金融知识

**输入**：
```
什么是市盈率？
```

**预期输出**：
```
市盈率（P/E Ratio）是指股票价格除以每股收益的比率，
用于评估股票的估值水平。

计算公式：市盈率 = 股价 / 每股收益

- 高市盈率：可能表示市场对公司未来增长预期较高，或股票被高估
- 低市盈率：可能表示股票被低估，或公司增长前景不佳
```

## 🔧 开发模式说明

### 后端热重载

FastAPI使用 `--reload` 模式，代码修改会自动重启：

```python
# 修改 ai_agent/api.py 或其他文件
# 保存后自动重启服务
```

### 前端热重载

Next.js开发模式支持热模块替换（HMR）：

```tsx
// 修改 src/components/*.tsx 或其他文件
// 保存后浏览器自动刷新
```

## 🐛 常见问题

### 问题1：后端启动失败

**症状**：
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案**：
```bash
conda activate financial
pip install -r requirements.txt
```

### 问题2：前端无法连接后端

**症状**：
```
无法连接到后端服务，请确保FastAPI服务正在运行
```

**检查清单**：
1. ✅ Python后端是否在运行？（http://localhost:8000/docs）
2. ✅ 端口8000是否被占用？
3. ✅ `.env.local` 配置是否正确？

**解决方案**：
```bash
# 确保后端运行
python start_api.py --dev

# 检查端口
lsof -i :8000

# 验证环境变量
cat web-app/.env.local
```

### 问题3：npm install失败

**症状**：
```
npm ERR! network timeout
```

**解决方案**：
```bash
# 使用国内镜像
npm config set registry https://registry.npmmirror.com
npm install
```

### 问题4：页面空白

**解决方案**：
```bash
# 清除Next.js缓存
cd web-app
rm -rf .next
npm run dev
```

## 📦 生产环境部署

### 后端部署

```bash
# 使用多进程
python start_api.py --workers 4

# 或使用Gunicorn
gunicorn ai_agent.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 前端部署

```bash
cd web-app

# 构建
npm run build

# 启动
npm run start

# 或使用PM2
pm2 start npm --name "financial-qa-web" -- start
```

## 🎨 自定义配置

### 修改API地址

编辑 `web-app/.env.local`：

```env
NEXT_PUBLIC_API_URL=http://your-backend-url:8000
```

### 修改示例问题

编辑 `web-app/src/components/ExampleQuestions.tsx`：

```tsx
const EXAMPLE_QUESTIONS = [
  '你的问题1',
  '你的问题2',
  // ...
];
```

### 修改主题颜色

编辑 `web-app/tailwind.config.ts`：

```ts
theme: {
  extend: {
    colors: {
      primary: '#your-color',
    },
  },
},
```

## 📚 相关文档

- **后端API文档**: [API_GUIDE.md](API_GUIDE.md)
- **前端README**: [web-app/README.md](web-app/README.md)
- **项目总览**: [README.md](README.md)
- **FastAPI快速开始**: [FASTAPI_QUICKSTART.md](FASTAPI_QUICKSTART.md)

## ✅ 完整检查清单

启动前检查：

- [ ] Conda环境已激活（`conda activate financial`）
- [ ] Python依赖已安装（`pip install -r requirements.txt`）
- [ ] Node.js已安装（`node --version`）
- [ ] npm依赖已安装（在web-app目录运行`npm install`）

运行中检查：

- [ ] 后端运行在 http://localhost:8000
- [ ] 前端运行在 http://localhost:3000
- [ ] 可以访问Swagger文档
- [ ] 前端界面正常显示
- [ ] 示例问题可以点击
- [ ] 输入框可以输入和发送
- [ ] AI回答正常显示

---

**现在可以开始使用了！** 🎉

任何问题，请参考上面的故障排查部分。
