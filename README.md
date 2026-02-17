<div align="center">
    <h1>📝 dlogger</h1>
    <img height="20" alt="Python 3.7+" src="https://img.shields.io/badge/python-3.7+-blue">
    <img height="20" alt="License MIT" src="https://img.shields.io/badge/license-MIT-green">
    <img height="20" alt="Status" src="https://img.shields.io/badge/status-stable-brightgreen">
    <p><strong>dlogger</strong> — простой логгер для личных проектов</p>
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

## **📦 установка**

```bash
pip install dlogger-drawiks
```

---

## **📑 быстрый старт**

```python
from dlogger import logger

logger.info("привет, мир!")
logger.error("что-то пошло не так")
```

с настройкой:
```python
from dlogger import logger

logger.configure(
    level="INFO",
    log_file="app.log",
    rotation="10MB",
    retention="7 days",
    compression=True
)

logger.debug("это не будет показано")
logger.info("а это будет")
```

---

## **🧩 возможности**

- 🎨 **цветной вывод** — разные цвета для разных уровней
- 📁 **ротация по размеру** — `rotation="10MB"`
- ⏰ **ротация по времени** — `rotation="1 day"`
- 🗑️ **автоочистка** — `retention="7 days"`
- 📦 **сжатие** — `compression=True`
- 🚫 **без зависимостей** — только stdlib

---

## **📖 использование**

### уровни логирования

```python
logger.configure(level="INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### ротация по размеру

```python
logger.configure(
    log_file="app.log",
    rotation="10MB"  # или "500KB", "1GB"
)
```

когда файл достигнет 10MB → `app.log.20260216_143022`

### ротация по времени

```python
logger.configure(
    log_file="app.log",
    rotation="1 day"  # или "12 hours", "1 week"
)
```

### хранение логов

```python
logger.configure(
    log_file="app.log",
    retention="7 days"  # или "2 weeks", "5 hours"
)
```

логи старше 7 дней будут удалены автоматически

### сжатие старых логов

```python
logger.configure(
    log_file="app.log",
    rotation="10MB",
    compression=True  # старые логи → .gz
)
```

### полная настройка

```python
logger.configure(
    level="INFO",              # минимальный уровень
    log_file="logs/app.log",   # путь к файлу
    show_path=True,            # показывать файл:строку
    rotation="10MB",           # ротация по размеру
    retention="7 days",        # хранить логи 7 дней
    compression=True           # сжимать старые логи
)
```

---

## **💡 примеры**

### простое логирование

```python
from dlogger import logger

logger.info("сервер запущен на порту 8000")
logger.warning("память заполнена на 80%")
logger.error("не удалось подключиться к базе данных")
```

### с файлом

```python
from dlogger import logger

logger.configure(
    level="DEBUG",
    log_file="app.log"
)

logger.debug("начинаем обработку запроса")
logger.info("запрос обработан успешно")
```

### для продакшена

```python
from dlogger import logger

logger.configure(
    level="INFO",
    log_file="logs/production.log",
    rotation="50MB",
    retention="30 days",
    compression=True
)

logger.info("приложение запущено")
logger.error("критическая ошибка в модуле payments")
```

## **📝 формат логов**

**в консоли:**
```
[2024-02-16 14:30:22] INFO     | приложение запущено | main.py:15
```

**в файле:**
```
[2024-02-16 14:30:22] INFO     | приложение запущено | main.py:15
[2024-02-16 14:30:23] ERROR    | ошибка подключения | database.py:42
```

---

## **📜 лицензия**
[MIT](LICENSE)
