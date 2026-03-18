"""
Financial Tools for LangChain Agent
====================================

Custom tools that wrap the FinancialDataAPI for use in LangChain agents.
"""

from langchain_core.tools import tool
from ..data_api import FinancialDataAPI


@tool
def get_stock_price_tool(stock_name: str) -> str:
    """
    查询股票实时价格和基本信息。

    输入股票名称或代码，例如：
    - 中文名称："阿里巴巴"、"特斯拉"、"贵州茅台"
    - 英文名称："Alibaba"、"Tesla"、"Apple"
    - 股票代码："BABA"、"TSLA"、"AAPL"、"600519"

    返回：
    - 最新股价
    - 涨跌幅
    - 成交量
    - 总市值
    - 交易所信息
    """
    info = FinancialDataAPI.get_stock_info(stock_name)
    return FinancialDataAPI.format_stock_info(info)


@tool
def get_stock_history_tool(stock_name_and_days: str) -> str:
    """
    查询股票历史涨跌情况。

    输入格式："股票名称,天数" 或 "股票名称,时间段"

    示例：
    - "阿里巴巴,7" - 查询阿里巴巴最近7天的涨跌
    - "特斯拉,30" - 查询特斯拉最近30天的涨跌
    - "BABA,7" - 查询BABA最近7天的涨跌

    返回：
    - 期初期末价格
    - 涨跌幅和涨跌额
    - 期间最高最低价
    - 趋势判断（上涨/下跌/震荡）
    """
    try:
        # Parse input
        parts = stock_name_and_days.split(',')
        if len(parts) != 2:
            return "❌ 输入格式错误。请使用格式：'股票名称,天数'，例如：'阿里巴巴,7'"

        stock_name = parts[0].strip()
        days_str = parts[1].strip()

        try:
            days = int(days_str)
        except ValueError:
            return f"❌ 天数必须是数字，例如：7、30"

        if days < 1 or days > 365:
            return "❌ 天数必须在1-365之间"

        # Get price change analysis
        analysis = FinancialDataAPI.calculate_price_change(stock_name, days)
        return FinancialDataAPI.format_price_change(analysis, stock_name)

    except Exception as e:
        return f"❌ 查询失败：{str(e)}"


@tool
def get_market_index_tool(index_name: str) -> str:
    """
    查询市场指数行情。

    支持查询的指数：
    - 中国：上证指数、深证成指、创业板指、沪深300
    - 美国：标普500、纳斯达克、道琼斯

    示例输入：
    - "上证指数"
    - "纳斯达克"
    - "S&P500"

    返回：
    - 最新点位
    - 涨跌幅
    - 数据时间
    """
    info = FinancialDataAPI.get_market_index(index_name)
    return FinancialDataAPI.format_index_info(info)


# Tool list for export
def get_all_tools():
    """Get all financial tools as a list"""
    return [
        get_stock_price_tool,
        get_stock_history_tool,
        get_market_index_tool,
    ]
