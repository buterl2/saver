from typing import Any, Optional, Dict, List, Tuple
from data_script.utils.SAP import SAPSession
import data_script.config.constants as constant
from data_script.utils.logger import setup_logger
from data_script.utils.retry import retry_sap_operation
from data_script.transformation.routes import transform_routes
from data_script.utils.files_utils import convert_to_csv, rename, convert_to_json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Set up logger
logger = setup_logger("picking_extraction")

def _extract_ltap_internal(date: str, folder: str, filename: str) -> None:
    """Internal extraction function (called by retry wrapper)"""
    logger.info(f"Starting LTAP extraction for date: {date}, filename: {filename}, folder: {folder}")

    # Initialize SAP GUI
    extractor = SAPSession()

    # Start transaction and fill in fields
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.table("LTAP")
    extractor.checkbox_selection(constant.LTAP_CHECKBOX)
    extractor.findById("wnd[0]/usr/ctxtI1-LOW").text = constant.WAREHOUSE
    extractor.findById("wnd[0]/usr/ctxtI7-LOW").text = date
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()
    logger.info("Transaction executed successfully")

    # Save
    extractor.save_to_folder(folder, filename)
    logger.info(f"Data saved to {filename}")

def _extract_hutolink_(transaction: str, folder: str, filename: str) -> None:
    """Internal extraction function (called by retry wrapper)"""
    logger.info(f"Starting {transaction} extraction, filename: {filename}, folder: {folder}")

    # Initialize SAP
    extractor = SAPSession()

    # Start transaction and fill in fields
    extractor.StartTransaction("Z_TABU_DIS")
    extractor.table(transaction)
    extractor.checkbox_selection(constant.HUTOLINK_CHECKBOX)
    extractor.findById('wnd[0]/usr/ctxtI1-LOW').text = constant.WAREHOUSE
    extractor.findById("wnd[0]/usr/btn%_I5_%_APP_%-VALU_PUSH").press()
    extractor.findById("wnd[1]/tbar[0]/btn[23]").press()
    extractor.findById("wnd[2]/usr/ctxtDY_PATH").text = f"{constant.OUTPUT_PATH}/{folder}"
    extractor.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "picking_deliveries.csv"
    extractor.findById("wnd[2]/tbar[0]/btn[0]").press()
    extractor.findById("wnd[1]/tbar[0]/btn[8]").press()
    extractor.findById("wnd[0]/tbar[1]/btn[8]").press()

    # Save to folder
    extractor.save_to_folder(folder, filename)
    logger.info(f"Data saved to {filename}")

def extract_hutolink(transaction: str, folder: str, filename: str) -> None:
    """
    Extract HUTOLINK data for picking productivity with automatic retry

    Args:
        transaction: Used transaction for the extraction
        folder: Output folder
        filename: Output filename
    """
    retry_sap_operation(
        lambda: _extract_hutolink_(transaction, folder, filename),
        func_name="extract_hutolink"
    )

def extract_ltap(date: str, folder: str, filename: str) -> None:
    """
    Extract LTAP data for picking productivity with automatic retry
    
    Args:
        date: Date string for the extraction
        folder: Ouput folder
        filename: Output filename
    """
    retry_sap_operation(
        lambda: _extract_ltap_internal(date, folder, filename),
        func_name="extract_ltap"
    )

def retrieve_deliveries() -> None:
    """Internal retrieving function (called by retry wrapper)"""
    # Convert and rename the picking file
    convert_to_csv("picking", "picking")
    rename("picking", "picking", constant.LTAP_DF)

    # Retrieve deliveries
    try:
        logger.debug(f"Reading picking.csv")

        # Read CSV file
        try:
            df = pd.read_csv(f"{constant.OUTPUT_PATH}/picking/picking.csv", encoding="utf-8")
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            logger.warning(f"UTF-8 encoding failed for picking.csv, trying latin-1")
            df = pd.read_csv(f"{constant.OUTPUT_PATH}/picking/picking.csv", encoding="latin-1")

        df["delivery"] = df["delivery"].fillna(0).astype(int)
        deliveries = df["delivery"].drop_duplicates()
        deliveries.to_csv(f"{constant.OUTPUT_PATH}/picking/picking_deliveries.csv", index=False)
        logger.info(f"Successfully retrieved {len(deliveries)} deliveries")
    except Exception as e:
        error_msg = f"Error retrieveing deliveries: {e}"
        logger.error(error_msg)
        raise

def combine() -> pd.DataFrame:
    """
    Combine HUTOLINK files with routes data.

    Reads zorf_hu_to_link.csv, zorf_huto_lnkhis.csv, and routes.csv,
    concatenates the first two, merges with routes, and removes duplicates.

    Returns:
        DataFrame: Combined dataframe with merged route information

    Raises:
        FileNotFoundError: If any required file is missing
        KeyError: if required columns don't exist
        ValueError: If merge/concat operations fail
    """
    logger.info("Starting to combine HUTOLINK files with routes")

    file_paths = {
        "zorf_hu_to_link": f"{constant.OUTPUT_PATH}/picking/zorf_hu_to_link.csv",
        "zorf_huto_lnkhis": f"{constant.OUTPUT_PATH}/picking/zorf_huto_lnkhis.csv",
        "routes": f"{constant.OUTPUT_PATH}/misc/routes.csv"
    }

    # Validate files exist
    for name, path in file_paths.items():
        if not Path(path).exists():
            error_msg = f"Required file not found: {name} at {path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        logger.debug(f"Found {name} file: {path}")

    try:
        # Read first file
        logger.debug("Reading zorf_hu_to_link.csv")
        try:
            df1 = pd.read_csv(file_paths["zorf_hu_to_link"], encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for zorf_hu_to_link.csv, trying latin-1")
            df1 = pd.read_csv(file_paths["zorf_hu_to_link"], encoding="latin-1")

        logger.debug(f"zorf_hu_to_link.csv: {len(df1)} rows, {len(df1.columns)} columns")
        logger.debug(f"Columns: {list(df1.columns)}")

        # Read second file
        logger.debug("Reading zorf_huto_lnkhis.csv")
        try:
            df2 = pd.read_csv(file_paths["zorf_huto_lnkhis"], encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for zorf_huto_lnkhis.csv, trying latin-1")
            df2 = pd.read_csv(file_paths["zorf_huto_lnkhis"], encoding="latin-1")

        logger.debug(f"zorf_huto_lnkhis.csv: {len(df2)} rows, {len(df2.columns)} columns")
        logger.debug(f"Columns: {list(df2.columns)}")

        # Read routes file
        logger.debug("Reading routes.csv")
        try:
            df3 = pd.read_csv(file_paths["routes"], encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for routes.csv, trying latin-1")
            df3 = pd.read_csv(file_paths["routes"], encoding="latin-1")

        logger.debug(f"routes.csv: {len(df3)} rows, {len(df3.columns)} columns")
        logger.debug(f"Columns: {list(df3.columns)}")

        # Validate required columns exist
        required_cols_df1_df2 = ["route", "document"]
        required_cols_df3 = ["route"]

        for col in required_cols_df1_df2:
            if col not in df1.columns:
                error_msg = f"Required column '{col}' not found in zorf_hu_to_link.csv. Available columns: {list(df1.columns)}"
                logger.error(error_msg)
                raise KeyError(error_msg)
            if col not in df2.columns:
                error_msg = f"Required column '{col}' not found in zorf_huto_lnkhis.csv. Available columns: {list(df1.columns)}"
                logger.error(error_msg)
                raise KeyError(error_msg)

        if "route" not in df3.columns:
            error_msg = f"Required column 'route' not found in routes.csv. Available columns: {list(df3.columns)}"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        logger.debug("All required columns validated")

        # Concatenate the two HUTOLINK dataframes
        logger.info("Concatenating zorf_hu_to_link and zorf_huto_lnkhis")
        try:
            combined = pd.concat([df1, df2], ignore_index=True)
            logger.info(f"Successfully concatenated: {len(combined)} total rows (df1: {len(df1)}, df2: {len(df2)})")
        except Exception as e:
            error_msg = f"Failed to concatenate dataframes: {e}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

        # Merge with routes
        logger.info("Merging combined data with routes")
        try:
            before_merge_count = len(combined)
            combined = combined.merge(df3, on="route", how="left")
            after_merge_count = len(combined)

            # Check how many rows got route information
            routes_matched = combined["route"].notna().sum() if "route" in combined.columns else 0
            routes_unmatched = combined["route"].isna().sum() if "route" in combined.columns else 0

            logger.info(f"Merge completed: {after_merge_count} rows (before: {before_merge_count})")
            logger.info(f"Routes matched: {routes_matched}, Routes unmatched: {routes_unmatched}")
        except Exception as e:
            error_msg = f"Failed to merge with routes: {e}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e

        # Drop duplicates
        logger.info("Removing duplicates based on 'document' column")
        try:
            before_dedup_count = len(combined)
            combined = combined.drop_duplicates(subset="document", keep="first")
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
        error_msg = f"Unexcepted error during combine operation: {e}"
        logger.error(error_msg, exc_info=True)
        raise

def build_floor_mapping(floors_config: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Build floor mapping from configuration dictionary.

    Args:
        floors_config: Dictionary mapping floor names to lists of area codes

    Returns:
        Dictionary: mapping area codes to floor names

    Raises:
        ValueError: If floors_config is invalid or empty
    """
    floor_mapping: Dict[str, str] = {}

    try:
        # Validate input
        if not floors_config:
            logger.error("FLOORS configuration is empty or None")
            raise ValueError("FLOORS configuration cannot be empty")
        
        if not isinstance(floors_config, dict):
            logger.error(f"FLOORS configuration must be a dict, got {type(floors_config)}")
            raise ValueError(f"FLOORS configuration must be a dict, got {type(floors_config)}")

        logger.debug(f"Building floor mapping from {len(floors_config)} floors")

        # Build mapping with validation
        for floor, areas in floors_config.items():
            try:
                # Validate floor name
                if not floor or not isinstance(floor, str):
                    logger.warning(f"Invalid floor name: {floor}, skipping")
                    continue

                # Validate areas list
                if not areas:
                    logger.warning(f"No areas defined for floor '{floor}', skipping")
                    continue

                if not isinstance(areas, list):
                    logger.warning(f"Areas for floor '{floor}' must be a list, got {type(areas)}, skipping")
                    continue

                # Process each area
                for area in areas:
                    try:
                        if not areas or not isinstance(area, str):
                            logger.warning(f"Invalid area '{area}' for floor '{floor}', skipping")
                            continue

                        area = area.strip()
                        if not area:
                            logger.warning(f"Empty area string for floor '{floor}', skipping")
                            continue

                        # Check for duplicates
                        if area in floor_mapping:
                            logger.warning(
                                f"Area '{area}' is already mapped to '{floor_mapping[area]}', "
                                f"overwriting with '{floor}'"
                            )

                        floor_mapping[area] = floor
                        logger.debug(f"Mapped aread '{area}' to floor '{floor}'")

                    except Exception as e:
                        logger.error(f"Error processing floor '{floor}': {e}")
                        continue
                
            except Exception as e:
                logger.erro(f"Error processing floor '{floor}': {e}")
                continue

        # Validate result
        if not floor_mapping:
            logger.error("Floor mapping is empty after processing")
            raise ValueError("No valid floor mappings could be created")

        logger.info(f"Successfully built floor mapping with {len(floor_mapping)} area-to-floor mappings")
        logger.debug(f"Floor mapping covers {len(set(floor_mapping.values()))} unique floors")

        return floor_mapping

    except ValueError as e:
        logger.error(f"Failed to build floor mapping: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error building floor mapping: {e}", exc_info=True)
        raise ValueError(f"Unexpected error building floor mapping: {e}") from e

def prepare_ltap_data(combined: pd.DataFrame, floor_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Prepare LTAP data by loading, transforming, and enriching with route/floor information.

    Args:
        combined: DataFrame with route information merged from HUTOLINK data
        floor_mapping: Dictionary mapping picking areas to floor names
    
    Returns:
        Processed DataFrame with flow, floor, and hour columns added
    
    Raises:
        FileNotFoundError: If the LTAP CSV file doesn't exist
        ValueError: If required columns are missing or data is invalid
        KeyError: If floor_mapping is missing required areas
    """
    file_path = f"{constant.OUTPUT_PATH}/picking/picking.csv"

    try:
        logger.info(f"Loading LTAP data from {file_path}")

        # Load CSV with error handling
        try:
            ltap: pd.DataFrame = pd.read_csv(file_path, encoding="utf-8")
            logger.debug(f"Successfully loaded LTAP data: {ltap.shape[0]} rows, {ltap.shape[1]} columns")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed, trying latin-1")
            try:
                ltap = pd.read_csv(file_path, encoding="latin-1")
                logger.debug(f"Successfully loaded LTAP data with latin-1: {ltap.shape[0]} rows")
            except Exception as e:
                logger.error(f"Failed to load LTAP CSV file: {e}")
                raise FileNotFoundError(f"Could not read LTAP file at {file_path}") from e
        except FileNotFoundError:
            logger.error(f"LTAP file not found at {file_path}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading LTAP file: {e}", exc_info=True)
            raise

        # Validate required columns exist
        required_columns = ["actual_quantity", "delivery", "picking_area", "confirmation_time"]
        missing_columns = [col for col in required_columns if col not in ltap.columns]
        if missing_columns:
            logger.error(f"Missing required columns in LTAP data: {missing_columns}")
            raise ValueError(f"Missing required columns: {missing_columns}")

        logger.debug(f"LTAP data containes columns: {list(ltap.columns)}")

        # Convert actual_quantity to numeric
        try:
            initial_nulls = ltap["actual_quantity"].isna().sum()
            ltap["actual_quantity"] = pd.to_numeric(
                ltap["actual_quantity"],
                errors="coerce"
            ).fillna(0).astype(int)
            converted_nulls = (ltap["actual_quantity"] == 0).sum() - initial_nulls
            if converted_nulls > 0:
                logger.warning(f"Converted {converted_nulls} null/invalid actual_quantity values to 0")
            logger.debug(f"Converted actual_quantity to int: {ltap["actual_quantity"].dtype}")
        except Exception as e:
            logger.error(f"Error converting actual_quantity to numberic: {e}")
            raise ValueError(f"Failed to convert actual_quantity columns: {e}") from e

        # Convert delivery to int
        try:
            initial_nulls = ltap["delivery"].isna().sum()
            ltap["delivery"] = ltap["delivery"].fillna(0).astype(int)
            if initial_nulls > 0:
                logger.warning(f"Converted {initial_nulls} null delivery values to 0")
            logger.debug(f"Converted delivery to int: {ltap["delivery"].dtype}")
        except Exception as e:
            logger.error(f"Error converting delivery to int: {e}")
            raise ValueError(f"Failed to convert delivery column: {e}") from e

        # Merge with combined dataframe
        try:
            if combined.empty:
                logger.warning("Combined dataframe is empty, merge will result in all NaN values")

            initial_rows = len(ltap)
            ltap = ltap.merge(combined, left_on="delivery", right_on="document", how="left")

            merged_rows = len(ltap)
            if merged_rows != initial_rows:
                logger.warning(f"Row count changed after merge: {initial_rows} -> {merged_rows}")

            unmatched = ltap["document"].isna().sum()
            if unmatched > 0:
                logger.warning(f"{unmatched} deliveries ({unmatched/initial_rows*100:.1f}%) have not matching route information")

            logger.debug(f"Successfully merged with combined data: {merged_rows} rows")
        except KeyError as e:
            logger.error(f"Missing column for merge: {e}")
            raise ValueError(f"Required column for merge not found: {e}") from e
        except Exception as e:
            logger.error(f"Error durring merge operation: {e}", exc_info=True)
            raise

        # Filter out unknown flows
        try:
            initial_rows = len(ltap)
            ltap["flow"] = ltap["flow"].fillna("unknown")
            unknown_count = (ltap["flow"] == "unknown").sum()

            if unknown_count > 0:
                logger.warning(f"Found {unknown_count} rows ({unknown_count/initial_rows*100:.1f}%) with unknown flow")

            ltap = ltap[ltap["flow"] != "unknown"].copy()
            filtered_rows = len(ltap)
            removed_rows = initial_rows - filtered_rows

            if removed_rows > 0:
                logger.info(f"Filtered out {removed_rows} rows with unknown flow. Remaining: {filtered_rows} rows")
            else:
                logger.debug("No rows with unknown flow found")
        except Exception as e:
            logger.error(f"Error filtering unknown flows: {e}")
            raise

        # Transform flow values
        try:
            y2_count = (ltap["flow"] == "y2").sum()
            if y2_count > 0:
                ltap["flow"] = ltap["flow"].replace("y2", "a_flow")
                logger.debug(f"Replaced {y2_count} 'y2' flow values with 'a_flow'")
        except Exception as e:
            logger.error(f"Error replacing flow values: {e}")
            raise

        # Map picking_area to floor using floor_mapping
        try:
            if not floor_mapping:
                logger.error("Floor mapping is empty")
                raise ValueError("Floor mapping cannot be empty")

            # Check for unmapped picking areas
            unique_areas = ltap["picking_area"].dropna().unique()
            unmapped_areas = [area for area in unique_areas if area not in floor_mapping]

            if unmapped_areas:
                logger.warning(
                    f"Found {len(unmapped_areas)} unmapped picking areas: {unmapped_areas[:10]}"
                )
                unmapped_count = ltap["picking_area"].isin(unmapped_areas).sum()
                logger.warning(f"{unmapped_count} rows ({unmapped_count/len(ltap)*100:.1f}%) have unmapped picking areas")

            ltap["floor"] = ltap["picking_area"].map(floor_mapping)

            # Check how many rows got a floor mapping
            mapped_count = ltap["floor"].notna().sum()
            unmapped_count = ltap["floor"].isna().sum()

            logger.info(
                f"Floor mapping complete: {mapped_count} rows mapped ({mapped_count/len(ltap)*100:.1f}%), "
                f"{unmapped_count} rows unmapped ({unmapped_count/len(ltap)*100:.1f}%)"
            )

            if unmapped_count > 0:
                # log some examples for unmapped areas
                unmapped_examples = ltap[ltap["floor"].isna()]["picking_area"].value_counts().head(5)
                logger.debug(f"Top unmapped picking areas: {dict(unmapped_examples)}")

        except KeyError as e:
            logger.error(f"Missing column for floor mapping: {e}")
            raise ValueError(f"Required column 'picking_area' not found: {e}") from e
        except Exception as e:
            logger.error(f"Error mapping picking areas to floors: {e}", exc_info=True)
            raise

        # Extract hour from confirmation_time
        try:
            if "confirmation_time" not in ltap.columns:
                logger.error("confirmation_time column not found")
                raise ValueError("confirmation_time column is required")

            # Check for null/empty confirmation times
            null_times = ltap["confirmation_time"].isna().sum()
            if null_times > 0:
                logger.warning(f"Found {null_times} rows with null confirmation_time")

            # Extract hour
            ltap["hour"] = ltap["confirmation_time"].str.slice(0, 2)

            # Validate hour format
            invalid_hours = ltap["hour"].str.match(r'^\d{2}$', na=False).sum()
            valid_hours = ltap["hour"].notna().sum() - invalid_hours

            if invalid_hours < len(ltap) - null_times:
                logger.warning(
                    f"Some hours may be invalid format. "
                    f"Valid: {valid_hours}, invalid/Null: {len(ltap) - valid_hours}"
                )

            logger.debug(f"Extracted hour from confirmation_time for {valid_hours} rows")

        except Exception as e:
            logger.error(f"Error extracting hour from confirmation_time: {e}", exc_info=True)
            raise

        # Final validation
        logger.info(
            f"LTAP data preparation complete: {len(ltap)} rows, {len(ltap.columns)} columns. "
            f"Flows: {ltap["flow"].nunique()} unique, floors: {ltap["floor"].notna().sum()} mapped"
        )

        return ltap

    except (FileNotFoundError, ValueError, KeyError) as e:
        logger.error(f"Failed to prepare LTAP data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prepare_ltap_data: {e}", exc_info=True)
        raise RuntimeError(f"Unexpected error preparing LTAP data: {e}") from e

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

def calculate_picking_hourly_productivity(ltap: pd.DataFrame) -> Tuple[Dict[str, Dict[str, Dict[str, Dict[str, Any]]]], Dict[str, Dict[str, Dict[str, int]]]]:
    """
    Calculate hourly productivity metrics for picking operations.
    
    Groups data by user, floor, flow, and hour, then calculates adjusted counts
    accounting for breaks and assigns productivity colors based on thresholds.
    
    Args:
        ltap: DataFrame with columns: user, floor, flow, hour
        
    Returns:
        Tuple containing:
            - nested_dict: Dictionary with productivity data by user/floor/flow/hour
            - total_hours: Dictionary tracking total hours worked by user/floor/flow
            
    Raises:
        ValueError: If required columns are missing or config values are invalid
        KeyError: If floor not found in PRODUCTIVITY_THRESHOLDS
        ZeroDivisionError: If break multiplier is zero
    """
    try:
        logger.info("Starting hourly productivity calculation for picking operations")
        
        # Validate required columns
        required_columns = ["user", "floor", "flow", "hour"]
        missing_columns = [col for col in required_columns if col not in ltap.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns for productivity calculation: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check for empty dataframe
        if ltap.empty:
            logger.warning("LTAP dataframe is empty, returning empty productivity results")
            return {}, {}
        
        # Validate config values exist
        try:
            breaks_config = constant.BREAKS if hasattr(constant, 'BREAKS') else {}
            thresholds_config = constant.PRODUCTIVITY_THRESHOLDS if hasattr(constant, 'PRODUCTIVITY_THRESHOLDS') else {}
            
            if not breaks_config:
                logger.warning("BREAKS configuration not found, break adjustments will be skipped")
            if not thresholds_config:
                error_msg = "PRODUCTIVITY_THRESHOLDS configuration not found"
                logger.error(error_msg)
                raise ValueError(error_msg)
        except AttributeError as e:
            logger.error(f"Configuration error: {e}")
            raise ValueError(f"Missing required configuration: {e}") from e
        
        # Check for null values in grouping columns
        null_counts = {}
        for col in required_columns:
            null_count = ltap[col].isna().sum()
            if null_count > 0:
                null_counts[col] = null_count
                logger.warning(
                    f"Found {null_count} null values ({null_count/len(ltap)*100:.1f}%) "
                    f"in column '{col}'"
                )
        
        # Perform groupby operation
        try:
            logger.debug("Grouping data by user, floor, flow, and hour")
            lines_per_hour = ltap.groupby(required_columns).size()
            
            if lines_per_hour.empty:
                logger.warning("Groupby result is empty - no data matches grouping criteria")
                return {}, {}
            
            total_groups = len(lines_per_hour)
            total_lines = lines_per_hour.sum()
            logger.info(
                f"Groupby completed: {total_groups} unique groups, {total_lines} total lines"
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
        nested_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        total_hours = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        # Track statistics
        break_adjustments = 0
        missing_thresholds = 0
        invalid_floors = set()
        processed_groups = 0
        error_groups = 0
        
        # Process each group
        logger.debug("Processing groups and calculating productivity metrics")
        for (user, floor, flow, hour), count in lines_per_hour.items():
            try:
                processed_groups += 1
                
                # Validate inputs
                if pd.isna(user) or pd.isna(floor) or pd.isna(flow) or pd.isna(hour):
                    logger.debug(f"Skipping group with null values: user={user}, floor={floor}, flow={flow}, hour={hour}")
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
                            total_hours[user][floor][flow] += 1
                        else:
                            adjusted_count = count / break_multiplier
                            total_hours[user][floor][flow] += break_multiplier
                            break_adjustments += 1
                            logger.debug(
                                f"Applied break adjustment for hour {hour_str}: "
                                f"{count} -> {adjusted_count:.2f} (multiplier: {break_multiplier})"
                            )
                    else:
                        adjusted_count = count
                        total_hours[user][floor][flow] += 1
                
                except ZeroDivisionError as e:
                    logger.error(f"Division by zero error for hour '{hour_str}': {e}")
                    adjusted_count = count
                    total_hours[user][floor][flow] += 1
                except Exception as e:
                    logger.error(f"Error calculating break adjustment: {e}")
                    adjusted_count = count
                    total_hours[user][floor][flow] += 1
                
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
                            # Check if get_productivity_color function exists
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
                nested_dict[user][floor][flow][hour_str] = {
                    "count": int(count),
                    "productivity_color": color
                }
                
            except Exception as e:
                error_groups += 1
                logger.error(
                    f"Error processing group (user={user}, floor={floor}, flow={flow}, hour={hour}): {e}",
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
        unique_flows = set()
        for user_data in nested_dict.values():
            unique_floors.update(user_data.keys())
            for floor_data in user_data.values():
                unique_flows.update(floor_data.keys())
        
        logger.debug(
            f"Result summary: {unique_users} users, {len(unique_floors)} floors, "
            f"{len(unique_flows)} flows"
        )
        
        return nested_dict, total_hours
        
    except ValueError as e:
        logger.error(f"Validation error in productivity calculation: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in calculate_picking_hourly_productivity: {e}", exc_info=True)
        raise RuntimeError(f"Unexpected error calculating productivity: {e}") from e

def calculate_picking_aggregate_metrics(
    ltap: pd.DataFrame, 
    nested_dict: Dict[str, Dict[str, Dict[str, Any]]], 
    total_hours: Dict[str, Dict[str, Dict[str, int]]], 
    lines_per_user: pd.Series
) -> None:
    """
    Calculate aggregate productivity metrics and update nested dictionary.
    
    Calculates hours worked, productivity, items picked, ratio, and assigns
    productivity colors for each user/floor/flow combination.
    
    Args:
        ltap: DataFrame with picking data (must contain: user, floor, flow, actual_quantity)
        nested_dict: Dictionary to update with aggregate metrics (modified in place)
        total_hours: Dictionary with hours worked by user/floor/flow
        lines_per_user: Series with lines picked grouped by user/floor/flow
        
    Raises:
        ValueError: If required columns are missing or data is invalid
        KeyError: If floor not found in thresholds or missing keys in dictionaries
    """
    try:
        logger.info("Starting aggregate metrics calculation for picking productivity")
        
        # Validate inputs
        if ltap.empty:
            logger.warning("LTAP dataframe is empty, no aggregate metrics to calculate")
            return
        
        if lines_per_user.empty:
            logger.warning("lines_per_user Series is empty, no metrics to calculate")
            return
        
        if not nested_dict:
            logger.warning("nested_dict is empty, will create new entries")
        
        if not total_hours:
            logger.warning("total_hours dictionary is empty, all hours_worked will be 0")
        
        # Validate required columns in ltap
        required_columns = ["user", "floor", "flow", "actual_quantity"]
        missing_columns = [col for col in required_columns if col not in ltap.columns]
        if missing_columns:
            error_msg = f"Missing required columns in ltap: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate config
        try:
            thresholds_config = constant.PRODUCTIVITY_THRESHOLDS if hasattr(constant, 'PRODUCTIVITY_THRESHOLDS') else {}
            if not thresholds_config:
                error_msg = "PRODUCTIVITY_THRESHOLDS configuration not found"
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
        
        total_groups = len(lines_per_user)
        logger.info(f"Processing {total_groups} user/floor/flow combinations")
        
        # Process each group
        for (user, floor, flow), lines_picked in lines_per_user.items():
            try:
                processed_count += 1
                
                # Validate group key values
                if pd.isna(user) or pd.isna(floor) or pd.isna(flow):
                    logger.debug(
                        f"Skipping group with null values: user={user}, floor={floor}, flow={flow}"
                    )
                    error_count += 1
                    continue
                
                # Convert to strings and strip whitespace
                user_str = str(user).strip() if not pd.isna(user) else None
                floor_str = str(floor).strip() if not pd.isna(floor) else None
                flow_str = str(flow).strip() if not pd.isna(flow) else None
                
                if not all([user_str, floor_str, flow_str]):
                    logger.debug(f"Skipping group with empty values: user={user_str}, floor={floor_str}, flow={flow_str}")
                    error_count += 1
                    continue
                
                # Validate lines_picked
                if pd.isna(lines_picked) or lines_picked <= 0:
                    logger.warning(
                        f"Invalid lines_picked value ({lines_picked}) for "
                        f"user={user_str}, floor={floor_str}, flow={flow_str}"
                    )
                    error_count += 1
                    continue
                
                # Get hours worked
                try:
                    hours_worked = total_hours.get(user_str, {}).get(floor_str, {}).get(flow_str, 0)
                    
                    if hours_worked == 0:
                        missing_hours_count += 1
                        logger.debug(
                            f"No hours worked data for user={user_str}, floor={floor_str}, flow={flow_str}"
                        )
                except (KeyError, TypeError) as e:
                    logger.warning(
                        f"Error accessing hours_worked for user={user_str}, floor={floor_str}, flow={flow_str}: {e}"
                    )
                    hours_worked = 0
                    missing_hours_count += 1
                
                # Calculate productivity
                try:
                    if hours_worked > 0:
                        productivity = lines_picked / hours_worked
                    else:
                        productivity = 0
                        zero_productivity_count += 1
                        logger.debug(
                            f"Zero hours worked for user={user_str}, floor={floor_str}, flow={flow_str}, "
                            f"productivity set to 0"
                        )
                except ZeroDivisionError:
                    logger.warning(
                        f"Division by zero error for user={user_str}, floor={floor_str}, flow={flow_str}"
                    )
                    productivity = 0
                    zero_productivity_count += 1
                except Exception as e:
                    logger.error(f"Error calculating productivity: {e}")
                    productivity = 0
                
                # Calculate items picked
                try:
                    filter_mask = (
                        (ltap["user"] == user_str) & 
                        (ltap["floor"] == floor_str) & 
                        (ltap["flow"] == flow_str)
                    )
                    items_picked = ltap.loc[filter_mask, "actual_quantity"].sum()
                    
                    # Handle NaN result
                    if pd.isna(items_picked):
                        items_picked = 0
                        logger.debug(
                            f"No items found for user={user_str}, floor={floor_str}, flow={flow_str}"
                        )
                    else:
                        items_picked = float(items_picked)
                
                except KeyError as e:
                    logger.error(
                        f"Column error calculating items_picked for user={user_str}, "
                        f"floor={floor_str}, flow={flow_str}: {e}"
                    )
                    items_picked = 0
                except Exception as e:
                    logger.error(
                        f"Error calculating items_picked for user={user_str}, "
                        f"floor={floor_str}, flow={flow_str}: {e}"
                    )
                    items_picked = 0
                
                # Calculate ratio
                try:
                    if lines_picked > 0:
                        ratio = items_picked / lines_picked
                    else:
                        ratio = 0
                        logger.debug(
                            f"Zero lines_picked for user={user_str}, floor={floor_str}, flow={flow_str}, "
                            f"ratio set to 0"
                        )
                except ZeroDivisionError:
                    logger.warning(
                        f"Division by zero error calculating ratio for "
                        f"user={user_str}, floor={floor_str}, flow={flow_str}"
                    )
                    ratio = 0
                except Exception as e:
                    logger.error(f"Error calculating ratio: {e}")
                    ratio = 0
                
                # Get productivity color
                try:
                    if floor_str not in thresholds_config:
                        missing_thresholds_count += 1
                        invalid_floors.add(floor_str)
                        logger.warning(
                            f"No productivity thresholds found for floor '{floor_str}', "
                            f"using default color for user={user_str}, flow={flow_str}"
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
                    if flow_str not in nested_dict[user_str][floor_str]:
                        nested_dict[user_str][floor_str][flow_str] = {}
                except Exception as e:
                    logger.error(f"Error creating nested_dict structure: {e}")
                    error_count += 1
                    continue
                
                # Update nested dictionary
                try:
                    nested_dict[user_str][floor_str][flow_str]["hours_worked"] = int(hours_worked)
                    nested_dict[user_str][floor_str][flow_str]["productivity"] = round(productivity, 2)
                    nested_dict[user_str][floor_str][flow_str]["productivity_color"] = color
                    nested_dict[user_str][floor_str][flow_str]["items_picked"] = int(items_picked)
                    nested_dict[user_str][floor_str][flow_str]["lines_picked"] = int(lines_picked)
                    nested_dict[user_str][floor_str][flow_str]["ratio"] = round(ratio, 2)
                    
                    logger.debug(
                        f"Updated metrics for user={user_str}, floor={floor_str}, flow={flow_str}: "
                        f"productivity={productivity:.2f}, items={int(items_picked)}, "
                        f"lines={int(lines_picked)}, ratio={ratio:.2f}, color={color}"
                    )
                
                except (ValueError, TypeError) as e:
                    logger.error(
                        f"Error updating nested_dict for user={user_str}, "
                        f"floor={floor_str}, flow={flow_str}: {e}"
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
                    f"Unexpected error processing group (user={user}, floor={floor}, flow={flow}): {e}",
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
                nested_dict[user][floor][flow].get("productivity", 0)
                for user in nested_dict
                for floor in nested_dict[user]
                for flow in nested_dict[user][floor]
                if "productivity" in nested_dict[user][floor][flow]
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
            f"Unexpected error in calculate_picking_aggregate_metrics: {e}",
            exc_info=True
        )
        raise RuntimeError(f"Unexpected error calculating aggregate metrics: {e}") from e

if __name__ == "__main__":
    try:
        TODAY = constant.get_today()

        # Transform routes
        logger.info("Starting picking extraction workflow")
        try:
            transform_routes()
            logger.info("Routes transformation completed successfully")
        except Exception as e:
            logger.warning(f"Routes transformation failed, continuing with extraction: {e}")

        # Extract LTAP data
        extract_ltap(TODAY, "picking", "picking")
        logger.info("Extraction of LTAP was successfully, now retrieving deliveries")

        # Retrieve deliveries from extracted LTAP file
        retrieve_deliveries()

        # Extract HUTOLINK files
        extract_hutolink("ZORF_HU_TO_LINK", "picking", "zorf_hu_to_link")
        extract_hutolink("ZORF_HUTO_LNKHIS", "picking", "zorf_huto_lnkhis")

        # Converting and renaming HUTOLINK files
        logger.info("Converting and renaming both files")
        convert_to_csv("zorf_hu_to_link", "picking")
        convert_to_csv("zorf_huto_lnkhis", "picking")
        rename("zorf_hu_to_link", "picking", constant.HUTOLINK_DF)
        rename("zorf_huto_lnkhis", "picking", constant.HUTOLINK_DF)

        # Combining HUTOLINK files with routes
        logger.info("Both files were successfully transformed now combining them with the routes")
        combined = combine()

        # Floor mapping
        try:
            FLOOR_MAPPING = build_floor_mapping(constant.FLOORS)
        except ValueError as e:
            logger.error(f"Failed to create floor mapping: {e}. Using empty mapping.")
            FLOOR_MAPPING = {}

        # Prepare LTAP data
        ltap = prepare_ltap_data(combined, FLOOR_MAPPING)

        # Calculate grouped metrics
        try:
            logger.info("Calculating grouped metrics: lines per user by floor and flow")
            
            # Validate required columns exist before grouping
            required_groupby_columns = ["user", "floor", "flow"]
            missing_columns = [col for col in required_groupby_columns if col not in ltap.columns]
            
            if missing_columns:
                error_msg = f"Cannot calculate grouped metrics: missing required columns {missing_columns}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.debug(f"Grouping by columns: {required_groupby_columns}")
            
            # Check for empty dataframe
            if ltap.empty:
                logger.warning("LTAP dataframe is empty, groupby will return empty result")
                lines_per_user = pd.Series(dtype='int64', name='count')
            else:
                # Check for null values in grouping columns
                null_counts = {}
                for col in required_groupby_columns:
                    null_count = ltap[col].isna().sum()
                    if null_count > 0:
                        null_counts[col] = null_count
                        logger.warning(
                            f"Found {null_count} null values ({null_count/len(ltap)*100:.1f}%) "
                            f"in grouping column '{col}'"
                        )
                
                # Perform groupby operation
                try:
                    lines_per_user = ltap.groupby(required_groupby_columns).size()
                    
                    # Validate result
                    if lines_per_user.empty:
                        logger.warning("Groupby result is empty - no data matches grouping criteria")
                    else:
                        # Log summary statistics
                        total_groups = len(lines_per_user)
                        total_lines = lines_per_user.sum()
                        min_lines = lines_per_user.min()
                        max_lines = lines_per_user.max()
                        mean_lines = lines_per_user.mean()
                        
                        logger.info(
                            f"Groupby completed successfully: "
                            f"{total_groups} unique groups, "
                            f"{total_lines} total lines, "
                            f"range: {min_lines}-{max_lines} lines per group, "
                            f"mean: {mean_lines:.1f} lines per group"
                        )
                        
                        # Log distribution by floor and flow
                        if "floor" in lines_per_user.index.names:
                            floor_counts = lines_per_user.groupby(level="floor").sum()
                            logger.debug(f"Lines by floor: {dict(floor_counts)}")
                        
                        if "flow" in lines_per_user.index.names:
                            flow_counts = lines_per_user.groupby(level="flow").sum()
                            logger.debug(f"Lines by flow: {dict(flow_counts)}")
                        
                        # Log top groups
                        top_groups = lines_per_user.nlargest(10)
                        logger.debug(f"Top 10 groups by line count:\n{top_groups}")
                
                except KeyError as e:
                    error_msg = f"Column error during groupby operation: {e}"
                    logger.error(error_msg)
                    raise ValueError(error_msg) from e
                except Exception as e:
                    error_msg = f"Unexpected error during groupby operation: {e}"
                    logger.error(error_msg, exc_info=True)
                    raise RuntimeError(error_msg) from e
            
            logger.debug(f"Grouped metrics calculation complete. Result type: {type(lines_per_user)}")
            
        except ValueError as e:
            logger.error(f"Failed to calculate grouped metrics: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calculating grouped metrics: {e}", exc_info=True)
            raise

        # Calculate hourly productivity
        nested_dict, total_hours = calculate_picking_hourly_productivity(ltap)

        # Calculate aggregate metrics
        calculate_picking_aggregate_metrics(ltap, nested_dict, total_hours, lines_per_user)

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
                total_flows = sum(
                    len(flows) 
                    for floors in nested_dict.values() 
                    for flows in floors.values()
                )
                total_hours = sum(
                    len(hours) 
                    for floors in nested_dict.values() 
                    for flows in floors.values() 
                    for hours in flows.values()
                )
                
                logger.debug(
                    f"Converting structure: {total_users} users, {total_floors} floors, "
                    f"{total_flows} flows, {total_hours} hour entries"
                )
                
                # Convert nested defaultdict to regular dict
                try:
                    result = {
                        k: {
                            k2: {
                                k3: dict(v3) if isinstance(v3, dict) else v3
                                for k3, v3 in v2.items()
                            }
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
        convert_to_json("picking", "picking", result)

        logger.info("Picking extraction workflow completed successfully")

    except Exception as e:
        logger.error(f"Picking extraction workflow failed: {e}", exc_info=True)
        raise