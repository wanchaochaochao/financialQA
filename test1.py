"""
金融资产问答系统 - LangChain RAG Demo
======================================
功能：
1. 知识库问答（RAG）：文档加载 → 切分 → 向量化 → 向量数据库存储 → 检索增强生成
2. 实时数据获取：通过自定义 Tool 对接金融数据 API（如股价查询）
3. Agent 路由：自动判断用户意图，选择走 RAG 还是实时数据查询
"""

import os
from pathlib import Path

# ==================== 1. 配置 ====================

# 使用 OpenAI 兼容接口（可替换为任何 LLM provider）
# 请设置环境变量或在此处填写
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-api-key-here")
#OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")  # 可换成其他兼容接口
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-BNB9wtkenpzSeZM04qY8L9Je5tLqbBlnOnqocqv84K3NoLR3")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai-proxy.org/v1")  # 可换成其他兼容接口

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# ==================== 2. 导入依赖 ====================

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool, tool
from langchain_core.documents import Document


# ==================== 3. 准备示例知识库文档 ====================

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge_base"


def create_sample_knowledge_base():
    """创建示例金融知识库文档（首次运行时自动生成）"""
    KNOWLEDGE_DIR.mkdir(exist_ok=True)

    docs = {
        "基金产品介绍.txt": """
# 稳健增长混合基金 A（代码：001234）

## 基金概况
- 基金类型：混合型基金
- 成立日期：2020年3月15日
- 基金经理：张明远
- 管理费率：1.2%/年
- 托管费率：0.2%/年
- 最低申购金额：100元
- 风险等级：中等风险（R3）

## 投资策略
本基金采用"核心+卫星"策略，核心仓位配置大盘蓝筹股和优质债券，
卫星仓位适度参与成长股和可转债投资。股票仓位占比 60%-80%，
债券仓位占比 20%-40%。

## 历史业绩
- 2023年收益率：12.5%
- 2024年收益率：8.3%
- 2025年收益率：15.2%
- 成立以来年化收益：10.8%

## 持仓前十大股票（2025年报）
1. 贵州茅台 - 8.5%
2. 宁德时代 - 6.2%
3. 招商银行 - 5.8%
4. 比亚迪 - 5.1%
5. 腾讯控股 - 4.9%
""",
        "风控管理制度.txt": """
# 公司风险控制管理制度

## 第一章 总则
第一条 为规范公司风险管理，防范和化解金融风险，保护投资者合法权益，
根据《证券投资基金法》等相关法律法规，制定本制度。

## 第二章 风险分类
公司面临的主要风险包括：
1. 市场风险：因市场价格波动导致投资组合价值变动的风险
2. 信用风险：交易对手或债务人违约的风险
3. 流动性风险：无法以合理价格及时变现资产的风险
4. 操作风险：内部流程、人员、系统或外部事件导致损失的风险
5. 合规风险：违反法律法规和监管要求的风险

## 第三章 风险限额
- 单只股票持仓不得超过基金净值的 10%
- 单一行业持仓不得超过基金净值的 30%
- 投资组合 VaR(95%, 1天) 不得超过基金净值的 2%
- 跟踪误差（指数基金）不得超过 4%

## 第四章 风险监控
风控部门每日进行以下监控：
- 持仓集中度监控
- VaR 值计算和预警
- 流动性压力测试（每月）
- 信用评级变动跟踪
""",
        "客户服务FAQ.txt": """
# 客户常见问题（FAQ）

## 开户相关
Q: 如何开通基金账户？
A: 您可以通过以下方式开户：
1. 下载我司 APP，按照提示完成实名认证和风险评估
2. 携带身份证前往任一合作银行网点办理
3. 通过我司官网在线开户

Q: 开户需要什么条件？
A: 年满 18 周岁的中国公民，持有有效身份证件和银行卡即可开户。

## 申购赎回
Q: 基金申购后多久确认？
A: T 日 15:00 前提交的申购申请，T+1 个工作日确认份额。

Q: 赎回到账需要多长时间？
A: 货币基金 T+1 到账，股票/混合基金 T+3 到 T+5 到账，QDII 基金 T+7 到 T+10 到账。

Q: 基金定投如何设置？
A: 在 APP 中选择目标基金，点击"定投"按钮，设置扣款日期、金额和扣款账户即可。
支持周定投和月定投两种方式。

## 费用相关
Q: 基金有哪些费用？
A: 主要费用包括：
- 申购费：前端收费一般 1.5%（APP 申购通常打 1 折，即 0.15%）
- 赎回费：持有不满 7 天收 1.5%，满 7 天不满 1 年收 0.5%，满 1 年免赎回费
- 管理费：按日计提，年化约 1.0%-1.5%
- 托管费：按日计提，年化约 0.15%-0.25%
""",
        "投资研究报告.txt": """
# 2025年四季度A股市场展望

## 宏观经济分析
2025年中国GDP增速预计为5.2%，经济延续稳步复苏态势。
随着消费场景持续恢复，社会消费品零售总额同比增长6.5%。
制造业PMI连续8个月位于荣枯线上方，显示经济内生动力增强。

## 行业配置建议

### 超配行业
1. **人工智能与半导体**：AI大模型应用加速落地，算力需求持续增长，
   关注英伟达产业链和国产替代机会。
2. **新能源**：光伏组件价格企稳回升，储能装机量超预期，
   行业盈利拐点已现。
3. **医药生物**：创新药出海加速，GLP-1等重磅品种放量，
   估值处于历史低位。

### 标配行业
1. **消费**：白酒需求边际改善，大众消费品量价齐升。
2. **金融**：银行息差收窄趋缓，保险NBV增速回升。

### 低配行业
1. **房地产**：行业仍处于调整期，关注政策超预期的可能。
2. **传统能源**：原油价格中枢下移，煤炭需求进入平台期。

## 风险提示
- 地缘政治风险加剧
- 美联储降息节奏不及预期
- 国内消费复苏力度不及预期
""",
    }

    for filename, content in docs.items():
        filepath = KNOWLEDGE_DIR / filename
        if not filepath.exists():
            filepath.write_text(content, encoding="utf-8")
            print(f"  ✅ 创建示例文档：{filename}")

    return KNOWLEDGE_DIR


# ==================== 4. RAG 核心流程 ====================


def build_rag_chain(knowledge_dir: Path, llm: ChatOpenAI) -> RetrievalQA:
    """
    构建完整的 RAG 链：加载文档 → 切分 → 向量化 → 向量数据库 → 检索QA
    """

    # --- 4.1 文档加载 ---
    print("\n📄 [Step 1] 加载知识库文档...")
    documents = []
    for file_path in knowledge_dir.glob("*.txt"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        documents.extend(loader.load())
    print(f"   加载了 {len(documents)} 个文档")

    # --- 4.2 文档切分 ---
    print("✂️  [Step 2] 文档切分...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,           # 每个切片最多 500 字符
        chunk_overlap=100,        # 相邻切片重叠 100 字符，保证上下文连续性
        separators=["\n\n", "\n", "。", "；", " ", ""],  # 中文友好的分隔符
        length_function=len,
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"   切分为 {len(split_docs)} 个文本块")

    # 打印前3个切片示例
    for i, doc in enumerate(split_docs[:3]):
        print(f"   📝 切片 {i+1}（{len(doc.page_content)} 字符）：{doc.page_content[:80]}...")

    # --- 4.3 向量化 + 存储到 FAISS 向量数据库 ---
    print("🔢 [Step 3] 向量化 & 构建向量数据库（FAISS）...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",  # 也可换成其他 embedding 模型
        openai_api_base=OPENAI_BASE_URL,
    )

    # 创建 FAISS 向量数据库（内存模式，也可持久化到磁盘）
    vectorstore = FAISS.from_documents(split_docs, embeddings)

    # 可选：持久化到磁盘
    faiss_index_path = knowledge_dir.parent / "faiss_index"
    vectorstore.save_local(str(faiss_index_path))
    print(f"   向量数据库已保存到：{faiss_index_path}")

    # --- 4.4 构建检索器 ---
    retriever = vectorstore.as_retriever(
        search_type="similarity",     # 相似度检索
        search_kwargs={"k": 3},       # 返回 top-3 相关文档
    )

    # --- 4.5 构建 RAG Prompt ---
    rag_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""你是一位专业的金融顾问助手。请根据以下参考资料回答用户的问题。
如果参考资料中没有相关信息，请如实告知用户。
回答要准确、专业，适当引用数据。

参考资料：
{context}

用户问题：{question}

专业回答：""",
    )

    # --- 4.6 组装 RetrievalQA 链 ---
    print("🔗 [Step 4] 组装 RetrievalQA 链...")
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",           # stuff = 把所有检索到的文档拼接后一次传入 LLM
        retriever=retriever,
        return_source_documents=True,  # 返回来源文档，方便溯源
        chain_type_kwargs={"prompt": rag_prompt},
    )

    print("   ✅ RAG 链构建完成！\n")
    return rag_chain


# ==================== 5. 实时金融数据工具 ====================


@tool
def get_stock_price(stock_name: str) -> str:
    """查询股票实时价格。输入股票名称或代码，返回最新股价信息。
    例如输入：贵州茅台、宁德时代、600519"""

    # ============================================================
    # 🔧 这里对接真实的金融数据 API
    # 实际使用时替换为：
    #   - Wind API / 万得
    #   - 同花顺 iFind API
    #   - Tushare Pro API
    #   - 东方财富 API
    #   - AKShare (免费开源)
    # ============================================================

    # Demo 模拟数据
    mock_data = {
        "贵州茅台": {"code": "600519.SH", "price": 1856.50, "change": "+1.2%", "volume": "3.2万手", "market_cap": "2.33万亿"},
        "宁德时代": {"code": "300750.SZ", "price": 245.80, "change": "-0.5%", "volume": "8.5万手", "market_cap": "1.08万亿"},
        "招商银行": {"code": "600036.SH", "price": 38.25, "change": "+0.8%", "volume": "12.1万手", "market_cap": "9652亿"},
        "比亚迪": {"code": "002594.SZ", "price": 312.40, "change": "+2.3%", "volume": "5.7万手", "market_cap": "9089亿"},
        "腾讯控股": {"code": "0700.HK", "price": 425.60, "change": "+1.5%", "volume": "1580万股", "market_cap": "4.08万亿港元"},
    }

    # 模糊匹配
    for name, data in mock_data.items():
        if stock_name in name or stock_name in data["code"]:
            return (
                f"📈 {name}（{data['code']}）\n"
                f"  最新价：{data['price']} 元\n"
                f"  涨跌幅：{data['change']}\n"
                f"  成交量：{data['volume']}\n"
                f"  总市值：{data['market_cap']}\n"
                f"  数据时间：2025年12月20日 15:00"
            )

    return f"未找到股票「{stock_name}」的数据，请检查名称或代码是否正确。"


@tool
def get_market_index(index_name: str) -> str:
    """查询市场指数行情。输入指数名称，如：上证指数、深证成指、创业板指"""

    mock_indices = {
        "上证指数": {"code": "000001.SH", "price": 3356.78, "change": "+0.65%"},
        "深证成指": {"code": "399001.SZ", "price": 10892.34, "change": "+0.82%"},
        "创业板指": {"code": "399006.SZ", "price": 2198.56, "change": "+1.15%"},
        "沪深300": {"code": "000300.SH", "price": 3987.45, "change": "+0.73%"},
    }

    for name, data in mock_indices.items():
        if index_name in name:
            return (
                f"📊 {name}（{data['code']}）\n"
                f"  最新点位：{data['price']}\n"
                f"  涨跌幅：{data['change']}\n"
                f"  数据时间：2025年12月20日 15:00"
            )

    return f"未找到指数「{index_name}」的数据。支持查询：上证指数、深证成指、创业板指、沪深300"


# ==================== 6. 构建 Agent（路由：RAG + 实时数据） ====================


def build_agent(rag_chain: RetrievalQA, llm: ChatOpenAI) -> AgentExecutor:
    """
    构建 Agent，自动路由用户问题到：
    - 知识库问答（RAG）
    - 实时数据查询（股价、指数等）
    """

    # 将 RAG 链包装为 Tool
    rag_tool = Tool(
        name="knowledge_base_qa",
        func=lambda q: rag_chain.invoke({"query": q})["result"],
        description=(
            "金融知识库问答工具。用于查询公司内部知识，包括：基金产品信息、"
            "风控制度、客户FAQ、投资研究报告等。当用户询问公司产品、规章制度、"
            "投资策略等问题时，使用此工具。"
        ),
    )

    tools = [rag_tool, get_stock_price, get_market_index]

    # 使用 ReAct Agent prompt
    react_prompt = PromptTemplate.from_template(
        """你是一位专业的金融助手。你可以使用以下工具来回答用户的问题：

{tools}

工具名称列表：{tool_names}

请使用以下格式回答：

Question: 用户的问题
Thought: 我需要思考应该使用哪个工具
Action: 工具名称（必须是 [{tool_names}] 中的一个）
Action Input: 工具的输入参数
Observation: 工具返回的结果
... (可以重复多次 Thought/Action/Action Input/Observation)
Thought: 我现在知道最终答案了
Final Answer: 给用户的最终回答

注意：
- 如果问到股价、行情、实时数据，使用 get_stock_price 或 get_market_index
- 如果问到公司产品、制度、行业研究等知识性问题，使用 knowledge_base_qa
- 回答要专业、准确、使用中文

开始！

Question: {input}
Thought: {agent_scratchpad}"""
    )

    agent = create_react_agent(llm, tools, react_prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,         # 打印推理过程
        handle_parsing_errors=True,
        max_iterations=5,
    )

    return agent_executor


# ==================== 7. 主程序 ====================


def main():
    print("=" * 60)
    print("🏦 金融资产问答系统 - LangChain RAG Demo")
    print("=" * 60)

    # 1. 初始化 LLM
    print("\n🤖 初始化 LLM...")
    llm = ChatOpenAI(
        model="gpt-4.1-mini",     # 可换成 gpt-4o 或其他模型
        temperature=0,
        base_url=OPENAI_BASE_URL,
    )

    # 2. 创建示例知识库
    print("\n📚 准备知识库...")
    knowledge_dir = create_sample_knowledge_base()

    # 3. 构建 RAG 链
    rag_chain = build_rag_chain(knowledge_dir, llm)

    # 4. 构建 Agent
    print("🤖 构建智能 Agent...")
    agent = build_agent(rag_chain, llm)
    print("   ✅ Agent 构建完成！\n")

    # 5. 示例问题测试
    test_questions = [
        # RAG 知识库问题
        "稳健增长混合基金A的风险等级是多少？历史业绩如何？",
        "公司的风控制度中，单只股票的持仓上限是多少？",
        "基金赎回到账需要多长时间？",
        "2025年四季度有哪些超配行业建议？",
        # 实时数据问题
        "贵州茅台现在的股价是多少？",
        "帮我查一下上证指数的最新行情",
    ]

    print("=" * 60)
    print("📝 开始测试问答...")
    print("=" * 60)

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─' * 50}")
        print(f"❓ 问题 {i}：{question}")
        print(f"{'─' * 50}")
        try:
            result = agent.invoke({"input": question})
            print(f"\n💡 回答：{result['output']}")
        except Exception as e:
            print(f"\n❌ 出错：{e}")

    # 6. 交互模式
    print("\n" + "=" * 60)
    print("💬 进入交互模式（输入 'quit' 退出）")
    print("=" * 60)

    while True:
        question = input("\n🙋 请输入问题：").strip()
        if question.lower() in ("quit", "exit", "q", "退出"):
            print("👋 再见！")
            break
        if not question:
            continue

        try:
            result = agent.invoke({"input": question})
            print(f"\n💡 回答：{result['output']}")
        except Exception as e:
            print(f"\n❌ 出错：{e}")


# ==================== 8. 仅测试 RAG 部分（不需要 Agent） ====================


def test_rag_only():
    """仅测试 RAG 知识库问答，不使用 Agent"""

    print("=" * 60)
    print("📚 RAG 知识库问答测试（无 Agent 模式）")
    print("=" * 60)

    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, base_url=OPENAI_BASE_URL)

    knowledge_dir = create_sample_knowledge_base()
    rag_chain = build_rag_chain(knowledge_dir, llm)

    questions = [
        "稳健增长基金的基金经理是谁？管理费率多少？",
        "公司风控制度中的VaR限额是多少？",
        "基金定投怎么设置？",
    ]

    for q in questions:
        print(f"\n❓ {q}")
        result = rag_chain.invoke({"query": q})
        print(f"💡 {result['result']}")
        print(f"📄 来源：{[doc.metadata['source'] for doc in result['source_documents']]}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--rag-only":
        test_rag_only()
    else:
        main()
