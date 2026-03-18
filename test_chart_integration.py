"""
测试图表工具集成
================
测试 chart_tools 是否正常工作
"""

import json
from ai_agent.chart_tools import (
    generate_financial_chart,
    generate_chart_from_text,
    get_chart_tools
)

print("=" * 60)
print("📊 测试图表工具集成")
print("=" * 60)

# 测试1: 生成折线图
print("\n📈 测试1: 生成折线图")
request_data = {
    "chart_type": "line",
    "title": "基金年度收益率趋势",
    "data": [
        {"label": "2023年", "value": 12.5},
        {"label": "2024年", "value": 8.3},
        {"label": "2025年", "value": 15.2}
    ]
}
result = generate_financial_chart.invoke(json.dumps(request_data))
print(f"结果: {result}")

# 测试2: 生成饼图
print("\n🥧 测试2: 生成饼图")
request_data = {
    "chart_type": "pie",
    "title": "资产配置比例",
    "data": [
        {"label": "股票", "value": 60},
        {"label": "债券", "value": 30},
        {"label": "现金", "value": 10}
    ]
}
result = generate_financial_chart.invoke(json.dumps(request_data))
print(f"结果: {result}")

# 测试3: 从文本生成图表
print("\n📝 测试3: 从文本自动解析生成图表")
text_data = """
2023年收益率：12.5%
2024年收益率：8.3%
2025年收益率：15.2%
"""
result = generate_chart_from_text.invoke(text_data)
print(f"结果: {result}")

# 测试4: 验证工具列表
print("\n📋 测试4: 验证工具列表")
tools = get_chart_tools()
print(f"✅ 找到 {len(tools)} 个图表工具:")
for tool in tools:
    print(f"  - {tool.name}: {tool.description[:50]}...")

print("\n🎉 所有测试完成!")
print("=" * 60)
