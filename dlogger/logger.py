
from datetime import datetime
from typing import Optional, Literal, List, Union
import threading
import inspect
import os

from .handlers.base import Handler, LogRecord
from .handlers.console import ConsoleHandler
from .handlers.file import FileHandler
from .formatters.exception import ExceptionFormatter

class dLogger:
    """main logger class - facade over handlers."""

    LEVELS = {
        "TRACE": (10, "#00bcd4"),
        "DEBUG": (10, "#3b82f6"),
        "INFO": (20, "#ffffff"),
        "SUCCESS": (30, "#4caf50"),
        "WARNING": (30, "#ff9800"),
        "ERROR": (40, "#f44336"),
        "CRITICAL": (50, "#f44336"),
    }

    def __init__(self):
        self._level = 10
        self._handlers: List[Handler] = []
        self._lock = threading.Lock()
        self._context_cache = {}

        self.add_handler(ConsoleHandler(level="TRACE"))

    @property
    def handlers(self) -> List[Handler]:
        return self._handlers

    def add_handler(self, handler: Handler):
        """add a handler to the logger."""
        with self._lock:
            self._handlers.append(handler)

    def remove_handler(self, handler: Handler):
        """remove a handler from the logger."""
        with self._lock:
            if handler in self._handlers:
                self._handlers.remove(handler)

    def configure(
        self,
        level: Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"] = "DEBUG",
        log_file: Optional[str] = None,
        show_path: bool = True,
        rotation: Optional[str] = None,
        retention: Optional[str] = None,
        compression: bool = False,
        time_format: Literal[
            "%Y-%m-%d %H:%M:%S",
            "%H:%M:%S",
            "%d.%m.%Y %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f"
        ] = "%Y-%m-%d %H:%M:%S"
    ):
        """
        configure logger settings.

        args:
            level: Logging level
            log_file: Path to log file
            show_path: Show module:function: in logs
            rotation: Log rotation ("10MB", "1GB", "1 day", "12 hours")
            retention: How long to keep logs ("7 days", "1 month")
            compression: Compress old logs to .gz
            time_format: Time format string
        """
        self._level = self.LEVELS.get(level.upper(), (10,))[0]

        for handler in self._handlers:
            handler.set_level(level)
            if isinstance(handler, ConsoleHandler):
                handler._show_path = show_path

        if log_file:
            file_handler = FileHandler(
                filename=log_file,
                level=level,
                rotation=rotation,
                retention=retention,
                compression=compression,
                time_format=time_format,
            )
            self.add_handler(file_handler)

        return self

    def _get_context(self) -> str:
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back
            if not caller_frame:
                return "unknown"
            
            caller_frame = caller_frame.f_back
            if not caller_frame:
                return "unknown"
            
            caller_frame = caller_frame.f_back
            if not caller_frame:
                return "unknown"
            
            filename = caller_frame.f_code.co_filename
            lineno = caller_frame.f_lineno
            
            cache_key = (filename, lineno)
            if cache_key in self._context_cache:
                return self._context_cache[cache_key]
            
            if "dlogger" not in caller_frame.f_globals.get("__name__", ""):
                module = caller_frame.f_globals.get("__name__", "unknown")
                function = caller_frame.f_code.co_name
                result = f"{module}:{function}:"
                
                with self._lock:
                    if len(self._context_cache) < 128:
                        self._context_cache[cache_key] = result
                
                return result
            
            return "unknown"
        finally:
            del frame

    def _log(self, level_name: str, msg: str):
        level_data = self.LEVELS.get(level_name)
        if not level_data:
            return

        level_val, clr = level_data
        if level_val < self._level:
            return

        context = self._get_context()
        now = datetime.now()

        record = LogRecord(
            level=level_name,
            level_value=level_val,
            message=msg,
            context=context,
            timestamp=now,
            color=clr,
        )

        with self._lock:
            for handler in self._handlers:
                handler.emit(record)

    def trace(self, msg: str):
        self._log("TRACE", msg)

    def debug(self, msg: str):
        self._log("DEBUG", msg)

    def info(self, msg: str):
        self._log("INFO", msg)

    def success(self, msg: str):
        self._log("SUCCESS", msg)

    def warning(self, msg: str):
        self._log("WARNING", msg)

    def error(self, msg: str):
        self._log("ERROR", msg)

    def critical(self, msg: str):
        self._log("CRITICAL", msg)

    def exception(self, msg: str, exc: Optional[BaseException] = None):
        """log exception with traceback.
        
        args:
            msg: message
            exc: exception object (optional, uses sys.exc_info() if not provided)
        """
        if exc is None:
            exc = ExceptionFormatter.get_current_exception()
        
        if exc:
            tb = ExceptionFormatter.format_exception(exc)
            full_msg = f"{msg}\n{tb}"
        else:
            full_msg = msg
        
        self._log("ERROR", full_msg)

logger = dLogger()
