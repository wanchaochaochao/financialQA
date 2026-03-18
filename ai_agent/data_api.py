"""
Financial Data API Module
==========================

Integrates with external financial data APIs (Yahoo Finance, etc.)
to retrieve real-time and historical market data.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
from .config import Config


class FinancialDataAPI:
    """
    Financial data retrieval class using Yahoo Finance API.

    Supports:
    - Real-time stock prices
    - Historical price data
    - Price change calculations (7-day, 30-day)
    - Market indices
    - Basic stock information
    """

    # Stock symbol mappings (Chinese names to ticker symbols)
    SYMBOL_MAP = {
        # Chinese A-shares
        "贵州茅台": "600519.SS",
        "茅台": "600519.SS",
        "宁德时代": "300750.SZ",
        "招商银行": "600036.SS",
        "比亚迪": "002594.SZ",
        "中国平安": "601318.SS",
        "平安": "601318.SS",

        # US stocks
        "阿里巴巴": "BABA",
        "BABA": "BABA",
        "Alibaba": "BABA",
        "特斯拉": "TSLA",
        "Tesla": "TSLA",
        "TSLA": "TSLA",
        "苹果": "AAPL",
        "Apple": "AAPL",
        "AAPL": "AAPL",
        "微软": "MSFT",
        "Microsoft": "MSFT",
        "MSFT": "MSFT",
        "谷歌": "GOOGL",
        "Google": "GOOGL",
        "GOOGL": "GOOGL",
        "亚马逊": "AMZN",
        "Amazon": "AMZN",
        "AMZN": "AMZN",
        "英伟达": "NVDA",
        "NVIDIA": "NVDA",
        "NVDA": "NVDA",

        # HK stocks
        "腾讯": "0700.HK",
        "腾讯控股": "0700.HK",
        "Tencent": "0700.HK",
        "0700": "0700.HK",
    }

    # Market indices
    INDEX_MAP = {
        "上证指数": "000001.SS",
        "上证": "000001.SS",
        "深证成指": "399001.SZ",
        "深证": "399001.SZ",
        "创业板指": "399006.SZ",
        "创业板": "399006.SZ",
        "沪深300": "000300.SS",
        "标普500": "^GSPC",
        "S&P500": "^GSPC",
        "纳斯达克": "^IXIC",
        "NASDAQ": "^IXIC",
        "道琼斯": "^DJI",
        "DJI": "^DJI",
    }

    @classmethod
    def resolve_symbol(cls, query: str) -> Optional[str]:
        """
        Resolve stock name or code to Yahoo Finance ticker symbol.

        Args:
            query: Stock name or code (e.g., "阿里巴巴", "BABA", "600519")

        Returns:
            Yahoo Finance ticker symbol or None if not found
        """
        query = query.strip()

        # Direct match in symbol map
        if query in cls.SYMBOL_MAP:
            return cls.SYMBOL_MAP[query]

        # Try fuzzy match
        for name, symbol in cls.SYMBOL_MAP.items():
            if query in name or name in query:
                return symbol

        # Try as-is (might be a valid ticker)
        return query

    @classmethod
    def resolve_index(cls, query: str) -> Optional[str]:
        """Resolve index name to ticker symbol"""
        query = query.strip()

        if query in cls.INDEX_MAP:
            return cls.INDEX_MAP[query]

        for name, symbol in cls.INDEX_MAP.items():
            if query in name or name in query:
                return symbol

        return None

    @classmethod
    def get_stock_info(cls, stock_query: str) -> Dict:
        """
        Get real-time stock information.

        Args:
            stock_query: Stock name or ticker symbol

        Returns:
            Dictionary containing stock information
        """
        try:
            symbol = cls.resolve_symbol(stock_query)
            if not symbol:
                return {"error": f"无法识别股票：{stock_query}"}

            stock = yf.Ticker(symbol)
            info = stock.info

            # Get current price (try different fields)
            current_price = (
                info.get("currentPrice") or
                info.get("regularMarketPrice") or
                info.get("previousClose")
            )

            if current_price is None:
                return {"error": f"无法获取 {stock_query} 的价格数据"}

            # Calculate change
            prev_close = info.get("previousClose", current_price)
            change_amount = current_price - prev_close
            change_percent = (change_amount / prev_close * 100) if prev_close else 0

            return {
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName") or stock_query,
                "current_price": round(current_price, 2),
                "previous_close": round(prev_close, 2),
                "change_amount": round(change_amount, 2),
                "change_percent": round(change_percent, 2),
                "volume": info.get("volume", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange", "N/A"),
            }

        except Exception as e:
            return {"error": f"获取股票信息失败：{str(e)}"}

    @classmethod
    def get_stock_history(
        cls,
        stock_query: str,
        period: str = "1mo",
        days: Optional[int] = None
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Get historical stock price data.

        Args:
            stock_query: Stock name or ticker
            period: Time period ("1mo", "3mo", "1y", etc.)
            days: Specific number of days (alternative to period)

        Returns:
            Tuple of (DataFrame with historical data, error message)
        """
        try:
            symbol = cls.resolve_symbol(stock_query)
            if not symbol:
                return None, f"无法识别股票：{stock_query}"

            stock = yf.Ticker(symbol)

            if days:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                hist = stock.history(start=start_date, end=end_date)
            else:
                hist = stock.history(period=period)

            if hist.empty:
                return None, f"无法获取 {stock_query} 的历史数据"

            return hist, None

        except Exception as e:
            return None, f"获取历史数据失败：{str(e)}"

    @classmethod
    def calculate_price_change(
        cls,
        stock_query: str,
        days: int = 7
    ) -> Dict:
        """
        Calculate price change over a specific period.

        Args:
            stock_query: Stock name or ticker
            days: Number of days to look back

        Returns:
            Dictionary with price change analysis
        """
        hist, error = cls.get_stock_history(stock_query, days=days + 5)

        if error:
            return {"error": error}

        if len(hist) < 2:
            return {"error": "历史数据不足"}

        try:
            # Get start and end prices
            start_price = hist['Close'].iloc[0]
            end_price = hist['Close'].iloc[-1]

            change_amount = end_price - start_price
            change_percent = (change_amount / start_price * 100)

            # Calculate high and low
            high = hist['Close'].max()
            low = hist['Close'].min()

            # Determine trend
            if change_percent > 2:
                trend = "上涨"
            elif change_percent < -2:
                trend = "下跌"
            else:
                trend = "震荡"

            return {
                "period": f"{days}日",
                "start_price": round(start_price, 2),
                "end_price": round(end_price, 2),
                "change_amount": round(change_amount, 2),
                "change_percent": round(change_percent, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "trend": trend,
                "data_points": len(hist),
            }

        except Exception as e:
            return {"error": f"计算涨跌幅失败：{str(e)}"}

    @classmethod
    def get_market_index(cls, index_query: str) -> Dict:
        """
        Get market index information.

        Args:
            index_query: Index name

        Returns:
            Dictionary containing index information
        """
        try:
            symbol = cls.resolve_index(index_query)
            if not symbol:
                return {"error": f"无法识别指数：{index_query}"}

            index = yf.Ticker(symbol)
            hist = index.history(period="2d")

            if hist.empty:
                return {"error": f"无法获取 {index_query} 的数据"}

            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[0] if len(hist) > 1 else current_price

            change_amount = current_price - prev_close
            change_percent = (change_amount / prev_close * 100) if prev_close else 0

            return {
                "symbol": symbol,
                "name": index_query,
                "current_value": round(current_price, 2),
                "previous_close": round(prev_close, 2),
                "change_amount": round(change_amount, 2),
                "change_percent": round(change_percent, 2),
            }

        except Exception as e:
            return {"error": f"获取指数信息失败：{str(e)}"}

    @classmethod
    def format_stock_info(cls, info: Dict) -> str:
        """Format stock information for display"""
        if "error" in info:
            return f"❌ {info['error']}"

        symbol_info = f"{info['name']} ({info['symbol']})" if info.get('name') else info['symbol']
        change_sign = "+" if info['change_percent'] >= 0 else ""

        return f"""【数据来源】Yahoo Finance API - 实时市场数据

📈 {symbol_info}
  最新价：{info['current_price']} {info.get('currency', '')}
  涨跌幅：{change_sign}{info['change_percent']}% ({change_sign}{info['change_amount']})
  成交量：{info.get('volume', 'N/A')}
  总市值：{info.get('market_cap', 'N/A')}
  交易所：{info.get('exchange', 'N/A')}
  数据时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

注：以上为客观市场数据，非AI推测"""

    @classmethod
    def format_price_change(cls, analysis: Dict, stock_name: str = "") -> str:
        """Format price change analysis for display"""
        if "error" in analysis:
            return f"❌ {analysis['error']}"

        change_sign = "+" if analysis['change_percent'] >= 0 else ""

        return f"""【数据来源】Yahoo Finance API - 历史市场数据

📊 {stock_name} {analysis['period']}涨跌分析
  期初价格：{analysis['start_price']}
  期末价格：{analysis['end_price']}
  涨跌幅：{change_sign}{analysis['change_percent']}% ({change_sign}{analysis['change_amount']})
  期间最高：{analysis['high']}
  期间最低：{analysis['low']}
  趋势判断：{analysis['trend']}
  数据点数：{analysis['data_points']} 个交易日
  数据时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

注：以上为客观历史数据，非AI推测"""

    @classmethod
    def format_index_info(cls, info: Dict) -> str:
        """Format market index information for display"""
        if "error" in info:
            return f"❌ {info['error']}"

        change_sign = "+" if info['change_percent'] >= 0 else ""

        return f"""【数据来源】Yahoo Finance API - 指数数据

📊 {info['name']} ({info['symbol']})
  最新点位：{info['current_value']}
  涨跌幅：{change_sign}{info['change_percent']}% ({change_sign}{info['change_amount']})
  数据时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

注：以上为客观指数数据，非AI推测"""
