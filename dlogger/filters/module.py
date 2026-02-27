
from ..handlers.base import Filter, LogRecord

class ModuleFilter(Filter):
    """filter that includes only records from specific modules."""

    def __init__(self, modules: list[str]):
        self.modules = modules

    def filter(self, record: LogRecord) -> bool:
        return any(mod in record.context for mod in self.modules)
