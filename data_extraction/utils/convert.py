import pandas as pd
import data_extraction.config.config as config
import json
from data_extraction.utils import default_logger as logger

def convert_to_csv(filename):
    # Try UTF-8 first (code page 1100), with error handling
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(f"{config.OUTPUT_PATH}{filename}.txt", sep='\t', skiprows=3, nrows=1, header=0, encoding=encoding)
            columns = df.columns.tolist()
            df = pd.read_csv(f"{config.OUTPUT_PATH}{filename}.txt", sep='\t', skiprows=5, header=None, names=columns, on_bad_lines='skip', encoding=encoding)
            df = df.dropna(how='all')
            df.to_csv(f"{config.OUTPUT_PATH}{filename}.csv", index=False, encoding='utf-8')
            logger.info(f"{filename} was successfully converted to CSV")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    raise ValueError("Could not decode file with any standard encoding")

def convert_to_json(filename, dictionary):
    with open(f"{config.OUTPUT_PATH}{filename}.json", "w") as f:
        json.dump(dictionary, f, indent=4)
    logger.info(f"{filename} was successfully converted to JSON")