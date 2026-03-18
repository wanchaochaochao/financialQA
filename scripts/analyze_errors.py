"""
Error Analysis Script
=====================

Analyzes QA logs to identify patterns in failures and generate
improvement recommendations.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict

# Add parent directory to path to import ai_agent modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_agent.logger import QALogger
from ai_agent.monitor import PerformanceMonitor


class ErrorAnalyzer:
    """Analyzes error logs and generates reports"""

    def __init__(self, days: int = 7):
        """
        Initialize error analyzer.

        Args:
            days: Number of days to analyze
        """
        self.logger = QALogger()
        self.monitor = PerformanceMonitor(self.logger)
        self.days = days

    def get_all_errors(self) -> List[Dict]:
        """
        Collect all error logs from the analysis period.

        Returns:
            List of error log entries
        """
        all_errors = []
        today = datetime.now()

        for i in range(self.days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            error_logs = self.logger.get_error_logs(date)
            all_errors.extend(error_logs)

        return all_errors

    def analyze_error_patterns(self, errors: List[Dict]) -> Dict:
        """
        Analyze patterns in error logs.

        Args:
            errors: List of error log entries

        Returns:
            Dictionary with pattern analysis
        """
        if not errors:
            return {
                "total_errors": 0,
                "error_types": {},
                "common_questions": {},
                "time_distribution": {},
            }

        # Error type classification
        error_types = defaultdict(int)
        for error in errors:
            if error.get("error_message"):
                # Extract error type from message
                msg = error["error_message"]
                if "timeout" in msg.lower():
                    error_types["timeout"] += 1
                elif "api" in msg.lower() or "connection" in msg.lower():
                    error_types["api_error"] += 1
                elif "parse" in msg.lower() or "parsing" in msg.lower():
                    error_types["parsing_error"] += 1
                elif "tool" in msg.lower():
                    error_types["tool_error"] += 1
                else:
                    error_types["other"] += 1

        # Common failed questions
        failed_questions = [e["question"] for e in errors if e.get("question")]
        question_counter = Counter(failed_questions)
        common_questions = dict(question_counter.most_common(10))

        # Time distribution (hour of day)
        time_distribution = defaultdict(int)
        for error in errors:
            if error.get("timestamp"):
                hour = datetime.fromisoformat(error["timestamp"]).hour
                time_distribution[hour] += 1

        return {
            "total_errors": len(errors),
            "error_types": dict(error_types),
            "common_questions": common_questions,
            "time_distribution": dict(sorted(time_distribution.items())),
        }

    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """
        Generate improvement recommendations based on error analysis.

        Args:
            analysis: Error pattern analysis

        Returns:
            List of recommendations
        """
        recommendations = []

        if analysis["total_errors"] == 0:
            return ["✅ 无错误记录，系统运行正常"]

        error_types = analysis.get("error_types", {})

        # Timeout errors
        if error_types.get("timeout", 0) > 0:
            recommendations.append(
                f"🕐 发现 {error_types['timeout']} 次超时错误，建议："
                "\n   - 增加请求超时时间"
                "\n   - 优化 LLM 调用参数"
                "\n   - 考虑添加响应缓存"
            )

        # API errors
        if error_types.get("api_error", 0) > 0:
            recommendations.append(
                f"🔌 发现 {error_types['api_error']} 次 API 错误，建议："
                "\n   - 检查网络连接稳定性"
                "\n   - 验证 API 密钥是否有效"
                "\n   - 添加 API 重试机制"
            )

        # Parsing errors
        if error_types.get("parsing_error", 0) > 0:
            recommendations.append(
                f"📝 发现 {error_types['parsing_error']} 次解析错误，建议："
                "\n   - 优化 Agent Prompt 提示词"
                "\n   - 增强输出格式约束"
                "\n   - 添加输出验证逻辑"
            )

        # Tool errors
        if error_types.get("tool_error", 0) > 0:
            recommendations.append(
                f"🔧 发现 {error_types['tool_error']} 次工具错误，建议："
                "\n   - 检查工具函数实现"
                "\n   - 添加工具异常处理"
                "\n   - 验证工具输入参数"
            )

        # Repeated failed questions
        common_questions = analysis.get("common_questions", {})
        if common_questions:
            top_question = list(common_questions.keys())[0]
            count = common_questions[top_question]
            recommendations.append(
                f"❓ 问题 \"{top_question}\" 失败了 {count} 次，建议："
                "\n   - 分析该问题为何失败"
                "\n   - 优化相关工具或知识库"
                "\n   - 添加针对性的测试用例"
            )

        return recommendations

    def generate_report(self) -> str:
        """
        Generate comprehensive error analysis report.

        Returns:
            Formatted report string
        """
        errors = self.get_all_errors()
        analysis = self.analyze_error_patterns(errors)
        recommendations = self.generate_recommendations(analysis)

        # Build report
        report = [
            "=" * 70,
            "📊 错误分析报告",
            "=" * 70,
            f"\n📅 分析周期: 最近 {self.days} 天",
            f"📈 总错误数: {analysis['total_errors']}",
            ""
        ]

        # Error types
        if analysis['error_types']:
            report.append("\n📋 错误类型分布:")
            for error_type, count in sorted(
                analysis['error_types'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                report.append(f"   • {error_type}: {count} 次")

        # Common failed questions
        if analysis['common_questions']:
            report.append("\n❓ 最常失败的问题（Top 5）:")
            for i, (question, count) in enumerate(
                list(analysis['common_questions'].items())[:5],
                1
            ):
                short_q = question[:50] + "..." if len(question) > 50 else question
                report.append(f"   {i}. [{count}次] {short_q}")

        # Time distribution
        if analysis['time_distribution']:
            report.append("\n🕐 错误时间分布（按小时）:")
            max_errors = max(analysis['time_distribution'].values())
            for hour, count in analysis['time_distribution'].items():
                bar_length = int((count / max_errors) * 30)
                bar = "█" * bar_length
                report.append(f"   {hour:02d}:00 | {bar} {count}")

        # Recommendations
        report.append("\n💡 改进建议:")
        for i, rec in enumerate(recommendations, 1):
            report.append(f"\n{i}. {rec}")

        report.append("\n" + "=" * 70)

        return "\n".join(report)

    def export_to_file(self, filename: Optional[str] = None):
        """
        Export error analysis to file.

        Args:
            filename: Output filename (default: error_analysis_YYYY-MM-DD.txt)
        """
        if filename is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"error_analysis_{date_str}.txt"

        report = self.generate_report()

        output_path = Path(__file__).parent.parent / "logs" / filename
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        return output_path


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze QA error logs")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to analyze (default: 7)"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export report to file"
    )

    args = parser.parse_args()

    print("\n🔍 分析错误日志...\n")

    analyzer = ErrorAnalyzer(days=args.days)
    report = analyzer.generate_report()

    print(report)

    if args.export:
        output_path = analyzer.export_to_file()
        print(f"\n✅ 报告已导出到: {output_path}")


if __name__ == "__main__":
    main()
