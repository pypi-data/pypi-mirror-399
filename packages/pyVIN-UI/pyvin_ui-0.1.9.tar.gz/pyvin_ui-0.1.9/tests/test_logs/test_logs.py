"""Tests for logging setup"""

import logging
from src.logs.logs import setup_logger


class TestSetupLogger:
    """Tests for setup_logger function"""

    def test_creates_logger(self):
        """Test that logger is created"""
        logger = setup_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "pyVIN"

    def test_logger_level_is_debug(self):
        """Test that logger level is set to DEBUG"""
        logger = setup_logger()
        assert logger.level == logging.DEBUG

    def test_has_file_handler(self):
        """Test that file handler is added"""
        logger = setup_logger()
        file_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(file_handlers) > 0

    def test_has_console_handler(self):
        """Test that console handler is added"""
        logger = setup_logger()
        console_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.StreamHandler)
            and not isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(console_handlers) > 0

    def test_custom_file_handler_level(self):
        """Test custom file handler level"""
        # Clear existing handlers to avoid interference from previous tests
        logger = logging.getLogger("pyVIN")
        logger.handlers.clear()

        logger = setup_logger(fh_lev=logging.INFO)
        file_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(file_handlers) > 0
        assert file_handlers[-1].level == logging.INFO

    def test_custom_console_handler_level(self):
        """Test custom console handler level"""
        # Clear existing handlers to avoid interference from previous tests
        logger = logging.getLogger("pyVIN")
        logger.handlers.clear()

        logger = setup_logger(ch_lev=logging.WARNING)
        console_handlers = [
            h
            for h in logger.handlers
            if isinstance(h, logging.StreamHandler)
            and not isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(console_handlers) > 0
        assert console_handlers[-1].level == logging.WARNING

    def test_handlers_have_formatter(self):
        """Test that handlers have formatters"""
        logger = setup_logger()
        for handler in logger.handlers:
            assert handler.formatter is not None

    def test_returns_logger_instance(self):
        """Test that function returns a logger instance"""
        result = setup_logger()
        assert isinstance(result, logging.Logger)
