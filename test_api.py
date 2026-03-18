#!/usr/bin/env python
"""
API测试脚本
==========

快速测试FastAPI服务的各个端点。

使用方法：
    1. 先启动API服务：python start_api.py --dev
    2. 然后运行此脚本：python test_api.py
"""

import requests
import json
import time
from typing import Dict, Any


# API基础URL
BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_response(response: requests.Response):
    """格式化打印响应"""
    print(f"\n状态码: {response.status_code}")
    try:
        data = response.json()
        print("响应内容:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"响应内容: {response.text}")


def test_root():
    """测试根端点"""
    print_section("1️⃣ 测试根端点 GET /")

    try:
        response = requests.get(f"{BASE_URL}/")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_health():
    """测试健康检查"""
    print_section("2️⃣ 测试健康检查 GET /api/health")

    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_status():
    """测试系统状态"""
    print_section("3️⃣ 测试系统状态 GET /api/status")

    try:
        response = requests.get(f"{BASE_URL}/api/status")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_chat_stock_price():
    """测试问答 - 股价查询"""
    print_section("4️⃣ 测试问答 - 股价查询 POST /api/chat")

    question = "阿里巴巴现在的股价是多少？"
    print(f"\n问题: {question}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"question": question},
            timeout=60  # LLM响应可能需要时间
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            print("\n" + "─" * 70)
            print("📝 问题:", data.get("question"))
            print("💡 回答:")
            print(data.get("answer"))
            print("─" * 70)

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_chat_knowledge():
    """测试问答 - 知识库查询"""
    print_section("5️⃣ 测试问答 - 知识库查询 POST /api/chat")

    question = "什么是市盈率？"
    print(f"\n问题: {question}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"question": question},
            timeout=60
        )
        print_response(response)

        if response.status_code == 200:
            data = response.json()
            print("\n" + "─" * 70)
            print("📝 问题:", data.get("question"))
            print("💡 回答:")
            print(data.get("answer"))
            print("─" * 70)

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_models():
    """测试模型信息"""
    print_section("6️⃣ 测试模型信息 GET /api/models")

    try:
        response = requests.get(f"{BASE_URL}/api/models")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_config():
    """测试配置信息"""
    print_section("7️⃣ 测试配置信息 GET /api/config")

    try:
        response = requests.get(f"{BASE_URL}/api/config")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("🧪 Financial QA API - 测试脚本")
    print("=" * 70)
    print(f"\nAPI服务地址: {BASE_URL}")
    print("\n正在检查服务是否可用...")

    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ 服务正在运行")
        else:
            print("❌ 服务响应异常")
            return
    except Exception as e:
        print(f"\n❌ 无法连接到API服务")
        print(f"   错误: {e}")
        print("\n请先启动API服务：")
        print("   python start_api.py --dev")
        return

    # 运行测试
    results = []

    results.append(("根端点", test_root()))
    time.sleep(0.5)

    results.append(("健康检查", test_health()))
    time.sleep(0.5)

    results.append(("系统状态", test_status()))
    time.sleep(0.5)

    results.append(("模型信息", test_models()))
    time.sleep(0.5)

    results.append(("配置信息", test_config()))
    time.sleep(0.5)

    print("\n" + "=" * 70)
    print("⏳ 开始测试问答功能（可能需要较长时间）...")
    print("=" * 70)

    results.append(("问答-股价", test_chat_stock_price()))
    time.sleep(1)

    results.append(("问答-知识库", test_chat_knowledge()))

    # 打印测试总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name:15s} {status}")

    print("\n" + "─" * 70)
    print(f"  总计: {passed}/{total} 个测试通过")
    print("─" * 70)

    if passed == total:
        print("\n🎉 所有测试通过！API服务运行正常。")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查错误信息。")

    print("\n💡 提示:")
    print("   - API文档: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("   - 详细使用指南: API_GUIDE.md")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
