
from typing import Optional
from dcolor import color

from .base import Handler, LogRecord

class ConsoleHandler(Handler):
    """handler that writes log records to console/stdout."""

    def __init__(
        self,
        level: str = "TRACE",
        formatter: Optional[object] = None,
        show_path: bool = True,
    ):
        super().__init__(level=level, formatter=formatter)
        self._show_path = show_path
        self._separator = color('|', 'white')
        self._dash = color('-', 'white')

    def emit(self, record: LogRecord):
        """emit a log record to console."""
        if not self._should_log(record):
            return

        time_str = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        context = record.context if self._show_path else ""

        is_critical = record.level == "CRITICAL"

        msg = (
            f"{color(time_str, '#4caf50')} "
            f"{self._separator} {color(f'{record.level: <8}', record.color or '#ffffff', 'bold', *(('underline',) if is_critical else ()))} "
            f"{self._separator} {color(context, '#00bcd4')} "
            f"{self._dash} {record.message}"
        )
        print(msg)
