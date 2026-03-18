"""
测试图表 HTTP 访问功能
====================
测试生成的图表是否可以通过 HTTP 访问
"""

import json
from ai_agent.chart_tools import generate_financial_chart, generate_chart_from_text

print("=" * 60)
print("🌐 测试图表 HTTP 访问功能")
print("=" * 60)

# 测试1: 生成折线图并获取 URL
print("\n📈 测试1: 生成折线图")
request_data = {
    "chart_type": "line",
    "title": "月度销售趋势",
    "data": [
        {"label": "1月", "value": 100},
        {"label": "2月", "value": 120},
        {"label": "3月", "value": 150}
    ]
}
result = generate_financial_chart.invoke(json.dumps(request_data))
print("返回结果：")
print(result)
print()

# 测试2: 从文本生成图表
print("📝 测试2: 从文本生成图表")
text_data = """
苹果公司：35%
微软：25%
谷歌：20%
其他：20%
"""
result = generate_chart_from_text.invoke(text_data)
print("返回结果：")
print(result)
print()

print("=" * 60)
print("✅ 测试完成！")
print()
print("📌 启动 Python 后端以访问图表：")
print("   cd /Users/wanchao/financialQA")
print("   python -m ai_agent.api")
print()
print("📌 然后在浏览器中访问上面显示的 URL")
print("=" * 60)
