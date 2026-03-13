
def uvicorn_config(dlogger):
    """generate uvicorn log config using dlogger."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "dlogger": {
                "()": "dlogger.handlers.compat.CompatHandler",
                "dlogger": dlogger,
            }
        },
        "loggers": {
            "uvicorn": {"handlers": ["dlogger"], "level": "DEBUG"},
            "uvicorn.access": {"handlers": ["dlogger"], "level": "INFO"},
        },
    }
