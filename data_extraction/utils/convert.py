import pandas as pd
import data_extraction.config.config as config
import json
from data_extraction.utils import default_logger as logger

def convert_to_csv(filename, dtype=None):
    """
    Convert a tab-separated text file to CSV format.
    
    Args:
        filename: Name of the file (without extension) to convert
        dtype: Optional dictionary mapping column names to data types.
               For example: {'column_name': 'str'} to read a column as string.
               Useful for preventing scientific notation in large numbers.
    
    Returns:
        DataFrame: The converted data as a pandas DataFrame
    """
    # Try UTF-8 first (code page 1100), with error handling
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(f"{config.OUTPUT_PATH}{filename}.txt", sep='\t', skiprows=3, nrows=1, header=0, encoding=encoding)
            columns = df.columns.tolist()
            df = pd.read_csv(f"{config.OUTPUT_PATH}{filename}.txt", sep='\t', skiprows=5, header=None, names=columns, on_bad_lines='skip', encoding=encoding, dtype=dtype)
            df = df.dropna(how='all')
            df.to_csv(f"{config.OUTPUT_PATH}{filename}.csv", index=False, encoding='utf-8')
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    raise ValueError("Could not decode file with any standard encoding")

def convert_to_json(filename, dictionary):
    with open(f"{config.OUTPUT_PATH}{filename}.json", "w") as f:
        json.dump(dictionary, f, indent=4)