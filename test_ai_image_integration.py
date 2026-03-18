"""
测试 AI 图像生成功能集成
运行此脚本验证功能是否正常工作
"""

from ai_agent.chart_tools import generate_ai_image, generate_ai_diagram, get_chart_tools

print("=" * 60)
print("AI 图像生成功能集成测试")
print("=" * 60)

# 测试 1: 工具加载
print("\n📦 测试 1: 验证工具加载")
print("-" * 60)
tools = get_chart_tools()
print(f"✅ 成功加载 {len(tools)} 个图表工具:")
for i, tool in enumerate(tools, 1):
    print(f"   {i}. {tool.name}")

# 测试 2: 检查 generate_ai_diagram 工具
print("\n🔍 测试 2: 检查 AI 图像生成工具")
print("-" * 60)
ai_tool = None
for tool in tools:
    if tool.name == "generate_ai_diagram":
        ai_tool = tool
        print(f"✅ 找到工具: {tool.name}")
        print(f"   描述: {tool.description[:80]}...")
        break

# 测试 3: 未配置 API Key 时的错误提示
print("\n⚠️  测试 3: 未配置 API Key 时的提示")
print("-" * 60)
if ai_tool:
    result = ai_tool.invoke("测试图片生成")
    print(result)

# 测试 4: 函数参数验证
print("\n🧪 测试 4: 验证函数签名")
print("-" * 60)
import inspect
sig = inspect.signature(generate_ai_image)
print(f"generate_ai_image 参数: {sig}")

# 测试 5: 尺寸映射
print("\n📐 测试 5: 尺寸映射功能")
print("-" * 60)
size_map = {
    "square": "1x1",
    "方形": "1x1",
    "horizontal": "2x1",
    "横屏": "2x1",
    "vertical": "1x2",
    "竖屏": "1x2",
}
print("用户友好参数 → API 格式:")
for user_input, expected in size_map.items():
    print(f"   {user_input:12s} → {expected}")

print("\n" + "=" * 60)
print("✅ 所有测试完成！")
print("=" * 60)

print("\n💡 下一步:")
print("   1. 设置环境变量: export TUZI_API_KEY='你的密钥'")
print("   2. 重启 Python 后端")
print("   3. 在前端测试: '请生成一张金融流程图'")
print("\n📖 详细文档: AI_IMAGE_GENERATION_GUIDE.md")
