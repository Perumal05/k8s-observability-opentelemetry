import logging
import sys
from pythonjsonlogger import json as json_logger
from app.config import settings


class CustomJsonFormatter(json_logger.JsonFormatter):
    """Custom JSON log formatter adding service metadata and timestamp."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["service"] = settings.APP_NAME
        log_record["environment"] = settings.APP_ENV
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        
        # Ensure timestamp is ISO-8601 formatted
        if not log_record.get("timestamp"):
            import datetime
            log_record["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()


def setup_logging():
    """Configure structured JSON logging to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Silence overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Retrieve logger instance with given name."""
    return logging.getLogger(name)
