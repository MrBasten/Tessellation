"""Кастомный логгер для модуля.
"""
import logging

class CustomFormatter(logging.Formatter):
    """Кастомный цветной форматер для логера.
    """
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: format,
        logging.INFO: format,
        logging.WARNING: format,
        logging.ERROR: format,
        logging.CRITICAL: format
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        
        return formatter.format(record)

def get_logger(name: str, log_level: str = 'INFO') -> logging.Logger:
    """Генератор логера для скрипта в модуле.

    Args:
        name (str): Имя скрипта (получется подстановкой в качестве аргумента __name__).
        log_level (str, optional): Уровень логирования (стандартный для logging). Defaults to 'INFO'.

    Returns:
        logging.Logger: Готовый логгер.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    stream_heandler = logging.StreamHandler()
    stream_heandler.setFormatter(CustomFormatter())
    logger.addHandler(stream_heandler)
    
    return logger