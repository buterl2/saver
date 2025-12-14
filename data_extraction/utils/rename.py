import pandas as pd
import data_extraction.config.config as config
from data_extraction.utils import default_logger as logger
from typing import Any, Optional, Dict

def rename(filename: str, mapping: Dict[str, str], dtype: Optional[Dict[str, str]] = None) -> None:
    df = pd.read_csv(f"{config.OUTPUT_PATH}{filename}.csv", dtype=dtype)
    df = df.rename(columns=mapping)
    df.to_csv(f"{config.OUTPUT_PATH}{filename}.csv", index=False)
    