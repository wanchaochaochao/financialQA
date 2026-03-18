# Agent 超时限制修复说明

## 问题描述

用户遇到错误：
```
Agent stopped due to iteration limit or time limit.
```

## 问题原因

### 1. 迭代次数限制太少

**之前的配置：**
```python
AGENT_MAX_ITERATIONS = 5  # 太少
```

**问题分析：**
当 Agent 处理复杂任务（如生成图表）时，可能需要：
1. 理解用户问题（1次迭代）
2. 决定使用哪个工具（1次）
3. 调用数据查询工具（1次）
4. 调用图表工具（1次）
5. 格式化结果（1次）
6. 可能的重试或调整（1-2次）

**总计：5-7次迭代**，超过限制。

### 2. 缺少执行时间限制

之前没有设置 `max_execution_time`，导致无法控制长时间运行的任务。

## 解决方案

### 修改1: 增加迭代次数限制

**文件：`ai_agent/config.py`**

```python
# 从
AGENT_MAX_ITERATIONS = 5

# 改为
AGENT_MAX_ITERATIONS = 15
```

### 修改2: 添加执行时间限制

**文件：`ai_agent/config.py`**

```python
# 新增
AGENT_MAX_EXECUTION_TIME = 60  # 秒
```

### 修改3: 应用配置到 AgentExecutor

**文件：`ai_agent/agent_core.py`**

```python
self.agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=Config.AGENT_VERBOSE,
    handle_parsing_errors=True,
    max_iterations=Config.AGENT_MAX_ITERATIONS,        # 15次
    max_execution_time=Config.AGENT_MAX_EXECUTION_TIME, # 60秒 (新增)
)
```

## 新配置说明

| 配置项 | 之前值 | 新值 | 说明 |
|--------|--------|------|------|
| `AGENT_MAX_ITERATIONS` | 5 | 15 | 最大迭代次数，足够处理复杂任务 |
| `AGENT_MAX_EXECUTION_TIME` | 未设置 | 60秒 | 最大执行时间，1分钟内完成 |

## 使用方法

### 1. 重启 Python 后端

配置更改后，需要重启后端以应用新配置：

```bash
cd /Users/wanchao/financialQA

# 停止当前运行的后端（Ctrl+C）

# 重新启动
/Users/wanchao/miniconda3/envs/financial/bin/python -m ai_agent.api
```

### 2. 测试

现在可以测试之前失败的复杂任务：

```
请帮我查询阿里巴巴最近5天的股价，并绘制成折线图
```

这个任务需要：
1. 理解问题
2. 调用股价查询工具
3. 处理数据
4. 调用图表工具
5. 返回结果和图片

现在有 15 次迭代和 60 秒时间，足够完成。

## 环境变量覆盖（可选）

如果需要进一步调整，可以使用环境变量：

```bash
# 增加到 20 次迭代
export AGENT_MAX_ITERATIONS=20

# 增加到 120 秒（2分钟）
export AGENT_MAX_EXECUTION_TIME=120

# 启动后端
python -m ai_agent.api
```

## 监控和调试

### 查看 Agent 详细执行过程

在 `ai_agent/config.py` 中：
```python
AGENT_VERBOSE = True  # 默认已开启
```

这会在日志中显示：
- 每次工具调用
- Agent 的思考过程
- 迭代次数

### 日志示例

```
Thought: 我需要先查询股价数据
Action: get_stock_history_tool
Action Input: {"symbol": "BABA", "period": "5d"}
Observation: [股价数据]

Thought: 现在需要生成图表
Action: generate_financial_chart
Action Input: {"chart_type": "line", ...}
Observation: 图表已生成！

Thought: 我现在知道最终答案了
Final Answer: [包含图表的回复]
```

## 性能优化建议

### 1. 合理设置限制

- **简单查询**：5-8次迭代通常足够
- **复杂任务**（如图表）：10-15次迭代
- **多步骤分析**：15-20次迭代

### 2. 执行时间

- **数据查询**：通常 5-10 秒
- **图表生成**：通常 2-5 秒
- **复杂任务**：30-60 秒
- **建议设置**：60 秒（覆盖大部分场景）

### 3. 优化提示词

在 `agent_core.py` 的 prompt 中，已经有明确的工具选择指南，帮助 Agent 更快找到正确工具。

## 故障排查

### 问题：仍然超时

**可能原因：**
1. 任务确实太复杂
2. 工具响应慢（如网络请求）
3. LLM 响应慢

**解决：**
```bash
# 增加限制
export AGENT_MAX_ITERATIONS=20
export AGENT_MAX_EXECUTION_TIME=120
```

### 问题：Agent 执行太慢

**可能原因：**
1. 迭代次数设置太高
2. LLM 模型太慢

**解决：**
1. 检查是否使用了快速模型（如 gpt-4.1-mini）
2. 优化提示词，减少不必要的思考

### 问题：配置未生效

**解决：**
1. 确认已重启 Python 后端
2. 检查环境变量是否正确
3. 查看日志确认配置值

## 总结

**修改后的优势：**
- ✅ 支持更复杂的任务（15次迭代）
- ✅ 有效的时间控制（60秒限制）
- ✅ 避免无限循环
- ✅ 用户体验更好

**适用场景：**
- 多步骤数据查询和分析
- 图表生成和可视化
- 结合多个工具的复杂任务
- 需要多次尝试的任务

现在你的 AI Agent 可以处理更复杂的金融数据分析和可视化任务了！
