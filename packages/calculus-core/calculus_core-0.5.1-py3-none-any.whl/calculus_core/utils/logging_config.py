"""
Logging Configuration
"""

import logging
import sys
from typing import Optional

# Default format: Time | Level | Logger Name | Message
DEFAULT_FORMAT = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_output: bool = True,
) -> None:
    """
    Configure the root logger for the application.

    Args:
        level: Logging level (default: INFO)
        log_file: Path to a file to write logs to (optional)
        console_output: Whether to output logs to stderr (default: True)
    """
    handlers = []

    if console_output:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(
            logging.Formatter(DEFAULT_FORMAT, DATE_FORMAT)
        )
        handlers.append(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(DEFAULT_FORMAT, DATE_FORMAT)
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,  # Override any existing configuration
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for a specific component.

    Args:
        name: Component name (e.g. 'calculus_core.service_layer')

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
