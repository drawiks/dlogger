<div align="center">
    <h1>📝 dlogger</h1>
    <a href="https://pypi.org/project/dlogger-drawiks/">
        <img alt="PyPI version" src="https://img.shields.io/pypi/v/dlogger-drawiks?color=blue">
    </a>
    <img height="20" alt="Python 3.7+" src="https://img.shields.io/badge/python-3.7+-blue">
    <img height="20" alt="License MIT" src="https://img.shields.io/badge/license-MIT-green">
    <img height="20" alt="Status" src="https://img.shields.io/badge/status-stable-brightgreen">
    <p><strong>dlogger</strong> - простой логгер для личных проектов</p>
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

- 🎨 **TrueColor вывод** - поддержка HEX/RGB благодаря [dcolor](https://github.com/drawiks/dcolor)
- 🚀 **высокая производительность** - использование буфера и кэширование контекста вызовов
- 🧵 **потокобезопасность** - стабильность в многопоточных приложениях благодаря блокировкам
- 💾 **гарантия записи** - автоматический сброс буфера при корректном завершении программы
- 📁 **умная ротация** - по размеру (`10MB`, `1GB`) или времени (`1 day`, `12 hours`)
- 🗑️ **автоочистка** - удаление старых файлов по расписанию (`retention="30 days"`)
- 📦 **сжатие** - автоматическое архивирование старых логов в `.gz`
- 🛠️ **минимум зависимостей** - только [dcolor](https://github.com/drawiks/dcolor)
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
    time_format="%H:%M:%S"     # формат времени - 14:30:22
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
    time_format="%Y-%m-%d %H:%M:%S"
)

logger.info("приложение запущено")
logger.error("критическая ошибка в модуле payments")
```

## **📝 формат логов**

**в консоли:**
```
2026-02-17 14:09:13 | INFO     | src.bot:run: - init
```

**в файле:**
```
2026-02-17 14:09:13 | INFO     | src.main:run: init
2026-02-17 14:09:13 | ERROR    | src.main:run: error
```

---

## **📜 лицензия**
[MIT](https://github.com/drawiks/dlogger/blob/main/LICENSE)
