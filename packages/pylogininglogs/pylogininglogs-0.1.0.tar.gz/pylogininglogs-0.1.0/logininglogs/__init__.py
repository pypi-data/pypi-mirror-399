# ==================== pyloggin/__init__.py (FIXED) ====================
"""
pyloggin - A custom logging library wrapper
"""

import logging
import sys
from typing import Optional

__version__ = "0.1.0"

def _setup_default_logger():
    """Set up a default logger configuration"""
    logger = logging.getLogger('pyloggin')
    
    # Only add handlers if they don't exist
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

# Create default logger instance
logger = _setup_default_logger()

# Export all logging levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# Custom logging functions that use our configured logger
def debug(msg, *args, **kwargs):
    """Log a debug message"""
    logger.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    """Log an info message"""
    logger.info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    """Log a warning message"""
    logger.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    """Log an error message"""
    logger.error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    """Log a critical message"""
    logger.critical(msg, *args, **kwargs)

def set_level(level):
    """Set the logging level"""
    logger.setLevel(level)

def get_logger(name: Optional[str] = None):
    """Get a logger instance with optional custom name"""
    if name:
        return logging.getLogger(name)
    return logger

def add_file_handler(filename: str, level=logging.INFO):
    """Add a file handler to the logger"""
    file_handler = logging.FileHandler(filename)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

# Re-export specific logging utilities (not functions that would override ours)
from logging import (
    Formatter, Handler, StreamHandler, FileHandler,
    LogRecord, Filter, LoggerAdapter,
    getLogger, getLoggerClass, setLoggerClass,
    basicConfig, shutdown, disable,
    NOTSET, FATAL
)

__all__ = [
    'debug', 'info', 'warning', 'error', 'critical',
    'set_level', 'get_logger', 'add_file_handler',
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'NOTSET', 'FATAL',
    'logger',
    'Formatter', 'Handler', 'StreamHandler', 'FileHandler',
    'LogRecord', 'Filter', 'LoggerAdapter',
    'getLogger', 'getLoggerClass', 'setLoggerClass',
    'basicConfig', 'shutdown', 'disable',
    '__version__'
]