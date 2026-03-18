"""
金融数据可视化工具 - Chart Tools
================================
功能：
1. 数据解析：从文本/表格/JSON 中提取结构化数据
2. 标准图表：折线图、饼图、柱状图、雷达图等（matplotlib）
3. AI图像生成：流程图、商业模型图等复杂图像（预留功能）
4. LangChain Tool 集成：可注册到 Agent，实现自然语言驱动绘图

依赖：
    matplotlib, pandas, requests, Pillow
"""

import os
import json
import re
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import matplotlib
matplotlib.use("Agg")  # 非交互后端，适用于服务器/脚本环境
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import requests

from langchain_core.tools import tool
from .config import Config

# ==================== 配置 ====================

# 图表输出目录（在 ai_agent 目录下）
CHART_OUTPUT_DIR = Config.BASE_DIR / "chart_output"
CHART_OUTPUT_DIR.mkdir(exist_ok=True)

# API 基础 URL（用于生成可访问的图片 URL）
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# AI 图像生成 API 配置（tu-zi.com - OpenAI 兼容接口）
TUZI_API_URL = "https://api.tu-zi.com/v1/images/generations"
TUZI_API_KEY = os.getenv("TUZI_API_KEY", "")
TUZI_MODEL = "gemini-3.1-flash-image-preview"

# ==================== 1. 中文字体配置 ====================


def setup_chinese_font():
    """
    配置 matplotlib 中文字体。
    优先使用项目内嵌字体，找不到时回退到系统字体。
    """
    # 方案1: 项目内嵌字体
    bundled_font_dir = Path(__file__).parent.parent / "fonts"
    if bundled_font_dir.exists():
        for ext in ["*.ttf", "*.otf", "*.ttc"]:
            for font_file in bundled_font_dir.glob(ext):
                fm.fontManager.addfont(str(font_file))
        bundled_names = ["Noto Sans SC", "Noto Sans CJK SC", "Source Han Sans SC"]
        available = {f.name for f in fm.fontManager.ttflist}
        for name in bundled_names:
            if name in available:
                plt.rcParams["font.sans-serif"] = [name]
                plt.rcParams["axes.unicode_minus"] = False
                return name

    # 方案2: 系统字体
    system_fonts = [
        "PingFang SC", ".PingFang SC",
        "Heiti SC", "STHeiti",
        "Arial Unicode MS",
        "Noto Sans CJK SC",
        "WenQuanYi Micro Hei",
        "WenQuanYi Zen Hei",
        "Microsoft YaHei", "SimHei",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in system_fonts:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name]
            plt.rcParams["axes.unicode_minus"] = False
            return name

    plt.rcParams["axes.unicode_minus"] = False
    return None


CHINESE_FONT = setup_chinese_font()


# ==================== 2. 数据解析层 ====================


def parse_kv_from_text(text: str) -> pd.DataFrame:
    """
    从文本中提取 key-value 数据对。
    支持格式：
      - "2023年收益率：12.5%"
      - "贵州茅台 - 8.5%"
      - "GDP增速预计为5.2%"
    """
    patterns = [
        # 模式1: "xxx：数字%" 或 "xxx: 数字"
        r"[·\-\d.]*\s*(.+?)[：:]\s*([\d.]+)%?",
        # 模式2: "xxx - 数字%"
        r"[·\-\d.]*\s*(.+?)\s*[-–]\s*([\d.]+)%?",
    ]

    results = []
    for line in text.strip().split("\n"):
        line = line.strip().lstrip("- ·•*1234567890.")
        if not line:
            continue
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                key = match.group(1).strip()
                try:
                    value = float(match.group(2))
                    results.append({"label": key, "value": value})
                except ValueError:
                    pass
                break

    return pd.DataFrame(results) if results else pd.DataFrame(columns=["label", "value"])


def parse_table_data(data_input: str) -> pd.DataFrame:
    """
    智能解析多种格式输入为 DataFrame。
    支持：JSON字符串、CSV格式、Markdown表格、key-value文本
    """
    data_input = data_input.strip()

    # 尝试1: JSON
    try:
        parsed = json.loads(data_input)
        if isinstance(parsed, list):
            return pd.DataFrame(parsed)
        elif isinstance(parsed, dict):
            return pd.DataFrame([parsed])
    except (json.JSONDecodeError, ValueError):
        pass

    # 尝试2: CSV 格式（含逗号分隔的多行）
    if "," in data_input and "\n" in data_input:
        lines = data_input.strip().split("\n")
        if len(lines) >= 2:
            try:
                from io import StringIO
                return pd.read_csv(StringIO(data_input))
            except Exception:
                pass

    # 尝试3: Markdown 表格
    if "|" in data_input:
        lines = [l.strip() for l in data_input.split("\n") if l.strip() and not l.strip().startswith("|--")]
        if len(lines) >= 2:
            headers = [h.strip() for h in lines[0].split("|") if h.strip()]
            rows = []
            for line in lines[1:]:
                if set(line.replace("|", "").strip()) <= {"-", " ", ":"}:
                    continue
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) == len(headers):
                    rows.append(cells)
            if rows:
                return pd.DataFrame(rows, columns=headers)

    # 尝试4: key-value 文本
    return parse_kv_from_text(data_input)


# ==================== 3. 标准图表绘制层 ====================


def _save_chart(fig, chart_name: str) -> str:
    """保存图表并返回文件路径"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{chart_name}_{timestamp}.png"
    filepath = CHART_OUTPUT_DIR / filename
    fig.savefig(str(filepath), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(filepath)


def _get_chart_url(filepath: str) -> str:
    """将文件路径转换为可访问的 HTTP URL"""
    filename = Path(filepath).name
    return f"{API_BASE_URL}/charts/{filename}"


def draw_line_chart(df: pd.DataFrame, title: str = "折线图",
                    x_label: str = "", y_label: str = "") -> str:
    """绘制折线图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["label"], df["value"], marker="o", linewidth=2, markersize=8,
            color="#1f77b4", markerfacecolor="#ff7f0e")
    ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="x", rotation=30)

    # 数据标注
    for i, row in df.iterrows():
        ax.annotate(f"{row['value']:.1f}", (row["label"], row["value"]),
                    textcoords="offset points", xytext=(0, 10), ha="center", fontsize=10)

    fig.tight_layout()
    return _save_chart(fig, "line_chart")


def draw_bar_chart(df: pd.DataFrame, title: str = "柱状图",
                   x_label: str = "", y_label: str = "",
                   horizontal: bool = False) -> str:
    """绘制柱状图（垂直或水平）"""
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.Set2(range(len(df)))

    if horizontal:
        bars = ax.barh(df["label"], df["value"], color=colors, edgecolor="white", height=0.6)
        for bar, val in zip(bars, df["value"]):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}", va="center", fontsize=10)
    else:
        bars = ax.bar(df["label"], df["value"], color=colors, edgecolor="white", width=0.6)
        for bar, val in zip(bars, df["value"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f"{val:.1f}", ha="center", fontsize=10)
        ax.tick_params(axis="x", rotation=30)

    ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.grid(True, alpha=0.3, axis="x" if horizontal else "y")
    fig.tight_layout()
    return _save_chart(fig, "bar_chart")


def draw_pie_chart(df: pd.DataFrame, title: str = "饼图") -> str:
    """绘制饼图 / 环形图"""
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.Set3(range(len(df)))

    wedges, texts, autotexts = ax.pie(
        df["value"], labels=df["label"], autopct="%1.1f%%",
        colors=colors, startangle=90, pctdistance=0.8,
        wedgeprops={"edgecolor": "white", "linewidth": 2, "width": 0.4}  # 环形图效果
    )
    for text in autotexts:
        text.set_fontsize(10)
        text.set_fontweight("bold")

    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    fig.tight_layout()
    return _save_chart(fig, "pie_chart")


def draw_radar_chart(df: pd.DataFrame, title: str = "雷达图") -> str:
    """绘制雷达图（用于多维度对比分析）"""
    import numpy as np

    categories = df["label"].tolist()
    values = df["value"].tolist()
    N = len(categories)

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles += [angles[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.fill(angles, values_plot, color="#1f77b4", alpha=0.25)
    ax.plot(angles, values_plot, color="#1f77b4", linewidth=2, marker="o", markersize=6)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    fig.tight_layout()
    return _save_chart(fig, "radar_chart")


def draw_multi_line_chart(data_dict: dict, title: str = "多折线趋势图",
                          x_label: str = "", y_label: str = "") -> str:
    """
    绘制多条折线的趋势对比图。
    data_dict 格式: {"系列名": {"labels": [...], "values": [...]}, ...}
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.tab10.colors

    for i, (name, series) in enumerate(data_dict.items()):
        ax.plot(series["labels"], series["values"], marker="o", linewidth=2,
                label=name, color=colors[i % len(colors)])

    ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return _save_chart(fig, "multi_line_chart")


def draw_stacked_bar_chart(categories: list, groups: dict,
                            title: str = "堆叠柱状图") -> str:
    """
    绘制堆叠柱状图。
    categories: X轴标签列表
    groups: {"组名": [对应每个category的值], ...}
    """
    import numpy as np
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(categories))
    width = 0.5
    bottom = np.zeros(len(categories))
    colors = plt.cm.Set2.colors

    for i, (group_name, values) in enumerate(groups.items()):
        ax.bar(x, values, width, label=group_name, bottom=bottom,
               color=colors[i % len(colors)], edgecolor="white")
        bottom += np.array(values)

    ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    return _save_chart(fig, "stacked_bar_chart")


# ==================== 4. AI 图像生成层（预留功能） ====================


def generate_ai_image(prompt: str, size: str = "horizontal",
                      quality: str = "standard") -> str:
    """
    调用 tu-zi.com AI 图像生成 API（OpenAI 兼容格式）。
    用于生成复杂的流程图、商业模型图、金融概念图等。

    参数:
        prompt: 图像描述（中英文均可）
        size: 图片比例，支持：
            - "square" / "方形" → "1x1" (1:1 正方形)
            - "horizontal" / "横屏" → "2x1" (16:9 横屏，默认)
            - "vertical" / "竖屏" → "1x2" (9:16 竖屏)
            - 或直接传比例如 "2x1", "1x8" 等
        quality: 画质，支持 "standard" / "hd" / "4k"（默认 standard）
    返回:
        保存后的图片路径 或 错误信息
    """
    if not TUZI_API_KEY:
        return "AI图像生成功能未配置。请设置环境变量 TUZI_API_KEY"

    # 尺寸映射（用户友好 → API 格式）
    size_map = {
        "square": "1x1",
        "方形": "1x1",
        "horizontal": "2x1",
        "横屏": "2x1",
        "vertical": "1x2",
        "竖屏": "1x2",
    }
    api_size = size_map.get(size, size)  # 如果不在映射中，直接使用原值

    headers = {
        "Authorization": f"Bearer {TUZI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": TUZI_MODEL,
        "prompt": prompt,
        "size": api_size,
        "quality": quality,
        "response_format": "b64_json",  # 使用 base64 格式，避免二次下载
    }

    try:
        # 发送请求
        resp = requests.post(TUZI_API_URL, headers=headers, json=payload, timeout=120)

        if resp.status_code != 200:
            return f"AI图像生成失败 (HTTP {resp.status_code}): {resp.text[:200]}"

        result = resp.json()

        # 解析 base64 图像数据
        data_list = result.get("data", [])
        if not data_list:
            return "AI图像API返回空数据"

        image_base64 = data_list[0].get("b64_json")
        if not image_base64:
            return "AI图像API响应中缺少 b64_json 字段"

        # 解码并保存图片
        image_bytes = base64.b64decode(image_base64)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_image_{timestamp}.png"
        filepath = CHART_OUTPUT_DIR / filename
        filepath.write_bytes(image_bytes)

        return str(filepath)

    except requests.exceptions.SSLError as e:
        return f"SSL错误: {e}。macOS用户可运行: /Applications/Python*/Install\\ Certificates.command"
    except requests.exceptions.Timeout:
        return "AI图像生成超时（120秒），请稍后重试"
    except requests.RequestException as e:
        return f"网络请求失败: {e}"
    except (KeyError, IndexError, TypeError) as e:
        return f"AI图像API响应解析失败: {e}"
    except Exception as e:
        return f"未知错误: {e}"


# ==================== 5. LangChain Tool 封装 ====================


@tool
def generate_financial_chart(request: str) -> str:
    """根据用户自然语言请求生成金融图表。

    支持的图表类型：折线图、柱状图、饼图、雷达图。
    输入格式：JSON字符串，包含以下字段：
    - chart_type: 图表类型 (line/bar/pie/radar)
    - title: 图表标题
    - data: 数据，格式为 [{"label": "标签", "value": 数值}, ...]

    示例输入：
    {"chart_type": "line", "title": "基金收益率趋势", "data": [{"label": "2023", "value": 12.5}, {"label": "2024", "value": 8.3}]}
    """
    try:
        params = json.loads(request)
    except json.JSONDecodeError:
        return "输入格式错误，请提供有效的JSON字符串。"

    chart_type = params.get("chart_type", "bar")
    title = params.get("title", "金融数据图表")
    data = params.get("data", [])

    if not data:
        return "未提供数据，无法绘图。"

    df = pd.DataFrame(data)
    if "label" not in df.columns or "value" not in df.columns:
        return "数据格式错误，需要包含 'label' 和 'value' 字段。"

    chart_funcs = {
        "line": draw_line_chart,
        "bar": draw_bar_chart,
        "pie": draw_pie_chart,
        "radar": draw_radar_chart,
    }

    func = chart_funcs.get(chart_type)
    if not func:
        return f"不支持的图表类型: {chart_type}。支持: line, bar, pie, radar"

    filepath = func(df, title=title)
    chart_url = _get_chart_url(filepath)
    # 返回紧凑的 Markdown 格式，避免多行干扰 Agent 解析
    return f"✅ 图表已生成：![{title}]({chart_url})"


@tool
def generate_chart_from_text(text_data: str) -> str:
    """从文本数据中自动提取数值并生成图表。

    直接粘贴包含数值的文本即可，工具会自动解析数据并生成柱状图。
    例如输入:
    "2023年收益率：12.5%
     2024年收益率：8.3%
     2025年收益率：15.2%"
    """
    df = parse_kv_from_text(text_data)
    if df.empty:
        return "无法从文本中提取数值数据，请检查格式。"

    filepath = draw_bar_chart(df, title="数据分析图表")
    chart_url = _get_chart_url(filepath)
    # 返回紧凑的 Markdown 格式，避免多行干扰 Agent 解析
    return f"✅ 已提取 {len(df)} 条数据并生成图表：![数据分析图表]({chart_url})"


@tool
def generate_ai_diagram(description: str) -> str:
    """生成复杂的商业/金融概念图（AI 图像生成）。

    使用 tu-zi.com AI 图像生成 API，适用于：流程图、商业模型图、金融架构图、概念图等。
    输入图像的描述（中英文均可），AI 会根据描述生成对应的图片。

    需要配置环境变量 TUZI_API_KEY 才能使用。

    示例描述：
    - "一个金融风控系统的流程图，包含数据采集、风险评估、预警、处置四个步骤"
    - "资产配置的金字塔模型图，底层是现金和债券，中层是股票，顶层是另类投资"
    - "股票市场技术分析的K线图，包含均线和成交量，专业金融风格"
    - "公司组织架构图，树状结构，包含董事会、管理层、各部门"
    """
    if not TUZI_API_KEY:
        return ("❌ AI图像生成功能未配置。\n"
                "请设置环境变量 TUZI_API_KEY 以启用此功能。\n"
                "获取 API Key: https://tu-zi.com")

    # 调用 AI 图像生成，默认使用横屏格式和标准画质
    filepath = generate_ai_image(description, size="horizontal", quality="standard")

    # 检查是否返回错误信息
    if filepath.startswith("❌") or filepath.startswith("AI图像") or filepath.startswith("SSL") or filepath.startswith("网络"):
        return filepath  # 直接返回错误信息

    # 成功生成，返回图片 URL
    chart_url = _get_chart_url(filepath)
    return f"✅ AI图像已生成：![AI生成图像]({chart_url})"


@tool
def generate_multi_line_chart(request: str) -> str:
    """生成多条折线对比图，用于对比多个系列的趋势变化。

    适用场景：多只股票对比、多个指标趋势对比、多个产品销量对比等。

    输入格式：JSON字符串，包含以下字段：
    - title: 图表标题
    - x_label: X轴标签（可选）
    - y_label: Y轴标签（可选）
    - series: 多个系列的数据字典，格式为：
      {
        "系列1名称": {"labels": ["标签1", "标签2", ...], "values": [数值1, 数值2, ...]},
        "系列2名称": {"labels": ["标签1", "标签2", ...], "values": [数值1, 数值2, ...]},
        ...
      }

    示例输入：
    {
      "title": "三只股票走势对比",
      "x_label": "月份",
      "y_label": "股价（元）",
      "series": {
        "阿里巴巴": {"labels": ["1月", "2月", "3月"], "values": [180, 185, 190]},
        "腾讯": {"labels": ["1月", "2月", "3月"], "values": [420, 430, 425]},
        "百度": {"labels": ["1月", "2月", "3月"], "values": [150, 145, 148]}
      }
    }
    """
    try:
        params = json.loads(request)
    except json.JSONDecodeError:
        return "输入格式错误，请提供有效的JSON字符串。"

    title = params.get("title", "多折线趋势对比图")
    x_label = params.get("x_label", "")
    y_label = params.get("y_label", "")
    series = params.get("series", {})

    if not series:
        return "未提供数据系列，无法绘图。"

    # 验证数据格式
    for name, data in series.items():
        if "labels" not in data or "values" not in data:
            return f"系列'{name}'数据格式错误，需要包含'labels'和'values'字段。"
        if len(data["labels"]) != len(data["values"]):
            return f"系列'{name}'的labels和values长度不匹配。"

    filepath = draw_multi_line_chart(series, title=title, x_label=x_label, y_label=y_label)
    chart_url = _get_chart_url(filepath)
    return f"✅ 多折线图已生成：![{title}]({chart_url})"


@tool
def generate_stacked_bar_chart(request: str) -> str:
    """生成堆叠柱状图，用于展示多个类别的组成结构和变化趋势。

    适用场景：收入构成分析、成本结构对比、多业务线占比变化等。

    输入格式：JSON字符串，包含以下字段：
    - title: 图表标题
    - categories: X轴类别标签列表（如：["Q1", "Q2", "Q3"]）
    - groups: 各组数据字典，格式为：
      {
        "组1名称": [对应每个category的值],
        "组2名称": [对应每个category的值],
        ...
      }

    示例输入：
    {
      "title": "季度收入构成分析",
      "categories": ["第一季度", "第二季度", "第三季度"],
      "groups": {
        "广告收入": [50, 55, 60],
        "游戏收入": [30, 35, 40],
        "云服务": [20, 28, 35]
      }
    }
    """
    try:
        params = json.loads(request)
    except json.JSONDecodeError:
        return "输入格式错误，请提供有效的JSON字符串。"

    title = params.get("title", "堆叠柱状图")
    categories = params.get("categories", [])
    groups = params.get("groups", {})

    if not categories:
        return "未提供类别标签（categories），无法绘图。"
    if not groups:
        return "未提供分组数据（groups），无法绘图。"

    # 验证数据格式
    for group_name, values in groups.items():
        if len(values) != len(categories):
            return f"分组'{group_name}'的数据长度({len(values)})与类别数量({len(categories)})不匹配。"

    filepath = draw_stacked_bar_chart(categories, groups, title=title)
    chart_url = _get_chart_url(filepath)
    return f"✅ 堆叠柱状图已生成：![{title}]({chart_url})"


def get_chart_tools() -> List:
    """获取所有绘图工具列表，用于集成到 LangChain Agent"""
    return [
        generate_financial_chart,      # 单系列图表：折线图、柱状图、饼图、雷达图
        generate_multi_line_chart,     # 多折线对比图
        generate_stacked_bar_chart,    # 堆叠柱状图
        generate_chart_from_text,      # 从文本自动提取数据并绘图
        generate_ai_diagram            # AI图像生成（预留功能）
    ]
