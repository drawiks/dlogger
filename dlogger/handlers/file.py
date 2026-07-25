
import json
from typing import Optional, Literal
from datetime import datetime, timedelta
import threading
import atexit
import gzip
import os
import queue

from .base import Handler, LogRecord, Formatter

class FileHandler(Handler):
    """handler that writes log records to a file with rotation and compression support."""

    def __init__(
        self,
        filename: str,
        level: str = "TRACE",
        formatter: Optional[Formatter] = None,
        rotation: Optional[str] = None,
        retention: Optional[str] = None,
        compression: bool = False,
        serialize: bool = False,
        enqueue: bool = False,
        buffer_size: int = 100,
        time_format: str = "%Y-%m-%d %H:%M:%S",
    ):
        super().__init__(level=level, formatter=formatter)
        self._filename = filename
        self._rotation_size = None
        self._rotation_time = None
        self._retention_days = None
        self._compression = compression
        self._serialize = serialize
        self._enqueue = enqueue
        self._time_format = time_format

        self._lock = threading.Lock()
        self._buffer = []
        self._buffer_size = buffer_size
        self._log_count = 0
        self._check_rotation_every = 100

        self._ensure_log_directory()

        if rotation:
            self._parse_rotation(rotation)

        if retention:
            self._retention_days = self._parse_retention(retention)

        if self._retention_days:
            self._cleanup_old_logs()

        if self._enqueue:
            self._queue = queue.Queue()
            self._worker = threading.Thread(target=self._enqueue_worker, daemon=True)
            self._worker.start()

        atexit.register(self.close)

    def _enqueue_worker(self):
        while True:
            try:
                record = self._queue.get(timeout=0.1)
                if record is None:
                    break
                self._write_record(record)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Enqueue worker error: {e}")

    def _parse_rotation(self, rotation: str):
        rotation = rotation.strip().lower()

        if "kb" in rotation or "mb" in rotation or "gb" in rotation:
            value = float(rotation.replace("kb", "").replace("mb", "").replace("gb", "").strip())

            if "kb" in rotation:
                self._rotation_size = int(value * 1024)
            elif "mb" in rotation:
                self._rotation_size = int(value * 1024 * 1024)
            elif "gb" in rotation:
                self._rotation_size = int(value * 1024 * 1024 * 1024)

        elif "hour" in rotation or "day" in rotation or "week" in rotation:
            parts = rotation.split()
            value = int(parts[0])
            unit = parts[1] if len(parts) > 1 else rotation.replace(str(value), "").strip()

            if "hour" in unit:
                self._rotation_time = value * 3600
            elif "day" in unit:
                self._rotation_time = value * 86400
            elif "week" in unit:
                self._rotation_time = value * 604800

    def _parse_retention(self, retention: str) -> int:
        retention = retention.strip().lower()
        parts = retention.split()
        value = int(parts[0])
        unit = parts[1] if len(parts) > 1 else retention.replace(str(value), "").strip()

        if "day" in unit:
            return value
        elif "week" in unit:
            return value * 7
        elif "month" in unit:
            return value * 30
        return value

    def _ensure_log_directory(self):
        log_dir = os.path.dirname(self._filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    def _should_rotate(self) -> bool:
        if not os.path.exists(self._filename):
            return False

        if self._rotation_size:
            file_size = os.path.getsize(self._filename)
            if file_size >= self._rotation_size:
                return True

        if self._rotation_time:
            creation_time = datetime.fromtimestamp(os.path.getctime(self._filename))
            time_diff = (datetime.now() - creation_time).total_seconds()
            if time_diff >= self._rotation_time:
                return True
        return False

    def _rotate_log(self):
        if not os.path.exists(self._filename):
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_name = f"{self._filename}.{timestamp}"

        try:
            os.rename(self._filename, rotated_name)

            if self._compression:
                self._compress_file(rotated_name)

            if self._retention_days:
                self._cleanup_old_logs()
        except Exception as e:
            print(f"⚠️ Error during log rotation: {e}")

    def _compress_file(self, filepath: str):
        try:
            with open(filepath, 'rb') as f_in:
                with gzip.open(f"{filepath}.gz", 'wb') as f_out:
                    for line in f_in:
                        f_out.write(line)
            os.remove(filepath)
        except Exception as e:
            print(f"⚠️ Error during file compression: {e}")

    def _cleanup_old_logs(self):
        if not self._retention_days:
            return

        try:
            log_dir = os.path.dirname(self._filename) or "."
            base_name = os.path.basename(self._filename)

            cutoff_date = datetime.now() - timedelta(days=self._retention_days)

            for filename in os.listdir(log_dir):
                if not filename.startswith(base_name):
                    continue

                if filename == base_name:
                    continue

                filepath = os.path.join(log_dir, filename)

                if os.path.isfile(filepath):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_mtime < cutoff_date:
                        os.remove(filepath)
        except Exception as e:
            print(f"⚠️ Error during log cleanup: {e}")

    def _flush_buffer(self):
        if not self._buffer:
            return

        buffer_to_write = self._buffer
        self._buffer = []

        try:
            if not os.path.exists(self._filename):
                self._ensure_log_directory()

            with open(self._filename, "a", encoding="utf-8") as f:
                f.writelines(buffer_to_write)
        except Exception as e:
            print(f"⚠️ Buffer write error: {e}")
            self._buffer = buffer_to_write + self._buffer

    def _format_record(self, record: LogRecord) -> str:
        time_str = record.timestamp.strftime(self._time_format)
        context = record.context

        if self._serialize:
            log_entry = {
                "time": time_str,
                "level": record.level,
                "level_value": record.level_value,
                "context": context,
                "message": record.message,
                "pid": record.pid,
            }
            if record.extra:
                log_entry["extra"] = record.extra
            return json.dumps(log_entry, ensure_ascii=False) + "\n"
        else:
            return f"[{time_str}] | {record.level: <8} | {context} {record.message}\n"

    def _write_record(self, record: LogRecord):
        log_line = self._format_record(record)

        with self._lock:
            self._buffer.append(log_line)

            if len(self._buffer) >= self._buffer_size:
                self._flush_buffer()

            self._log_count += 1

            if self._log_count % self._check_rotation_every == 0:
                if self._should_rotate():
                    self._flush_buffer()
                    self._rotate_log()

    def emit(self, record: LogRecord):
        """emit a log record to file."""
        if not self._should_log(record):
            return

        if self._enqueue:
            self._queue.put(record)
        else:
            self._write_record(record)

    def close(self):
        """flush buffer and close the handler."""
        if self._enqueue:
            self._queue.put(None)
            self._worker.join(timeout=5)

        with self._lock:
            self._flush_buffer()
