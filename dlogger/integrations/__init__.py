
import configparser


def uvicorn_config(dlogger, logger_names=None):
    """generate uvicorn log config using dlogger.
    
    args:
        dlogger: dlogger instance (usually root logger)
        logger_names: list of logger names to route through dlogger
    
    returns:
        dict for uvicorn log_config
    """
    if logger_names is None:
        logger_names = ["uvicorn", "uvicorn.access"]

    loggers = {}
    for name in logger_names:
        loggers[name] = {"handlers": ["dlogger"], "level": "DEBUG"}

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "dlogger": {
                "()": "dlogger.handlers.compat.CompatHandler",
                "dlogger": dlogger,
            }
        },
        "loggers": loggers,
    }


def load(config_path: str = "dlogger.conf"):
    """load dlogger config from file and generate uvicorn config.
    
    args:
        config_path: path to dlogger.conf
    
    returns:
        dict for uvicorn log_config
    
    raises:
        FileNotFoundError: if config file does not exist
    """
    import os
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    config = configparser.ConfigParser()
    config.read(config_path)

    logger_names = []
    if config.has_section("loggers"):
        logger_names = [k.strip() for k in config.get("loggers", "keys").split(",")]

    from dlogger import get_logger

    for name in logger_names:
        section = f"logger_{name}"
        if not config.has_section(section):
            continue

        lgr = get_logger(name)

        level = config.get(section, "level", fallback="DEBUG")
        log_file = config.get(section, "log_file", fallback=None)
        rotation = config.get(section, "rotation", fallback=None)
        retention = config.get(section, "retention", fallback=None)
        compression = config.getboolean(section, "compression", fallback=False)
        time_format = config.get(section, "time_format", fallback="%Y-%m-%d %H:%M:%S")

        lgr.configure(
            level=level,
            log_file=log_file,
            rotation=rotation,
            retention=retention,
            compression=compression,
            time_format=time_format,
        )

    root_logger = get_logger("root")
    return uvicorn_config(root_logger, logger_names=logger_names)
