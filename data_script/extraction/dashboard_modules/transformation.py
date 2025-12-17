from typing import Dict, Optional
import data_script.config.constants as constant
from data_script.utils.logger import setup_logger
from data_script.utils.files_utils import convert_to_csv, rename
import pandas as pd
from pathlib import Path

# Set up logger
logger = setup_logger("dashboard_transformation")

def extract_bflow_routes() -> None:
    """
    Extract b_flow routes from routes.csv file.
    
    Reads routes.csv, filters for b_flow, and saves to bflow_routes.csv.
    
    Raises:
        FileNotFoundError: If routes.csv doesn't exist
        KeyError: If required columns don't exist
        ValueError: If filtering operations fail
    """
    try:
        logger.info("Starting b_flow routes extraction")
        
        routes_file = f"{constant.OUTPUT_PATH}/misc/routes.csv"
        
        # Validate file exists
        if not Path(routes_file).exists():
            error_msg = f"Required file not found: routes.csv at {routes_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logger.debug(f"Reading routes.csv from {routes_file}")
        
        # Read CSV file
        try:
            routes_df = pd.read_csv(routes_file, encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for routes.csv, trying latin-1")
            routes_df = pd.read_csv(routes_file, encoding="latin-1")
        
        logger.debug(f"routes.csv: {len(routes_df)} rows, {len(routes_df.columns)} columns")
        
        # Validate required columns exist
        if "flow" not in routes_df.columns:
            error_msg = f"Required column 'flow' not found in routes.csv. Available columns: {list(routes_df.columns)}"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        if "route" not in routes_df.columns:
            error_msg = f"Required column 'route' not found in routes.csv. Available columns: {list(routes_df.columns)}"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        # Filter for b_flow
        logger.debug("Filtering for b_flow routes")
        bflow_routes_df = routes_df.loc[routes_df["flow"] == "b_flow", "route"]
        
        bflow_count = len(bflow_routes_df)
        logger.info(f"Found {bflow_count} b_flow routes")
        
        # Save to CSV
        output_file = f"{constant.OUTPUT_PATH}/misc/bflow_routes.csv"
        bflow_routes_df.to_csv(output_file, index=False)
        logger.info(f"Successfully saved b_flow routes to bflow_routes.csv")
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error during b_flow routes extraction: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def extract_deliveries(input_file: str, output_file: str) -> None:
    """
    Extract unique deliveries from a CSV file.
    
    Args:
        input_file: Input CSV filename (relative to dashboard folder)
        output_file: Output CSV filename (relative to dashboard folder)
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        KeyError: If 'delivery' column doesn't exist
        ValueError: If data processing fails
    """
    try:
        logger.info(f"Extracting deliveries from {input_file} to {output_file}")
        
        input_path = f"{constant.OUTPUT_PATH}/dashboard/{input_file}"
        
        # Validate file exists
        if not Path(input_path).exists():
            error_msg = f"Required file not found: {input_file} at {input_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logger.debug(f"Reading {input_file}")
        
        # Read CSV file
        try:
            df = pd.read_csv(input_path, encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 encoding failed for {input_file}, trying latin-1")
            df = pd.read_csv(input_path, encoding="latin-1")
        
        logger.debug(f"{input_file}: {len(df)} rows, {len(df.columns)} columns")
        
        # Validate required columns exist
        if "delivery" not in df.columns:
            error_msg = f"Required column 'delivery' not found in {input_file}. Available columns: {list(df.columns)}"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        # Extract deliveries
        df["delivery"] = df["delivery"].fillna(0).astype(int)
        deliveries_df = df["delivery"].drop_duplicates()
        
        delivery_count = len(deliveries_df)
        logger.info(f"Extracted {delivery_count} unique deliveries")
        
        # Save to CSV
        output_path = f"{constant.OUTPUT_PATH}/dashboard/{output_file}"
        deliveries_df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved deliveries to {output_file}")
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error extracting deliveries: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def extract_to_number_from_zorf_huto_link_for_dashboard() -> None:
    """
    Extract unique TO numbers from ZORF HUTO LINK files.
    
    Reads zorf_hu_to_link_likp.csv, zorf_hu_to_link_vl06f.csv, and zorf_huto_lnkhis_likp.csv,
    extracts unique TO numbers from each, and saves them to separate CSV files.
    
    Raises:
        FileNotFoundError: If any required file is missing
        KeyError: If required columns don't exist
        ValueError: If data processing fails
    """
    try:
        logger.info("Starting TO number extraction from ZORF HUTO LINK files")
        
        file_paths = {
            "zorf_hu_to_link_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_hu_to_link_likp.csv",
            "zorf_hu_to_link_vl06f": f"{constant.OUTPUT_PATH}/dashboard/zorf_hu_to_link_vl06f.csv",
            "zorf_huto_lnkhis_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_huto_lnkhis_likp.csv"
        }
        
        # Validate files exist
        for name, path in file_paths.items():
            if not Path(path).exists():
                error_msg = f"Required file not found: {name} at {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            logger.debug(f"Found {name} file: {path}")
        
        # Process each file
        output_files = {
            "zorf_hu_to_link_likp": "hu_to_link_likp_to_numbers.csv",
            "zorf_hu_to_link_vl06f": "hu_to_link_vl06f_to_numbers.csv",
            "zorf_huto_lnkhis_likp": "huto_lnkhis_likp_to_numbers.csv"
        }
        
        for file_key, input_path in file_paths.items():
            try:
                logger.debug(f"Reading {file_key}")
                
                # Read CSV file
                try:
                    df = pd.read_csv(input_path, encoding="utf-8")
                except UnicodeDecodeError:
                    logger.warning(f"UTF-8 encoding failed for {file_key}, trying latin-1")
                    df = pd.read_csv(input_path, encoding="latin-1")
                
                logger.debug(f"{file_key}: {len(df)} rows, {len(df.columns)} columns")
                
                # Validate required columns exist
                if "to_number" not in df.columns:
                    error_msg = f"Required column 'to_number' not found in {file_key}. Available columns: {list(df.columns)}"
                    logger.error(error_msg)
                    raise KeyError(error_msg)
                
                # Extract TO numbers
                df["to_number"] = df["to_number"].fillna(0).astype(int)
                to_number_df = df["to_number"].drop_duplicates()
                
                to_number_count = len(to_number_df)
                logger.info(f"Extracted {to_number_count} unique TO numbers from {file_key}")
                
                # Save to CSV
                output_path = f"{constant.OUTPUT_PATH}/dashboard/{output_files[file_key]}"
                to_number_df.to_csv(output_path, index=False)
                logger.info(f"Successfully saved TO numbers to {output_files[file_key]}")
                
            except (FileNotFoundError, KeyError):
                raise
            except Exception as e:
                error_msg = f"Error processing {file_key}: {e}"
                logger.error(error_msg, exc_info=True)
                raise RuntimeError(error_msg) from e
        
        logger.info("Successfully extracted TO numbers from all ZORF HUTO LINK files")
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error extracting TO numbers: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def convert_likp_for_dashboard() -> None:
    """
    Convert and rename LIKP dashboard file.
    
    Converts the LIKP text file to CSV and renames columns according to LIKP_DF mapping.
    
    Raises:
        FileNotFoundError: If LIKP file doesn't exist
        ValueError: If conversion or renaming fails
    """
    try:
        logger.info("Starting LIKP dashboard file conversion and renaming")
        
        convert_to_csv("likp_dashboard", "dashboard")
        logger.info("LIKP file converted to CSV successfully")
        
        rename("likp_dashboard", "dashboard", constant.LIKP_DF)
        logger.info("LIKP file columns renamed successfully")
        
    except FileNotFoundError as e:
        logger.error(f"File not found during LIKP conversion: {e}")
        raise
    except Exception as e:
        error_msg = f"Error converting/renaming LIKP file: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def convert_vl06f_for_dashboard() -> None:
    """
    Convert and rename VL06F dashboard file.
    
    Converts the VL06F text file to CSV and renames columns according to VL06F_DF mapping.
    Handles 'Handling Unit' column as string type.
    
    Raises:
        FileNotFoundError: If VL06F file doesn't exist
        ValueError: If conversion or renaming fails
    """
    try:
        logger.info("Starting VL06F dashboard file conversion and renaming")
        
        convert_to_csv("vl06f_dashboard", "dashboard", dtype={"Handling Unit": "str"})
        logger.info("VL06F file converted to CSV successfully")
        
        rename("vl06f_dashboard", "dashboard", constant.VL06F_DF, dtype={"Handling Unit": "str"})
        logger.info("VL06F file columns renamed successfully")
        
    except FileNotFoundError as e:
        logger.error(f"File not found during VL06F conversion: {e}")
        raise
    except Exception as e:
        error_msg = f"Error converting/renaming VL06F file: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def convert_zorf_huto_link_for_dashboard() -> None:
    """
    Convert and rename ZORF HUTO LINK dashboard files.
    
    Converts and renames three ZORF HUTO LINK files:
    - zorf_hu_to_link_likp
    - zorf_hu_to_link_vl06f
    - zorf_huto_lnkhis_likp
    
    Handles 'Handling Unit' column as string type.
    
    Raises:
        FileNotFoundError: If any ZORF file doesn't exist
        ValueError: If conversion or renaming fails
    """
    try:
        logger.info("Starting ZORF HUTO LINK dashboard files conversion and renaming")
        
        files = ["zorf_hu_to_link_likp", "zorf_hu_to_link_vl06f", "zorf_huto_lnkhis_likp"]
        
        for filename in files:
            try:
                logger.debug(f"Converting {filename}")
                convert_to_csv(filename, "dashboard", dtype={"Handling Unit": "str"})
                logger.debug(f"{filename} converted to CSV successfully")
                
                logger.debug(f"Renaming {filename}")
                rename(filename, "dashboard", constant.HUTOLINK_DASHBOARD_DF, dtype={"Handling Unit": "str"})
                logger.debug(f"{filename} columns renamed successfully")
                
            except FileNotFoundError as e:
                logger.error(f"File not found during {filename} conversion: {e}")
                raise
            except Exception as e:
                error_msg = f"Error converting/renaming {filename}: {e}"
                logger.error(error_msg, exc_info=True)
                raise RuntimeError(error_msg) from e
        
        logger.info("Successfully converted and renamed all ZORF HUTO LINK files")
        
    except (FileNotFoundError, RuntimeError):
        raise
    except Exception as e:
        error_msg = f"Unexpected error in ZORF HUTO LINK conversion: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def convert_ltap_to_numbers() -> None:
    """
    Convert and rename LTAP TO numbers files.
    
    Converts and renames three LTAP files:
    - ltap_likp_to_numbers
    - ltap_vl06f_to_numbers
    - ltap_likp_to_numbers_two
    
    Raises:
        FileNotFoundError: If any LTAP file doesn't exist
        ValueError: If conversion or renaming fails
    """
    try:
        logger.info("Starting LTAP TO numbers files conversion and renaming")
        
        files = ["ltap_likp_to_numbers", "ltap_vl06f_to_numbers", "ltap_likp_to_numbers_two"]
        
        for filename in files:
            try:
                logger.debug(f"Converting {filename}")
                convert_to_csv(filename, "dashboard")
                logger.debug(f"{filename} converted to CSV successfully")
                
                logger.debug(f"Renaming {filename}")
                rename(filename, "dashboard", constant.LTAP_DASHBOARD_DF)
                logger.debug(f"{filename} columns renamed successfully")
                
            except FileNotFoundError as e:
                logger.error(f"File not found during {filename} conversion: {e}")
                raise
            except Exception as e:
                error_msg = f"Error converting/renaming {filename}: {e}"
                logger.error(error_msg, exc_info=True)
                raise RuntimeError(error_msg) from e
        
        logger.info("Successfully converted and renamed all LTAP TO numbers files")
        
    except (FileNotFoundError, RuntimeError):
        raise
    except Exception as e:
        error_msg = f"Unexpected error in LTAP conversion: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

