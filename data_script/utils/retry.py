from data_script.utils.SAP import SAPSession
from data_script.utils.logger import setup_logger
import data_script.config.constants as constant
from typing import Callable, TypeVar, Optional
import time

logger = setup_logger("sap_recovery")

T = TypeVar("T")

def recover_from_sap_error() -> None:
    """Attempt to recover from SAP errors by closing error dialogs"""
    try:
        recover = SAPSession()
        # Try to close error dialogs by pressing back button multiple times
        for i in range(3):
            try:
                recover.findById("").press()
                logger.debug(f"Recovery: Pressed back button (attempt {i+1})")
            except Exception:
                # No more dialogs to close
                break
    except Exception as e:
        logger.warning(f"Recovery attempt failed: {e}")

def retry_sap_operation(
    func: Callable[[], T],
    max_retries: int = constant.MAX_RETRIES,
    wait_seconds: float = constant.WAIT_SECONDS,
    raise_on_failure: bool = True,
    func_name: Optional[str] = None
) -> Optional[T]:
    """
    Retry a SAP operation with exponential backoff and error recovery

    Args:
        func: Function to retry (should be a callable that takes no arguments)
        max_retires: Maximum number of retry attempts
        wait_seconds: Base wait time in seconds (will be multiplied by 2^attempt)
        raise_on_failure: Wheter to raise exception after all retries fall
        func_name: Display name for the function (for logging)

    Returns:
        Result of the function, or None if raise_on_failure is False
    """
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
            error_type = type(e).__name__
            error_msg = str(e)
            
            logger.warning(
                f"{func_display} failed on attempt {attempt + 1 }/{max_retries} "
                f"({error_type}): {error_msg}"
            )

            if attempt < max_retries - 1:
                # Attempt recovery
                try:
                    recover_from_sap_error()
                    logger.debug("Recovery attempt completed")
                except Exception as recovery_error:
                    logger.warning(f"Recovery attempt failed: {recovery_error}")
                
                # Exponential backoff: wait longer with each retry
                wait_time = wait_seconds * (2 ** attempt)
                logger.info(f"Waiting {wait_time:.2f} seconds before retry...")
                time.sleep(wait_time)
            else:
                # Last attempt failed
                logger.error(
                    f"{func_display} failed after {max_retries} attempts. "
                    f"Last error ({error_type}): {error_msg}",
                    exc_info=True
                )

    if raise_on_failure:
        raise last_exception from None
    else:
        return None