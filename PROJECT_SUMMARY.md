# 金融AI问答系统 - 项目总结

## 📁 项目结构

```
financialQA/
├── ai_agent/                      # 🆕 核心AI模块（自包含）
│   ├── __init__.py               # 模块初始化
│   ├── config.py                 # ⚙️  配置管理
│   ├── data_api.py               # 📊 金融数据API（yfinance）
│   ├── rag_system.py             # 📚 RAG知识库系统
│   ├── agent_core.py             # 🤖 Agent核心逻辑
│   ├── main.py                   # 🚀 CLI主程序入口
│   ├── api.py                    # 🌐 FastAPI后端服务
│   ├── tools/                    # 🛠️  自定义工具
│   │   ├── __init__.py
│   │   └── financial_tools.py    # 金融查询工具
│   ├── knowledge_base/           # 📖 知识库文档（自动生成）
│   │   ├── 基金产品介绍.txt
│   │   ├── 风控管理制度.txt
│   │   ├── 客户服务FAQ.txt
│   │   ├── 投资研究报告.txt
│   │   └── 金融术语词典.txt
│   └── faiss_index/              # 🗄️  向量数据库（自动生成）
│       ├── index.faiss
│       └── index.pkl
│
├── test1.py                      # 📝 原始测试文件（保留参考）
├── 题目.md                        # 📋 项目需求文档
├── requirements.txt              # 📦 Python依赖清单
├── .env.example                  # 🔑 环境变量模板
├── README.md                     # 📖 项目说明文档
├── PROJECT_SUMMARY.md            # 📊 本文件
├── quick_test.py                 # 🧪 快速测试脚本
├── start_api.py                  # 🚀 API服务启动脚本
├── start_api.sh                  # 🚀 API服务启动脚本（Shell）
├── start_api.bat                 # 🚀 API服务启动脚本（Windows）
├── test_api.py                   # 🧪 API测试脚本
├── API_GUIDE.md                  # 📖 API使用指南
└── FASTAPI_QUICKSTART.md         # ⚡ FastAPI快速开始
```

## 🎯 核心功能实现

### ✅ 已完成功能

#### 1. 配置管理 (config.py)
- [x] OpenAI API 配置
- [x] LLM 模型参数管理
- [x] RAG 参数配置
- [x] 路径管理
- [x] 环境变量支持

#### 2. 金融数据API (data_api.py)
- [x] Yahoo Finance 集成
- [x] 实时股价查询
- [x] 历史数据获取（7日、30日涨跌）
- [x] 市场指数行情
- [x] 中英文股票名称映射
- [x] 数据格式化输出
- [x] 错误处理

**支持的股票：**
- 美股：BABA（阿里巴巴）、TSLA（特斯拉）、AAPL（苹果）、NVDA（英伟达）等
- A股：600519（贵州茅台）、300750（宁德时代）、600036（招商银行）等
- 港股：0700（腾讯控股）等

**支持的指数：**
- 中国：上证指数、深证成指、创业板指、沪深300
- 美国：标普500、纳斯达克、道琼斯

#### 3. RAG知识库系统 (rag_system.py)
- [x] 自动创建示例知识库
- [x] 文档加载（TextLoader）
- [x] 文档切分（RecursiveCharacterTextSplitter）
- [x] 向量化存储（FAISS）
- [x] 相似度检索
- [x] RetrievalQA 链构建
- [x] 向量库持久化

**知识库内容：**
- 基金产品介绍
- 风控管理制度
- 客户服务FAQ
- 投资研究报告
- 金融术语词典

#### 4. LangChain 工具 (tools/financial_tools.py)
- [x] `get_stock_price_tool` - 实时股价查询
- [x] `get_stock_history_tool` - 历史涨跌分析
- [x] `get_market_index_tool` - 市场指数查询

#### 5. Agent核心 (agent_core.py)
- [x] ReAct Agent 构建
- [x] 自动路由逻辑（RAG vs API）
- [x] 多工具协同
- [x] Prompt 工程优化
- [x] 错误处理

#### 6. 主程序 (main.py)
- [x] CLI 交互界面
- [x] 测试问题集
- [x] 交互模式
- [x] 参数配置（--test, --interactive, --rebuild）

## 🔧 技术栈

### 核心框架
- **LangChain**: ReAct Agent + RAG
- **LLM**: OpenAI GPT-4.1-mini（可替换为其他模型）
- **Embedding**: OpenAI text-embedding-ada-002

### 数据源
- **金融数据**: Yahoo Finance API (yfinance)
- **向量数据库**: FAISS

### 开发工具
- Python 3.8+
- pandas, numpy
- python-dotenv

## 📝 使用指南

### 1️⃣ 安装依赖

```bash
cd /Users/wanchao/financialQA
pip install -r requirements.txt
```

### 2️⃣ 配置环境变量（可选）

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# vim .env
```

### 3️⃣ 快速测试

```bash
# 运行快速测试脚本
python quick_test.py
```

### 4️⃣ 运行主程序

```bash
# 默认模式：测试问题 + 交互
python -m ai_agent.main

# 仅测试问题
python -m ai_agent.main --test

# 仅交互模式
python -m ai_agent.main --interactive

# 重建知识库
python -m ai_agent.main --rebuild
```

## 💡 使用示例

### 示例问题

**市场数据类：**
- "阿里巴巴当前股价是多少？"
- "BABA最近7天涨跌情况如何？"
- "特斯拉近期走势如何？"
- "上证指数最新行情？"

**知识库类：**
- "什么是市盈率？"
- "收入和净利润的区别是什么？"
- "稳健增长基金的风险等级？"
- "公司风控制度中单只股票持仓上限？"

**综合类：**
- "贵州茅台最近30天走势如何？公司基金有持仓吗？"

## 🎨 架构亮点

### 1. 模块化设计
- 每个模块职责单一
- 易于测试和维护
- 便于后续扩展

### 2. 真实数据源
- 集成 Yahoo Finance 真实市场数据
- 替代了 test1.py 的模拟数据
- 支持全球主要市场股票查询

### 3. 智能路由
- ReAct Agent 自动判断问题类型
- 行情类 → API 查询
- 知识类 → RAG 检索
- 综合类 → 多工具协同

### 4. Prompt 工程
- 明确区分"客观数据"和"分析性描述"
- 要求标注数据来源
- 减少 LLM hallucination

### 5. 可配置性
- 统一配置文件
- 支持环境变量
- 灵活的参数调整

## 📊 与 test1.py 对比

| 特性 | test1.py | 新架构 (ai_agent) |
|------|----------|------------------|
| 代码结构 | 单文件500行 | 6个模块，清晰分层 |
| 数据源 | 模拟数据 | 真实API（yfinance） |
| 股票支持 | 5只（硬编码） | 全球市场（自动查询） |
| 配置管理 | 散落代码中 | 统一config.py |
| 可扩展性 | 低 | 高（模块化） |
| 测试性 | 难 | 易（独立模块） |
| 维护性 | 低 | 高 |

## 🚀 下一步规划

### Phase 2: Web 平台（待实现）
- [ ] Next.js 前端界面
- [ ] FastAPI 后端API
- [ ] RESTful API 设计
- [ ] 用户认证
- [ ] 对话历史

### Phase 3: 高级功能
- [ ] Web Search 集成（新闻获取）
- [ ] 多轮对话上下文
- [ ] 财报数据集成
- [ ] 技术指标计算
- [ ] 投资组合分析

### Phase 4: 优化
- [ ] 向量库升级（Chroma/Qdrant）
- [ ] LLM 缓存
- [ ] 数据源扩展
- [ ] 性能优化

## ⚠️ 注意事项

1. **API 限制**
   - Yahoo Finance 免费API有请求限制
   - 建议添加缓存机制

2. **数据准确性**
   - 免费API可能有延迟
   - 生产环境建议用付费数据源

3. **成本控制**
   - LLM调用会产生费用
   - 建议设置使用限额

## 📄 项目文件说明

### 核心代码文件

1. **config.py** (3.1KB)
   - 所有配置的统一管理
   - 环境变量支持
   - 路径管理

2. **data_api.py** (11KB)
   - 金融数据API封装
   - Yahoo Finance集成
   - 股票/指数查询
   - 历史数据分析

3. **rag_system.py** (13KB)
   - 知识库管理
   - 文档加载和切分
   - 向量化存储
   - 检索链构建

4. **agent_core.py** (5.3KB)
   - Agent构建和管理
   - 工具路由
   - Prompt工程

5. **tools/financial_tools.py** (2.7KB)
   - LangChain工具封装
   - 三个核心查询工具

6. **main.py** (4.6KB)
   - CLI界面
   - 测试和交互模式

### 文档文件

1. **README.md**
   - 完整项目说明
   - 安装和使用指南
   - 示例演示

2. **PROJECT_SUMMARY.md**
   - 本文件
   - 项目总结

3. **.env.example**
   - 环境变量模板

4. **requirements.txt**
   - Python依赖清单

## ✅ 完成状态

### 已完成（Phase 1）
- ✅ 项目结构搭建
- ✅ 配置管理模块
- ✅ 金融数据API集成
- ✅ RAG知识库系统
- ✅ LangChain工具封装
- ✅ Agent核心逻辑
- ✅ CLI交互界面
- ✅ 文档和说明

### 待实现（Phase 2+）
- ⏸️ Next.js Web 平台
- ⏸️ 后端API服务
- ⏸️ Web Search集成
- ⏸️ 高级分析功能

## 📞 支持

如有问题，请参考：
1. README.md - 详细使用说明
2. quick_test.py - 快速测试验证
3. test1.py - 原始参考实现

---

**开发完成时间**: 2026-03-14
**当前版本**: v1.0.0
**状态**: Phase 1 完成 ✅
