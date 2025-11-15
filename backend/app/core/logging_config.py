"""
Structured JSON Logging Configuration.

Provides JSON-formatted logging for better log aggregation and analysis.
Based on TRUTH_FREE.md Phase 5.4.
"""

import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_json_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up structured JSON logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured root logger with JSON formatting

    Features:
        - JSON-formatted logs for easy parsing
        - Includes timestamp, name, level, message
        - Outputs to stdout for container environments
        - Compatible with log aggregation tools (Grafana Loki, ELK, etc.)
    """
    # Get root logger
    logger = logging.getLogger()

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Create stdout handler
    log_handler = logging.StreamHandler(sys.stdout)

    # JSON formatter with custom format
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    logger.info(
        "Structured JSON logging initialized",
        extra={"log_level": level, "format": "json"}
    )

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Logger instance

    Usage:
        logger = get_logger(__name__)
        logger.info("Message", extra={"user_id": 123, "action": "login"})
    """
    return logging.getLogger(name)
