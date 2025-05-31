import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from src.shared.config import settings


def setup_logger(name: str, console: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    class SafeFormatter(logging.Formatter):
        def format(self, record):
            if not hasattr(record, 'extra_data'):
                record.extra_data = ""  # Значение по умолчанию
            return super().format(record)

    formatter = SafeFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message) - s%(extra_data)s'
    )

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    os.makedirs(settings.log_dir, exist_ok=True)

    file_handler = TimedRotatingFileHandler(
        settings.log_file,
        when="midnight",
        interval=1,
        backupCount=7
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
