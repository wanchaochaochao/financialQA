# 图表 HTTP 访问功能说明

## 功能概述

图表工具现在支持通过 HTTP 访问生成的图片，前端可以直接显示图表。

## 实现方式

### 1. 后端静态文件服务

在 `ai_agent/api.py` 中添加了 FastAPI StaticFiles 挂载：

```python
# 挂载图表静态文件目录
app.mount("/charts", StaticFiles(directory=str(chart_output_dir)), name="charts")
```

### 2. 工具返回值改进

所有图表工具现在返回包含 HTTP URL 的消息：

```
图表已生成！
访问链接: http://localhost:8000/charts/line_chart_20260316_225747.png
文件路径: /Users/wanchao/financialQA/ai_agent/chart_output/line_chart_20260316_225747.png
```

## 使用方法

### 启动 Python 后端

```bash
cd /Users/wanchao/financialQA

# 使用 financial conda 环境
/Users/wanchao/miniconda3/envs/financial/bin/python -m ai_agent.api

# 或者先激活环境
conda activate financial
python -m ai_agent.api
```

后端将在 `http://localhost:8000` 启动。

### 生成图表

```python
import json
from ai_agent.chart_tools import generate_financial_chart

request = {
    "chart_type": "line",
    "title": "销售趋势",
    "data": [
        {"label": "Q1", "value": 100},
        {"label": "Q2", "value": 150},
        {"label": "Q3", "value": 200}
    ]
}

result = generate_financial_chart.invoke(json.dumps(request))
print(result)
# 输出:
# 图表已生成！
# 访问链接: http://localhost:8000/charts/line_chart_20260316_225747.png
# 文件路径: /Users/wanchao/financialQA/ai_agent/chart_output/line_chart_20260316_225747.png
```

### 访问图表

#### 方式1: 浏览器直接访问

打开浏览器，访问返回的 URL：
```
http://localhost:8000/charts/line_chart_20260316_225747.png
```

#### 方式2: 使用 curl 下载

```bash
curl http://localhost:8000/charts/line_chart_20260316_225747.png -o chart.png
```

#### 方式3: 在前端显示

在 Next.js 或其他前端框架中：

```jsx
// React/Next.js 示例
function ChartDisplay({ chartUrl }) {
  return (
    <div>
      <img src={chartUrl} alt="Financial Chart" />
    </div>
  );
}

// 使用
<ChartDisplay chartUrl="http://localhost:8000/charts/line_chart_20260316_225747.png" />
```

## 测试步骤

### 1. 生成测试图表

```bash
/Users/wanchao/miniconda3/envs/financial/bin/python test_chart_http.py
```

这将生成两个测试图表并显示访问 URL。

### 2. 启动后端

```bash
cd /Users/wanchao/financialQA
/Users/wanchao/miniconda3/envs/financial/bin/python -m ai_agent.api
```

### 3. 访问图表

在浏览器中访问测试脚本输出的 URL，例如：
```
http://localhost:8000/charts/line_chart_20260316_225747.png
```

应该能看到生成的图表图片。

### 4. 测试 API 端点

访问 API 文档页面：
```
http://localhost:8000/docs
```

## 配置选项

### 修改 API 基础 URL

如果部署到生产环境，需要修改 API_BASE_URL：

```bash
export API_BASE_URL="https://your-domain.com"
```

或在代码中修改 `ai_agent/chart_tools.py`:

```python
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
```

## 目录结构

```
/Users/wanchao/financialQA/
├── ai_agent/
│   ├── api.py              # FastAPI 服务（已添加静态文件挂载）
│   ├── chart_tools.py      # 图表工具（已更新返回 HTTP URL）
│   └── chart_output/       # 图表输出目录（通过 /charts 路径访问）
│       ├── line_chart_*.png
│       ├── bar_chart_*.png
│       └── pie_chart_*.png
```

## API 端点

### 静态文件访问

- **路径**: `/charts/{filename}`
- **方法**: GET
- **示例**: `http://localhost:8000/charts/line_chart_20260316_225747.png`

### 核心 API 端点

- **聊天**: `POST /api/chat`
- **健康检查**: `GET /api/health`
- **API 文档**: `GET /docs`

## 前端集成示例

### Next.js 集成

```typescript
// 在聊天界面中解析 AI 返回的图表 URL
function parseChatResponse(response: string): {
  text: string;
  chartUrl?: string;
} {
  const urlMatch = response.match(/访问链接:\s*(http[^\s]+)/);

  return {
    text: response,
    chartUrl: urlMatch ? urlMatch[1] : undefined
  };
}

// 显示组件
function ChatMessage({ message }: { message: string }) {
  const { text, chartUrl } = parseChatResponse(message);

  return (
    <div className="chat-message">
      <p>{text}</p>
      {chartUrl && (
        <img
          src={chartUrl}
          alt="Chart"
          className="chart-image"
        />
      )}
    </div>
  );
}
```

## 安全注意事项

1. **CORS 配置**: 生产环境应限制 `allow_origins`
2. **文件访问**: 只能访问 `chart_output` 目录中的文件
3. **文件大小**: matplotlib 生成的图片通常在 25-60KB
4. **自动清理**: 考虑定期清理旧图表文件

## 故障排查

### 问题1: 无法访问图片 (404)

**原因**: 后端未启动或图片不存在

**解决**:
```bash
# 检查后端是否运行
curl http://localhost:8000/api/health

# 检查图片文件是否存在
ls -lh ai_agent/chart_output/
```

### 问题2: CORS 错误

**原因**: 前端域名未在 CORS 配置中

**解决**: 修改 `ai_agent/api.py` 中的 `allow_origins`

### 问题3: 图片路径错误

**原因**: API_BASE_URL 配置不正确

**解决**: 设置正确的环境变量：
```bash
export API_BASE_URL="http://localhost:8000"
```

## 总结

现在图表功能完全支持 HTTP 访问，前端可以：
1. 通过 AI Agent 生成图表
2. 从返回消息中提取 HTTP URL
3. 直接在网页中显示图表图片

这使得金融数据可视化可以无缝集成到 Web 应用中！
