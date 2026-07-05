import logging
import sys

# ANSI color codes for terminal output styling
RESET = "\033[0m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"


class ColoredFormatter(logging.Formatter):
    """
    A custom logging formatter that injects ANSI color codes
    based on the log level to improve terminal readability.
    """

    # Define the visual structure for each log level.
    # The datefmt will be applied to %(asctime)s automatically.
    FORMATS = {
        logging.DEBUG: f"{CYAN}[DEBUG] %(asctime)s - %(message)s{RESET}",
        logging.INFO: f"{GREEN}[INFO] %(asctime)s - %(message)s{RESET}",
        logging.WARNING: f"{YELLOW}[WARNING] %(asctime)s - %(message)s{RESET}",
        logging.ERROR: f"{RED}{BOLD}[ERROR] %(asctime)s - %(message)s{RESET}",
        logging.CRITICAL: f"{RED}{BOLD}[FATAL] %(asctime)s - "
        f"%(message)s{RESET}",
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Overrides the default format method to apply the specific
        color scheme based on the record's logging level.
        """
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        # Only show Hours:Minutes:Seconds to keep the output clean
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


def setup_logger(name: str = "fly_in_logger") -> logging.Logger:
    """
    Configures and returns a globally accessible, colored logger instance.
    Ensures handlers are not duplicated if called multiple times across
    modules.

    Args:
        name: The internal name of the logger.

    Returns:
        A configured logging.Logger object.
    """
    logger = logging.getLogger(name)

    # Set the global threshold.
    # Use DEBUG during development to see pathfinding logic,
    # switch to INFO for the final defense to only show drone movements.
    logger.setLevel(logging.DEBUG)

    # Prevent adding multiple handlers if the module is imported several times
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)

    # Prevent the logger from passing messages to the root logger
    # (avoids double printing if other libraries also use logging)
    logger.propagate = False

    return logger


# Create a default instance that can be imported directly
logger = setup_logger()
