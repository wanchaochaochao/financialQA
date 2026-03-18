# 🚀 快速开始指南

## 5分钟上手金融AI问答系统

### Step 1: 安装依赖 (1分钟)

```bash
cd /Users/wanchao/financialQA
pip install -r requirements.txt
```

如果安装速度慢，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Step 2: 快速测试 (30秒)

```bash
python quick_test.py
```

如果看到 `✅ All basic tests passed!`，说明系统正常！

### Step 3: 运行主程序 (1分钟)

```bash
python -m ai_agent.main
```

系统会：
1. 自动创建知识库
2. 构建向量数据库
3. 运行测试问题
4. 进入交互模式

### Step 4: 开始提问！ (随便玩)

在交互模式中，你可以问：

**查股价：**
```
阿里巴巴现在的股价是多少？
```

**看涨跌：**
```
特斯拉最近7天涨跌情况如何？
```

**学知识：**
```
什么是市盈率？
```

**查资料：**
```
稳健增长基金的风险等级是多少？
```

输入 `quit` 或 `exit` 退出。

---

## 🎯 常见问题

### Q: 需要配置 OpenAI API Key 吗？

A: **代码中已经包含了测试用的 API Key**，可以直接运行。

如果要用自己的API Key：
```bash
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY
```

### Q: 支持哪些股票？

A: 支持全球主要市场：
- **美股**: AAPL, TSLA, BABA, NVDA, MSFT, GOOGL...
- **A股**: 600519(茅台), 300750(宁德), 600036(招行)...
- **港股**: 0700(腾讯)...

可以用**中文名称**或**股票代码**查询！

### Q: 知识库有什么内容？

A: 包含5个示例文档：
1. 基金产品介绍
2. 风控管理制度
3. 客户服务FAQ
4. 投资研究报告
5. 金融术语词典

这些文档会在首次运行时自动创建在 `knowledge_base/` 目录。

### Q: 速度慢怎么办？

A: 第一次运行需要：
- 下载股票数据（yfinance）
- 构建向量数据库（FAISS）

**第二次运行会快很多**，因为会加载已有的向量库！

如果还是慢，可能是：
1. 网络问题（访问 Yahoo Finance 慢）
2. LLM 响应慢（OpenAI API延迟）

---

## 🎮 进阶使用

### 仅运行测试问题（不进交互）

```bash
python -m ai_agent.main --test
```

### 仅交互模式（跳过测试）

```bash
python -m ai_agent.main --interactive
```

### 重建知识库

```bash
python -m ai_agent.main --rebuild
```

---

## 🐛 遇到问题？

### ImportError: No module named 'xxx'

```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### API Key错误

检查 `ai_agent/config.py` 中的 `OPENAI_API_KEY` 是否正确。

### 向量库加载失败

```bash
# 删除并重建
rm -rf faiss_index
python -m ai_agent.main --rebuild
```

---

## 📚 更多信息

- **完整说明**: 查看 `README.md`
- **项目总结**: 查看 `PROJECT_SUMMARY.md`
- **原始实现**: 查看 `test1.py`

---

**祝你使用愉快！** 🎉
