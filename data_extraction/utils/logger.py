import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

def setup_logger(name: str = __name__, log_file: Optional[Union[str, Path]] = None, log_level: int = logging.INFO) -> logging.Logger:
    # CREATE LOGGER
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # AVOID ADDING HANDLERS MULTIPLE TIMES IF LOGGER ALREADY EXISTS
    if logger.handlers:
        return logger

    # CREATE LOGS DIRECTORY IF IT DOESN'T EXISTS
    if log_file is None:
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
    else:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

    # CREATE FORMATTERS
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # FILE HANDLER - LOGS EVERYTHING
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)

    # ADD HANDLERS TO LOGGER
    logger.addHandler(file_handler)

    return logger

default_logger = setup_logger('data_extraction')