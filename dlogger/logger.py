
from datetime import datetime
from typing import Optional, Literal, List, Callable, Union, Dict
import threading
import inspect
import contextlib
import contextvars

from .handlers.base import Handler, LogRecord
from .handlers.console import ConsoleHandler
from .handlers.file import FileHandler
from .formatters.exception import ExceptionFormatter

_context_var: contextvars.ContextVar[Dict] = contextvars.ContextVar("dlogger_context", default={})

class dLogger:
    """main logger class - facade over handlers."""

    LEVELS = {
        "TRACE": (5, "#00bcd4"),
        "DEBUG": (10, "#3b82f6"),
        "INFO": (20, "#ffffff"),
        "SUCCESS": (25, "#4caf50"),
        "WARNING": (30, "#ff9800"),
        "ERROR": (40, "#f44336"),
        "CRITICAL": (50, "#f44336"),
    }

    def __init__(self, name: str = None):
        self._name = name
        self._parent = None
        self._level = 10
        self._handlers: List[Handler] = []
        self._lock = threading.Lock()
        self._context_cache = {}

        if name is None:
            self.add_handler(ConsoleHandler(level="TRACE"))

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self):
        return self._parent

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
        serialize: bool = False,
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
            serialize: Output logs as JSON
            time_format: Time format string
        """
        self._level = self.LEVELS.get(level.upper(), (10,))[0]

        for handler in self._handlers:
            handler.set_level(level)
            if isinstance(handler, ConsoleHandler):
                handler.show_path = show_path

        if log_file:
            existing = [h for h in self._handlers if isinstance(h, FileHandler)]
            for h in existing:
                self.remove_handler(h)

            file_handler = FileHandler(
                filename=log_file,
                level=level,
                rotation=rotation,
                retention=retention,
                compression=compression,
                serialize=serialize,
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

            while caller_frame:
                module_name = caller_frame.f_globals.get("__name__", "")
                if "dlogger" not in module_name:
                    filename = caller_frame.f_code.co_filename
                    co_name = caller_frame.f_code.co_name

                    cache_key = (filename, co_name)
                    with self._lock:
                        if cache_key in self._context_cache:
                            return self._context_cache[cache_key]

                    function = caller_frame.f_code.co_name
                    result = f"{module_name}:{function}:"

                    with self._lock:
                        if len(self._context_cache) < 128:
                            self._context_cache[cache_key] = result

                    return result

                caller_frame = caller_frame.f_back

            return "unknown"
        finally:
            del frame

    def _log(self, level_name: str, msg: Union[str, Callable[[], str]], context: str = None, extra: Dict = None):
        level_data = self.LEVELS.get(level_name)
        if not level_data:
            return

        level_val, clr = level_data
        effective_level = self._level
        if self._parent and not self._handlers:
            effective_level = self._parent._level
        if level_val < effective_level:
            return

        if callable(msg):
            msg = msg()

        context = context or self._get_context()
        now = datetime.now()

        ctx_extra = _context_var.get({})
        merged_extra = {**ctx_extra, **(extra or {})}

        record = LogRecord(
            level=level_name,
            level_value=level_val,
            message=msg,
            context=context,
            timestamp=now,
            color=clr,
            extra=merged_extra if merged_extra else None,
        )

        handlers = self._handlers if self._handlers else (self._parent._handlers if self._parent else [])

        with self._lock:
            for handler in handlers:
                handler.emit(record)

    def trace(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("TRACE", msg, context)

    def debug(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("DEBUG", msg, context)

    def info(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("INFO", msg, context)

    def success(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("SUCCESS", msg, context)

    def warning(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("WARNING", msg, context)

    def error(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("ERROR", msg, context)

    def critical(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("CRITICAL", msg, context)

    def exception(self, msg: Union[str, Callable[[], str]], exc: Optional[BaseException] = None, context: str = None):
        """log exception with traceback.

        args:
            msg: message
            exc: exception object (optional, uses sys.exc_info() if not provided)
            context: context string (optional)
        """
        if exc is None:
            exc = ExceptionFormatter.get_current_exception()

        if exc:
            tb = ExceptionFormatter.format_exception(exc)
            full_msg = f"{msg}\n{tb}"
        else:
            full_msg = msg

        self._log("ERROR", full_msg, context)

    def bind(self, **kwargs) -> "BoundLogger":
        """bind key-value context to logger. all subsequent log calls will include this context."""
        return BoundLogger(self, kwargs)

    @staticmethod
    @contextlib.contextmanager
    def contextualize(**kwargs):
        """temporary context manager for scoped context. async-safe via contextvars."""
        prev = _context_var.get({})
        merged = {**prev, **kwargs}
        token = _context_var.set(merged)
        try:
            yield
        finally:
            _context_var.reset(token)

    def __repr__(self) -> str:
        name = f"'{self._name}'" if self._name else "root"
        return f"<dLogger {name} level={self._level} handlers={len(self._handlers)}>"


class BoundLogger:
    """logger wrapper with bound context. all log calls include bound key-value pairs."""

    def __init__(self, parent: dLogger, extra: Dict):
        self._parent = parent
        self._extra = extra

    @property
    def name(self) -> str:
        return self._parent.name

    @property
    def handlers(self) -> List[Handler]:
        return self._parent.handlers

    def add_handler(self, handler: Handler):
        self._parent.add_handler(handler)

    def remove_handler(self, handler: Handler):
        self._parent.remove_handler(handler)

    def configure(self, **kwargs):
        return self._parent.configure(**kwargs)

    def bind(self, **kwargs) -> "BoundLogger":
        return BoundLogger(self._parent, {**self._extra, **kwargs})

    @staticmethod
    @contextlib.contextmanager
    def contextualize(**kwargs):
        return dLogger.contextualize(**kwargs)

    def _log(self, level_name: str, msg: Union[str, Callable[[], str]], context: str = None):
        self._parent._log(level_name, msg, context, extra=self._extra)

    def trace(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("TRACE", msg, context)

    def debug(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("DEBUG", msg, context)

    def info(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("INFO", msg, context)

    def success(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("SUCCESS", msg, context)

    def warning(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("WARNING", msg, context)

    def error(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("ERROR", msg, context)

    def critical(self, msg: Union[str, Callable[[], str]], context: str = None):
        self._log("CRITICAL", msg, context)

    def exception(self, msg: Union[str, Callable[[], str]], exc: Optional[BaseException] = None, context: str = None):
        if exc is None:
            exc = ExceptionFormatter.get_current_exception()

        if exc:
            tb = ExceptionFormatter.format_exception(exc)
            full_msg = f"{msg}\n{tb}"
        else:
            full_msg = msg

        self._log("ERROR", full_msg, context)

    def __repr__(self) -> str:
        return f"<BoundLogger {self._parent!r} extra={self._extra}>"


logger = dLogger()
