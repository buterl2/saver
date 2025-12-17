"""
Main scheduler for extraction workflows.

This script runs picking, packing, and dashboard extraction scripts continuously
on weekdays (Monday-Friday) between 08:00 and 23:30. It runs the scripts repeatedly
during the time window, with a delay between executions. It waits until the next
valid execution window if started outside these constraints.
"""

import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from data_script.utils.logger import setup_logger

# Set up logger
logger = setup_logger("main_scheduler")

# Execution time window
START_TIME = "08:00"
END_TIME = "23:30"

# Delay between script executions (in seconds) when running continuously
EXECUTION_DELAY = 60  # 1 minute between runs

# Scripts to run in order
SCRIPTS = [
    "data_script.extraction.picking",
    "data_script.extraction.packing",
    "data_script.extraction.dashboard"
]


def is_weekday(date: datetime) -> bool:
    """
    Check if the given date is a weekday (Monday-Friday).
    
    Args:
        date: The datetime to check
        
    Returns:
        True if weekday (0=Monday, 6=Sunday), False otherwise
    """
    return date.weekday() < 5  # 0-4 are Monday-Friday


def is_within_time_window(now: datetime, start_time: str, end_time: str) -> bool:
    """
    Check if the current time is within the execution window.
    
    Args:
        now: Current datetime
        start_time: Start time string in HH:MM format
        end_time: End time string in HH:MM format
        
    Returns:
        True if within time window, False otherwise
    """
    try:
        start_hour, start_minute = map(int, start_time.split(":"))
        end_hour, end_minute = map(int, end_time.split(":"))
        
        current_time = now.time()
        start = datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0).time()
        end = datetime.now().replace(hour=end_hour, minute=end_minute, second=0, microsecond=0).time()
        
        return start <= current_time <= end
    except Exception as e:
        logger.error(f"Error parsing time window: {e}")
        return False


def calculate_next_execution_time(now: datetime, start_time: str) -> datetime:
    """
    Calculate the next valid execution time.
    
    Args:
        now: Current datetime
        start_time: Start time string in HH:MM format
        
    Returns:
        Next valid execution datetime
    """
    try:
        start_hour, start_minute = map(int, start_time.split(":"))
        
        # Set target time for today
        target = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        
        # If target is in the future today and today is a weekday, use it
        if now < target and is_weekday(target):
            return target
        
        # Otherwise, move to next day
        target = target + timedelta(days=1)
        
        # Find next weekday
        while not is_weekday(target):
            target = target + timedelta(days=1)
        
        return target
        
    except Exception as e:
        logger.error(f"Error calculating next execution time: {e}")
        # Fallback: next Monday at start time
        start_hour, start_minute = map(int, start_time.split(":"))
        days_until_monday = (7 - now.weekday()) % 7 or 7
        next_monday = now + timedelta(days=days_until_monday)
        return next_monday.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)


def wait_until_time(target_time: datetime) -> None:
    """
    Wait until the target time is reached.
    
    Args:
        target_time: Target datetime to wait for
    """
    now = datetime.now()
    if target_time <= now:
        return
        
    wait_seconds = (target_time - now).total_seconds()
    logger.info(f"Waiting until {target_time.strftime('%Y-%m-%d %H:%M:%S')} ({wait_seconds:.0f} seconds)")
    
    # Wait in smaller intervals to allow for interruption
    while datetime.now() < target_time:
        remaining = (target_time - datetime.now()).total_seconds()
        if remaining > 60:
            time.sleep(60)  # Sleep in 1-minute intervals
            logger.debug(f"Still waiting... {remaining:.0f} seconds remaining")
        else:
            time.sleep(remaining)
            break
    
    logger.info(f"Target time reached: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def run_script(script_module: str) -> bool:
    """
    Run a script module as a subprocess.
    
    Args:
        script_module: Module path (e.g., "data_script.extraction.picking")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Starting script: {script_module}")
        
        # Run the script as a module
        result = subprocess.run(
            [sys.executable, "-m", script_module],
            check=False,
            capture_output=False,  # Let output go to console
            cwd=Path(__file__).parent.parent  # Run from project root
        )
        
        if result.returncode == 0:
            logger.info(f"Script {script_module} completed successfully")
            return True
        else:
            logger.error(f"Script {script_module} failed with return code {result.returncode}")
            return False
            
    except KeyboardInterrupt:
        logger.warning(f"Script {script_module} interrupted by user")
        raise
    except Exception as e:
        logger.error(f"Error running script {script_module}: {e}", exc_info=True)
        return False


def run_all_scripts() -> bool:
    """
    Run all scripts in sequence.
    
    Returns:
        True if all scripts succeeded, False otherwise
    """
    logger.info("=" * 80)
    logger.info("Starting extraction workflow sequence")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    for i, script in enumerate(SCRIPTS, 1):
        logger.info(f"Step {i}/{len(SCRIPTS)}: Running {script}")
        
        try:
            success = run_script(script)
            if not success:
                logger.error(f"Script {script} failed. Stopping workflow sequence.")
                return False
        except KeyboardInterrupt:
            logger.warning("Workflow sequence interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Unexpected error running {script}: {e}", exc_info=True)
            return False
    
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info("=" * 80)
    logger.info(f"All scripts completed successfully in {elapsed:.0f} seconds")
    logger.info("=" * 80)
    
    return True


def main() -> None:
    """
    Main scheduler loop.
    
    Runs scripts continuously on weekdays between START_TIME and END_TIME.
    Waits for the next valid execution window if outside these constraints.
    """
    logger.info("=" * 80)
    logger.info("Main Scheduler Started")
    logger.info("=" * 80)
    logger.info(f"Execution window: Weekdays, {START_TIME} - {END_TIME}")
    logger.info(f"Scripts to run: {', '.join(SCRIPTS)}")
    logger.info(f"Execution delay between runs: {EXECUTION_DELAY} seconds")
    logger.info("=" * 80)
    
    try:
        while True:
            now = datetime.now()
            logger.info(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} ({now.strftime('%A')})")
            
            # Check if we're in a valid execution window
            if is_weekday(now) and is_within_time_window(now, START_TIME, END_TIME):
                logger.info("Current time is within valid execution window - running scripts continuously")
                
                # Continuous execution loop - run scripts repeatedly while within time window
                while True:
                    # Check if we're still in the valid window before running
                    now = datetime.now()
                    if not is_weekday(now) or not is_within_time_window(now, START_TIME, END_TIME):
                        logger.info(f"Time window ended. Current time: {now.strftime('%H:%M:%S')}, window: {START_TIME} - {END_TIME}")
                        break
                    
                    # Run all scripts
                    run_all_scripts()
                    
                    # Check again if we're still in the window after execution
                    now = datetime.now()
                    if not is_weekday(now) or not is_within_time_window(now, START_TIME, END_TIME):
                        logger.info(f"Time window ended after execution. Current time: {now.strftime('%H:%M:%S')}, window: {START_TIME} - {END_TIME}")
                        break
                    
                    # Wait before next execution
                    logger.info(f"Waiting {EXECUTION_DELAY} seconds before next execution...")
                    time.sleep(EXECUTION_DELAY)
                
            else:
                # Outside valid window, wait until next valid time
                if not is_weekday(now):
                    logger.info(f"Current day ({now.strftime('%A')}) is not a weekday. Waiting for next weekday...")
                else:
                    logger.info(f"Current time ({now.strftime('%H:%M:%S')}) is outside execution window ({START_TIME} - {END_TIME})")
                
                next_execution = calculate_next_execution_time(now, START_TIME)
                logger.info(f"Next execution scheduled for: {next_execution.strftime('%Y-%m-%d %H:%M:%S')} ({next_execution.strftime('%A')})")
                
                wait_until_time(next_execution)
    
    except KeyboardInterrupt:
        logger.info("=" * 80)
        logger.info("Scheduler interrupted by user. Shutting down...")
        logger.info("=" * 80)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error in scheduler: {e}", exc_info=True)
        logger.error("Scheduler will exit. Please restart manually.")
        sys.exit(1)


if __name__ == "__main__":
    main()

