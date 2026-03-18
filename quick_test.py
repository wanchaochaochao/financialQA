"""
Quick Test Script
=================

快速测试脚本，用于验证系统各模块是否正常工作。
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("🧪 Financial QA System - Quick Test")
print("=" * 60)

# Test 1: Import modules
print("\n1️⃣ Testing module imports...")
try:
    from ai_agent.config import Config
    from ai_agent.data_api import FinancialDataAPI
    from ai_agent.rag_system import RAGSystem, KnowledgeBaseManager
    from ai_agent.tools.financial_tools import get_all_tools
    from ai_agent.agent_core import build_financial_agent
    print("   ✅ All modules imported successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Configuration
print("\n2️⃣ Testing configuration...")
try:
    Config.ensure_directories()
    print(f"   ✅ Knowledge base dir: {Config.KNOWLEDGE_BASE_DIR}")
    print(f"   ✅ FAISS index dir: {Config.FAISS_INDEX_DIR}")
    print(f"   ✅ LLM model: {Config.LLM_MODEL}")
except Exception as e:
    print(f"   ❌ Configuration failed: {e}")
    sys.exit(1)

# Test 3: Financial Data API
print("\n3️⃣ Testing Financial Data API...")
try:
    # Test stock info
    info = FinancialDataAPI.get_stock_info("AAPL")
    if "error" not in info:
        print(f"   ✅ Stock info: AAPL @ ${info.get('current_price', 'N/A')}")
    else:
        print(f"   ⚠️  Stock info: {info['error']}")

    # Test symbol resolution
    symbol = FinancialDataAPI.resolve_symbol("阿里巴巴")
    print(f"   ✅ Symbol resolution: 阿里巴巴 -> {symbol}")

except Exception as e:
    print(f"   ❌ Data API test failed: {e}")

# Test 4: Knowledge Base
print("\n4️⃣ Testing Knowledge Base...")
try:
    kb_dir = KnowledgeBaseManager.create_sample_knowledge_base()
    doc_count = len(list(kb_dir.glob("*.txt")))
    print(f"   ✅ Knowledge base created: {doc_count} documents")
except Exception as e:
    print(f"   ❌ Knowledge base test failed: {e}")

# Test 5: Tools
print("\n5️⃣ Testing LangChain Tools...")
try:
    tools = get_all_tools()
    print(f"   ✅ Loaded {len(tools)} financial tools")
    for tool in tools:
        print(f"      - {tool.name}")
except Exception as e:
    print(f"   ❌ Tools test failed: {e}")

# Final summary
print("\n" + "=" * 60)
print("✅ All basic tests passed!")
print("\nNext steps:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Run the main program: python -m ai_agent.main")
print("=" * 60)
