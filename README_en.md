<div align="center">
    <h1>📝 dlogger</h1>
    <a href="https://pypi.org/project/dlogger-drawiks/">
        <img alt="PyPI version" src="https://img.shields.io/pypi/v/dlogger-drawiks?color=blue">
    </a>
    <img height="20" alt="Python 3.7+" src="https://img.shields.io/badge/python-3.7+-blue">
    <img height="20" alt="License MIT" src="https://img.shields.io/badge/license-MIT-green">
    <img height="20" alt="Status" src="https://img.shields.io/badge/status-stable-brightgreen">
    <p><strong>dlogger</strong> — simple logger for personal projects</p>
    <blockquote>(─‿‿─)</blockquote>
</div>

---

```
     ____    __
    / __ \  / /   ____   ____ _ ____ _ ___   _____
   / / / / / /   / __ \ / __ `// __ `// _ \ / ___/
  / /_/ / / /___/ /_/ // /_/ // /_/ //  __// /
 /_____/ /_____/\____/ \__, / \__, / \___//_/
                      /____/ /____/
```

## **📦 installation**

```bash
pip install dlogger-drawiks
```

---

## **📑 quick start**

```python
from dlogger import logger

logger.info("hello, world!")
logger.error("something went wrong")
```

with configuration:
```python
from dlogger import logger

logger.configure(
    level="INFO",
    log_file="app.log",
    rotation="10MB",
    retention="7 days",
    compression=True
)

logger.debug("this won't be shown")
logger.info("but this will")
```

---

## **🧩 features**

- 🎨 **TrueColor output** — HEX/RGB support powered by [dcolor](https://github.com/drawiks/dcolor)
- 🚀 **high performance** — use of buffers and call context caching
- 🧵 **thread safety** — stability in multithreaded applications thanks to locks
- 💾 **write guarantee** — automatic buffer reset upon correct program termination
- 📁 **smart rotation** — by size (`10MB`, `1GB`) or time (`1 day`, `12 hours`)
- 🗑️ **auto cleanup** — scheduled deletion of old files (`retention="30 days"`)
- 📦 **compression** — automatic archiving of old logs to `.gz`
- 🛠️ **minimal dependencies** — only [dcolor](https://github.com/drawiks/dcolor)
- ✅ **reliability** — protection from memory leaks, data loss and deadlocks
---

## **📖 usage**

### log levels

```python
logger.configure(level="INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### size-based rotation

```python
logger.configure(
    log_file="app.log",
    rotation="10MB"  # or "500KB", "1GB"
)
```

once the file reaches 10MB → `app.log.20260216_143022`

### time-based rotation

```python
logger.configure(
    log_file="app.log",
    rotation="1 day"  # or "12 hours", "1 week"
)
```

### log retention

```python
logger.configure(
    log_file="app.log",
    retention="7 days"  # or "2 weeks", "1 month"
)
```

logs older than 7 days will be deleted automatically

### compression

```python
logger.configure(
    log_file="app.log",
    rotation="10MB",
    compression=True  # old logs → .gz
)
```

### full configuration

```python
logger.configure(
    level="INFO",              # minimum log level
    log_file="logs/app.log",   # path to log file
    show_path=True,            # show module:function:
    rotation="10MB",           # size-based rotation
    retention="7 days",        # keep logs for 7 days
    compression=True           # compress old logs
    time_format="%H:%M:%S"     # time format - 14:30:22
)
```

---

## **💡 examples**

### simple logging

```python
from dlogger import logger

logger.info("server started on port 8000")
logger.warning("memory usage at 80%")
logger.error("failed to connect to database")
```

### with file

```python
from dlogger import logger

logger.configure(
    level="DEBUG",
    log_file="app.log"
)

logger.debug("starting request processing")
logger.info("request processed successfully")
```

### for production

```python
from dlogger import logger

logger.configure(
    level="INFO",
    log_file="logs/production.log",
    rotation="50MB",
    retention="30 days",
    compression=True
    time_format="%Y-%m-%d %H:%M:%S"
)

logger.info("application started")
logger.error("critical error in payments module")
```

---

## **📝 log format**

**console:**
```
2026-02-17 14:09:13 | INFO     | src.bot:run: - init
```

**file:**
```
2026-02-17 14:09:13 | INFO     | src.main:run: init
2026-02-17 14:09:13 | ERROR    | src.main:run: error
```

---

## **📜 license**
[MIT](https://github.com/drawiks/dlogger/blob/main/LICENSE)
