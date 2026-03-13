
import logging


class CompatHandler(logging.Handler):
    """handler that receives logs from standard logging."""

    def __init__(self, dlogger):
        super().__init__()
        self._dlogger = dlogger

    def emit(self, record: logging.LogRecord):
        """emit a log record from logging to dlogger."""
        if record.levelno < logging.DEBUG:
            level_name = "trace"
        else:
            level_map = {
                logging.DEBUG: "debug",
                logging.INFO: "info",
                logging.WARNING: "warning",
                logging.ERROR: "error",
                logging.CRITICAL: "critical",
            }
            level_name = level_map.get(record.levelno, "info")

        msg = record.getMessage()
        context = f"{record.name}:{record.module}:{record.funcName}:"

        if record.exc_info:
            self._dlogger.exception(msg, context=context)
        else:
            getattr(self._dlogger, level_name)(msg, context=context)
