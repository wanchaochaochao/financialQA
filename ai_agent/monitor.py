"""
Performance Monitoring System
==============================

Real-time performance monitoring and metrics aggregation for the
financial QA system.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from collections import defaultdict

from .logger import QALogger


class PerformanceMonitor:
    """
    Real-time performance monitoring and metrics aggregation.

    Features:
    - Aggregates metrics from log files
    - Tracks performance trends
    - Generates monitoring reports
    - Provides dashboard data
    """

    def __init__(self, logger: Optional[QALogger] = None):
        """
        Initialize performance monitor.

        Args:
            logger: QA logger instance (optional)
        """
        self.logger = logger or QALogger()

    def get_realtime_metrics(self) -> dict:
        """
        Get real-time metrics from current session.

        Returns:
            Dictionary with real-time metrics
        """
        return self.logger.get_session_metrics()

    def get_daily_metrics(self, date: Optional[str] = None) -> dict:
        """
        Get metrics for a specific day.

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            Dictionary with daily metrics
        """
        return self.logger.get_statistics(date)

    def get_multi_day_metrics(self, days: int = 7) -> List[dict]:
        """
        Get metrics for the past N days.

        Args:
            days: Number of days to look back

        Returns:
            List of daily metrics
        """
        metrics = []
        today = datetime.now()

        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_metrics = self.get_daily_metrics(date)
            if daily_metrics["total_requests"] > 0:
                metrics.append(daily_metrics)

        return metrics

    def get_performance_trends(self, days: int = 7) -> dict:
        """
        Analyze performance trends over time.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with trend analysis
        """
        multi_day_metrics = self.get_multi_day_metrics(days)

        if not multi_day_metrics:
            return {
                "trend_period_days": days,
                "data_available": False,
            }

        # Calculate trends
        dates = [m["date"] for m in multi_day_metrics]
        success_rates = [m["success_rate"] for m in multi_day_metrics]
        avg_response_times = [m["average_response_time_ms"] for m in multi_day_metrics]
        total_requests = [m["total_requests"] for m in multi_day_metrics]

        return {
            "trend_period_days": days,
            "data_available": True,
            "dates": dates,
            "total_requests": {
                "values": total_requests,
                "sum": sum(total_requests),
                "average": sum(total_requests) / len(total_requests),
            },
            "success_rate": {
                "values": success_rates,
                "average": sum(success_rates) / len(success_rates),
                "min": min(success_rates),
                "max": max(success_rates),
                "trend": "improving" if success_rates[0] > success_rates[-1] else "declining",
            },
            "response_time_ms": {
                "values": avg_response_times,
                "average": sum(avg_response_times) / len(avg_response_times),
                "min": min(avg_response_times),
                "max": max(avg_response_times),
                "trend": "improving" if avg_response_times[0] < avg_response_times[-1] else "declining",
            },
        }

    def get_tool_usage_stats(self, days: int = 7) -> dict:
        """
        Get tool usage statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with tool usage stats
        """
        multi_day_metrics = self.get_multi_day_metrics(days)

        # Aggregate tool usage
        total_tool_usage = defaultdict(int)
        for daily in multi_day_metrics:
            for tool, count in daily.get("tools_usage", {}).items():
                total_tool_usage[tool] += count

        # Calculate percentages
        total_uses = sum(total_tool_usage.values())
        tool_percentages = {
            tool: (count / total_uses * 100) if total_uses > 0 else 0
            for tool, count in total_tool_usage.items()
        }

        # Sort by usage
        sorted_tools = sorted(total_tool_usage.items(), key=lambda x: x[1], reverse=True)

        return {
            "period_days": days,
            "total_tool_calls": total_uses,
            "tool_usage_counts": dict(sorted_tools),
            "tool_usage_percentages": tool_percentages,
            "most_used_tool": sorted_tools[0][0] if sorted_tools else None,
        }

    def get_error_analysis(self, days: int = 7) -> dict:
        """
        Analyze errors over time.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with error analysis
        """
        multi_day_metrics = self.get_multi_day_metrics(days)

        # Aggregate error types
        total_error_types = defaultdict(int)
        total_errors = 0

        for daily in multi_day_metrics:
            total_errors += daily.get("failed_requests", 0)
            for error_type, count in daily.get("error_types", {}).items():
                total_error_types[error_type] += count

        # Sort by frequency
        sorted_errors = sorted(total_error_types.items(), key=lambda x: x[1], reverse=True)

        return {
            "period_days": days,
            "total_errors": total_errors,
            "error_types": dict(sorted_errors),
            "most_common_error": sorted_errors[0][0] if sorted_errors else None,
            "error_type_count": len(total_error_types),
        }

    def generate_health_report(self) -> dict:
        """
        Generate overall system health report.

        Returns:
            Dictionary with health indicators
        """
        today_metrics = self.get_daily_metrics()
        week_trends = self.get_performance_trends(days=7)

        # Determine health status
        success_rate = today_metrics.get("success_rate", 0)
        avg_response_time = today_metrics.get("average_response_time_ms", 0)

        # Health thresholds
        if success_rate >= 0.95 and avg_response_time <= 2000:
            health_status = "excellent"
            health_score = 95
        elif success_rate >= 0.90 and avg_response_time <= 3000:
            health_status = "good"
            health_score = 80
        elif success_rate >= 0.80 and avg_response_time <= 5000:
            health_status = "fair"
            health_score = 60
        else:
            health_status = "poor"
            health_score = 40

        # Generate recommendations
        recommendations = []
        if success_rate < 0.90:
            recommendations.append("成功率低于90%，建议检查错误日志和失败案例")
        if avg_response_time > 3000:
            recommendations.append("平均响应时间超过3秒，建议优化查询性能")
        if today_metrics.get("total_requests", 0) == 0:
            recommendations.append("今日暂无请求数据")

        return {
            "health_status": health_status,
            "health_score": health_score,
            "timestamp": datetime.now().isoformat(),
            "today_metrics": today_metrics,
            "weekly_trends": week_trends,
            "recommendations": recommendations,
        }

    def generate_dashboard_data(self) -> dict:
        """
        Generate comprehensive dashboard data.

        Returns:
            Dictionary with all dashboard metrics
        """
        return {
            "realtime": self.get_realtime_metrics(),
            "today": self.get_daily_metrics(),
            "trends_7d": self.get_performance_trends(days=7),
            "tool_usage_7d": self.get_tool_usage_stats(days=7),
            "error_analysis_7d": self.get_error_analysis(days=7),
            "health_report": self.generate_health_report(),
        }


# Global monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_monitor() -> PerformanceMonitor:
    """Get global monitor instance (singleton)"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor
