"""
Logging Configuration for UACE

Provides comprehensive logging with tqdm progress bars.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class TqdmLoggingHandler(logging.Handler):
    """
    Logging handler that works with tqdm progress bars.
    Prevents logging from disrupting progress bar display.
    """
    
    def emit(self, record):
        try:
            from tqdm import tqdm
            msg = self.format(record)
            tqdm.write(msg)
        except ImportError:
            # Fallback if tqdm not available
            print(self.format(record))


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for better readability."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    # Emoji prefixes
    EMOJI = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
    }
    
    def format(self, record):
        # Add color
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.EMOJI.get(levelname, '')} {levelname}{self.RESET}"
        
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    use_colors: bool = True,
    verbose: bool = False
) -> logging.Logger:
    """
    Setup UACE logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file to write logs to
        use_colors: Use colored output
        verbose: Enable verbose logging (DEBUG level)
        
    Returns:
        Configured logger
    """
    
    # Set level
    if verbose:
        level = "DEBUG"
    
    log_level = getattr(logging, level.upper())
    
    # Create logger
    logger = logging.getLogger("uace")
    logger.setLevel(log_level)
    logger.handlers.clear()  # Remove existing handlers
    
    # Console handler with tqdm support
    console_handler = TqdmLoggingHandler()
    console_handler.setLevel(log_level)
    
    # Format
    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
    
    return logger


def get_logger(name: str = "uace") -> logging.Logger:
    """Get or create a logger."""
    return logging.getLogger(name)


# Create default logger
logger = get_logger()


class UACELogger:
    """
    UACE-specific logger with tqdm integration.
    """
    
    def __init__(self, name: str = "uace", verbose: bool = False):
        self.logger = logging.getLogger(name)
        self.verbose = verbose
        
    def debug(self, msg: str):
        """Log debug message."""
        self.logger.debug(msg)
    
    def info(self, msg: str):
        """Log info message."""
        self.logger.info(msg)
    
    def warning(self, msg: str):
        """Log warning message."""
        self.logger.warning(msg)
    
    def error(self, msg: str):
        """Log error message."""
        self.logger.error(msg)
    
    def critical(self, msg: str):
        """Log critical message."""
        self.logger.critical(msg)


__all__ = [
    "setup_logging",
    "get_logger",
    "logger",
    "UACELogger",
]
