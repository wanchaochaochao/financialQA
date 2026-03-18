"""
Financial Data API Module
==========================

Integrates with external financial data APIs (Yahoo Finance, AKShare, etc.)
to retrieve real-time and historical market data.
"""

import yfinance as yf
import akshare as ak
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
from .config import Config
import time
import requests


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

    # 缓存机制（减少API请求，避免限流）
    _cache = {}
    _cache_ttl = 300  # 缓存5分钟

    # Alpha Vantage 速率限制（每秒1次请求）
    _last_alphavantage_call = 0
    _alphavantage_delay = 1.2  # 1.2秒延迟，留点余量

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
    def _get_cache(cls, key: str) -> Optional[Dict]:
        """获取缓存数据"""
        if key in cls._cache:
            data, timestamp = cls._cache[key]
            if time.time() - timestamp < cls._cache_ttl:
                return data
            else:
                del cls._cache[key]
        return None

    @classmethod
    def _set_cache(cls, key: str, data: Dict):
        """设置缓存数据"""
        cls._cache[key] = (data, time.time())

    @classmethod
    def get_stock_info(cls, stock_query: str) -> Dict:
        """
        Get real-time stock information.

        Args:
            stock_query: Stock name or ticker symbol

        Returns:
            Dictionary containing stock information
        """
        # 检查缓存
        cache_key = f"stock_info:{stock_query}"
        cached = cls._get_cache(cache_key)
        if cached:
            return cached

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

            result = {
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

            # 缓存成功的结果
            cls._set_cache(cache_key, result)
            return result

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
        # 检查缓存
        cache_key = f"price_change:{stock_query}:{days}"
        cached = cls._get_cache(cache_key)
        if cached:
            return cached

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

            result = {
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

            # 缓存成功的结果
            cls._set_cache(cache_key, result)
            return result

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

    # ==================== AKShare 数据获取方法 ====================

    @classmethod
    def get_stock_info_akshare(cls, stock_query: str) -> Dict:
        """
        使用 AKShare 获取A股实时数据（备用方案，无限流）

        Args:
            stock_query: 股票名称或代码（如"贵州茅台"、"600519"）

        Returns:
            Dictionary containing stock information
        """
        try:
            query = stock_query.strip()

            # 步骤1：将股票名称转换为代码
            stock_code = None
            if query.isdigit() and len(query) == 6:
                # 已经是6位代码
                stock_code = query
            else:
                # 通过名称查找代码
                code_name_df = ak.stock_info_a_code_name()
                result = code_name_df[code_name_df['name'].str.contains(query, na=False)]
                if result.empty:
                    return {"error": f"未找到A股股票：{stock_query}"}
                stock_code = result.iloc[0]['code']

            # 步骤2：获取个股实时信息
            info_df = ak.stock_individual_info_em(symbol=stock_code)

            # 将 DataFrame 转换为字典（item -> value）
            info_dict = dict(zip(info_df['item'], info_df['value']))

            # 获取实时行情（需要另一个接口）
            # 使用股票代码名称映射获取名称
            code_name_df = ak.stock_info_a_code_name()
            stock_name = code_name_df[code_name_df['code'] == stock_code]['name'].iloc[0]

            current_price = float(info_dict.get('最新', 0))

            return {
                "symbol": stock_code,
                "name": stock_name,
                "current_price": current_price,
                "previous_close": current_price,  # AKShare个股接口没有昨收，用当前价
                "change_amount": 0,  # 无涨跌额数据
                "change_percent": 0,  # 无涨跌幅数据
                "volume": "N/A",
                "market_cap": float(info_dict.get('总市值', 0)),
                "currency": "CNY",
                "exchange": "A股",
                "data_source": "AKShare"
            }
        except Exception as e:
            return {"error": f"AKShare 获取数据失败：{str(e)}"}

    @classmethod
    def get_stock_history_akshare(cls, symbol: str, days: int = 30) -> Dict:
        """
        使用 AKShare 获取A股历史数据

        Args:
            symbol: 股票代码（如"600519"）
            days: 天数

        Returns:
            Dictionary with price change analysis
        """
        try:
            # 去掉 .SS .SZ 后缀，AKShare 只需要纯代码
            if '.' in symbol:
                symbol = symbol.split('.')[0]

            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days+5)).strftime("%Y%m%d")

            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )

            if df.empty or len(df) < 2:
                return {"error": "无历史数据"}

            start_price = float(df.iloc[0]['收盘'])
            end_price = float(df.iloc[-1]['收盘'])
            change_amount = end_price - start_price
            change_percent = (change_amount / start_price * 100)

            # 趋势判断
            if change_percent > 2:
                trend = "上涨"
            elif change_percent < -2:
                trend = "下跌"
            else:
                trend = "震荡"

            return {
                "symbol": symbol,
                "period": f"{len(df)}日",
                "start_price": round(start_price, 2),
                "end_price": round(end_price, 2),
                "change_amount": round(change_amount, 2),
                "change_percent": round(change_percent, 2),
                "high": round(float(df['最高'].max()), 2),
                "low": round(float(df['最低'].min()), 2),
                "trend": trend,
                "data_points": len(df),
                "data_source": "AKShare"
            }
        except Exception as e:
            return {"error": f"AKShare 获取历史数据失败：{str(e)}"}

    # ==================== Alpha Vantage 数据获取方法 ====================

    @classmethod
    def get_stock_info_alphavantage(cls, symbol: str) -> Dict:
        """
        使用 Alpha Vantage API 获取股票实时数据（纯 requests，无需额外库）

        Args:
            symbol: 股票代码（如"BABA", "AAPL"）

        Returns:
            Dictionary containing stock information
        """
        api_key = Config.ALPHA_VANTAGE_API_KEY
        if not api_key or api_key == "your_alpha_vantage_key":
            return {"error": "Alpha Vantage API key not configured"}

        # 速率限制：确保每次请求间隔至少1.2秒
        current_time = time.time()
        elapsed = current_time - cls._last_alphavantage_call
        if elapsed < cls._alphavantage_delay:
            time.sleep(cls._alphavantage_delay - elapsed)
        cls._last_alphavantage_call = time.time()

        try:
            # 使用 Alpha Vantage GLOBAL_QUOTE API
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # 检查错误
            if "Error Message" in data:
                return {"error": f"未找到股票：{symbol}"}

            if "Note" in data:
                return {"error": "Alpha Vantage API 请求过于频繁"}

            # 提取数据
            quote = data.get("Global Quote", {})
            if not quote:
                return {"error": f"未找到股票数据：{symbol}"}

            current_price = float(quote.get("05. price", 0))
            prev_close = float(quote.get("08. previous close", 0))
            change = float(quote.get("09. change", 0))
            change_percent = float(quote.get("10. change percent", "0").rstrip('%'))
            volume = int(quote.get("06. volume", 0))

            return {
                "symbol": symbol,
                "name": symbol,
                "current_price": round(current_price, 2),
                "previous_close": round(prev_close, 2),
                "change_amount": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": volume,
                "market_cap": "N/A",
                "currency": "USD",
                "exchange": "Alpha Vantage",
                "data_source": "Alpha Vantage"
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"Alpha Vantage 网络请求失败：{str(e)}"}
        except Exception as e:
            return {"error": f"Alpha Vantage 获取数据失败：{str(e)}"}

    @classmethod
    def get_stock_info_with_fallback(cls, stock_query: str) -> Dict:
        """
        多API降级策略：Alpha Vantage -> AKShare (不使用yfinance避免限流)

        Args:
            stock_query: 股票名称或代码

        Returns:
            Dictionary containing stock information
        """
        # 策略1: 优先使用 Alpha Vantage（稳定，免费500次/天）
        # 先将股票名转为symbol
        symbol = cls.resolve_symbol(stock_query) or stock_query
        # 去掉后缀（如 .SS, .SZ）
        if '.' in symbol:
            symbol = symbol.split('.')[0]

        alphavantage_result = cls.get_stock_info_alphavantage(symbol)
        if "error" not in alphavantage_result:
            return alphavantage_result

        # 策略2: 如果是中文名或A股代码，尝试 AKShare（国内网络）
        if any('\u4e00' <= c <= '\u9fff' for c in stock_query) or \
           (stock_query.isdigit() and len(stock_query) == 6):
            akshare_result = cls.get_stock_info_akshare(stock_query)
            if "error" not in akshare_result:
                return akshare_result
            # 所有API都失败
            return {
                "error": f"Alpha Vantage: {alphavantage_result.get('error', 'Unknown')} | AKShare: {akshare_result.get('error', 'Unknown')}"
            }

        # 非中文股票，只使用 Alpha Vantage
        return alphavantage_result

    @classmethod
    def calculate_price_change_with_fallback(cls, stock_query: str, days: int = 7) -> Dict:
        """
        多API降级策略：历史数据查询
        """
        # 策略1: yfinance
        yfinance_result = cls.calculate_price_change(stock_query, days)

        if "error" not in yfinance_result:
            return yfinance_result

        # 策略2: AKShare（A股）
        symbol = cls.resolve_symbol(stock_query)
        if symbol and ('SS' in symbol or 'SZ' in symbol):
            akshare_result = cls.get_stock_history_akshare(symbol, days)
            if "error" not in akshare_result:
                return akshare_result
            # 都失败，返回合并的错误信息
            return {
                "error": f"yfinance: {yfinance_result.get('error', 'Unknown')} | AKShare: {akshare_result.get('error', 'Unknown')}"
            }

        # 只有 yfinance 失败，返回 yfinance 的错误
        return yfinance_result
