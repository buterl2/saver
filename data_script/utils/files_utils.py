import pandas as pd
import data_script.config.constants as constant
from data_script.utils.logger import setup_logger
from typing import Any, Optional, Dict
from pathlib import Path
import json

# Setup logger
logger = setup_logger("file_transform")

def convert_to_csv(filename: str, folder: str, dtype: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Convert a tab-separated text file to CSV format.

    Args:
        filename: Name of the file (without extension) to convert
        folder: Name of the folder where the file is located
        dtype: Optional dictionary mapping column names to data types.

    Returns:
        DataFrame: The converted data as a pandas DataFrame

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file cannot be decoded with any standard encoding
        pd.errors.EmptyDataError: If the file is empty
    """
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    file_path = f"{constant.OUTPUT_PATH}/{folder}/{filename}"
    txt_file_path = f"{file_path}.txt"

    logger.info(f"Started converting {filename}")

    # Check if the file exists
    if not Path(txt_file_path).exists():
        error_msg = f"File does not exists: {txt_file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    for encoding in encodings:
        try:
            logger.debug(f"Attempting to read {filename} with encoding: {encoding}")

            # Read header to get column names
            df = pd.read_csv(f"{file_path}.txt", sep="\t", skiprows=3, nrows=1, header=0, encoding=encoding)
            columns = df.columns.tolist()

            # Read full data
            df = pd.read_csv(f"{file_path}.txt", sep="\t", skiprows=5, header=None, names=columns, on_bad_lines="skip", encoding=encoding, dtype=dtype)
            df = df.dropna(how="all")

            # Save to CSV
            df.to_csv(f"{file_path}.csv", index=False, encoding="utf-8")
            return df

        except (UnicodeDecodeError, UnicodeError) as e:
            logger.warning(f"Failed to decode {filename} with encoding {encoding}: {e}")
            continue
        except pd.errors.EmptyDataError:
            logger.error(f"File is empty: {txt_file_path}")
            raise
        except Exception as e:
            logger.error(f"Error converting file {filename} with encoding {encoding}: {e}", exc_info=True)
            raise

    error_msg = f"Could not decode file {filename} with any standard encoding. Tried: {', '.join(encodings)}"
    logger.error(error_msg)
    raise ValueError(error_msg)

def rename(filename: str, folder: str, mapping: Dict[str, str], dtype: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Rename columns of a CSV file

    Args:
        filename: Name of the file (without extension) to convert
        folder: Name of the folder where the file is located
        mapping: Dictionary mapping columns names to new names
        dtype: Optional dictionary mapping column names to data types

    Returns:
        DataFrame: The converted data as a pandas DataFrame

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If mapping is empty or columns don't exists in the file
        pd.errors.EmptyDataError: If the file is empty
    """
    file_path = f"{constant.OUTPUT_PATH}/{folder}/{filename}"
    csv_file_path = f"{file_path}.csv"

    logger.info(f"Started renaming columns in {filename}")

    # Check if the file exists
    if not Path(csv_file_path).exists():
        error_msg = f"File does not exists: {csv_file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        logger.debug(f"Reading {filename}")

        # Read CSV file
        try:
            df = pd.read_csv(csv_file_path, dtype=dtype, encoding="utf-8")
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            logger.warning(f"UTF-8 encoding failed for {filename}, trying latin-1")
            df = pd.read_csv(csv_file_path, dtype=dtype, encoding="latin-1")

        logger.debug(f"File contains {len(df)} rows and {len(df.columns)} columns")
        logger.debug(f"Original columns: {list(df.columns)}")
        
        # Rename columns
        df = df.rename(columns=mapping)
        logger.debug(f"Renamed columns: {mapping}")
        logger.debug(f"New columns: {list(df.columns)}")

        # Save back to CSV
        df.to_csv(csv_file_path, index=False, encoding="utf-8")
        logger.info(f"Successfully renamed columns in {filename}. Renamed {len(mapping)} column(s)")

        return df

    except FileNotFoundError:
        # Re-raise FileNotFoundError
        raise
    except pd.errors.EmptyDataError:
        error_msg = f"File is empty: {csv_file_path}"
        logger.error(error_msg)
        raise
    except ValueError as e:
        # Re-raise ValueError
        raise
    except PermissionError as e:
        error_msg = f"Permission denied when writing to {csv_file_path}: {e}"
        logger.error(error_msg)
        raise PermissionError(error_msg) from e
    except Exception as e:
        error_msg = f"Error renaming columns in {filename}: {e}"
        logger.error(error_msg)
        raise

def convert_to_json(filename: str, folder: str, dictionary: Dict[str, Any]) -> None:
    """
    Convert a dictionary to JSON format and save to file.
    
    Args:
        filename: Name of the file (without extension) to create
        folder: Name of the folder where the file should be saved
        dictionary: Dictionary to serialize to JSON
        
    Raises:
        ValueError: If dictionary is None or invalid
        FileNotFoundError: If the output directory doesn't exist and can't be created
        PermissionError: If permission is denied when writing to the file
        TypeError: If dictionary contains non-serializable objects
    """
    try:
        logger.info(f"Starting JSON conversion for {filename} in folder {folder}")
        
        # Validate inputs
        if dictionary is None:
            error_msg = "Dictionary cannot be None"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not isinstance(dictionary, dict):
            error_msg = f"Expected dict, got {type(dictionary)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not filename or not isinstance(filename, str):
            error_msg = f"Filename must be a non-empty string, got {type(filename)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not folder or not isinstance(folder, str):
            error_msg = f"Folder must be a non-empty string, got {type(folder)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Build file path
        output_dir = Path(f"{constant.OUTPUT_PATH}/{folder}")
        file_path = output_dir / f"{filename}.json"
        
        logger.debug(f"Output file path: {file_path}")
        
        # Create directory if it doesn't exist
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured output directory exists: {output_dir}")
        except PermissionError as e:
            error_msg = f"Permission denied creating directory {output_dir}: {e}"
            logger.error(error_msg)
            raise PermissionError(error_msg) from e
        except Exception as e:
            error_msg = f"Error creating directory {output_dir}: {e}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg) from e
        
        # Check if file already exists (for logging)
        if file_path.exists():
            logger.debug(f"File already exists, will be overwritten: {file_path}")
        
        # Validate dictionary can be serialized (basic check)
        try:
            # Try to serialize a small sample to catch obvious issues
            json.dumps(dictionary, indent=4)
            logger.debug("Dictionary passed JSON serialization validation")
        except TypeError as e:
            error_msg = f"Dictionary contains non-serializable objects: {e}"
            logger.error(error_msg)
            raise TypeError(error_msg) from e
        except Exception as e:
            logger.warning(f"Unexpected error during serialization check: {e}")
        
        # Write to file
        try:
            logger.debug(f"Writing dictionary to {file_path}")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(dictionary, f, indent=4, ensure_ascii=False)
            
            # Verify file was created and has content
            if not file_path.exists():
                error_msg = f"File was not created: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            file_size = file_path.stat().st_size
            if file_size == 0:
                logger.warning(f"File was created but is empty: {file_path}")
            else:
                logger.debug(f"File created successfully, size: {file_size} bytes")
            
            # Log dictionary statistics
            dict_size = len(dictionary)
            logger.info(
                f"Successfully converted dictionary to JSON: {file_path}. "
                f"Dictionary contains {dict_size} top-level keys, file size: {file_size} bytes"
            )
        
        except PermissionError as e:
            error_msg = f"Permission denied writing to {file_path}: {e}"
            logger.error(error_msg)
            raise PermissionError(error_msg) from e
        except OSError as e:
            error_msg = f"OS error writing to {file_path}: {e}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
        except TypeError as e:
            error_msg = f"Type error during JSON serialization: {e}"
            logger.error(error_msg)
            raise TypeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error writing JSON file: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
    
    except (ValueError, TypeError) as e:
        logger.error(f"Validation error in convert_to_json: {e}")
        raise
    except (FileNotFoundError, PermissionError, IOError) as e:
        logger.error(f"File operation error in convert_to_json: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in convert_to_json: {e}", exc_info=True)
        raise RuntimeError(f"Unexpected error converting to JSON: {e}") from e