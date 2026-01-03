import logging
import sys


def setup_logger(name: str = "zopassport", level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with the specified name and level.

    Args:
        name: Logger name (default: "zopassport")
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handler if logger doesn't have one
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    logger.propagate = False
    return logger


# Default logger instance
logger = setup_logger()


def set_log_level(level: str) -> None:
    """
    Set the logging level for the default logger.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger.setLevel(level)


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (default: uses root zopassport logger)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"zopassport.{name}")
    return logger
