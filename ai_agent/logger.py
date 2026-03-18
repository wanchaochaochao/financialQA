"""
QA Logging System
=================

Logs all question-answer interactions for monitoring, evaluation,
and continuous improvement.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from .config import Config


@dataclass
class QALogEntry:
    """Single question-answer log entry"""
    timestamp: str
    question: str
    answer: str
    response_time_ms: float
    success: bool
    tools_used: List[str]
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class QALogger:
    """
    Question-Answer Logger for monitoring and evaluation.

    Features:
    - Logs all QA interactions to JSONL file
    - Tracks response time
    - Records success/failure status
    - Captures tool usage patterns
    - Thread-safe logging
    """

    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize QA logger.

        Args:
            log_dir: Directory to store log files (default: project_root/logs)
        """
        if log_dir is None:
            self.log_dir = Config.BASE_DIR.parent / "logs"
        else:
            self.log_dir = log_dir

        self.log_dir.mkdir(exist_ok=True)

        # Create log file path with date
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"qa_logs_{today}.jsonl"

        # Initialize session metrics
        self.session_start = datetime.now()
        self.session_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time_ms": 0.0,
            "tools_usage": {},
        }

    def log_qa(
        self,
        question: str,
        answer: str,
        response_time_ms: float,
        success: bool = True,
        tools_used: Optional[List[str]] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a question-answer interaction.

        Args:
            question: User question
            answer: Agent answer
            response_time_ms: Response time in milliseconds
            success: Whether the request was successful
            tools_used: List of tools used by the agent
            error_message: Error message if request failed
            metadata: Additional metadata
        """
        # Create log entry
        entry = QALogEntry(
            timestamp=datetime.now().isoformat(),
            question=question,
            answer=answer,
            response_time_ms=response_time_ms,
            success=success,
            tools_used=tools_used or [],
            error_message=error_message,
            metadata=metadata,
        )

        # Write to log file (JSONL format)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

        # Update session metrics
        self._update_session_metrics(entry)

    def _update_session_metrics(self, entry: QALogEntry) -> None:
        """Update session-level metrics"""
        self.session_metrics["total_requests"] += 1

        if entry.success:
            self.session_metrics["successful_requests"] += 1
        else:
            self.session_metrics["failed_requests"] += 1

        self.session_metrics["total_response_time_ms"] += entry.response_time_ms

        # Track tool usage
        for tool in entry.tools_used:
            if tool not in self.session_metrics["tools_usage"]:
                self.session_metrics["tools_usage"][tool] = 0
            self.session_metrics["tools_usage"][tool] += 1

    def get_session_metrics(self) -> dict:
        """
        Get current session metrics.

        Returns:
            Dictionary with session metrics
        """
        total_requests = self.session_metrics["total_requests"]

        if total_requests == 0:
            return {
                "session_start": self.session_start.isoformat(),
                "total_requests": 0,
                "success_rate": 0.0,
                "average_response_time_ms": 0.0,
                "tools_usage": {},
            }

        return {
            "session_start": self.session_start.isoformat(),
            "session_duration_seconds": (datetime.now() - self.session_start).total_seconds(),
            "total_requests": total_requests,
            "successful_requests": self.session_metrics["successful_requests"],
            "failed_requests": self.session_metrics["failed_requests"],
            "success_rate": self.session_metrics["successful_requests"] / total_requests,
            "average_response_time_ms": self.session_metrics["total_response_time_ms"] / total_requests,
            "tools_usage": self.session_metrics["tools_usage"],
        }

    def load_logs(self, date: Optional[str] = None) -> List[Dict]:
        """
        Load logs from file.

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            List of log entries
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        log_file = self.log_dir / f"qa_logs_{date}.jsonl"

        if not log_file.exists():
            return []

        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                logs.append(json.loads(line))

        return logs

    def get_error_logs(self, date: Optional[str] = None) -> List[Dict]:
        """
        Get all error logs for a specific date.

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            List of error log entries
        """
        all_logs = self.load_logs(date)
        return [log for log in all_logs if not log["success"]]

    def get_statistics(self, date: Optional[str] = None) -> dict:
        """
        Get statistics for a specific date.

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            Dictionary with statistics
        """
        logs = self.load_logs(date)

        if not logs:
            return {
                "total_requests": 0,
                "success_rate": 0.0,
                "average_response_time_ms": 0.0,
                "tools_usage": {},
                "error_types": {},
            }

        total_requests = len(logs)
        successful_requests = sum(1 for log in logs if log["success"])
        total_response_time = sum(log["response_time_ms"] for log in logs)

        # Tool usage statistics
        tools_usage = {}
        for log in logs:
            for tool in log["tools_used"]:
                if tool not in tools_usage:
                    tools_usage[tool] = 0
                tools_usage[tool] += 1

        # Error type statistics
        error_types = {}
        for log in logs:
            if not log["success"] and log.get("error_message"):
                error_msg = log["error_message"]
                # Extract error type (first part of error message)
                error_type = error_msg.split(":")[0] if ":" in error_msg else "Unknown"
                if error_type not in error_types:
                    error_types[error_type] = 0
                error_types[error_type] += 1

        return {
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": total_requests - successful_requests,
            "success_rate": successful_requests / total_requests,
            "average_response_time_ms": total_response_time / total_requests,
            "median_response_time_ms": sorted([log["response_time_ms"] for log in logs])[total_requests // 2],
            "tools_usage": tools_usage,
            "error_types": error_types,
        }


# Global logger instance
_global_logger: Optional[QALogger] = None


def get_logger() -> QALogger:
    """Get global logger instance (singleton)"""
    global _global_logger
    if _global_logger is None:
        _global_logger = QALogger()
    return _global_logger


def log_qa_interaction(
    question: str,
    answer: str,
    response_time_ms: float,
    success: bool = True,
    tools_used: Optional[List[str]] = None,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Convenience function to log QA interaction using global logger.

    Args:
        question: User question
        answer: Agent answer
        response_time_ms: Response time in milliseconds
        success: Whether the request was successful
        tools_used: List of tools used
        error_message: Error message if failed
        metadata: Additional metadata
    """
    logger = get_logger()
    logger.log_qa(
        question=question,
        answer=answer,
        response_time_ms=response_time_ms,
        success=success,
        tools_used=tools_used,
        error_message=error_message,
        metadata=metadata,
    )
