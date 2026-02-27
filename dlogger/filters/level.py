
from ..handlers.base import Filter, LogRecord

class LevelFilter(Filter):
    """filter that filters records based on log level."""

    def __init__(self, min_level: str = "TRACE"):
        from dlogger.logger import dLogger
        level_data = dLogger.LEVELS.get(min_level.upper())
        self._min_level = level_data[0] if level_data else 10

    def filter(self, record: LogRecord) -> bool:
        """return True if record level is >= min_level."""
        return record.level_value >= self._min_level
