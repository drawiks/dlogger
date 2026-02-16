

from datetime import datetime
from typing import Optional, Union
from termcolor import colored
import inspect

class dLogger:
    LEVELS = {
        "DEBUG": (10, "cyan"),
        "INFO": (20, "blue"),
        "WARNING": (30, "yellow"),
        "ERROR": (40, "red"),
        "CRITICAL": (50, "red", ["bold"])
    }

    def __init__(self):
        self._level = 10
        self._log_file = None
        self._show_path = True

    def configure(self, level: str = "DEBUG", log_file: Optional[str] = None, show_path: bool = True):
        self._level = self.LEVELS.get(level.upper(), (10,))[0]
        self._log_file = log_file
        self._show_path = show_path
        return self

    def _get_context(self):
        stack = inspect.stack()
        
        for frame_info in stack[2:]:
            if frame_info.filename != __file__:
                return f"{frame_info.filename}:{frame_info.lineno}"
        return "unknown"
    
    def _log(self, level_name: str, msg: str):
        level_val, color, *attrs = self.LEVELS[level_name] + (None,)
        
        if level_val < self._level:
            return
        
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context = f" | {self._get_context()}" if self._show_path else ""
        
        console_msg = (
            f"{colored(f'[{time_str}]', 'green')} "
            f"{colored(f'{level_name: <8}', color=color, attrs=attrs[0] if attrs[0] else [])} "
            f"{colored('|', 'white')} {msg}"
            f"{colored(context, 'dark_grey')}"
        )
        print(console_msg)
        
        if self._log_file:
            try:
                with open(self._log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{time_str}] {level_name: <8} | {msg}{context}\n")
            except Exception as e:
                print(f"❌ Error writing to log file: {e}")
    
    
    def debug(self, msg: str): self._log("DEBUG", msg)
    def info(self, msg: str): self._log("INFO", msg)
    def warning(self, msg: str): self._log("WARNING", msg)
    def error(self, msg: str): self._log("ERROR", msg)
    def critical(self, msg: str): self._log("CRITICAL", msg)

logger = dLogger()