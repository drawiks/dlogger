
import sys
import traceback
from typing import Optional

from ..handlers.base import Formatter

class ExceptionFormatter(Formatter):
    """formatter that formats exceptions with traceback."""

    def format(self, record: "handlers.LogRecord") -> str:
        """format a log record with exception traceback."""
        raise NotImplementedError

    @staticmethod
    def format_exception(exc: Optional[BaseException]) -> str:
        """
        format exception with full traceback.

        args:
            exc: exception object

        returns:
            formatted traceback string
        """
        if exc:
            return ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        return ""

    @staticmethod
    def get_current_exception() -> Optional[BaseException]:
        """
        get current exception from sys.exc_info().

        returns:
            current exception or None
        """
        exc_info = sys.exc_info()
        return exc_info[1]
