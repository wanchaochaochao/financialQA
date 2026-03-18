"""
Agent Core Module
=================

Builds and manages the LangChain ReAct agent that routes queries
to appropriate tools (RAG or financial data APIs).
"""

from typing import List
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate

from .config import Config
from .rag_system import RAGSystem
from .tools.financial_tools import get_all_tools
from .chart_tools import get_chart_tools


class FinancialQAAgent:
    """
    Financial Question Answering Agent.

    Routes user queries to:
    1. Market data APIs (for real-time prices, historical data)
    2. RAG knowledge base (for financial concepts, company policies)
    """

    def __init__(self, llm: ChatOpenAI, rag_system: RAGSystem):
        """
        Initialize the agent.

        Args:
            llm: Language model instance
            rag_system: RAG system instance
        """
        self.llm = llm
        self.rag_system = rag_system
        self.agent_executor = None

        self._build_agent()

    def _build_agent(self):
        """Build the ReAct agent with all tools"""

        # Get financial data tools
        financial_tools = get_all_tools()

        # Get chart visualization tools
        chart_tools = get_chart_tools()

        # Wrap RAG system as a tool
        rag_tool = Tool(
            name="knowledge_base_qa",
            func=lambda q: self.rag_system.query(q)["result"],
            description=(
                "金融知识库问答工具。用于查询：\n"
                "1. 金融术语和概念（如：市盈率是什么？收入和净利润的区别？）\n"
                "2. 公司产品信息（如：稳健增长基金的风险等级？）\n"
                "3. 公司制度规定（如：风控制度中的持仓限额？）\n"
                "4. 投资研究报告（如：2025年行业配置建议？）\n"
                "5. 客户服务FAQ（如：基金赎回到账时间？）\n\n"
                "注意：此工具不能查询实时行情数据，行情数据请使用其他工具。"
            ),
        )

        # Combine all tools
        tools = [rag_tool] + financial_tools + chart_tools

        # Create ReAct prompt
        react_prompt = PromptTemplate.from_template(
            """你是一位专业的金融问答助手。你可以使用以下工具来回答用户的问题：

{tools}

工具名称列表：{tool_names}

**工具选择指南**：
1. 如果问题涉及**实时股价、行情、涨跌幅**等市场数据，使用 get_stock_price_tool 或 get_stock_history_tool 或 get_market_index_tool
2. 如果问题涉及**金融概念、公司产品、制度、研究报告、FAQ**等知识性内容，使用 knowledge_base_qa
3. 如果问题涉及**数据可视化、绘制图表**（如折线图、饼图、柱状图、雷达图），使用 generate_financial_chart 或 generate_chart_from_text
4. 如果问题同时涉及多个方面，可以多次使用不同的工具

**回答要求（关键）**：
1. 回答要准确、专业、结构清晰
2. **严格区分"客观数据"（来自工具）和"分析性描述"（来自你的推理）**
3. **绝不编造数据**：如果工具没有返回相关数据，明确告知用户"暂无数据"，不要猜测
4. **数据来源已在工具输出中标注**：直接使用工具返回的格式化结果，其中已包含数据来源标签
5. **承认局限性**：如果无法回答或数据不足，诚实告知用户
6. **看到工具成功标识（✅）后，立即输出 Final Answer**，不要重复调用相同工具
7. 使用中文回答

**幻觉控制原则**：
- ✅ 正确：基于工具返回的客观数据回答
- ❌ 错误：编造、推测、臆想不存在的数据
- ✅ 正确："根据Yahoo Finance数据，阿里巴巴最新股价为..."
- ❌ 错误："我认为阿里巴巴股价大约是..."

使用以下格式：

Question: 用户的问题
Thought: 我需要思考应该使用哪个工具来回答这个问题
Action: 工具名称（必须是 [{tool_names}] 中的一个）
Action Input: 工具的输入参数
Observation: 工具返回的结果
... (可以重复多次 Thought/Action/Action Input/Observation)
Thought: 我现在知道最终答案了
Final Answer: 给用户的最终回答（结构化、专业、数据驱动）

开始！

Question: {input}
Thought: {agent_scratchpad}"""
        )

        # Create agent
        agent = create_react_agent(self.llm, tools, react_prompt)

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=Config.AGENT_VERBOSE,
            handle_parsing_errors=True,
            max_iterations=Config.AGENT_MAX_ITERATIONS,
            max_execution_time=Config.AGENT_MAX_EXECUTION_TIME,
        )

    def query(self, question: str) -> dict:
        """
        Query the agent with a question.

        Args:
            question: User question

        Returns:
            Dictionary with 'input' and 'output'
        """
        try:
            result = self.agent_executor.invoke({"input": question})
            return result
        except Exception as e:
            return {
                "input": question,
                "output": f"❌ 查询失败：{str(e)}"
            }

    def chat(self, question: str) -> str:
        """
        Simplified chat interface.

        Args:
            question: User question

        Returns:
            Agent's answer as a string
        """
        result = self.query(question)
        return result.get("output", "抱歉，我无法回答这个问题。")


def build_financial_agent(rebuild_kb: bool = False) -> FinancialQAAgent:
    """
    Build a complete financial QA agent.

    Args:
        rebuild_kb: Whether to rebuild the knowledge base from scratch

    Returns:
        FinancialQAAgent instance
    """
    # Initialize LLM
    llm = ChatOpenAI(
        model=Config.LLM_MODEL,
        temperature=Config.LLM_TEMPERATURE,
        base_url=Config.OPENAI_BASE_URL,
    )

    # Initialize RAG system
    print("🤖 Initializing RAG system...")
    rag_system = RAGSystem(llm, rebuild=rebuild_kb)

    # Build agent
    print("🤖 Building agent...")
    agent = FinancialQAAgent(llm, rag_system)
    print("✅ Agent ready!\n")

    return agent
