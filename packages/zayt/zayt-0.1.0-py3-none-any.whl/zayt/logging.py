import logging
import logging.config
import sys

import structlog

from zayt.conf.settings import Settings


def setup(settings: Settings):
    root_level = settings.logging.get("root", "WARN").upper()
    log_format = settings.logging.get(
        "format", "console" if sys.stderr.isatty() else "logfmt"
    )

    match log_format:
        case "console":
            renderer = structlog.dev.ConsoleRenderer(colors=True)
        case "json":
            renderer = structlog.processors.JSONRenderer()
        case "logfmt":
            renderer = structlog.processors.LogfmtRenderer(
                key_order=["timestamp", "level", "event"]
            )
        case "keyvalue":
            renderer = structlog.processors.KeyValueRenderer(
                key_order=["timestamp", "level", "event"]
            )
        case _:
            raise ValueError("Invalid log format")

    timestamper = structlog.processors.TimeStamper(
        fmt="%Y-%m-%d %H:%M:%S" if log_format == "console" else "iso"
    )

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        timestamper,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    extra_loggers = {
        "sqlalchemy.engine.Engine": {
            "level": root_level,
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn": {
            "handlers": [],
            "propagate": True,
        },
        "_granian": {
            "handlers": [],
            "propagate": True,
        },
        "granian.access": {
            "handlers": [],
            "propagate": True,
        },
    }

    loggers = {
        module: {"level": level.upper(), "handlers": ["console"], "propagate": False}
        for module, level in settings.logging.get("level", {}).items()
    }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        renderer,
                    ],
                    "foreign_pre_chain": shared_processors,
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": root_level,
            },
            "loggers": extra_loggers | loggers,
        }
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# class DevFormatter(logging.Formatter):
#     def __init__(self, *args, **kwargs):
#         super().__init__(datefmt="%Y-%m-%d %H:%M:%S")
#
#     def format(self, record: logging.LogRecord) -> str:
#         message = record.getMessage()
#
#         if ctx := getattr(record, "ctx", None):
#             values = {}
#             for key, value in ctx.items():
#                 if isinstance(value, (int, float, bool, str)):
#                     values[key] = value
#                 elif isinstance(value, (date, time, datetime)):
#                     values[key] = value.isoformat()
#                 elif isinstance(value, Decimal):
#                     values[key] = str(value)
#                 else:
#                     values[key] = json.dumps(str(value))
#
#             context = " ".join(
#                 f"{name}={value}"
#                 for name, value in values.items()
#             )
#         else:
#             context = None
#
#         record.asctime = self.formatTime(record, self.datefmt)
#
#         if context:
#             s = f"{record.asctime} {record.levelname:8} {message:45} [{record.name}] {context}"
#         else:
#             s = f"{record.asctime} {record.levelname:8} {message}"
#
#         if record.exc_info:
#             # Cache the traceback text to avoid converting it multiple times
#             # (it's constant anyway)
#             if not record.exc_text:
#                 record.exc_text = self.formatException(record.exc_info)
#         if record.exc_text:
#             if s[-1:] != "\n":
#                 s = s + "\n"
#             s = s + record.exc_text
#         if record.stack_info:
#             if s[-1:] != "\n":
#                 s = s + "\n"
#             s = s + self.formatStack(record.stack_info)
#
#         return s
#
#
# class JsonFormatter(logging.Formatter):
#     def format(self, record: logging.LogRecord) -> str:
#         values = {
#             "time": datetime.fromtimestamp(record.created).isoformat(),
#             "level": record.levelname,
#             "event": record.getMessage(),
#             "source": record.name,
#         }
#
#         if ctx := getattr(record, "ctx", None):
#             for key, value in ctx.items():
#                 if isinstance(value, (int, float, bool, str)):
#                     values[key] = value
#                 elif isinstance(value, (date, time, datetime)):
#                     values[key] = value.isoformat()
#                 else:
#                     values[key] = str(value)
#
#         if record.exc_info:
#             # Cache the traceback text to avoid converting it multiple times
#             # (it's constant anyway)
#             if not record.exc_text:
#                 record.exc_text = self.formatException(record.exc_info)
#
#         if record.exc_text:
#             values["exception"] = record.exc_text
#
#         if record.stack_info:
#             values["stack"] = self.formatStack(record.stack_info)
#
#         return json.dumps(values)
