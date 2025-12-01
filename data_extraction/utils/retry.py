import time
from data_extraction.utils.recover import recover_from_error
import data_extraction.config.config as config
from data_extraction.utils import default_logger as logger

def retry(func, max_retries=config.MAX_RETRIES, wait_seconds=config.WAIT_SECONDS):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                recover_from_error()
                time.sleep(wait_seconds)
            else:
                break