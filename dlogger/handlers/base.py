
from abc import ABC, abstractmethod
from typing import Optional, List, Any
from datetime import datetime

class Formatter:
    """base formatter interface."""

    def format(self, record: "LogRecord") -> str:
        """format a log record."""
        raise NotImplementedError

class LogRecord:
    """represents a single log event."""

    def __init__(
        self,
        level: str,
        level_value: int,
        message: str,
        context: str,
        timestamp: datetime,
        color: Optional[str] = None,
    ):
        self.level = level
        self.level_value = level_value
        self.message = message
        self.context = context
        self.timestamp = timestamp
        self.color = color

class Filter(ABC):
    """base filter interface."""

    @abstractmethod
    def filter(self, record: LogRecord) -> bool:
        """return True if record should be logged."""
        raise NotImplementedError

class Handler(ABC):
    """abstract base class for log handlers."""

    def __init__(
        self,
        level: str = "TRACE",
        formatter: Optional[Formatter] = None,
        filters: Optional[List[Filter]] = None,
    ):
        self._level = 10
        self._formatter = formatter
        self._filters = filters or []
        self.set_level(level)

    @property
    def level(self) -> int:
        return self._level

    @property
    def formatter(self) -> Optional[Formatter]:
        return self._formatter

    @formatter.setter
    def formatter(self, value: Optional[Formatter]):
        self._formatter = value

    @property
    def filters(self) -> List[Filter]:
        return self._filters

    def add_filter(self, filter_obj: Filter):
        """add a filter to this handler."""
        self._filters.append(filter_obj)

    def set_level(self, level: str):
        """set the handler's minimum log level."""
        from dlogger.logger import dLogger
        level_data = dLogger.LEVELS.get(level.upper())
        if level_data:
            self._level = level_data[0]

    def _should_log(self, record: LogRecord) -> bool:
        """check if record should be logged based on level and filters."""
        if record.level_value < self._level:
            return False

        for filter_obj in self._filters:
            if not filter_obj.filter(record):
                return False
        return True

    @abstractmethod
    def emit(self, record: LogRecord):
        """emit a log record. Must be implemented by subclasses."""
        raise NotImplementedError

    def close(self):
        """close the handler and release resources."""
        pass
