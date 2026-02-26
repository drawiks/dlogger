
from ..handlers.base import Formatter, LogRecord

class SimpleFormatter(Formatter):
    """simple formatter that formats log records as plain text."""

    def __init__(self, time_format: str = "%Y-%m-%d %H:%M:%S"):
        self._time_format = time_format

    def format(self, record: LogRecord) -> str:
        """format a log record as plain text."""
        time_str = record.timestamp.strftime(self._time_format)
        return f"[{time_str}] | {record.level: <8} | {record.context} {record.message}"
