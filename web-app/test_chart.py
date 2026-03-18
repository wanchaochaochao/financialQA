"""
金融数据可视化工具 - Chart Tools
================================
功能：
1. 数据解析：从文本/表格/JSON/RAG结果中提取结构化数据
2. 标准图表：折线图、饼图、柱状图、雷达图等（matplotlib）
3. AI图像生成：流程图、商业模型图等复杂图像（调用AI大模型API）
4. LangChain Tool 集成：可注册到 Agent，实现自然语言驱动绘图

依赖安装：
    pip install matplotlib pandas plotly requests Pillow

使用方式：
    1. 独立运行：python chart_tools.py
    2. 集成到 test1.py 的 Agent：
       from chart_tools import get_chart_tools
       tools = [rag_tool, ...] + get_chart_tools()
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # 非交互后端，适用于服务器/脚本环境
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import requests

from langchain_core.tools import tool

# ==================== 配置 ====================

# 图表输出目录
CHART_OUTPUT_DIR = Path(__file__).parent / "chart_output"
CHART_OUTPUT_DIR.mkdir(exist_ok=True)

# AI 图像生成 API 配置（nanobanana 或其他兼容 API）
AI_IMAGE_API_URL = os.getenv("AI_IMAGE_API_URL", "https://api.nanobanana.com/v1/images/generations")
AI_IMAGE_API_KEY = os.getenv("AI_IMAGE_API_KEY", "your-api-key-here")

# ==================== 1. 中文字体配置 ====================


#def setup_chinese_font():
#    """配置 matplotlib 中文字体，macOS / Linux / Windows 自适应"""
#    font_candidates = [
#        "PingFang SC",        # macOS
#        "Heiti SC",           # macOS
#        "Microsoft YaHei",    # Windows
#        "SimHei",             # Windows/Linux
#        "WenQuanYi Micro Hei",  # Linux
#        "Noto Sans CJK SC",  # Linux
#    ]
#    available_fonts = {f.name for f in fm.fontManager.ttflist}
#    for font_name in font_candidates:
#        if font_name in available_fonts:
#            plt.rcParams["font.sans-serif"] = [font_name]
#            plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
#            return font_name
#    # 回退：尝试系统默认
#    plt.rcParams["axes.unicode_minus"] = False
#    return None

def setup_chinese_font():
    """
    配置 matplotlib 中文字体。
    优先使用项目内嵌的字体文件（跨平台通用），
    找不到时回退到系统字体。
    """
    # ---- 方案1: 项目内嵌字体（最可靠，跨 macOS / Ubuntu / Docker 通用） ----
    bundled_font_dir = Path(__file__).parent / "fonts"
    if bundled_font_dir.exists():
        for font_file in bundled_font_dir.glob("*.ttf"):
            fm.fontManager.addfont(str(font_file))
        for font_file in bundled_font_dir.glob("*.ttc"):
            fm.fontManager.addfont(str(font_file))
        # 注册后按优先级尝试
        bundled_names = ["Noto Sans SC", "Noto Sans CJK SC", "Source Han Sans SC"]
        available = {f.name for f in fm.fontManager.ttflist}
        for name in bundled_names:
            if name in available:
                plt.rcParams["font.sans-serif"] = [name]
                plt.rcParams["axes.unicode_minus"] = False
                return name

    # ---- 方案2: 回退到系统字体 ----
    system_fonts = [
        "PingFang SC", ".PingFang SC",       # macOS
        "Heiti SC", "STHeiti",               # macOS
        "Arial Unicode MS",                  # macOS
        "Noto Sans CJK SC",                  # Ubuntu (apt install fonts-noto-cjk)
        "WenQuanYi Micro Hei",              # Ubuntu (apt install fonts-wqy-microhei)
        "WenQuanYi Zen Hei",                # Ubuntu
        "Microsoft YaHei", "SimHei",         # Windows
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


# ==================== 4. AI 图像生成层 ====================


def generate_ai_image(prompt: str, size: str = "1024x1024",
                      style: str = "natural") -> str:
    """
    调用 AI 大模型图像生成 API（兼容 OpenAI DALL-E / nanobanana 等接口）。
    用于生成复杂的流程图、商业模型图、金融概念图等。

    参数:
        prompt: 图像描述（英文效果更佳，中文也支持）
        size: 图片尺寸
        style: 风格 (natural / vivid)
    返回:
        保存后的图片路径
    """
    headers = {
        "Authorization": f"Bearer {AI_IMAGE_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt,
        "n": 1,
        "size": size,
        "style": style,
    }

    try:
        resp = requests.post(AI_IMAGE_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()

        # 获取图片 URL 并下载
        image_url = result["data"][0]["url"]
        image_resp = requests.get(image_url, timeout=30)
        image_resp.raise_for_status()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_generated_{timestamp}.png"
        filepath = CHART_OUTPUT_DIR / filename
        filepath.write_bytes(image_resp.content)

        return str(filepath)

    except requests.RequestException as e:
        return f"AI图像生成失败: {e}"
    except (KeyError, IndexError) as e:
        return f"AI图像API响应解析失败: {e}"


# ==================== 5. 高级分析图表 ====================


def draw_fund_performance_report(fund_data: dict) -> list[str]:
    """
    生成基金综合分析报告（多图组合）。

    fund_data 示例:
    {
        "name": "稳健增长混合基金A",
        "yearly_returns": {"2023": 12.5, "2024": 8.3, "2025": 15.2},
        "holdings": {"贵州茅台": 8.5, "宁德时代": 6.2, "招商银行": 5.8, "比亚迪": 5.1, "腾讯控股": 4.9},
        "risk_metrics": {"VaR限额": 2.0, "单股上限": 10.0, "行业上限": 30.0, "跟踪误差": 4.0}
    }
    """
    output_files = []
    fund_name = fund_data.get("name", "基金")

    # 图1: 历史业绩折线图
    if "yearly_returns" in fund_data:
        df = pd.DataFrame([
            {"label": year, "value": ret}
            for year, ret in fund_data["yearly_returns"].items()
        ])
        path = draw_line_chart(df, title=f"{fund_name} - 历史收益率(%)", y_label="收益率(%)")
        output_files.append(path)

    # 图2: 持仓占比饼图
    if "holdings" in fund_data:
        df = pd.DataFrame([
            {"label": stock, "value": pct}
            for stock, pct in fund_data["holdings"].items()
        ])
        # 添加"其他"
        other_pct = 100 - df["value"].sum()
        if other_pct > 0:
            df = pd.concat([df, pd.DataFrame([{"label": "其他", "value": other_pct}])],
                           ignore_index=True)
        path = draw_pie_chart(df, title=f"{fund_name} - 持仓分布")
        output_files.append(path)

    # 图3: 风控指标雷达图
    if "risk_metrics" in fund_data:
        df = pd.DataFrame([
            {"label": metric, "value": val}
            for metric, val in fund_data["risk_metrics"].items()
        ])
        path = draw_radar_chart(df, title=f"{fund_name} - 风控指标")
        output_files.append(path)

    return output_files


# ==================== 6. LangChain Tool 封装 ====================


@tool
def generate_financial_chart(request: str) -> str:
    """根据用户自然语言请求生成金融图表。

    支持的图表类型：折线图、柱状图、饼图、雷达图。
    输入格式：JSON字符串，包含以下字段：
    - chart_type: 图表类型 (line/bar/pie/radar)
    - title: 图表标题
    - data: 数据，格式为 [{"label": "标签", "value": 数值}, ...]

    示例输入：
    {"chart_type": "line", "title": "基金收益率趋势", "data": [{"label": "2023", "value": 12.5}, {"label": "2024", "value": 8.3}, {"label": "2025", "value": 15.2}]}
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
    return f"图表已生成并保存到: {filepath}"


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
    return f"已从文本中提取 {len(df)} 条数据，图表保存到: {filepath}"


@tool
def generate_ai_diagram(description: str) -> str:
    """生成复杂的商业/金融概念图。

    使用 AI 大模型图像生成，适用于：流程图、商业模型图、金融架构图等。
    输入图像的描述（中英文均可），AI会生成对应的图片。

    示例：
    - "一个金融风控系统的流程图，包含数据采集、风险评估、预警、处置四个步骤"
    - "资产配置的金字塔模型图，底层是现金和债券，中层是股票，顶层是另类投资"
    """
    if AI_IMAGE_API_KEY == "your-api-key-here":
        return ("AI图像生成API未配置。请设置环境变量 AI_IMAGE_API_KEY 和 AI_IMAGE_API_URL。\n"
                "支持的API: nanobanana、OpenAI DALL-E 等兼容接口。")

    filepath = generate_ai_image(description)
    if filepath.startswith("AI图像"):
        return filepath  # 返回错误信息
    return f"AI图像已生成并保存到: {filepath}"


def get_chart_tools() -> list:
    """获取所有绘图工具列表，用于集成到 LangChain Agent"""
    return [generate_financial_chart, generate_chart_from_text, generate_ai_diagram]


# ==================== 7. 演示 & 测试 ====================


def demo():
    """运行演示，使用知识库中的数据生成各类图表"""

    print("=" * 60)
    print("📊 金融数据可视化工具 - Demo")
    print(f"   中文字体: {CHINESE_FONT or '未检测到，可能显示方块'}")
    print(f"   输出目录: {CHART_OUTPUT_DIR}")
    print("=" * 60)

    # --- Demo 1: 基金历史业绩折线图 ---
    print("\n📈 Demo 1: 基金历史业绩折线图")
    df_returns = pd.DataFrame([
        {"label": "2023年", "value": 12.5},
        {"label": "2024年", "value": 8.3},
        {"label": "2025年", "value": 15.2},
    ])
    path = draw_line_chart(df_returns, title="稳健增长混合基金A - 年度收益率(%)",
                           x_label="年份", y_label="收益率(%)")
    print(f"   ✅ 已保存: {path}")

    # --- Demo 2: 持仓占比饼图 ---
    print("\n🥧 Demo 2: 持仓占比饼图")
    df_holdings = pd.DataFrame([
        {"label": "贵州茅台", "value": 8.5},
        {"label": "宁德时代", "value": 6.2},
        {"label": "招商银行", "value": 5.8},
        {"label": "比亚迪", "value": 5.1},
        {"label": "腾讯控股", "value": 4.9},
        {"label": "其他", "value": 69.5},
    ])
    path = draw_pie_chart(df_holdings, title="稳健增长混合基金A - 前五大持仓占比")
    print(f"   ✅ 已保存: {path}")

    # --- Demo 3: 行业配置柱状图 ---
    print("\n📊 Demo 3: 行业配置建议柱状图")
    df_industry = pd.DataFrame([
        {"label": "AI与半导体", "value": 3},     # 3=超配
        {"label": "新能源", "value": 3},
        {"label": "医药生物", "value": 3},
        {"label": "消费", "value": 2},            # 2=标配
        {"label": "金融", "value": 2},
        {"label": "房地产", "value": 1},          # 1=低配
        {"label": "传统能源", "value": 1},
    ])
    path = draw_bar_chart(df_industry, title="2025年Q4行业配置建议\n(3=超配, 2=标配, 1=低配)",
                          x_label="行业", y_label="配置等级")
    print(f"   ✅ 已保存: {path}")

    # --- Demo 4: 宏观经济指标柱状图 ---
    print("\n📊 Demo 4: 宏观经济指标")
    df_macro = pd.DataFrame([
        {"label": "GDP增速", "value": 5.2},
        {"label": "社零同比", "value": 6.5},
        {"label": "PMI", "value": 51.2},
    ])
    path = draw_bar_chart(df_macro, title="2025年宏观经济核心指标(%)", horizontal=True)
    print(f"   ✅ 已保存: {path}")

    # --- Demo 5: 风控指标雷达图 ---
    print("\n🕸️ Demo 5: 风控限额雷达图")
    df_risk = pd.DataFrame([
        {"label": "单股持仓上限(%)", "value": 10.0},
        {"label": "行业持仓上限(%)", "value": 30.0},
        {"label": "VaR限额(%)", "value": 2.0},
        {"label": "跟踪误差(%)", "value": 4.0},
    ])
    path = draw_radar_chart(df_risk, title="风控限额指标")
    print(f"   ✅ 已保存: {path}")

    # --- Demo 6: 从文本自动提取数据并绘图 ---
    print("\n🔍 Demo 6: 从文本自动解析数据")
    text_input = """
    2023年收益率：12.5%
    2024年收益率：8.3%
    2025年收益率：15.2%
    """
    df_auto = parse_kv_from_text(text_input)
    print(f"   解析结果:\n{df_auto.to_string(index=False)}")
    if not df_auto.empty:
        path = draw_line_chart(df_auto, title="文本自动解析 - 收益率趋势")
        print(f"   ✅ 已保存: {path}")

    # --- Demo 7: 基金综合报告（多图） ---
    print("\n📋 Demo 7: 基金综合分析报告")
    fund_data = {
        "name": "稳健增长混合基金A",
        "yearly_returns": {"2023年": 12.5, "2024年": 8.3, "2025年": 15.2},
        "holdings": {"贵州茅台": 8.5, "宁德时代": 6.2, "招商银行": 5.8,
                     "比亚迪": 5.1, "腾讯控股": 4.9},
        "risk_metrics": {"单股上限": 10.0, "行业上限": 30.0,
                         "VaR限额": 2.0, "跟踪误差": 4.0},
    }
    paths = draw_fund_performance_report(fund_data)
    for p in paths:
        print(f"   ✅ 已保存: {p}")

    print(f"\n🎉 所有图表已生成，共 {len(list(CHART_OUTPUT_DIR.glob('*.png')))} 个文件")
    print(f"   目录: {CHART_OUTPUT_DIR}")


if __name__ == "__main__":
    demo()