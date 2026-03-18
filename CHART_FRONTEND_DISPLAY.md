# 图表前端显示功能说明

## 功能概述

AI 生成的图表现在可以直接在 Next.js 前端聊天界面中显示，无需手动复制链接打开。

## 实现原理

### 1. 后端返回 Markdown 格式

**修改了 `ai_agent/chart_tools.py`**，现在返回 Markdown 图片语法：

```markdown
图表已生成！

![图表标题](http://localhost:8000/charts/line_chart_20260316_234253.png)

访问链接: http://localhost:8000/charts/line_chart_20260316_234253.png
```

### 2. 前端自动渲染

**修改了 `web-app/src/components/MessageItem.tsx`**：
- 使用 `ReactMarkdown` 渲染 AI 回复
- 添加了图片样式支持（圆角、阴影、响应式）

```tsx
<div className="prose prose-sm max-w-none
     prose-img:rounded-lg
     prose-img:shadow-md
     prose-img:max-w-full
     prose-img:h-auto">
  <ReactMarkdown>{message.content}</ReactMarkdown>
</div>
```

## 使用方法

### 1. 启动后端

```bash
cd /Users/wanchao/financialQA
/Users/wanchao/miniconda3/envs/financial/bin/python -m ai_agent.api
```

### 2. 启动前端

```bash
cd /Users/wanchao/financialQA/web-app
npm run dev
```

### 3. 访问前端

打开浏览器访问：`http://localhost:3000`

### 4. 登录

使用之前注册的用户名和密码登录。

### 5. 请求生成图表

在聊天框输入以下任意问题：

**示例1: 直接请求绘图**
```
请帮我生成一个折线图，显示过去4个月的销售额：1月100万，2月120万，3月150万，4月180万
```

**示例2: 从数据生成**
```
请帮我分析以下数据并绘制饼图：
股票：60%
债券：30%
现金：10%
```

**示例3: 基于查询结果**
```
请查询阿里巴巴最近5天的股价，并绘制成折线图
```

### 6. 查看图表

AI 回复中会直接显示图表图片，无需额外操作。

## 示例截图流程

```
用户输入：
┌────────────────────────────────────────┐
│ 请帮我生成一个折线图，显示月度销售额   │
└────────────────────────────────────────┘

AI 回复：
┌────────────────────────────────────────┐
│ 图表已生成！                           │
│                                        │
│ [显示折线图图片]                       │
│                                        │
│ 访问链接: http://localhost:8000/...   │
└────────────────────────────────────────┘
```

## 支持的图表类型

1. **折线图** (line) - 趋势分析
2. **柱状图** (bar) - 数值对比
3. **饼图** (pie) - 占比分析
4. **雷达图** (radar) - 多维度对比

## 技术细节

### 后端修改

**文件：`ai_agent/chart_tools.py`**

修改了 3 个工具函数的返回值：

1. `generate_financial_chart` (line 407-409)
2. `generate_chart_from_text` (line 425-427)
3. `generate_ai_diagram` (line 447-450)

**修改内容：**
```python
# 之前
return f"图表已生成！\n访问链接: {chart_url}\n文件路径: {filepath}"

# 现在
return f"图表已生成！\n\n![{title}]({chart_url})\n\n访问链接: {chart_url}"
```

### 前端修改

**文件：`web-app/src/components/MessageItem.tsx`**

添加了 Tailwind CSS 图片样式类：

```tsx
prose-img:rounded-lg      // 圆角
prose-img:shadow-md       // 阴影
prose-img:max-w-full      // 最大宽度100%
prose-img:h-auto          // 高度自动
```

## Markdown 图片语法

标准 Markdown 图片语法：
```markdown
![替代文本](图片URL)
```

示例：
```markdown
![月度销售额趋势](http://localhost:8000/charts/line_chart_20260316_234253.png)
```

ReactMarkdown 会将其渲染为：
```html
<img
  src="http://localhost:8000/charts/line_chart_20260316_234253.png"
  alt="月度销售额趋势"
/>
```

## 测试

运行测试脚本验证输出格式：

```bash
/Users/wanchao/miniconda3/envs/financial/bin/python test_chart_frontend.py
```

**预期输出：**
```
✅ 包含 Markdown 图片语法
✅ 包含图片 URL
```

## 故障排查

### 问题1: 图片不显示

**可能原因：**
- Python 后端未启动
- 图片 URL 错误

**解决：**
```bash
# 检查后端是否运行
curl http://localhost:8000/api/health

# 检查图片是否存在
curl http://localhost:8000/charts/xxx.png
```

### 问题2: 显示 URL 而不是图片

**可能原因：**
- ReactMarkdown 未正确解析
- 前端组件未更新

**解决：**
1. 重启 Next.js 开发服务器
2. 清除浏览器缓存
3. 检查 MessageItem.tsx 是否已更新

### 问题3: 图片太大/太小

**解决：**
修改 MessageItem.tsx 中的样式类，例如：
```tsx
prose-img:max-w-2xl  // 限制最大宽度
prose-img:w-auto     // 宽度自动
```

## 性能优化

### 图片懒加载（可选）

如果聊天中有很多图片，可以添加懒加载：

```tsx
<ReactMarkdown
  components={{
    img: ({ src, alt }) => (
      <img
        src={src}
        alt={alt}
        loading="lazy"
        className="rounded-lg shadow-md"
      />
    )
  }}
>
  {message.content}
</ReactMarkdown>
```

### 图片缓存

浏览器会自动缓存图片，相同的图片不会重复下载。

## 安全注意事项

1. **CORS 配置**：确保 Python 后端允许前端域名
2. **图片路径验证**：后端只提供 chart_output 目录中的文件
3. **文件大小限制**：matplotlib 生成的图片通常 25-60KB，性能良好

## 总结

现在用户可以：
1. 通过自然语言请求生成图表
2. 在聊天界面中直接查看图表
3. 无需手动打开链接
4. 支持所有 6 种图表类型

这使得金融数据可视化变得非常便捷，提升了用户体验！
