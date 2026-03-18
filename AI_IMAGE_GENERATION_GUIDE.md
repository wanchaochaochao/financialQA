# AI 图像生成功能使用指南

## 📌 功能概述

已成功集成 **tu-zi.com AI 图像生成 API**（OpenAI 兼容接口），可用于生成：
- 📊 流程图、架构图
- 📈 金融概念图、商业模型图
- 🎨 数据可视化图表
- 🏢 组织结构图等复杂图像

**模型**: `gemini-3.1-flash-image-preview`（支持中英文描述）

---

## 🔑 配置 API Key

### 方式 1: 设置环境变量（推荐）

```bash
export TUZI_API_KEY="你的API密钥"
```

### 方式 2: 写入 .env 文件

在项目根目录创建 `.env` 文件：
```bash
TUZI_API_KEY=你的API密钥
```

### 获取 API Key

访问：https://tu-zi.com

---

## 🚀 使用方法

### 1️⃣ 通过 Agent 自然语言调用（最简单）

在 Next.js 前端聊天框中输入：

```
请生成一张金融风控系统的流程图，包含数据采集、风险评估、预警、处置四个步骤
```

```
请帮我画一张资产配置的金字塔模型图，底层是现金和债券，中层是股票，顶层是另类投资
```

```
生成一张公司组织架构图，树状结构，包含董事会、管理层、各部门
```

Agent 会自动识别需求，调用 `generate_ai_diagram` 工具生成图片，并直接在前端显示。

---

### 2️⃣ 直接调用 Python 函数

```python
from ai_agent.chart_tools import generate_ai_image

# 基础调用（默认横屏 16:9，标准画质）
filepath = generate_ai_image("兔子在赛跑，卡通风格，色彩鲜艳")
print(filepath)  # 输出: /path/to/chart_output/ai_image_20260317_123456.png

# 指定尺寸和画质
filepath = generate_ai_image(
    prompt="一个金融风控系统的流程图",
    size="square",      # 方形 1:1
    quality="hd"        # 高清画质
)

# 支持的尺寸参数
# - "square" / "方形"    → 1:1 正方形
# - "horizontal" / "横屏" → 16:9 横屏（默认）
# - "vertical" / "竖屏"   → 9:16 竖屏
# - 或直接传比例: "1x8", "2x1", "3x1" 等

# 支持的画质参数
# - "standard"  标准画质（默认）
# - "hd"        高清
# - "4k"        超清
```

---

### 3️⃣ 通过 LangChain 工具调用

```python
from ai_agent.chart_tools import generate_ai_diagram

# generate_ai_diagram 是封装好的 LangChain 工具
result = generate_ai_diagram.invoke("股票市场技术分析的K线图，包含均线和成交量")
print(result)
# 输出: ✅ AI图像已生成：![AI生成图像](http://localhost:8000/charts/ai_image_xxx.png)
```

---

## 🧪 测试功能

### 测试 1: 验证工具加载

```bash
cd /Users/wanchao/financialQA
/Users/wanchao/miniconda3/envs/financial/bin/python -c "
from ai_agent.chart_tools import get_chart_tools
tools = get_chart_tools()
print(f'成功加载 {len(tools)} 个图表工具')
for tool in tools:
    print(f'  - {tool.name}')
"
```

**预期输出**：
```
成功加载 5 个图表工具
  - generate_financial_chart
  - generate_multi_line_chart
  - generate_stacked_bar_chart
  - generate_chart_from_text
  - generate_ai_diagram
```

### 测试 2: 测试未配置 API Key 时的提示

```bash
/Users/wanchao/miniconda3/envs/financial/bin/python -c "
from ai_agent.chart_tools import generate_ai_diagram
result = generate_ai_diagram.invoke('测试图片')
print(result)
"
```

**预期输出**：
```
❌ AI图像生成功能未配置。
请设置环境变量 TUZI_API_KEY 以启用此功能。
获取 API Key: https://tu-zi.com
```

### 测试 3: 完整功能测试（需要 API Key）

```bash
# 设置 API Key
export TUZI_API_KEY="你的密钥"

# 运行测试
/Users/wanchao/miniconda3/envs/financial/bin/python -c "
from ai_agent.chart_tools import generate_ai_image

result = generate_ai_image(
    '兔子在赛跑，卡通风格，色彩鲜艳，动感十足',
    size='horizontal',
    quality='standard'
)
print(result)
"
```

**成功时输出**：
```
/Users/wanchao/financialQA/chart_output/ai_image_20260317_123456.png
```

**失败时会返回详细错误信息**：
- `❌ AI图像生成功能未配置...` - API Key 未设置
- `AI图像生成失败 (HTTP 401)...` - API Key 无效
- `SSL错误...` - SSL 证书问题（macOS 常见）
- `AI图像生成超时...` - 网络超时
- `AI图像API响应解析失败...` - API 返回格式异常

---

## 📊 与其他图表工具的对比

| 工具 | 适用场景 | 输入格式 | 生成方式 |
|------|---------|---------|---------|
| `generate_financial_chart` | 单系列数据图表（折线、柱状、饼图、雷达） | 结构化数据 JSON | matplotlib |
| `generate_multi_line_chart` | 多系列趋势对比 | 结构化数据 JSON | matplotlib |
| `generate_stacked_bar_chart` | 堆叠柱状图 | 结构化数据 JSON | matplotlib |
| `generate_chart_from_text` | 从文本提取数据并绘图 | 自然语言文本 | matplotlib |
| **`generate_ai_diagram`** | **复杂概念图、流程图、架构图** | **自然语言描述** | **AI 生成** |

---

## ⚠️ 常见问题

### Q1: macOS SSL 错误怎么办？
```bash
/Applications/Python*/Install\ Certificates.command
```

### Q2: 生成的图片保存在哪里？
```
/Users/wanchao/financialQA/chart_output/ai_image_*.png
```

### Q3: 如何在前端访问生成的图片？
图片会自动通过 HTTP 服务暴露：
```
http://localhost:8000/charts/ai_image_20260317_123456.png
```

### Q4: 支持哪些图片比例？
- **1:1 正方形**: `size="square"` 或 `size="方形"` 或 `size="1x1"`
- **16:9 横屏**: `size="horizontal"` 或 `size="横屏"` 或 `size="2x1"`（默认）
- **9:16 竖屏**: `size="vertical"` 或 `size="竖屏"` 或 `size="1x2"`
- **自定义比例**: 直接传 `"1x8"`, `"3x1"` 等

### Q5: 如何提高生成质量？
1. **详细描述**: 包含风格、颜色、细节要求
2. **指定画质**: `quality="hd"` 或 `quality="4k"`
3. **合理尺寸**: 横向内容用 `"horizontal"`，竖向内容用 `"vertical"`

---

## 🎯 示例提示词

### 金融流程图
```
一个金融风控系统的流程图，现代商业风格，包含：数据采集→风险评估→预警机制→应急处置四个步骤，用箭头连接，配色专业
```

### 商业模型图
```
资产配置的金字塔模型图，从下到上分为三层：底层是现金和债券（绿色），中层是股票和基金（蓝色），顶层是另类投资（橙色），金融专业风格
```

### 组织架构图
```
公司组织架构图，树状结构，顶部是董事会，下层是CEO和管理层，底部是各职能部门（财务、人力、技术、市场），现代简约风格
```

### 技术分析图
```
股票市场技术分析的K线图，包含5日均线和10日均线，下方显示成交量柱状图，专业金融软件风格，深色背景
```

---

## 🔄 更新日志

**2026-03-17**:
- ✅ 集成 tu-zi.com AI 图像生成 API
- ✅ 替换旧的预留实现
- ✅ 支持中英文描述
- ✅ 支持多种尺寸比例和画质
- ✅ 完善错误处理和提示信息
- ✅ 集成到 LangChain Agent 工具链

---

## 📝 代码改动

**修改文件**: `/Users/wanchao/financialQA/ai_agent/chart_tools.py`

1. **新增配置**（第40-43行）:
```python
TUZI_API_URL = "https://api.tu-zi.com/v1/images/generations"
TUZI_API_KEY = os.getenv("TUZI_API_KEY", "")
TUZI_MODEL = "gemini-3.1-flash-image-preview"
```

2. **替换 `generate_ai_image` 函数**（第321-400行）:
   - 使用 tu-zi.com API
   - 支持 b64_json 格式
   - 添加尺寸映射
   - 完善错误处理

3. **更新 `generate_ai_diagram` 工具**（第475-496行）:
   - 更新文档字符串
   - 调整错误提示
   - 使用新的 API 配置

4. **新增 import**（第17行）:
```python
import base64
```

---

现在 AI 图像生成功能已完全集成，可以在 Python 后端和前端 Agent 中使用！
