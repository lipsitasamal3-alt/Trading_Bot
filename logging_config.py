"""
logging_config.py
=================
Configures the application-wide logging system.

Features:
    - File handler: Writes structured logs to logs/trading_bot.log
    - Console handler: Outputs WARNING+ level messages to stderr
    - Professional log format with timestamps, level, module, and message
    - Log rotation handled by RotatingFileHandler (10 MB max, 5 backups)
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LOG_DIR: str = "logs"
LOG_FILE: str = os.path.join(LOG_DIR, "trading_bot.log")
LOG_FORMAT: str = (
    "%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-25s | %(message)s"
)
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT: int = 5


def setup_logging(level: int = logging.DEBUG) -> logging.Logger:
    """
    Set up and return the root application logger.

    Creates the ``logs/`` directory if it does not exist, attaches a
    :class:`~logging.handlers.RotatingFileHandler` (DEBUG+) for persistent
    storage, and a :class:`~logging.StreamHandler` (WARNING+) for console
    visibility.

    Args:
        level (int): Minimum logging level for the file handler.
                     Defaults to ``logging.DEBUG``.

    Returns:
        logging.Logger: The configured root logger named ``"trading_bot"``.
    """
    # Ensure the log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers when the module is reloaded
    if logger.handlers:
        return logger

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # ------------------------------------------------------------------
    # File handler — captures everything DEBUG and above
    # ------------------------------------------------------------------
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # ------------------------------------------------------------------
    # Console handler — shows WARNING and above (keeps the terminal clean)
    # ------------------------------------------------------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.debug("Logging initialised. Log file: %s", LOG_FILE)
    return logger


# Module-level logger for use within this package
logger: logging.Logger = setup_logging()
