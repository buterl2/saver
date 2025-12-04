import data_extraction.config.config as config
import pandas as pd
from data_extraction.utils import default_logger as logger

def transform_routes():
    # CONVERT 
    df = pd.read_excel(f"{config.OUTPUT_PATH}routes.xlsx")
    df.to_csv(f"{config.OUTPUT_PATH}routes.csv", index=False) 