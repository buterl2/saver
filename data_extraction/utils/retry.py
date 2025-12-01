import time
from data_extraction.utils.recover import recover_from_error
import data_extraction.config.config as config
from data_extraction.utils import default_logger as logger
from typing import Callable, TypeVar, Optional

T = TypeVar("T")

def retry(
    func: Callable[[], T],
    max_retries: int = config.MAX_RETRIES,
    wait_seconds: float = config.WAIT_SECONDS,
    raise_on_failure: bool = True,
    func_name: Optional[str] = None
    ) -> Optional[T]:

    func_display = func_name or func.__name__
    last_exception = None

    for attempt in range(max_retries):
        try:
            result = func()
            if attempt > 0:
                logger.info(f"{func_display} succeeded on attempt {attempt + 1}")
            return result
        except Exception as e:
            last_exception = e
            logger.warning(
                f"{func_display} failed on attempt {attempt + 1}/{max_retries}: {e}"
            )

            if attempt < max_retries - 1:
                try:
                    recover_from_error()
                except Exception as recovery_error:
                    logger.warning(f"Recovery attempt failed: {recovery_error}")
                
                wait_time = wait_seconds * (2 ** attempt)
                logger.debug(f"Waiting {wait_time:.2f} seconds before retry...")
                time.sleep(wait_time)

    error_msg = (
        f"{func_display} failed after {max_retries} attempts. "
        f"Last error: {str(last_exception)}"
    )
    logger.error(error_msg, exc_info=last_exception)

    if raise_on_failure:
        raise last_exception from None
    else:
        return None