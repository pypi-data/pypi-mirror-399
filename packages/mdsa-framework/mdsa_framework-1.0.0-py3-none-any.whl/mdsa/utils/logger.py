"""
Structured Logging Module

Provides consistent logging configuration across the MDSA framework.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for better readability.

    Colors are disabled on Windows unless colorama is installed.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }

    def __init__(self, fmt=None, datefmt=None, use_colors=True):
        """
        Initialize colored formatter.

        Args:
            fmt: Log format string
            datefmt: Date format string
            use_colors: Whether to use colors (auto-detected for Windows)
        """
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors and self._colors_supported()

    def _colors_supported(self) -> bool:
        """Check if terminal supports colors."""
        # Check if running in a terminal
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False

        # Windows support
        if sys.platform == 'win32':
            try:
                import colorama
                colorama.init()
                return True
            except ImportError:
                return False

        # Unix/Linux/macOS
        return True

    def format(self, record):
        """Format log record with colors."""
        if self.use_colors:
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = (
                    f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
                )

        return super().format(record)


def setup_logger(
    name: str = 'mdsa',
    level: str = 'INFO',
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    Set up structured logger for MDSA framework.

    Args:
        name: Logger name (default: 'mdsa')
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Optional log file path
        use_colors: Use colored output in console

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> from mdsa.utils import setup_logger
        >>> logger = setup_logger('mdsa', level='DEBUG')
        >>> logger.info("Framework initialized")
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Console format
    console_fmt = (
        '%(asctime)s | %(levelname)-8s | %(name)s | '
        '%(filename)s:%(lineno)d | %(message)s'
    )
    console_formatter = ColoredFormatter(
        fmt=console_fmt,
        datefmt='%Y-%m-%d %H:%M:%S',
        use_colors=use_colors
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # File format (no colors)
        file_fmt = (
            '%(asctime)s | %(levelname)-8s | %(name)s | '
            '%(filename)s:%(lineno)d | %(message)s'
        )
        file_formatter = logging.Formatter(
            fmt=file_fmt,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {log_path}")

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger for a specific module.

    Args:
        name: Module name (use __name__)

    Returns:
        logging.Logger: Logger instance

    Example:
        >>> from mdsa.utils import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.debug("Processing request")
    """
    return logging.getLogger(name)


# Initialize default MDSA logger
_default_logger = None


def init_framework_logger(level: str = 'INFO', log_file: Optional[str] = None):
    """
    Initialize the default MDSA framework logger.

    This should be called once at framework initialization.

    Args:
        level: Log level
        log_file: Optional log file path
    """
    global _default_logger
    _default_logger = setup_logger('mdsa', level=level, log_file=log_file)
    return _default_logger


if __name__ == "__main__":
    # Demo usage
    logger = setup_logger('mdsa.demo', level='DEBUG')

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # With file logging
    logger_with_file = setup_logger(
        'mdsa.file_demo',
        level='DEBUG',
        log_file='logs/mdsa.log'
    )
    logger_with_file.info("This message goes to both console and file")
