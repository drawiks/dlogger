
from typing import Optional
from datetime import datetime
from termcolor import colored

import sys

class ConsoleHandler:
    COLORS = {
        "CRITICAL": "red",
        "ERROR": "red",
        "WARNING": "yellow",
        "INFO": "blue",
        "DEBUG": "cyan"
    }
    
    def emit(self, level, msg):
        time_str = colored(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]", "green")
        level_str = colored(f"{level: <8}", color=self.COLORS.get(level, "white"), attrs=["bold"])
        print(f"{time_str} {level_str} {msg}")

class FileHandler:
    def __init__(self, filename: str):
        self.filename = filename

    def emit(self, level, msg):
        try:
            with open(self.filename, "a", encoding="utf-8") as file:
                file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {level: <8} {msg}\n")
        except Exception as e:
            print(colored(f"❌ Failed to write log: {e}", "red"))

class Logger:
    LEVELS = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20, "DEBUG": 10}
    
    def __init__(self):
        self.level = self.LEVELS["DEBUG"]
        self.handlers = [ConsoleHandler()]
    
    def setup(self, log_path: Optional[str] = None, level: str = "DEBUG"):
        self.level = self.LEVELS.get(level, 10)
        if log_path:
            if not any(isinstance(h, FileHandler) for h in self.handlers):
                self.handlers.append(FileHandler(log_path))
        return self

    def log(self, level, msg):
        if self.LEVELS.get(level, 0) >= self.level:
            for handler in self.handlers:
                handler.emit(level, msg)
    
    def critical(self, msg): self.log("CRITICAL", msg)
    def error(self, msg): self.log("ERROR", msg)
    def warning(self, msg): self.log("WARNING", msg)
    def info(self, msg): self.log("INFO", msg)
    def debug(self, msg): self.log("DEBUG", msg)

logger = Logger()