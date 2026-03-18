"""
Financial Asset QA System - Main Entry Point
=============================================

Main program with CLI interface for testing the financial QA agent.
"""

import sys
from typing import List
from .agent_core import build_financial_agent
from .config import Config


def print_header():
    """Print system header"""
    print("=" * 70)
    print("🏦 金融资产问答系统 (Financial Asset QA System)")
    print("=" * 70)
    print("\n基于 LangChain ReAct Agent + RAG + Yahoo Finance API")
    print(f"LLM 模型: {Config.LLM_MODEL}")
    print(f"Embedding 模型: {Config.EMBEDDING_MODEL}")
    print()


def run_test_questions(agent):
    """Run a set of test questions"""
    test_questions = [
        # RAG 知识库问题
        {
            "category": "知识库 - 基金产品",
            "question": "稳健增长混合基金A的风险等级是多少？历史业绩如何？"
        },
        {
            "category": "知识库 - 风控制度",
            "question": "公司的风控制度中，单只股票的持仓上限是多少？"
        },
        {
            "category": "知识库 - 金融术语",
            "question": "什么是市盈率？收入和净利润的区别是什么？"
        },
        {
            "category": "知识库 - 投资研究",
            "question": "2025年四季度有哪些超配行业建议？"
        },

        # 实时数据问题
        {
            "category": "市场数据 - 股价查询",
            "question": "阿里巴巴现在的股价是多少？"
        },
        {
            "category": "市场数据 - 历史涨跌",
            "question": "特斯拉最近7天涨跌情况如何？"
        },
        {
            "category": "市场数据 - 指数行情",
            "question": "帮我查一下上证指数的最新行情"
        },

        # 综合问题
        {
            "category": "综合分析",
            "question": "贵州茅台最近30天走势如何？公司的基金有持仓吗？"
        },
    ]

    print("=" * 70)
    print("📝 开始测试问答...")
    print("=" * 70)

    for i, item in enumerate(test_questions, 1):
        print(f"\n{'─' * 70}")
        print(f"❓ 问题 {i} [{item['category']}]")
        print(f"   {item['question']}")
        print(f"{'─' * 70}")

        try:
            answer = agent.chat(item['question'])
            print(f"\n💡 回答：\n{answer}")
        except Exception as e:
            print(f"\n❌ 出错：{e}")

        print()


def run_interactive_mode(agent):
    """Run interactive chat mode"""
    print("=" * 70)
    print("💬 交互模式（输入 'quit' 或 'exit' 退出）")
    print("=" * 70)
    print("\n提示：您可以询问：")
    print("  - 股票行情（如：阿里巴巴股价、特斯拉7天涨跌）")
    print("  - 金融知识（如：什么是市盈率？）")
    print("  - 公司产品（如：基金产品信息、风控制度）")
    print()

    while True:
        try:
            question = input("\n🙋 请输入问题：").strip()

            if question.lower() in ("quit", "exit", "q", "退出"):
                print("👋 再见！")
                break

            if not question:
                continue

            answer = agent.chat(question)
            print(f"\n💡 回答：\n{answer}")

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 出错：{e}")


def main():
    """Main function"""
    # Parse arguments
    run_tests = "--test" in sys.argv
    rebuild_kb = "--rebuild" in sys.argv
    interactive_only = "--interactive" in sys.argv

    # Print header
    print_header()

    try:
        # Validate config
        Config.validate()

        # Build agent
        agent = build_financial_agent(rebuild_kb=rebuild_kb)

        # Run test questions
        if run_tests or not interactive_only:
            run_test_questions(agent)

        # Run interactive mode
        if not run_tests or interactive_only:
            run_interactive_mode(agent)

    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 系统错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    """
    使用方法：

    1. 运行测试问题 + 交互模式（默认）：
       python -m ai_agent.main

    2. 仅运行测试问题：
       python -m ai_agent.main --test

    3. 仅交互模式：
       python -m ai_agent.main --interactive

    4. 重建知识库：
       python -m ai_agent.main --rebuild
    """
    main()
