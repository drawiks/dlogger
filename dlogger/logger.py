
from datetime import datetime, timedelta
from typing import Optional
from dcolor import color
import inspect
import gzip
import os

class dLogger:
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
        self._log_file = None
        self._show_path = True
        self._rotation_size = None
        self._rotation_time = None
        self._retention_days = None
        self._compression = False
        self._current_file_creation = None

    def configure(
        self,
        level: str = "DEBUG",
        log_file: Optional[str] = None,
        show_path: bool = True,
        rotation: Optional[str] = None,
        retention: Optional[str] = None,
        compression: bool = False
    ):
        self._level = self.LEVELS.get(level.upper(), (10,))[0]
        self._log_file = log_file
        self._show_path = show_path
        self._compression = compression
        
        if rotation:
            self._parse_rotation(rotation)
        
        if retention:
            self._retention_days = self._parse_retention(retention)
        
        if log_file:
            self._ensure_log_directory()
            self._cleanup_old_logs()
        return self

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
        if self._log_file:
            log_dir = os.path.dirname(self._log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

    def _get_context(self) -> str:
        stack = inspect.stack()

        for frame_info in stack[2:]:
            if frame_info.filename != __file__:
                module = frame_info.frame.f_globals.get("__name__", "unknown")
                function = frame_info.function
                return f"{module}:{function}:"
        return "unknown"

    def _should_rotate(self) -> bool:
        if not self._log_file or not os.path.exists(self._log_file):
            return False
        
        if self._rotation_size:
            file_size = os.path.getsize(self._log_file)
            if file_size >= self._rotation_size:
                return True
        
        if self._rotation_time:
            if self._current_file_creation is None:
                self._current_file_creation = datetime.now()
            
            time_diff = (datetime.now() - self._current_file_creation).total_seconds()
            if time_diff >= self._rotation_time:
                return True
        return False

    def _rotate_log(self):
        if not self._log_file or not os.path.exists(self._log_file):
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = self._log_file
        rotated_name = f"{base_name}.{timestamp}"
        
        try:
            os.rename(self._log_file, rotated_name)

            if self._compression:
                self._compress_file(rotated_name)
            
            self._current_file_creation = datetime.now()
            self._cleanup_old_logs()
        except Exception as e:
            print(f"⚠️ Ошибка при ротации лога: {e}")

    def _compress_file(self, filepath: str):
        try:
            with open(filepath, 'rb') as f_in:
                with gzip.open(f"{filepath}.gz", 'wb') as f_out:
                    f_out.writelines(f_in)
            os.remove(filepath)
        except Exception as e:
            print(f"⚠️ Ошибка при сжатии файла: {e}")

    def _cleanup_old_logs(self):
        if not self._log_file or not self._retention_days:
            return
        
        try:
            log_dir = os.path.dirname(self._log_file) or "."
            base_name = os.path.basename(self._log_file)
            
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
            print(f"⚠️ Ошибка при очистке старых логов: {e}")

    def _log(self, level_name: str, msg: str):
        level_val, clr = self.LEVELS[level_name]
        if level_val < self._level:
            return

        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context = f"{self._get_context()}" if self._show_path else ""

        is_critical = level_name == "CRITICAL"

        console_msg = (
            f"{color(time_str, '#4caf50')} "
            f"{color('|', 'white')} {color(f'{level_name: <8}', clr, 'bold', *(('underline',) if is_critical else ()))} "
            f"{color('|', 'white')} {color(context, '#00bcd4')} "
            f"{color('-', 'white')} {msg}"
        )
        print(console_msg)

        if self._log_file:
            if self._should_rotate():
                self._rotate_log()
            try:
                with open(self._log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{time_str}] | {level_name: <8} | {context} {msg}\n")
            except Exception as e:
                print(f"{color('⚠️ ошибка записи в лог-файл:', '#ff9800')} {e}")

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

logger = dLogger()