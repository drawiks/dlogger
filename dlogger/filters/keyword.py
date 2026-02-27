
from ..handlers.base import Filter, LogRecord

class KeywordFilter(Filter):
    """filter that excludes records containing specific keywords."""

    def __init__(self, exclude: list[str], case_sensitive: bool = False):
        self.exclude = exclude
        self.case_sensitive = case_sensitive

    def filter(self, record: LogRecord) -> bool:
        msg = record.message if self.case_sensitive else record.message.lower()
        keywords = self.exclude if self.case_sensitive else [k.lower() for k in self.exclude]
        return not any(kw in msg for kw in keywords)
