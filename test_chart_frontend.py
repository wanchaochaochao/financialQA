"""
测试图表前端显示功能
===================
测试生成的图表是否返回正确的 Markdown 格式
"""

import json
from ai_agent.chart_tools import generate_financial_chart, generate_chart_from_text

print("=" * 70)
print("🖼️  测试图表前端显示功能")
print("=" * 70)

# 测试1: 生成折线图
print("\n📈 测试1: 生成折线图")
request_data = {
    "chart_type": "line",
    "title": "月度销售额趋势",
    "data": [
        {"label": "1月", "value": 100},
        {"label": "2月", "value": 120},
        {"label": "3月", "value": 150},
        {"label": "4月", "value": 180}
    ]
}
result = generate_financial_chart.invoke(json.dumps(request_data))
print("AI 返回的消息：")
print("-" * 70)
print(result)
print("-" * 70)
print()

# 检查是否包含 Markdown 图片语法
if "![" in result and "](" in result:
    print("✅ 包含 Markdown 图片语法")
else:
    print("❌ 未包含 Markdown 图片语法")

if "http://localhost:8000/charts/" in result:
    print("✅ 包含图片 URL")
else:
    print("❌ 未包含图片 URL")

print()

# 测试2: 从文本生成图表
print("📊 测试2: 从文本生成饼图数据")
text_data = """
股票：60%
债券：30%
现金：10%
"""
result = generate_chart_from_text.invoke(text_data)
print("AI 返回的消息：")
print("-" * 70)
print(result)
print("-" * 70)
print()

# 检查格式
if "![" in result and "](" in result:
    print("✅ 包含 Markdown 图片语法")
else:
    print("❌ 未包含 Markdown 图片语法")

print()
print("=" * 70)
print("📌 预期行为：")
print("   1. Python 后端启动: python -m ai_agent.api")
print("   2. Next.js 前端启动: cd web-app && npm run dev")
print("   3. 访问 http://localhost:3000")
print("   4. 登录后，在聊天框输入：请帮我生成一个折线图")
print("   5. AI 回复中应该直接显示图表图片")
print("=" * 70)
