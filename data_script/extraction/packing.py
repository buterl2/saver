from typing import Any, Optional, Dict, List, Tuple
from data_script.utils.SAP import SAPSession
import data_script.config.constants as constant
from data_script.utils.logger import setup_logger
from data_script.utils.retry import retry_sap_operation
from data_script.utils.files_utils import convert_to_csv, rename, convert_to_json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Set up logger
logger = setup_logger("packing_extraction")

def _extract_cdhdr_internal(date: str, folder: str, filename: str) -> None:
    """Internal extraction function (called by retry wrapper)"""
    logger.info(f"Starting CDHDR extraction for date: {date}, filename: {filename}, folder: {folder}")

    # Initialize SAP
    extractor = SAPSession()

    # Start transaction and fill in fields
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.table("CDHDR")
    extractor.checkbox_selection(constant.CDHDR_CHECKBOX)
    extractor.findById('wnd[0]/usr/ctxtI5-LOW').text = date
    extractor.findById("wnd[0]/usr/ctxtI7-LOW").text = "ZORF_BOX_CLOSING"
    extractor.findById("wnd[0]/usr/btn%_I4_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = f"{constant.OUTPUT_PATH}/misc/"
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "users.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    logger.info("Transaction executed successfully")

    # Save to folder
    extractor.save_to_folder(folder, filename)
    logger.info(f"Data saved to {filename}")

def extract_cdhdr(date: str, folder: str, filename: str) -> None:
    """
    Extract CDHDR data for packing productivity with automatic retry
    
    Args:
        date: Date string for the extraction
        folder: Ouput folder
        filename: Output filename
    """
    retry_sap_operation(
        lambda: _extract_cdhdr_internal(date, folder, filename),
        func_name="extract_cdhdr"
    )

def combine() -> pd.DataFrame:
    """
    Combine CDHDR file with users data.
    
    Reads packing.csv and users_floor.csv, merges them, and removes duplicates.
    
    Returns:
        DataFrame: Combined dataframe with merged user information
        
    Raises:
        FileNotFoundError: If any required file is missing
        KeyError: If required columns don't exist
        ValueError: If merge operations fail
    """
    logger.info("Starting to combine CDHDR file with users")
    
    file_paths = {
        "cdhdr": f"{constant.OUTPUT_PATH}/packing/packing.csv",
        "users": f"{constant.OUTPUT_PATH}/misc/users_floor.csv"
    }
    
    # Validate files exist
    for name, path in file_paths.items():
        if not Path(path).exists():
            error_msg = f"Required file not found: {name} at {path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        logger.debug(f"Found {name} file: {path}")
    
    try:
        # Read CDHDR file
        logger.debug("Reading packing.csv")
        try:
            cdhdr = pd.read_csv(file_paths["cdhdr"], encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for packing.csv, trying latin-1")
            cdhdr = pd.read_csv(file_paths["cdhdr"], encoding="latin-1")
        
        logger.debug(f"packing.csv: {len(cdhdr)} rows, {len(cdhdr.columns)} columns")
        logger.debug(f"Columns: {list(cdhdr.columns)}")
        
        # Read users file
        logger.debug("Reading users_floor.csv")
        try:
            users = pd.read_csv(file_paths["users"], encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for users_floor.csv, trying latin-1")
            users = pd.read_csv(file_paths["users"], encoding="latin-1")
        
        logger.debug(f"users_floor.csv: {len(users)} rows, {len(users.columns)} columns")
        logger.debug(f"Columns: {list(users.columns)}")
        
        # Validate required columns exist
        required_col_cdhdr = ["user"]
        required_col_users = ["user"]
        required_col_result = ["object_value"]
        
        for col in required_col_cdhdr:
            if col not in cdhdr.columns:
                error_msg = f"Required column '{col}' not found in packing.csv. Available columns: {list(cdhdr.columns)}"
                logger.error(error_msg)
                raise KeyError(error_msg)
        
        for col in required_col_users:
            if col not in users.columns:
                error_msg = f"Required column '{col}' not found in users_floor.csv. Available columns: {list(users.columns)}"
                logger.error(error_msg)
                raise KeyError(error_msg)
        
        logger.debug("All required columns validated")
        
        # Merge with users
        logger.info("Merging CDHDR data with users")
        try:
            before_merge_count = len(cdhdr)
            combined = cdhdr.merge(users, on="user", how="left")
            after_merge_count = len(combined)
            
            # Check how many rows got user information
            users_matched = combined["user"].notna().sum() if "user" in combined.columns else 0
            users_unmatched = combined["user"].isna().sum() if "user" in combined.columns else 0
            
            logger.info(f"Merge completed: {after_merge_count} rows (before: {before_merge_count})")
            logger.info(f"Users matched: {users_matched}, Users unmatched: {users_unmatched}")
        except Exception as e:
            error_msg = f"Failed to merge with users: {e}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e
        
        # Drop duplicates
        if "object_value" not in combined.columns:
            error_msg = f"Required column 'object_value' not found in combined data. Available columns: {list(combined.columns)}"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        logger.info("Removing duplicates based on 'object_value' column")
        try:
            before_dedup_count = len(combined)
            combined = combined.drop_duplicates(subset="object_value", keep="first")
            after_dedup_count = len(combined)
            duplicates_removed = before_dedup_count - after_dedup_count
            
            logger.info(f"Deduplication completed: {after_dedup_count} rows (removed {duplicates_removed} duplicates)")
        except Exception as e:
            error_msg = f"Failed to drop duplicates: {e}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e
        
        logger.info(f"Successfully combined files. Final result: {len(combined)} rows, {len(combined.columns)} columns")
        return combined
    
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except pd.errors.EmptyDataError as e:
        error_msg = f"One or more files are empty: {e}"
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Unexpected error during combine operation: {e}"
        logger.error(error_msg, exc_info=True)
        raise

def prepare_cdhdr_data(combined: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare CDHDR data by converting datetime and extracting hour.
    
    Args:
        combined: DataFrame with date and time columns
    
    Returns:
        Processed DataFrame with hour column added
    
    Raises:
        ValueError: If required columns are missing or data is invalid
        KeyError: If required columns don't exist
    """
    try:
        logger.info("Preparing CDHDR data: converting datetime and extracting hour")
        
        # Validate required columns exist
        required_columns = ["date", "time"]
        missing_columns = [col for col in required_columns if col not in combined.columns]
        if missing_columns:
            logger.error(f"Missing required columns in combined data: {missing_columns}")
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        logger.debug(f"Combined data contains columns: {list(combined.columns)}")
        
        # Check for empty dataframe
        if combined.empty:
            logger.warning("Combined dataframe is empty, datetime operations may fail")
        
        # Check for null values in date/time columns
        null_dates = combined["date"].isna().sum()
        null_times = combined["time"].isna().sum()
        if null_dates > 0:
            logger.warning(f"Found {null_dates} null values ({null_dates/len(combined)*100:.1f}%) in 'date' column")
        if null_times > 0:
            logger.warning(f"Found {null_times} null values ({null_times/len(combined)*100:.1f}%) in 'time' column")
        
        # Convert datetime
        try:
            logger.debug("Converting date and time to datetime")
            initial_rows = len(combined)
            combined["datetime"] = pd.to_datetime(
                combined["date"] + " " + combined["time"], 
                format="%d.%m.%Y %H:%M:%S", 
                errors="coerce"
            )
            
            # Check how many successful conversions
            successful_conversions = combined["datetime"].notna().sum()
            failed_conversions = initial_rows - successful_conversions
            
            if failed_conversions > 0:
                logger.warning(
                    f"Failed to convert {failed_conversions} rows ({failed_conversions/initial_rows*100:.1f}%) "
                    f"to datetime format"
                )
            else:
                logger.debug(f"Successfully converted {successful_conversions} rows to datetime")
        except Exception as e:
            logger.error(f"Error converting to datetime: {e}", exc_info=True)
            raise ValueError(f"Failed to convert datetime columns: {e}") from e
        
        # Add hour offset
        try:
            logger.debug("Adding 1 hour offset to datetime")
            combined["datetime"] += pd.DateOffset(hours=1)
            logger.debug("Hour offset applied successfully")
        except Exception as e:
            logger.error(f"Error adding hour offset: {e}", exc_info=True)
            raise ValueError(f"Failed to add hour offset: {e}") from e
        
        # Extract hour
        try:
            logger.debug("Extracting hour from datetime")
            combined["hour"] = combined["datetime"].dt.strftime("%H")
            
            # Validate hour extraction
            valid_hours = combined["hour"].notna().sum()
            invalid_hours = len(combined) - valid_hours
            
            if invalid_hours > 0:
                logger.warning(f"Failed to extract hour for {invalid_hours} rows")
            else:
                logger.debug(f"Successfully extracted hour for {valid_hours} rows")
        except Exception as e:
            logger.error(f"Error extracting hour: {e}", exc_info=True)
            raise ValueError(f"Failed to extract hour: {e}") from e
        
        # Drop datetime column
        try:
            logger.debug("Dropping datetime column")
            combined = combined.drop(columns="datetime")
            logger.debug("Datetime column dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping datetime column: {e}")
            raise
        
        logger.info(
            f"CDHDR data preparation complete: {len(combined)} rows, {len(combined.columns)} columns"
        )
        
        return combined
    
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to prepare CDHDR data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prepare_cdhdr_data: {e}", exc_info=True)
        raise RuntimeError(f"Unexpected error preparing CDHDR data: {e}") from e

def get_productivity_color(value: float, thresholds: List[int]) -> str:
    """
    Determine productivity color based on value and thresholds.
    
    Args:
        value: The productivity value to evaluate
        thresholds: List of 3 threshold values [low, medium, high]
        
    Returns:
        Color string: "red", "orange", "green", or "purple"
    """
    if not thresholds or len(thresholds) < 3:
        return "unknown"
    
    if value < thresholds[0]:
        return "red"
    elif value < thresholds[1]:
        return "orange"
    elif value < thresholds[2]:
        return "green"
    else:
        return "purple"

def calculate_packing_hourly_productivity(cdhdr: pd.DataFrame) -> Tuple[Dict[str, Dict[str, Dict[str, Any]]], Dict[str, Dict[str, int]]]:
    """
    Calculate hourly productivity metrics for packing operations.
    
    Groups data by user, floor, and hour, then calculates adjusted counts
    accounting for breaks and assigns productivity colors based on thresholds.
    
    Args:
        cdhdr: DataFrame with columns: user, floor, hour
        
    Returns:
        Tuple containing:
            - nested_dict: Dictionary with productivity data by user/floor/hour
            - total_hours: Dictionary tracking total hours worked by user/floor
            
    Raises:
        ValueError: If required columns are missing or config values are invalid
        KeyError: If floor not found in PACKING_THRESHOLDS
        ZeroDivisionError: If break multiplier is zero
    """
    try:
        logger.info("Starting hourly productivity calculation for packing operations")
        
        # Validate required columns
        required_columns = ["user", "floor", "hour"]
        missing_columns = [col for col in required_columns if col not in cdhdr.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns for productivity calculation: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check for empty dataframe
        if cdhdr.empty:
            logger.warning("CDHDR dataframe is empty, returning empty productivity results")
            return {}, {}
        
        # Validate config values exist
        try:
            breaks_config = constant.BREAKS if hasattr(constant, 'BREAKS') else {}
            thresholds_config = constant.PACKING_THRESHOLDS if hasattr(constant, 'PACKING_THRESHOLDS') else {}
            
            if not breaks_config:
                logger.warning("BREAKS configuration not found, break adjustments will be skipped")
            if not thresholds_config:
                error_msg = "PACKING_THRESHOLDS configuration not found"
                logger.error(error_msg)
                raise ValueError(error_msg)
        except AttributeError as e:
            logger.error(f"Configuration error: {e}")
            raise ValueError(f"Missing required configuration: {e}") from e
        
        # Check for null values in grouping columns
        null_counts = {}
        for col in required_columns:
            null_count = cdhdr[col].isna().sum()
            if null_count > 0:
                null_counts[col] = null_count
                logger.warning(
                    f"Found {null_count} null values ({null_count/len(cdhdr)*100:.1f}%) "
                    f"in column '{col}'"
                )
        
        # Perform groupby operation
        try:
            logger.debug("Grouping data by user, floor, and hour")
            packing_per_hour = cdhdr.groupby(required_columns).size()
            
            if packing_per_hour.empty:
                logger.warning("Groupby result is empty - no data matches grouping criteria")
                return {}, {}
            
            total_groups = len(packing_per_hour)
            total_packing = packing_per_hour.sum()
            logger.info(
                f"Groupby completed: {total_groups} unique groups, {total_packing} total packing"
            )
            
        except KeyError as e:
            error_msg = f"Column error during groupby: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during groupby: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
        
        # Initialize result dictionaries
        nested_dict = defaultdict(lambda: defaultdict(dict))
        total_hours = defaultdict(lambda: defaultdict(int))
        
        # Track statistics
        break_adjustments = 0
        missing_thresholds = 0
        invalid_floors = set()
        processed_groups = 0
        error_groups = 0
        
        # Process each group
        logger.debug("Processing groups and calculating productivity metrics")
        for (user, floor, hour), count in packing_per_hour.items():
            try:
                processed_groups += 1
                
                # Validate inputs
                if pd.isna(user) or pd.isna(floor) or pd.isna(hour):
                    logger.debug(f"Skipping group with null values: user={user}, floor={floor}, hour={hour}")
                    error_groups += 1
                    continue
                
                # Convert hour to string if needed
                hour_str = str(hour).strip() if not pd.isna(hour) else None
                if hour_str is None:
                    logger.debug(f"Skipping group with invalid hour: {hour}")
                    error_groups += 1
                    continue
                
                # Calculate adjusted count for breaks
                try:
                    if breaks_config and hour_str in breaks_config:
                        break_multiplier = breaks_config[hour_str]
                        
                        if break_multiplier == 0:
                            logger.warning(
                                f"Break multiplier is zero for hour '{hour_str}', "
                                f"using original count"
                            )
                            adjusted_count = count
                            total_hours[user][floor] += 1
                        else:
                            adjusted_count = count / break_multiplier
                            total_hours[user][floor] += break_multiplier
                            break_adjustments += 1
                            logger.debug(
                                f"Applied break adjustment for hour {hour_str}: "
                                f"{count} -> {adjusted_count:.2f} (multiplier: {break_multiplier})"
                            )
                    else:
                        adjusted_count = count
                        total_hours[user][floor] += 1
                
                except ZeroDivisionError as e:
                    logger.error(f"Division by zero error for hour '{hour_str}': {e}")
                    adjusted_count = count
                    total_hours[user][floor] += 1
                except Exception as e:
                    logger.error(f"Error calculating break adjustment: {e}")
                    adjusted_count = count
                    total_hours[user][floor] += 1
                
                # Determine productivity color
                try:
                    floor_str = str(floor).strip() if not pd.isna(floor) else None
                    
                    if floor_str not in thresholds_config:
                        missing_thresholds += 1
                        invalid_floors.add(floor_str)
                        logger.warning(
                            f"No productivity thresholds found for floor '{floor_str}', "
                            f"using default color"
                        )
                        color = "unknown"
                    else:
                        thresholds = thresholds_config[floor_str]
                        
                        # Validate thresholds
                        if not thresholds or len(thresholds) < 3:
                            logger.warning(
                                f"Invalid thresholds for floor '{floor_str}': {thresholds}, "
                                f"using default color"
                            )
                            color = "unknown"
                        else:
                            try:
                                color = get_productivity_color(adjusted_count, thresholds)
                            except NameError:
                                logger.error("get_productivity_color function not found, using default")
                                color = "unknown"
                            except Exception as e:
                                logger.error(f"Error in get_productivity_color: {e}")
                                color = "unknown"
                
                except Exception as e:
                    logger.error(f"Error determining productivity color: {e}")
                    color = "unknown"
                
                # Store result
                nested_dict[user][floor][hour_str] = {
                    "count": int(count),
                    "productivity_color": color
                }
                
            except Exception as e:
                error_groups += 1
                logger.error(
                    f"Error processing group (user={user}, floor={floor}, hour={hour}): {e}",
                    exc_info=True
                )
                continue
        
        # Log summary statistics
        successful_groups = processed_groups - error_groups
        logger.info(
            f"Productivity calculation complete: "
            f"{successful_groups}/{processed_groups} groups processed successfully, "
            f"{break_adjustments} break adjustments applied"
        )
        
        if missing_thresholds > 0:
            logger.warning(
                f"{missing_thresholds} groups had missing thresholds for floors: {invalid_floors}"
            )
        
        if error_groups > 0:
            logger.warning(f"{error_groups} groups had processing errors")
        
        # Log distribution summary
        unique_users = len(nested_dict)
        unique_floors = set()
        for user_data in nested_dict.values():
            unique_floors.update(user_data.keys())
        
        logger.debug(
            f"Result summary: {unique_users} users, {len(unique_floors)} floors"
        )
        
        return nested_dict, total_hours
        
    except ValueError as e:
        logger.error(f"Validation error in productivity calculation: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in calculate_packing_hourly_productivity: {e}", exc_info=True)
        raise RuntimeError(f"Unexpected error calculating productivity: {e}") from e

def calculate_packing_aggregate_metrics(
    nested_dict: Dict[str, Dict[str, Dict[str, Any]]], 
    total_hours: Dict[str, Dict[str, int]], 
    packing_per_user: pd.Series
) -> None:
    """
    Calculate aggregate productivity metrics and update nested dictionary.
    
    Calculates hours worked, productivity, boxes packed, and assigns
    productivity colors for each user/floor combination.
    
    Args:
        nested_dict: Dictionary to update with aggregate metrics (modified in place)
        total_hours: Dictionary with hours worked by user/floor
        packing_per_user: Series with boxes packed grouped by user/floor
        
    Raises:
        ValueError: If required data is invalid
        KeyError: If floor not found in thresholds or missing keys in dictionaries
    """
    try:
        logger.info("Starting aggregate metrics calculation for packing productivity")
        
        # Validate inputs
        if packing_per_user.empty:
            logger.warning("packing_per_user Series is empty, no metrics to calculate")
            return
        
        if not nested_dict:
            logger.warning("nested_dict is empty, will create new entries")
        
        if not total_hours:
            logger.warning("total_hours dictionary is empty, all hours_worked will be 0")
        
        # Validate config
        try:
            thresholds_config = constant.PACKING_THRESHOLDS if hasattr(constant, 'PACKING_THRESHOLDS') else {}
            if not thresholds_config:
                error_msg = "PACKING_THRESHOLDS configuration not found"
                logger.error(error_msg)
                raise ValueError(error_msg)
        except AttributeError as e:
            logger.error(f"Configuration error: {e}")
            raise ValueError(f"Missing required configuration: {e}") from e
        
        # Check if get_productivity_color function exists
        try:
            get_productivity_color
        except NameError:
            logger.error("get_productivity_color function not found")
            raise NameError("get_productivity_color function must be defined")
        
        # Track statistics
        processed_count = 0
        error_count = 0
        missing_hours_count = 0
        missing_thresholds_count = 0
        zero_productivity_count = 0
        invalid_floors = set()
        
        total_groups = len(packing_per_user)
        logger.info(f"Processing {total_groups} user/floor combinations")
        
        # Process each group
        for (user, floor), boxes_packed in packing_per_user.items():
            try:
                processed_count += 1
                
                # Validate group key values
                if pd.isna(user) or pd.isna(floor):
                    logger.debug(
                        f"Skipping group with null values: user={user}, floor={floor}"
                    )
                    error_count += 1
                    continue
                
                # Convert to strings and strip whitespace
                user_str = str(user).strip() if not pd.isna(user) else None
                floor_str = str(floor).strip() if not pd.isna(floor) else None
                
                if not all([user_str, floor_str]):
                    logger.debug(f"Skipping group with empty values: user={user_str}, floor={floor_str}")
                    error_count += 1
                    continue
                
                # Validate boxes_packed
                if pd.isna(boxes_packed) or boxes_packed <= 0:
                    logger.warning(
                        f"Invalid boxes_packed value ({boxes_packed}) for "
                        f"user={user_str}, floor={floor_str}"
                    )
                    error_count += 1
                    continue
                
                # Get hours worked
                try:
                    hours_worked = total_hours.get(user_str, {}).get(floor_str, 0)
                    
                    if hours_worked == 0:
                        missing_hours_count += 1
                        logger.debug(
                            f"No hours worked data for user={user_str}, floor={floor_str}"
                        )
                except (KeyError, TypeError) as e:
                    logger.warning(
                        f"Error accessing hours_worked for user={user_str}, floor={floor_str}: {e}"
                    )
                    hours_worked = 0
                    missing_hours_count += 1
                
                # Calculate productivity
                try:
                    if hours_worked > 0:
                        productivity = boxes_packed / hours_worked
                    else:
                        productivity = 0
                        zero_productivity_count += 1
                        logger.debug(
                            f"Zero hours worked for user={user_str}, floor={floor_str}, "
                            f"productivity set to 0"
                        )
                except ZeroDivisionError:
                    logger.warning(
                        f"Division by zero error for user={user_str}, floor={floor_str}"
                    )
                    productivity = 0
                    zero_productivity_count += 1
                except Exception as e:
                    logger.error(f"Error calculating productivity: {e}")
                    productivity = 0
                
                # Get productivity color
                try:
                    if floor_str not in thresholds_config:
                        missing_thresholds_count += 1
                        invalid_floors.add(floor_str)
                        logger.warning(
                            f"No productivity thresholds found for floor '{floor_str}', "
                            f"using default color for user={user_str}"
                        )
                        color = "unknown"
                    else:
                        thresholds = thresholds_config[floor_str]
                        
                        # Validate thresholds
                        if not thresholds or len(thresholds) < 3:
                            logger.warning(
                                f"Invalid thresholds for floor '{floor_str}': {thresholds}, "
                                f"using default color"
                            )
                            color = "unknown"
                        else:
                            try:
                                color = get_productivity_color(productivity, thresholds)
                            except Exception as e:
                                logger.error(f"Error in get_productivity_color: {e}")
                                color = "unknown"
                
                except Exception as e:
                    logger.error(f"Error determining productivity color: {e}")
                    color = "unknown"
                
                # Ensure nested_dict structure exists
                try:
                    if user_str not in nested_dict:
                        nested_dict[user_str] = {}
                    if floor_str not in nested_dict[user_str]:
                        nested_dict[user_str][floor_str] = {}
                except Exception as e:
                    logger.error(f"Error creating nested_dict structure: {e}")
                    error_count += 1
                    continue
                
                # Update nested dictionary
                try:
                    nested_dict[user_str][floor_str]["hours_worked"] = int(hours_worked)
                    nested_dict[user_str][floor_str]["productivity"] = round(productivity, 2)
                    nested_dict[user_str][floor_str]["productivity_color"] = color
                    nested_dict[user_str][floor_str]["boxes_packed"] = int(boxes_packed)
                    
                    logger.debug(
                        f"Updated metrics for user={user_str}, floor={floor_str}: "
                        f"productivity={productivity:.2f}, boxes={int(boxes_packed)}, "
                        f"color={color}"
                    )
                
                except (ValueError, TypeError) as e:
                    logger.error(
                        f"Error updating nested_dict for user={user_str}, "
                        f"floor={floor_str}: {e}"
                    )
                    error_count += 1
                    continue
                except Exception as e:
                    logger.error(
                        f"Unexpected error updating nested_dict: {e}",
                        exc_info=True
                    )
                    error_count += 1
                    continue
            
            except Exception as e:
                error_count += 1
                logger.error(
                    f"Unexpected error processing group (user={user}, floor={floor}): {e}",
                    exc_info=True
                )
                continue
        
        # Log summary statistics
        successful_count = processed_count - error_count
        logger.info(
            f"Aggregate metrics calculation complete: "
            f"{successful_count}/{processed_count} groups processed successfully"
        )
        
        if missing_hours_count > 0:
            logger.warning(f"{missing_hours_count} groups had missing or zero hours_worked")
        
        if missing_thresholds_count > 0:
            logger.warning(
                f"{missing_thresholds_count} groups had missing thresholds for floors: {invalid_floors}"
            )
        
        if zero_productivity_count > 0:
            logger.info(f"{zero_productivity_count} groups had zero productivity (zero hours worked)")
        
        if error_count > 0:
            logger.warning(f"{error_count} groups had processing errors")
        
        # Log sample statistics
        if successful_count > 0:
            # Calculate some aggregate stats from the results
            productivities = [
                nested_dict[user][floor].get("productivity", 0)
                for user in nested_dict
                for floor in nested_dict[user]
                if "productivity" in nested_dict[user][floor]
            ]
            
            if productivities:
                avg_productivity = sum(productivities) / len(productivities)
                max_productivity = max(productivities)
                min_productivity = min(productivities)
                logger.debug(
                    f"Productivity statistics: avg={avg_productivity:.2f}, "
                    f"min={min_productivity:.2f}, max={max_productivity:.2f}"
                )
        
    except ValueError as e:
        logger.error(f"Validation error in aggregate metrics calculation: {e}")
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in calculate_packing_aggregate_metrics: {e}",
            exc_info=True
        )
        raise RuntimeError(f"Unexpected error calculating aggregate metrics: {e}") from e

if __name__ == "__main__":
    try:
        TODAY = constant.get_today()

        # Extract CDHDR data
        logger.info("Starting packing extraction workflow")
        extract_cdhdr(TODAY, "packing", "packing")
        logger.info("Extraction of CDHDR was successfully")

        # Converting and renaming CDHDR file
        logger.info("Converting and renaming packing file")
        try:
            convert_to_csv("packing", "packing")
            rename("packing", "packing", constant.CDHDR_DF)
            logger.info("File conversion and renaming completed successfully")
        except Exception as e:
            logger.error(f"Error converting/renaming packing file: {e}", exc_info=True)
            raise

        # Combining CDHDR file with users
        logger.info("File was successfully transformed, now combining the file with the users file")
        combined = combine()

        # Prepare CDHDR data
        cdhdr = prepare_cdhdr_data(combined)

        # Calculate grouped metrics
        try:
            logger.info("Calculating grouped metrics: packing per user by floor")
            
            # Validate required columns exist before grouping
            required_groupby_columns = ["user", "floor"]
            missing_columns = [col for col in required_groupby_columns if col not in cdhdr.columns]
            
            if missing_columns:
                error_msg = f"Cannot calculate grouped metrics: missing required columns {missing_columns}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.debug(f"Grouping by columns: {required_groupby_columns}")
            
            # Check for empty dataframe
            if cdhdr.empty:
                logger.warning("CDHDR dataframe is empty, groupby will return empty result")
                packing_per_user = pd.Series(dtype='int64', name='count')
            else:
                # Check for null values in grouping columns
                null_counts = {}
                for col in required_groupby_columns:
                    null_count = cdhdr[col].isna().sum()
                    if null_count > 0:
                        null_counts[col] = null_count
                        logger.warning(
                            f"Found {null_count} null values ({null_count/len(cdhdr)*100:.1f}%) "
                            f"in grouping column '{col}'"
                        )
                
                # Perform groupby operation
                try:
                    packing_per_user = cdhdr.groupby(required_groupby_columns).size()
                    
                    # Validate result
                    if packing_per_user.empty:
                        logger.warning("Groupby result is empty - no data matches grouping criteria")
                    else:
                        # Log summary statistics
                        total_groups = len(packing_per_user)
                        total_packing = packing_per_user.sum()
                        min_packing = packing_per_user.min()
                        max_packing = packing_per_user.max()
                        mean_packing = packing_per_user.mean()
                        
                        logger.info(
                            f"Groupby completed successfully: "
                            f"{total_groups} unique groups, "
                            f"{total_packing} total packing, "
                            f"range: {min_packing}-{max_packing} packing per group, "
                            f"mean: {mean_packing:.1f} packing per group"
                        )
                        
                        # Log distribution by floor
                        if "floor" in packing_per_user.index.names:
                            floor_counts = packing_per_user.groupby(level="floor").sum()
                            logger.debug(f"Packing by floor: {dict(floor_counts)}")
                        
                        # Log top groups
                        top_groups = packing_per_user.nlargest(10)
                        logger.debug(f"Top 10 groups by packing count:\n{top_groups}")
                
                except KeyError as e:
                    error_msg = f"Column error during groupby operation: {e}"
                    logger.error(error_msg)
                    raise ValueError(error_msg) from e
                except Exception as e:
                    error_msg = f"Unexpected error during groupby operation: {e}"
                    logger.error(error_msg, exc_info=True)
                    raise RuntimeError(error_msg) from e
            
            logger.debug(f"Grouped metrics calculation complete. Result type: {type(packing_per_user)}")
            
        except ValueError as e:
            logger.error(f"Failed to calculate grouped metrics: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calculating grouped metrics: {e}", exc_info=True)
            raise

        # Calculate hourly productivity
        nested_dict, total_hours = calculate_packing_hourly_productivity(cdhdr)

        # Calculate aggregate metrics
        calculate_packing_aggregate_metrics(nested_dict, total_hours, packing_per_user)

        # Convert nested dict to regular dict for JSON serialization
        try:
            logger.info("Converting nested defaultdict to regular dict for JSON serialization")
            
            # Validate nested_dict
            if not nested_dict:
                logger.warning("nested_dict is empty, result will be empty")
                result = {}
            else:
                # Count structure depth and size for logging
                total_users = len(nested_dict)
                total_floors = sum(len(floors) for floors in nested_dict.values())
                total_hours_entries = sum(
                    len(hours) 
                    for floors in nested_dict.values() 
                    for hours in floors.values()
                )
                
                logger.debug(
                    f"Converting structure: {total_users} users, {total_floors} floors, "
                    f"{total_hours_entries} hour entries"
                )
                
                # Convert nested defaultdict to regular dict
                try:
                    result = {
                        k: {
                            k2: dict(v2) if isinstance(v2, dict) else v2
                            for k2, v2 in v.items()
                        }
                        for k, v in nested_dict.items()
                    }
                    
                    # Validate conversion
                    if not result:
                        logger.warning("Conversion resulted in empty dictionary")
                    else:
                        # Verify structure was preserved
                        converted_users = len(result)
                        if converted_users != total_users:
                            logger.warning(
                                f"User count mismatch after conversion: "
                                f"expected {total_users}, got {converted_users}"
                            )
                        
                        logger.info(
                            f"Successfully converted nested dict: {converted_users} users, "
                            f"{len(result)} top-level entries"
                        )
                
                except TypeError as e:
                    error_msg = f"Type error during dict conversion: {e}"
                    logger.error(error_msg)
                    raise ValueError(error_msg) from e
                except Exception as e:
                    error_msg = f"Error converting nested dict structure: {e}"
                    logger.error(error_msg, exc_info=True)
                    raise RuntimeError(error_msg) from e
            
            # Validate result can be serialized
            try:
                import json
                json.dumps(result)
                logger.debug("Converted dict passed JSON serialization validation")
            except TypeError as e:
                error_msg = f"Converted dict contains non-serializable objects: {e}"
                logger.error(error_msg)
                raise TypeError(error_msg) from e
            except Exception as e:
                logger.warning(f"Unexpected error during serialization validation: {e}")
        
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting nested dict: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in dict conversion: {e}", exc_info=True)
            raise

        # Save
        convert_to_json("packing", "packing", result)

        logger.info("Packing extraction workflow completed successfully")

    except Exception as e:
        logger.error(f"Packing extraction workflow failed: {e}", exc_info=True)
        raise