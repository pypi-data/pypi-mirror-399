"""
Unified logging configuration module.

Provides centralized logging configuration for GNS3 Copilot tools package,
eliminating duplicate logging setup code across modules.
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler


def setup_logger(
    name: str,
    log_file: str | None = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Set up unified logging configuration.

    Args:
        name (str): Logger name, typically the module name
        log_file (str, optional): Log file path, defaults to log/{name}.log
        console_level (int, optional): Console log level, defaults to INFO
        file_level (int, optional): File log level, defaults to DEBUG

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set logger level to DEBUG for maximum detail

    # Prevent duplicate handlers
    if not logger.handlers:
        # Create unified formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Configure file handler
        if log_file is None:
            log_file = f"log/{name}.log"

        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Configure file handler with timed rotation (every 7 days)
        file_handler = TimedRotatingFileHandler(
            log_file,
            when="D",  # Rotate daily
            interval=7,  # Every 7 days
            backupCount=5,  # Keep 5 backup files
            encoding="utf-8",
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Prevent propagation to root logger to avoid duplicate logging
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger, use default configuration if not configured.

    Args:
        name (str): Logger name

    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, use default configuration
    if not logger.handlers:
        return setup_logger(name)

    return logger


def configure_package_logging(level: int = logging.INFO) -> None:
    """
    Configure root log level for the entire package.

    Args:
        level (int): Log level
    """
    # Set package root logger
    package_logger = logging.getLogger("tools")
    package_logger.setLevel(level)

    # If no handlers, add a simple console handler
    if not package_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter("GNS3 Tools: %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        package_logger.addHandler(console_handler)


# Default logger configuration for all modules
DEFAULT_LOGGER_CONFIG = {
    "console_level": logging.ERROR,
    "file_level": logging.DEBUG,
}

# Predefined logging configurations for modules that need special settings
# Most modules will use DEFAULT_LOGGER_CONFIG, so only list exceptions here
LOGGER_CONFIGS: dict[str, dict[str, int]] = {
    # Add modules with special configurations here
    # Example:
    # "special_module": {"console_level": logging.INFO, "file_level": logging.DEBUG},
}


def setup_tool_logger(tool_name: str, config_name: str | None = None) -> logging.Logger:
    """
    Set up logger for specific tool using predefined configuration.

    Args:
        tool_name (str): Tool name (used for log file name)
        config_name (str, optional): Configuration name to look up in LOGGER_CONFIGS,
                                     defaults to tool_name. If not found, uses DEFAULT_LOGGER_CONFIG.

    Returns:
        logging.Logger: Configured logger instance
    """
    if config_name is None:
        config_name = tool_name

    # Get configuration, fall back to default if not found
    config = LOGGER_CONFIGS.get(config_name, DEFAULT_LOGGER_CONFIG)

    return setup_logger(
        name=tool_name,
        log_file=f"log/{tool_name}.log",
        console_level=config.get(
            "console_level", DEFAULT_LOGGER_CONFIG["console_level"]
        ),
        file_level=config.get("file_level", DEFAULT_LOGGER_CONFIG["file_level"]),
    )
