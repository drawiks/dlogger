from .logger import logger, dLogger
from .handlers import Handler, ConsoleHandler, FileHandler, LogRecord, Filter
from .formatters import Formatter, SimpleFormatter, ExceptionFormatter
from .filters import LevelFilter, KeywordFilter, ModuleFilter
from .integrations import uvicorn_config
from .handlers.compat import CompatHandler

__version__ = "0.3.6"

_loggers = {}
_MAX_LOGGERS = 128


def get_logger(name: str = None):
    """get a dlogger instance, compatible with logging.getLogger().
    
    args:
        name: optional name for named logger
    
    returns:
        dLogger instance
    """
    if name is None:
        return logger

    if name in _loggers:
        return _loggers[name]

    if len(_loggers) >= _MAX_LOGGERS:
        _loggers.clear()

    new_logger = dLogger(name=name)

    if "." in name:
        parent_name = name.rsplit(".", 1)[0]
        if parent_name in _loggers:
            new_logger._parent = _loggers[parent_name]

    _loggers[name] = new_logger
    return new_logger


__all__ = [
    "logger",
    "dLogger",
    "get_logger",
    "Handler",
    "ConsoleHandler",
    "FileHandler",
    "LogRecord",
    "Filter",
    "Formatter",
    "SimpleFormatter",
    "ExceptionFormatter",
    "LevelFilter",
    "KeywordFilter",
    "ModuleFilter",
    "CompatHandler",
    "uvicorn_config",
]
