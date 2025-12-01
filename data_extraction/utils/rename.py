import pandas as pd
import data_extraction.config.config as config
from data_extraction.utils import default_logger as logger

def rename(filename, mapping):
    df = pd.read_csv(f"{config.OUTPUT_PATH}{filename}.csv")
    df = df.rename(columns=mapping)
    df.to_csv(f"{config.OUTPUT_PATH}{filename}.csv", index=False)
    