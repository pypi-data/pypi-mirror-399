import pylogininglogs
import logging

def test_basic_logging():
    assert callable(pylogininglogs.info)
    assert callable(pylogininglogs.debug)
    assert callable(pylogininglogs.warning)
    assert callable(pylogininglogs.error)
    assert callable(pylogininglogs.critical)

def test_log_levels():
    # Test that log levels are defined
    assert pylogininglogs.DEBUG == logging.DEBUG
    assert pylogininglogs.INFO == logging.INFO
    assert pylogininglogs.WARNING == logging.WARNING
    assert pylogininglogs.ERROR == logging.ERROR
    assert pylogininglogs.CRITICAL == logging.CRITICAL

def test_get_logger():
    # Test getting a logger
    logger = pylogininglogs.get_logger('test')
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'test'

def test_set_level():
    # Test setting log level
    pylogininglogs.set_level(pylogininglogs.DEBUG)
    assert pylogininglogs.logger.level == logging.DEBUG