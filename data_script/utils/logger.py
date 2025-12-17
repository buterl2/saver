import logging
from pickle import FALSE
from typing import Optional, Union
from pathlib import Path
from datetime import datetime
import data_script.config.constants as constant

try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False

def setup_logger(name: str = __name__, log_file: Optional[Union[str, Path]] = None, log_level: int = logging.INFO, console_output: bool = True) -> logging.Logger:
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid adding handlers multiple times if logger already exists
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exists
    if log_file is None:
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"app_{datetime.now().strftime("%Y%m%d")}.log"
    else:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler - logs everything
    file_handler = logging.FileHandler(log_file, encoding=constant.ENCODING_LOGGER)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)

    # Console handler with colors
    if console_output:
        if COLORLOG_AVAILABLE:
            # Colored console formatter
            console_formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                }
            )
            console_handler = colorlog.StreamHandler()
        else:
            # Fallback to regular console handler
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler = logging.StreamHandler()

        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger