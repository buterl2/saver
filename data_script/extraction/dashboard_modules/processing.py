from typing import Dict, Set, Any, Union, List
import data_script.config.constants as constant
from data_script.utils.logger import setup_logger
import pandas as pd
from pathlib import Path
import json

# Set up logger
logger = setup_logger("dashboard_processing")

def determine_floor(source_bin: Union[str, float]) -> List[str]:
    """
    Determine floor(s) based on source bin first character.
    
    Args:
        source_bin: Source bin identifier (string or float)
    
    Returns:
        List of floor names: 'ground_floor', 'first_floor', 'second_floor'
    """
    if pd.isna(source_bin) or source_bin == '':
        return []

    source_bin_str = str(source_bin).strip()
    if len(source_bin_str) == 0:
        return []

    first_char = source_bin_str[0].upper()
    floors = []

    if first_char in ["F", "L", "X"]:
        floors.append("ground_floor")
    if first_char == "N":
        floors.append("first_floor")
    if first_char in ["Y", "O", "W"]:
        floors.append("second_floor")

    return floors

def create_deliveries_all_floors() -> None:
    """
    Create deliveries_all_floors.json with delivery counts by date, floor, and status.
    
    Processes VL06F dashboard data and ZORF files to count unique deliveries
    by date, floor (ground/first/second), and status (A/B/C).
    
    Raises:
        FileNotFoundError: If required files don't exist
        KeyError: If required columns don't exist
        ValueError: If data processing fails
    """
    try:
        logger.info("Starting deliveries_all_floors JSON creation")
        
        # File paths
        vl06f_file = f"{constant.OUTPUT_PATH}/dashboard/vl06f_dashboard.csv"
        zorf_files = {
            "zorf_hu_to_link_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_hu_to_link_likp.csv",
            "zorf_hu_to_link_vl06f": f"{constant.OUTPUT_PATH}/dashboard/zorf_hu_to_link_vl06f.csv",
            "zorf_huto_lnkhis_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_huto_lnkhis_likp.csv"
        }
        
        # Validate files exist
        if not Path(vl06f_file).exists():
            error_msg = f"Required file not found: vl06f_dashboard.csv at {vl06f_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        for name, path in zorf_files.items():
            if not Path(path).exists():
                error_msg = f"Required file not found: {name} at {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        
        logger.debug("Reading VL06F dashboard file")
        try:
            vl06f_df = pd.read_csv(vl06f_file, encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for vl06f_dashboard.csv, trying latin-1")
            vl06f_df = pd.read_csv(vl06f_file, encoding="latin-1")
        
        # Validate required columns
        required_cols = ["delivery", "gi_date", "wm"]
        missing_cols = [col for col in required_cols if col not in vl06f_df.columns]
        if missing_cols:
            error_msg = f"Missing required columns in vl06f_dashboard.csv: {missing_cols}"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        vl06f_df["delivery"] = vl06f_df["delivery"].fillna(0).astype(int)
        logger.debug(f"VL06F dashboard: {len(vl06f_df)} rows")
        
        # Read all zorf files
        all_zorf_dfs = []
        for name, path in zorf_files.items():
            logger.debug(f"Reading {name}")
            try:
                df = pd.read_csv(path, encoding="utf-8")
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 encoding failed for {name}, trying latin-1")
                df = pd.read_csv(path, encoding="latin-1")
            
            if "delivery" not in df.columns or "source_bin" not in df.columns:
                error_msg = f"Missing required columns in {name}"
                logger.error(error_msg)
                raise KeyError(error_msg)
            
            df["delivery"] = df["delivery"].fillna(0).astype(int)
            all_zorf_dfs.append(df)
            logger.debug(f"{name}: {len(df)} rows")
        
        # Create delivery -> floors mapping
        logger.debug("Creating delivery to floors mapping")
        delivery_to_floors: Dict[int, Set[str]] = {}
        
        for zorf_df in all_zorf_dfs:
            for _, row in zorf_df.iterrows():
                delivery = int(row['delivery'])
                source_bin = row['source_bin']
                
                if delivery == 0:
                    continue
                
                floors = determine_floor(source_bin)
                
                if delivery not in delivery_to_floors:
                    delivery_to_floors[delivery] = set()
                
                delivery_to_floors[delivery].update(floors)
        
        logger.info(f"Mapped {len(delivery_to_floors)} deliveries to floors")
        
        # Process VL06F data and track unique deliveries
        logger.debug("Processing VL06F data and counting unique deliveries")
        result: Dict[str, Dict[str, Any]] = {}
        
        for _, row in vl06f_df.iterrows():
            delivery = int(row['delivery'])
            gi_date = row['gi_date']
            wm = str(row['wm']).strip().upper()
            
            if delivery == 0:
                continue
            
            if wm not in ['A', 'B', 'C']:
                continue
            
            if pd.isna(gi_date) or gi_date == '':
                continue
            
            # Format date
            try:
                if isinstance(gi_date, str):
                    date_str = gi_date
                else:
                    date_str = pd.to_datetime(gi_date).strftime("%d.%m.%Y")
            except Exception:
                continue
            
            # Initialize date entry if not exists
            if date_str not in result:
                result[date_str] = {
                    'ground_floor': {
                        'a': {'amount_of_deliveries': set()},
                        'b': {'amount_of_deliveries': set()},
                        'c': {'amount_of_deliveries': set()}
                    },
                    'first_floor': {
                        'a': {'amount_of_deliveries': set()},
                        'b': {'amount_of_deliveries': set()},
                        'c': {'amount_of_deliveries': set()}
                    },
                    'second_floor': {
                        'a': {'amount_of_deliveries': set()},
                        'b': {'amount_of_deliveries': set()},
                        'c': {'amount_of_deliveries': set()}
                    },
                    'a': {'amount_of_deliveries': set()},
                    'b': {'amount_of_deliveries': set()},
                    'c': {'amount_of_deliveries': set()}
                }
            
            # Get floors for this delivery
            floors = delivery_to_floors.get(delivery, set())
            
            if not floors:
                continue
            
            # Add this delivery to each floor it belongs to
            for floor in floors:
                result[date_str][floor][wm.lower()]['amount_of_deliveries'].add(delivery)
            
            # Add to total count
            result[date_str][wm.lower()]['amount_of_deliveries'].add(delivery)
        
        # Convert sets to counts
        logger.debug("Converting sets to counts")
        for date_str in result:
            for floor in ['ground_floor', 'first_floor', 'second_floor']:
                for status in ['a', 'b', 'c']:
                    result[date_str][floor][status]['amount_of_deliveries'] = len(result[date_str][floor][status]['amount_of_deliveries'])
            
            for status in ['a', 'b', 'c']:
                result[date_str][status]['amount_of_deliveries'] = len(result[date_str][status]['amount_of_deliveries'])
        
        # Save to JSON file
        output_path = f"{constant.OUTPUT_PATH}/dashboard/deliveries_all_floors.json"
        logger.info(f"Saving deliveries_all_floors.json to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Successfully created deliveries_all_floors.json with {len(result)} dates")
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error creating deliveries_all_floors.json: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def create_hu_all_floors() -> None:
    """
    Create hu_all_floors.json with HU counts by date, floor, and picked status.
    
    Processes VL06F dashboard data, ZORF files, and LTAP files to determine
    which HUs are picked/not_picked and count them by date and floor.
    
    Raises:
        FileNotFoundError: If required files don't exist
        KeyError: If required columns don't exist
        ValueError: If data processing fails
    """
    try:
        logger.info("Starting hu_all_floors JSON creation")
        
        # File paths
        vl06f_file = f"{constant.OUTPUT_PATH}/dashboard/vl06f_dashboard.csv"
        zorf_files = {
            "zorf_hu_to_link_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_hu_to_link_likp.csv",
            "zorf_hu_to_link_vl06f": f"{constant.OUTPUT_PATH}/dashboard/zorf_hu_to_link_vl06f.csv",
            "zorf_huto_lnkhis_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_huto_lnkhis_likp.csv"
        }
        ltap_files = {
            "ltap_likp_to_numbers": f"{constant.OUTPUT_PATH}/dashboard/ltap_likp_to_numbers.csv",
            "ltap_likp_to_numbers_two": f"{constant.OUTPUT_PATH}/dashboard/ltap_likp_to_numbers_two.csv",
            "ltap_vl06f_to_numbers": f"{constant.OUTPUT_PATH}/dashboard/ltap_vl06f_to_numbers.csv"
        }
        
        # Validate files exist
        if not Path(vl06f_file).exists():
            error_msg = f"Required file not found: vl06f_dashboard.csv at {vl06f_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        for name, path in zorf_files.items():
            if not Path(path).exists():
                error_msg = f"Required file not found: {name} at {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        
        for name, path in ltap_files.items():
            if not Path(path).exists():
                error_msg = f"Required file not found: {name} at {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        
        logger.debug("Reading VL06F dashboard file")
        try:
            vl06f_df = pd.read_csv(vl06f_file, dtype={'hu': str}, encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for vl06f_dashboard.csv, trying latin-1")
            vl06f_df = pd.read_csv(vl06f_file, dtype={'hu': str}, encoding="latin-1")
        
        if "hu" not in vl06f_df.columns or "gi_date" not in vl06f_df.columns:
            error_msg = "Missing required columns in vl06f_dashboard.csv"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        logger.debug(f"VL06F dashboard: {len(vl06f_df)} rows")
        
        # Read all zorf files
        all_zorf_dfs = []
        for name, path in zorf_files.items():
            logger.debug(f"Reading {name}")
            try:
                df = pd.read_csv(path, dtype={'hu': str}, encoding="utf-8")
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 encoding failed for {name}, trying latin-1")
                df = pd.read_csv(path, dtype={'hu': str}, encoding="latin-1")
            
            if "hu" not in df.columns or "to_number" not in df.columns or "source_bin" not in df.columns:
                error_msg = f"Missing required columns in {name}"
                logger.error(error_msg)
                raise KeyError(error_msg)
            
            all_zorf_dfs.append(df)
            logger.debug(f"{name}: {len(df)} rows")
        
        # Read all ltap files
        all_ltap_dfs = []
        for name, path in ltap_files.items():
            logger.debug(f"Reading {name}")
            try:
                df = pd.read_csv(path, encoding="utf-8")
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 encoding failed for {name}, trying latin-1")
                df = pd.read_csv(path, encoding="latin-1")
            
            if "to_number" not in df.columns or "confirmation_date" not in df.columns:
                error_msg = f"Missing required columns in {name}"
                logger.error(error_msg)
                raise KeyError(error_msg)
            
            all_ltap_dfs.append(df)
            logger.debug(f"{name}: {len(df)} rows")
        
        # Create HU to info mapping
        logger.debug("Creating HU to info mapping")
        hu_to_info: Dict[str, Dict[str, Set[Any]]] = {}
        
        for zorf_df in all_zorf_dfs:
            for _, row in zorf_df.iterrows():
                hu = str(row['hu']).strip() if pd.notna(row['hu']) else ''
                to_number = row['to_number']
                source_bin = row['source_bin']
                
                if hu == '':
                    continue
                
                if hu not in hu_to_info:
                    hu_to_info[hu] = {'to_numbers': set(), 'source_bins': set()}
                
                if pd.notna(to_number):
                    hu_to_info[hu]['to_numbers'].add(to_number)
                if pd.notna(source_bin):
                    hu_to_info[hu]['source_bins'].add(source_bin)
        
        logger.info(f"Mapped {len(hu_to_info)} HUs to info")
        
        # Create to_number to confirmation_dates mapping
        logger.debug("Creating TO number to confirmation dates mapping")
        to_number_to_confirmation_dates: Dict[Any, List[bool]] = {}
        
        for ltap_df in all_ltap_dfs:
            for _, row in ltap_df.iterrows():
                to_number = row['to_number']
                confirmation_date = row['confirmation_date']
                
                if pd.notna(to_number):
                    if to_number not in to_number_to_confirmation_dates:
                        to_number_to_confirmation_dates[to_number] = []
                    
                    if pd.notna(confirmation_date) and str(confirmation_date).strip() != '':
                        to_number_to_confirmation_dates[to_number].append(True)
                    else:
                        to_number_to_confirmation_dates[to_number].append(False)
        
        logger.info(f"Mapped {len(to_number_to_confirmation_dates)} TO numbers to confirmation status")
        
        # Process VL06F data
        logger.debug("Processing VL06F data and determining picked status")
        result: Dict[str, Dict[str, Any]] = {}
        
        for _, row in vl06f_df.iterrows():
            hu = str(row['hu']).strip() if pd.notna(row['hu']) else ''
            gi_date = row['gi_date']
            
            if hu == '':
                continue
            
            if pd.isna(gi_date) or gi_date == '':
                continue
            
            # Format date
            try:
                if isinstance(gi_date, str):
                    date_str = gi_date
                else:
                    date_str = pd.to_datetime(gi_date).strftime("%d.%m.%Y")
            except Exception:
                continue
            
            # Convert HU from vl06f format to zorf format
            hu_with_zeros = f"00{hu}"
            
            if hu_with_zeros not in hu_to_info:
                continue
            
            # Get all to_numbers for this HU
            to_numbers = hu_to_info[hu_with_zeros]['to_numbers']
            
            if len(to_numbers) == 0:
                continue
            
            # Check if all to_numbers have confirmation_date
            is_picked = True
            for to_number in to_numbers:
                if to_number not in to_number_to_confirmation_dates:
                    is_picked = False
                    break
                
                confirmation_statuses = to_number_to_confirmation_dates[to_number]
                if len(confirmation_statuses) == 0 or not all(confirmation_statuses):
                    is_picked = False
                    break
            
            # Get floors from source_bins
            source_bins = hu_to_info[hu_with_zeros]['source_bins']
            floors = set()
            for source_bin in source_bins:
                floor_list = determine_floor(source_bin)
                floors.update(floor_list)
            
            if not floors:
                continue
            
            # Initialize date entry if not exists
            if date_str not in result:
                result[date_str] = {
                    'ground_floor': {
                        'picked': {'amount_of_hu': set()},
                        'not_picked': {'amount_of_hu': set()}
                    },
                    'first_floor': {
                        'picked': {'amount_of_hu': set()},
                        'not_picked': {'amount_of_hu': set()}
                    },
                    'second_floor': {
                        'picked': {'amount_of_hu': set()},
                        'not_picked': {'amount_of_hu': set()}
                    },
                    'picked': {'amount_of_hu': set()},
                    'not_picked': {'amount_of_hu': set()}
                }
            
            # Add this HU to each floor it belongs to
            picked_status = 'picked' if is_picked else 'not_picked'
            
            for floor in floors:
                result[date_str][floor][picked_status]['amount_of_hu'].add(hu)
            
            result[date_str][picked_status]['amount_of_hu'].add(hu)
        
        # Convert sets to counts
        logger.debug("Converting sets to counts")
        for date_str in result:
            for floor in ['ground_floor', 'first_floor', 'second_floor']:
                result[date_str][floor]['picked']['amount_of_hu'] = len(result[date_str][floor]['picked']['amount_of_hu'])
                result[date_str][floor]['not_picked']['amount_of_hu'] = len(result[date_str][floor]['not_picked']['amount_of_hu'])
            
            result[date_str]['picked']['amount_of_hu'] = len(result[date_str]['picked']['amount_of_hu'])
            result[date_str]['not_picked']['amount_of_hu'] = len(result[date_str]['not_picked']['amount_of_hu'])
        
        # Save to JSON file
        output_path = f"{constant.OUTPUT_PATH}/dashboard/hu_all_floors.json"
        logger.info(f"Saving hu_all_floors.json to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Successfully created hu_all_floors.json with {len(result)} dates")
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error creating hu_all_floors.json: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def create_lines_all_floors() -> None:
    """
    Create lines_all_floors.json with line counts by date, floor, and picked status.
    
    Processes VL06F dashboard data and LTAP files to count lines by date,
    floor, and whether they are picked or not.
    
    Raises:
        FileNotFoundError: If required files don't exist
        KeyError: If required columns don't exist
        ValueError: If data processing fails
    """
    try:
        logger.info("Starting lines_all_floors JSON creation")
        
        # File paths
        vl06f_file = f"{constant.OUTPUT_PATH}/dashboard/vl06f_dashboard.csv"
        ltap_file = f"{constant.OUTPUT_PATH}/dashboard/ltap_vl06f_to_numbers.csv"
        
        # Validate files exist
        if not Path(vl06f_file).exists():
            error_msg = f"Required file not found: vl06f_dashboard.csv at {vl06f_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        if not Path(ltap_file).exists():
            error_msg = f"Required file not found: ltap_vl06f_to_numbers.csv at {ltap_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logger.debug("Reading VL06F dashboard file")
        try:
            vl06f_df = pd.read_csv(vl06f_file, encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for vl06f_dashboard.csv, trying latin-1")
            vl06f_df = pd.read_csv(vl06f_file, encoding="latin-1")
        
        if "delivery" not in vl06f_df.columns or "gi_date" not in vl06f_df.columns:
            error_msg = "Missing required columns in vl06f_dashboard.csv"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        vl06f_df["delivery"] = vl06f_df["delivery"].fillna(0).astype(int)
        logger.debug(f"VL06F dashboard: {len(vl06f_df)} rows")
        
        logger.debug("Reading LTAP file")
        try:
            ltap_vl06f_to_numbers_df = pd.read_csv(ltap_file, encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for ltap_vl06f_to_numbers.csv, trying latin-1")
            ltap_vl06f_to_numbers_df = pd.read_csv(ltap_file, encoding="latin-1")
        
        if "destination_bin" not in ltap_vl06f_to_numbers_df.columns or "source_bin" not in ltap_vl06f_to_numbers_df.columns or "confirmation_date" not in ltap_vl06f_to_numbers_df.columns:
            error_msg = "Missing required columns in ltap_vl06f_to_numbers.csv"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        ltap_vl06f_to_numbers_df["destination_bin"] = ltap_vl06f_to_numbers_df["destination_bin"].fillna(0).astype(int)
        logger.debug(f"LTAP file: {len(ltap_vl06f_to_numbers_df)} rows")
        
        # Create delivery -> date mapping
        logger.debug("Creating delivery to date mapping")
        unique_deliveries = vl06f_df["delivery"].drop_duplicates()
        delivery_to_date: Dict[int, str] = {}
        
        for _, row in vl06f_df.iterrows():
            delivery = int(row['delivery'])
            gi_date = row['gi_date']
            
            if delivery == 0:
                continue
            
            if pd.isna(gi_date) or gi_date == '':
                continue
            
            try:
                if isinstance(gi_date, str):
                    date_str = gi_date
                else:
                    date_str = pd.to_datetime(gi_date).strftime("%d.%m.%Y")
            except Exception:
                continue
            
            if delivery not in delivery_to_date:
                delivery_to_date[delivery] = date_str
        
        logger.info(f"Mapped {len(delivery_to_date)} deliveries to dates")
        
        # Process each unique delivery
        logger.debug("Processing deliveries and counting lines")
        result: Dict[str, Dict[str, Any]] = {}
        
        for delivery in unique_deliveries:
            if delivery == 0:
                continue
            
            if delivery not in delivery_to_date:
                continue
            
            date_str = delivery_to_date[delivery]
            
            # Find matching rows in LTAP file
            matching_rows = ltap_vl06f_to_numbers_df[ltap_vl06f_to_numbers_df["destination_bin"] == delivery]
            
            if len(matching_rows) == 0:
                continue
            
            # Initialize date entry if not exists
            if date_str not in result:
                result[date_str] = {
                    'ground_floor': {
                        'picked': {'amount_of_lines': 0},
                        'not_picked': {'amount_of_lines': 0}
                    },
                    'first_floor': {
                        'picked': {'amount_of_lines': 0},
                        'not_picked': {'amount_of_lines': 0}
                    },
                    'second_floor': {
                        'picked': {'amount_of_lines': 0},
                        'not_picked': {'amount_of_lines': 0}
                    },
                    'picked': {'amount_of_lines': 0},
                    'not_picked': {'amount_of_lines': 0}
                }
            
            # Process each row
            for _, row in matching_rows.iterrows():
                source_bin = row['source_bin']
                confirmation_date = row['confirmation_date']
                
                floors = determine_floor(source_bin)
                
                if not floors:
                    continue
                
                is_picked = pd.notna(confirmation_date) and str(confirmation_date).strip() != ''
                picked_status = 'picked' if is_picked else 'not_picked'
                
                for floor in floors:
                    result[date_str][floor][picked_status]['amount_of_lines'] += 1
                
                result[date_str][picked_status]['amount_of_lines'] += 1
        
        # Save to JSON file
        output_path = f"{constant.OUTPUT_PATH}/dashboard/lines_all_floors.json"
        logger.info(f"Saving lines_all_floors.json to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Successfully created lines_all_floors.json with {len(result)} dates")
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error creating lines_all_floors.json: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def create_deliveries_all_floors_pgi() -> None:
    """
    Create deliveries_all_floors_pgi.json with PGI delivery counts for today.
    
    Processes LIKP dashboard data and ZORF files to count unique deliveries
    by floor for today's date (PGI - Post Goods Issue).
    
    Raises:
        FileNotFoundError: If required files don't exist
        KeyError: If required columns don't exist
        ValueError: If data processing fails
    """
    try:
        logger.info("Starting deliveries_all_floors_pgi JSON creation")
        
        today = constant.get_today()
        
        # File paths
        likp_file = f"{constant.OUTPUT_PATH}/dashboard/likp_dashboard.csv"
        zorf_files = {
            "zorf_hu_to_link_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_hu_to_link_likp.csv",
            "zorf_huto_lnkhis_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_huto_lnkhis_likp.csv"
        }
        
        # Validate files exist
        if not Path(likp_file).exists():
            error_msg = f"Required file not found: likp_dashboard.csv at {likp_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        for name, path in zorf_files.items():
            if not Path(path).exists():
                error_msg = f"Required file not found: {name} at {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        
        logger.debug("Reading LIKP dashboard file")
        try:
            likp_df = pd.read_csv(likp_file, encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for likp_dashboard.csv, trying latin-1")
            likp_df = pd.read_csv(likp_file, encoding="latin-1")
        
        if "delivery" not in likp_df.columns:
            error_msg = "Missing required column 'delivery' in likp_dashboard.csv"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        likp_df["delivery"] = likp_df["delivery"].fillna(0).astype(int)
        unique_deliveries = set(likp_df["delivery"].drop_duplicates())
        unique_deliveries.discard(0)
        logger.debug(f"Found {len(unique_deliveries)} unique deliveries")
        
        # Read zorf files
        all_zorf_dfs = []
        for name, path in zorf_files.items():
            logger.debug(f"Reading {name}")
            try:
                df = pd.read_csv(path, encoding="utf-8")
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 encoding failed for {name}, trying latin-1")
                df = pd.read_csv(path, encoding="latin-1")
            
            if "delivery" not in df.columns or "source_bin" not in df.columns:
                error_msg = f"Missing required columns in {name}"
                logger.error(error_msg)
                raise KeyError(error_msg)
            
            df["delivery"] = df["delivery"].fillna(0).astype(int)
            all_zorf_dfs.append(df)
            logger.debug(f"{name}: {len(df)} rows")
        
        # Create delivery -> floors mapping
        logger.debug("Creating delivery to floors mapping")
        delivery_to_floors: Dict[int, Set[str]] = {}
        
        for zorf_df in all_zorf_dfs:
            for _, row in zorf_df.iterrows():
                delivery = int(row['delivery'])
                source_bin = row['source_bin']
                
                if delivery == 0:
                    continue
                
                floors = determine_floor(source_bin)
                
                if delivery not in delivery_to_floors:
                    delivery_to_floors[delivery] = set()
                
                delivery_to_floors[delivery].update(floors)
        
        logger.info(f"Mapped {len(delivery_to_floors)} deliveries to floors")
        
        # Initialize result dictionary
        result: Dict[str, Dict[str, Any]] = {
            today: {
                'ground_floor': {'amount_of_deliveries_pgi': set()},
                'first_floor': {'amount_of_deliveries_pgi': set()},
                'second_floor': {'amount_of_deliveries_pgi': set()},
                'amount_of_deliveries_pgi': set()
            }
        }
        
        # Process each unique delivery
        logger.debug("Processing deliveries and counting by floor")
        for delivery in unique_deliveries:
            floors = delivery_to_floors.get(delivery, set())
            
            if not floors:
                continue
            
            for floor in floors:
                result[today][floor]['amount_of_deliveries_pgi'].add(delivery)
            
            result[today]['amount_of_deliveries_pgi'].add(delivery)
        
        # Convert sets to counts
        logger.debug("Converting sets to counts")
        result[today]['ground_floor']['amount_of_deliveries_pgi'] = len(result[today]['ground_floor']['amount_of_deliveries_pgi'])
        result[today]['first_floor']['amount_of_deliveries_pgi'] = len(result[today]['first_floor']['amount_of_deliveries_pgi'])
        result[today]['second_floor']['amount_of_deliveries_pgi'] = len(result[today]['second_floor']['amount_of_deliveries_pgi'])
        result[today]['amount_of_deliveries_pgi'] = len(result[today]['amount_of_deliveries_pgi'])
        
        # Save to JSON file
        output_path = f"{constant.OUTPUT_PATH}/dashboard/deliveries_all_floors_pgi.json"
        logger.info(f"Saving deliveries_all_floors_pgi.json to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Successfully created deliveries_all_floors_pgi.json for {today}")
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error creating deliveries_all_floors_pgi.json: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def create_hu_all_floors_pgi() -> None:
    """
    Create hu_all_floors_pgi.json with PGI HU counts for today.
    
    Processes ZORF files to count unique HUs by floor for today's date (PGI).
    
    Raises:
        FileNotFoundError: If required files don't exist
        KeyError: If required columns don't exist
        ValueError: If data processing fails
    """
    try:
        logger.info("Starting hu_all_floors_pgi JSON creation")
        
        today = constant.get_today()
        
        # File paths
        zorf_files = {
            "zorf_hu_to_link_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_hu_to_link_likp.csv",
            "zorf_huto_lnkhis_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_huto_lnkhis_likp.csv"
        }
        
        # Validate files exist
        for name, path in zorf_files.items():
            if not Path(path).exists():
                error_msg = f"Required file not found: {name} at {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        
        # Read zorf files
        all_zorf_dfs = []
        for name, path in zorf_files.items():
            logger.debug(f"Reading {name}")
            try:
                df = pd.read_csv(path, dtype={'hu': str}, encoding="utf-8")
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 encoding failed for {name}, trying latin-1")
                df = pd.read_csv(path, dtype={'hu': str}, encoding="latin-1")
            
            if "hu" not in df.columns or "source_bin" not in df.columns:
                error_msg = f"Missing required columns in {name}"
                logger.error(error_msg)
                raise KeyError(error_msg)
            
            all_zorf_dfs.append(df)
            logger.debug(f"{name}: {len(df)} rows")
        
        # Create HU -> floors mapping
        logger.debug("Creating HU to floors mapping")
        hu_to_floors: Dict[str, Set[str]] = {}
        
        for zorf_df in all_zorf_dfs:
            for _, row in zorf_df.iterrows():
                hu = str(row['hu']).strip() if pd.notna(row['hu']) else ''
                source_bin = row['source_bin']
                
                if hu == '':
                    continue
                
                floors = determine_floor(source_bin)
                
                if hu not in hu_to_floors:
                    hu_to_floors[hu] = set()
                
                hu_to_floors[hu].update(floors)
        
        logger.info(f"Mapped {len(hu_to_floors)} HUs to floors")
        
        # Initialize result dictionary
        result: Dict[str, Dict[str, Any]] = {
            today: {
                'ground_floor': {'amount_of_hu_pgi': set()},
                'first_floor': {'amount_of_hu_pgi': set()},
                'second_floor': {'amount_of_hu_pgi': set()},
                'amount_of_hu_pgi': set()
            }
        }
        
        # Process each unique HU
        logger.debug("Processing HUs and counting by floor")
        for hu, floors in hu_to_floors.items():
            if not floors:
                continue
            
            for floor in floors:
                result[today][floor]['amount_of_hu_pgi'].add(hu)
            
            result[today]['amount_of_hu_pgi'].add(hu)
        
        # Convert sets to counts
        logger.debug("Converting sets to counts")
        result[today]['ground_floor']['amount_of_hu_pgi'] = len(result[today]['ground_floor']['amount_of_hu_pgi'])
        result[today]['first_floor']['amount_of_hu_pgi'] = len(result[today]['first_floor']['amount_of_hu_pgi'])
        result[today]['second_floor']['amount_of_hu_pgi'] = len(result[today]['second_floor']['amount_of_hu_pgi'])
        result[today]['amount_of_hu_pgi'] = len(result[today]['amount_of_hu_pgi'])
        
        # Save to JSON file
        output_path = f"{constant.OUTPUT_PATH}/dashboard/hu_all_floors_pgi.json"
        logger.info(f"Saving hu_all_floors_pgi.json to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Successfully created hu_all_floors_pgi.json for {today}")
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error creating hu_all_floors_pgi.json: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def create_lines_all_floors_pgi() -> None:
    """
    Create lines_all_floors_pgi.json with PGI line counts for today.
    
    Processes ZORF files to count lines by floor for today's date (PGI).
    
    Raises:
        FileNotFoundError: If required files don't exist
        KeyError: If required columns don't exist
        ValueError: If data processing fails
    """
    try:
        logger.info("Starting lines_all_floors_pgi JSON creation")
        
        today = constant.get_today()
        
        # File paths
        zorf_files = {
            "zorf_hu_to_link_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_hu_to_link_likp.csv",
            "zorf_huto_lnkhis_likp": f"{constant.OUTPUT_PATH}/dashboard/zorf_huto_lnkhis_likp.csv"
        }
        
        # Validate files exist
        for name, path in zorf_files.items():
            if not Path(path).exists():
                error_msg = f"Required file not found: {name} at {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        
        # Initialize result dictionary
        result: Dict[str, Dict[str, Any]] = {
            today: {
                'ground_floor': {'amount_of_lines_pgi': 0},
                'first_floor': {'amount_of_lines_pgi': 0},
                'second_floor': {'amount_of_lines_pgi': 0},
                'amount_of_lines_pgi': 0
            }
        }
        
        # Process each row (each row represents a line)
        logger.debug("Processing lines and counting by floor")
        for name, path in zorf_files.items():
            logger.debug(f"Reading {name}")
            try:
                zorf_df = pd.read_csv(path, encoding="utf-8")
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 encoding failed for {name}, trying latin-1")
                zorf_df = pd.read_csv(path, encoding="latin-1")
            
            if "source_bin" not in zorf_df.columns:
                error_msg = f"Missing required column 'source_bin' in {name}"
                logger.error(error_msg)
                raise KeyError(error_msg)
            
            for _, row in zorf_df.iterrows():
                source_bin = row['source_bin']
                
                floors = determine_floor(source_bin)
                
                if not floors:
                    continue
                
                for floor in floors:
                    result[today][floor]['amount_of_lines_pgi'] += 1
                
                result[today]['amount_of_lines_pgi'] += 1
        
        # Save to JSON file
        output_path = f"{constant.OUTPUT_PATH}/dashboard/lines_all_floors_pgi.json"
        logger.info(f"Saving lines_all_floors_pgi.json to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Successfully created lines_all_floors_pgi.json for {today}")
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error creating lines_all_floors_pgi.json: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

def create_picking_hourly_dashboard() -> None:
    """
    Create picking_hourly_dashboard.json with hourly picking counts.
    
    Processes bflow_routes, picking productivity files, and LTAP data to count
    lines picked in 30-minute intervals for b_flow routes.
    
    Raises:
        FileNotFoundError: If required files don't exist
        KeyError: If required columns don't exist
        ValueError: If data processing fails
    """
    try:
        logger.info("Starting picking_hourly_dashboard JSON creation")
        
        # File paths
        bflow_routes_file = f"{constant.OUTPUT_PATH}/misc/bflow_routes.csv"
        picking_files = {
            "huto_lnkhis": f"{constant.OUTPUT_PATH}/picking/zorf_huto_lnkhis.csv",
            "hu_to_link": f"{constant.OUTPUT_PATH}/picking/zorf_hu_to_link.csv",
            "ltap": f"{constant.OUTPUT_PATH}/picking/picking.csv"
        }
        
        # Validate files exist
        if not Path(bflow_routes_file).exists():
            error_msg = f"Required file not found: bflow_routes.csv at {bflow_routes_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        for name, path in picking_files.items():
            if not Path(path).exists():
                error_msg = f"Required file not found: {name} at {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        
        # Read bflow_routes.csv
        logger.debug("Reading bflow_routes.csv")
        try:
            bflow_routes_df = pd.read_csv(bflow_routes_file, encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for bflow_routes.csv, trying latin-1")
            bflow_routes_df = pd.read_csv(bflow_routes_file, encoding="latin-1")
        
        if "route" not in bflow_routes_df.columns:
            error_msg = "Missing required column 'route' in bflow_routes.csv"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        valid_routes = set(bflow_routes_df['route'].str.strip().str.upper())
        logger.info(f"Found {len(valid_routes)} valid b_flow routes")
        
        # Read picking productivity files and create document -> route mapping
        logger.debug("Reading picking productivity files and creating document to route mapping")
        document_to_route: Dict[int, str] = {}
        
        for name, path in [("huto_lnkhis", picking_files["huto_lnkhis"]), ("hu_to_link", picking_files["hu_to_link"])]:
            logger.debug(f"Reading {name}")
            try:
                df = pd.read_csv(path, encoding="utf-8")
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 encoding failed for {name}, trying latin-1")
                df = pd.read_csv(path, encoding="latin-1")
            
            if "document" not in df.columns or "route" not in df.columns:
                error_msg = f"Missing required columns in {name}"
                logger.error(error_msg)
                raise KeyError(error_msg)
            
            for _, row in df.iterrows():
                document = row['document']
                route = str(row['route']).strip().upper() if pd.notna(row['route']) else ''
                if pd.notna(document) and route:
                    try:
                        doc_value = int(float(document))
                        document_to_route[doc_value] = route
                    except (ValueError, TypeError):
                        continue
        
        logger.info(f"Mapped {len(document_to_route)} documents to routes")
        
        # Read picking_productivity_ltap.csv
        logger.debug("Reading picking_productivity_ltap.csv")
        try:
            ltap_df = pd.read_csv(picking_files["ltap"], encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 encoding failed for picking_productivity_ltap.csv, trying latin-1")
            ltap_df = pd.read_csv(picking_files["ltap"], encoding="latin-1")
        
        if "destination_bin" not in ltap_df.columns or "confirmation_time" not in ltap_df.columns:
            error_msg = "Missing required columns in picking_productivity_ltap.csv"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        logger.debug(f"LTAP file: {len(ltap_df)} rows")
        
        # Process each row in ltap_df
        logger.debug("Processing LTAP data and counting lines by hour")
        result: Dict[str, Dict[str, int]] = {}
        
        for _, row in ltap_df.iterrows():
            destination_bin = row['destination_bin']
            confirmation_time = row['confirmation_time']
            
            if pd.isna(destination_bin):
                continue
            
            try:
                dest_bin_value = int(float(destination_bin))
            except (ValueError, TypeError):
                continue
            
            if dest_bin_value not in document_to_route:
                continue
            
            route = document_to_route[dest_bin_value]
            
            if route not in valid_routes:
                continue
            
            if pd.isna(confirmation_time) or confirmation_time == '':
                continue
            
            try:
                time_str = str(confirmation_time).strip()
                if ':' not in time_str:
                    continue
                
                time_parts = time_str.split(':')
                if len(time_parts) < 2:
                    continue
                
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                
                # Group into 30-minute intervals
                if minute < 30:
                    hour_key = f"{hour:02d}00"
                else:
                    hour_key = f"{hour:02d}30"
                
                if hour_key not in result:
                    result[hour_key] = {'lines_picked': 0}
                
                result[hour_key]['lines_picked'] += 1
                
            except (ValueError, IndexError, TypeError):
                continue
        
        # Sort by hour key
        sorted_result = dict(sorted(result.items()))
        
        # Save to JSON file
        output_path = f"{constant.OUTPUT_PATH}/dashboard/picking_hourly_dashboard.json"
        logger.info(f"Saving picking_hourly_dashboard.json to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_result, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Successfully created picking_hourly_dashboard.json with {len(sorted_result)} time intervals")
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error creating picking_hourly_dashboard.json: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

