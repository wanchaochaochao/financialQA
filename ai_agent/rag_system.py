"""
RAG Knowledge Base System
==========================

Manages document loading, chunking, vectorization, and retrieval
for the financial knowledge base.
"""

from pathlib import Path
from typing import List, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

from .config import Config


class KnowledgeBaseManager:
    """
    Manages the financial knowledge base:
    - Document creation and loading
    - Text chunking
    - Vector embedding and storage
    - Retrieval chain construction
    """

    @staticmethod
    def create_sample_knowledge_base() -> Path:
        """
        Create sample financial knowledge base documents.

        Returns:
            Path to the knowledge base directory
        """
        knowledge_dir = Config.KNOWLEDGE_BASE_DIR
        knowledge_dir.mkdir(exist_ok=True)

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
随着消费场景持续恢复,社会消费品零售总额同比增长6.5%。
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
            "金融术语词典.txt": """
# 金融术语词典

## 市盈率 (P/E Ratio)
市盈率是指股票价格除以每股收益的比率，用于评估股票的估值水平。
计算公式：市盈率 = 股价 / 每股收益
- 高市盈率：可能表示市场对公司未来增长预期较高，或股票被高估
- 低市盈率：可能表示股票被低估，或公司增长前景不佳

## 市净率 (P/B Ratio)
市净率是指股价与每股净资产的比率。
计算公式：市净率 = 股价 / 每股净资产
用于衡量股票价格相对于公司净资产的水平。

## 收入 vs 净利润
- **收入**（Revenue）：公司在一定期间内通过销售商品或提供服务获得的总收入
- **净利润**（Net Profit）：收入减去所有成本、费用、税金后的最终利润
- 关系：净利润 = 收入 - 成本 - 费用 - 税金

## 每股收益 (EPS)
每股收益是指公司净利润除以总股本。
计算公式：EPS = 净利润 / 总股本
是衡量公司盈利能力的重要指标。

## ROE (净资产收益率)
净资产收益率反映股东权益的收益水平。
计算公式：ROE = 净利润 / 净资产
- ROE > 15%：通常被认为是优秀的盈利能力
- ROE < 5%：盈利能力较弱

## 股息率 (Dividend Yield)
股息率是指每股股息与股价的比率。
计算公式：股息率 = 每股股息 / 股价
用于衡量投资股票的现金回报率。
""",
        }

        # Write documents to knowledge base directory
        created_count = 0
        for filename, content in docs.items():
            filepath = knowledge_dir / filename
            if not filepath.exists():
                filepath.write_text(content, encoding="utf-8")
                created_count += 1

        return knowledge_dir

    @staticmethod
    def load_documents(knowledge_dir: Path) -> List[Document]:
        """
        Load all text documents from the knowledge base directory.

        Args:
            knowledge_dir: Path to the knowledge base directory

        Returns:
            List of Document objects
        """
        documents = []
        for file_path in knowledge_dir.glob("*.txt"):
            try:
                loader = TextLoader(str(file_path), encoding="utf-8")
                documents.extend(loader.load())
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")

        return documents

    @staticmethod
    def split_documents(documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks for better retrieval.

        Args:
            documents: List of Document objects

        Returns:
            List of chunked Document objects
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "；", " ", ""],
            length_function=len,
        )

        split_docs = text_splitter.split_documents(documents)
        return split_docs

    @staticmethod
    def build_vectorstore(documents: List[Document]) -> FAISS:
        """
        Build FAISS vector store from documents.

        Args:
            documents: List of chunked Document objects

        Returns:
            FAISS vector store
        """
        embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            openai_api_base=Config.OPENAI_BASE_URL,
        )

        vectorstore = FAISS.from_documents(documents, embeddings)

        # Save to disk for persistence
        vectorstore.save_local(str(Config.FAISS_INDEX_DIR))

        return vectorstore

    @staticmethod
    def load_vectorstore() -> Optional[FAISS]:
        """
        Load existing FAISS vector store from disk.

        Returns:
            FAISS vector store or None if not found
        """
        if not Config.FAISS_INDEX_DIR.exists():
            return None

        try:
            embeddings = OpenAIEmbeddings(
                model=Config.EMBEDDING_MODEL,
                openai_api_base=Config.OPENAI_BASE_URL,
            )
            vectorstore = FAISS.load_local(
                str(Config.FAISS_INDEX_DIR),
                embeddings,
                allow_dangerous_deserialization=True
            )
            return vectorstore
        except Exception as e:
            print(f"Warning: Failed to load vector store: {e}")
            return None


class RAGSystem:
    """
    Complete RAG (Retrieval-Augmented Generation) system.
    """

    def __init__(self, llm: ChatOpenAI, rebuild: bool = False):
        """
        Initialize RAG system.

        Args:
            llm: Language model instance
            rebuild: Whether to rebuild the vector store from scratch
        """
        self.llm = llm
        self.vectorstore = None
        self.rag_chain = None

        # Create knowledge base if not exists
        knowledge_dir = KnowledgeBaseManager.create_sample_knowledge_base()

        # Try to load existing vector store
        if not rebuild:
            self.vectorstore = KnowledgeBaseManager.load_vectorstore()

        # Build vector store if needed
        if self.vectorstore is None:
            print("📚 Building knowledge base...")
            documents = KnowledgeBaseManager.load_documents(knowledge_dir)
            print(f"   Loaded {len(documents)} documents")

            split_docs = KnowledgeBaseManager.split_documents(documents)
            print(f"   Split into {len(split_docs)} chunks")

            self.vectorstore = KnowledgeBaseManager.build_vectorstore(split_docs)
            print("   ✅ Vector store built and saved")
        else:
            print("✅ Loaded existing vector store")

        # Build RAG chain
        self._build_rag_chain()

    def _build_rag_chain(self):
        """Build the RAG chain with retriever and prompt"""
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": Config.RETRIEVAL_TOP_K},
        )

        rag_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""你是一位专业的金融顾问助手。请根据以下参考资料回答用户的问题。

**重要指引**：
1. 如果参考资料中有相关信息，请基于资料回答，并适当引用关键数据
2. 如果参考资料中没有相关信息，请明确告知用户"知识库中暂无相关信息"
3. 回答要准确、专业、结构清晰
4. 区分"客观事实"和"分析性描述"
5. **必须**在回答开头添加"【数据来源】内部知识库"标签
6. **必须**在回答结尾添加"注：以上信息来自内部知识库，如需最新数据请查询实时行情"

参考资料：
{context}

用户问题：{question}

专业回答：""",
        )

        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": rag_prompt},
        )

    def query(self, question: str) -> dict:
        """
        Query the RAG system.

        Args:
            question: User question

        Returns:
            Dictionary with 'result' and 'source_documents'
        """
        return self.rag_chain.invoke({"query": question})

    def get_chain(self) -> RetrievalQA:
        """Get the RAG chain for use in agents"""
        return self.rag_chain
