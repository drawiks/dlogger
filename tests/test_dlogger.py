import os
import sys
import tempfile
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dlogger import (
    logger, dLogger, BoundLogger, get_logger, NullHandler,
    ConsoleHandler, FileHandler, LogRecord, Filter,
    Formatter, SimpleFormatter, ExceptionFormatter,
    LevelFilter, KeywordFilter, ModuleFilter,
)


class TestLevels:
    def test_unique_levels(self):
        levels = dLogger.LEVELS
        values = [v[0] for v in levels.values()]
        assert len(values) == len(set(values)), "levels must be unique"
        assert levels["TRACE"][0] < levels["DEBUG"][0]
        assert levels["DEBUG"][0] < levels["INFO"][0]
        assert levels["INFO"][0] < levels["SUCCESS"][0]
        assert levels["SUCCESS"][0] < levels["WARNING"][0]
        assert levels["WARNING"][0] < levels["ERROR"][0]
        assert levels["ERROR"][0] < levels["CRITICAL"][0]


class TestLogger:
    def test_root_logger_has_console_handler(self):
        assert len(logger.handlers) >= 1
        assert isinstance(logger.handlers[0], ConsoleHandler)

    def test_configure_returns_self(self):
        lgr = dLogger()
        result = lgr.configure(level="INFO")
        assert result is lgr

    def test_configure_replaces_file_handler(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = os.path.join(tmpdir, "test1.log")
            f2 = os.path.join(tmpdir, "test2.log")
            lgr = dLogger()
            lgr.configure(log_file=f1)
            assert len([h for h in lgr.handlers if isinstance(h, FileHandler)]) == 1
            lgr.configure(log_file=f2)
            file_handlers = [h for h in lgr.handlers if isinstance(h, FileHandler)]
            assert len(file_handlers) == 1
            assert file_handlers[0]._filename == f2

    def test_add_remove_handler(self):
        lgr = dLogger()
        initial_count = len(lgr.handlers)
        handler = ConsoleHandler(level="DEBUG")
        lgr.add_handler(handler)
        assert len(lgr.handlers) == initial_count + 1
        lgr.remove_handler(handler)
        assert len(lgr.handlers) == initial_count

    def test_repr(self):
        lgr = dLogger()
        assert "root" in repr(lgr)
        named = dLogger(name="test")
        assert "test" in repr(named)


class TestGetLogger:
    def test_default_returns_root(self):
        assert get_logger() is logger

    def test_named_logger(self):
        lgr = get_logger("test_module")
        assert isinstance(lgr, dLogger)
        assert lgr.name == "test_module"

    def test_same_name_returns_same_instance(self):
        lgr1 = get_logger("same_name")
        lgr2 = get_logger("same_name")
        assert lgr1 is lgr2

    def test_child_parent_relationship(self):
        parent = get_logger("parent")
        child = get_logger("parent.child")
        assert child._parent is parent


class TestBoundLogger:
    def test_bind_returns_bound_logger(self):
        bound = logger.bind(request_id="abc")
        assert isinstance(bound, BoundLogger)

    def test_bind_chaining(self):
        bound = logger.bind(a=1).bind(b=2)
        assert bound._extra == {"a": 1, "b": 2}

    def test_bound_logger_repr(self):
        bound = logger.bind(x=1)
        assert "BoundLogger" in repr(bound)


class TestContextualize:
    def test_contextualize_basic(self):
        import contextvars
        from dlogger.logger import _context_var

        with dLogger.contextualize(request_id="test-123"):
            ctx = _context_var.get()
            assert ctx.get("request_id") == "test-123"

        ctx = _context_var.get()
        assert "request_id" not in ctx

    def test_contextualize_nested(self):
        from dlogger.logger import _context_var

        with dLogger.contextualize(a=1):
            with dLogger.contextualize(b=2):
                ctx = _context_var.get()
                assert ctx.get("a") == 1
                assert ctx.get("b") == 2
            ctx = _context_var.get()
            assert ctx.get("a") == 1
            assert "b" not in ctx


class TestFilters:
    def test_level_filter(self):
        f = LevelFilter("WARNING")
        record = LogRecord("DEBUG", 10, "msg", "ctx", None)
        assert not f.filter(record)
        record2 = LogRecord("ERROR", 40, "msg", "ctx", None)
        assert f.filter(record2)

    def test_keyword_filter(self):
        f = KeywordFilter(exclude=["password", "secret"])
        record = LogRecord("INFO", 20, "my password is 123", "ctx", None)
        assert not f.filter(record)
        record2 = LogRecord("INFO", 20, "hello world", "ctx", None)
        assert f.filter(record2)

    def test_keyword_filter_case_insensitive(self):
        f = KeywordFilter(exclude=["PASSWORD"])
        record = LogRecord("INFO", 20, "my Password is 123", "ctx", None)
        assert not f.filter(record)

    def test_module_filter(self):
        f = ModuleFilter(modules=["database:", "api:"])
        record = LogRecord("INFO", 20, "msg", "database:connect:", None)
        assert f.filter(record)
        record2 = LogRecord("INFO", 20, "msg", "other:func:", None)
        assert not f.filter(record2)


class TestFormatters:
    def test_simple_formatter(self):
        from datetime import datetime
        f = SimpleFormatter()
        record = LogRecord("INFO", 20, "hello", "module:func:", datetime(2026, 1, 1, 12, 0, 0))
        result = f.format(record)
        assert "INFO" in result
        assert "hello" in result

    def test_exception_formatter_format_exception(self):
        try:
            raise ValueError("test error")
        except ValueError as e:
            tb = ExceptionFormatter.format_exception(e)
            assert "ValueError" in tb
            assert "test error" in tb

    def test_exception_formatter_get_current_exception(self):
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            exc = ExceptionFormatter.get_current_exception()
            assert exc is not None
            assert isinstance(exc, RuntimeError)

        exc = ExceptionFormatter.get_current_exception()
        assert exc is None


class TestNullHandler:
    def test_null_handler_emit(self):
        handler = NullHandler()
        record = LogRecord("INFO", 20, "msg", "ctx", None)
        handler.emit(record)


class TestFileHandler:
    def test_file_handler_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.log")
            handler = FileHandler(filepath)
            record = LogRecord("INFO", 20, "test message", "ctx", datetime.now())
            handler.emit(record)
            handler.close()
            assert os.path.exists(filepath)
            with open(filepath) as f:
                content = f.read()
            assert "test message" in content

    def test_file_handler_serialize(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.json")
            handler = FileHandler(filepath, serialize=True)
            record = LogRecord("INFO", 20, "test message", "ctx", datetime.now(), extra={"key": "value"})
            handler.emit(record)
            handler.close()
            with open(filepath) as f:
                line = f.readline()
            data = json.loads(line)
            assert data["message"] == "test message"
            assert data["extra"]["key"] == "value"

    def test_file_handler_rotation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.log")
            handler = FileHandler(filepath, rotation="1KB")
            for i in range(200):
                record = LogRecord("INFO", 20, f"line {i}" * 10, "ctx", datetime.now())
                handler.emit(record)
            handler.close()
            files = os.listdir(tmpdir)
            rotated = [f for f in files if f != "test.log"]
            assert len(rotated) >= 1, f"expected rotated files, got {files}"


class TestLazyFormatting:
    def test_lazy_not_called_when_disabled(self):
        called = []
        def msg_factory():
            called.append(True)
            return "hello"

        lgr = dLogger()
        lgr._level = 50
        lgr._log("DEBUG", msg_factory)
        assert not called

    def test_lazy_called_when_enabled(self):
        called = []
        def msg_factory():
            called.append(True)
            return "hello"

        lgr = dLogger()
        lgr._level = 10
        lgr._log("DEBUG", msg_factory)
        assert called
